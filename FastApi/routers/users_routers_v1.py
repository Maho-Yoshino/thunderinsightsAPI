import subprocess
import json
import mariadb
import time
import datetime
import socket
import sys
import requests
import os
import glob
import random
from datetime import datetime, timezone
from celery import Celery
from kombu import Exchange, Queue
from urllib3.exceptions import InsecureRequestWarning
from app.wt_bin_parser.wt_bin_parser import parse_file, parse_data
from fastapi import APIRouter, Path, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import Annotated
from pydantic import BaseModel


router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

# Stop Python from warning about the certificate
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Function to get api token from database
def dbcon():
    # Connect to MariaDB  
    try:
        conn = mariadb.connect(
            user="<username>",
            password="<password>",
            host="192.168.3.1",
            port=13306,
            database="war_thunder_stats_v1"

        )
    except mariadb.Error as e:
        #print(f"Error connecting to MariaDB Platform: {e}")
        #sys.exit(1)
        raise HTTPException(status_code=500, detail="Unable to connect to internal database")
        return
    
    return conn
    
def get_terse(userids):
    delimiter = ";"
    
    # convert int to string
    temp = list(map(str, userids))
    
    useridsString = delimiter.join(temp)
     
    # Get connection
    conn = dbcon()
    
    # Get database cursor
    cur = conn.cursor(dictionary=True)
    
    # Pull token information row if any tokens with more than 5 minutes left exist
    cur.execute("SELECT * FROM WarThunder.AccessToken WHERE WarThunder.AccessToken.LastRefresh > NOW() LIMIT 1")
    
    # Fetch results from select
    results = cur.fetchall()
    
    # Close the cursor after use
    cur.close()

    # Download BLK file
    if results:
        token = results[0]['Token']
        uidHint = results[0]['UidHint']

        # Calls the char server (Probably character server), to get public stats
        url = ['https://char-lw-nl-005-2.warthunder.com/char','https://char-lw-nl-005-3.warthunder.com/char','https://char-lw-nl-005-4.warthunder.com/char','https://char-lw-nl-005-5.warthunder.com/char']
        headers = {'token': token,'action': 'cln_get_users_terse_info','User-Agent': 'wt','usersList': useridsString,'uidHint': str(uidHint)}
        userStatsResponse = requests.post(random.choice(url), headers=headers, stream=True)
        
        binary = bytearray()
        for chunk in userStatsResponse.iter_content(chunk_size=128):
            binary.extend(chunk)

        if len(binary) < 3:
            raise HTTPException(status_code=500, detail="No extra data about user, feel free to try again later.")
            return
        try:
            decodedExtraUserInfo = parse_data(binary)
        except:
            raise HTTPException(status_code=500, detail="We failed to decode the information from the game api or there was no information about the users.")
            return
        
        return decodedExtraUserInfo
    else:
        raise HTTPException(status_code=500, detail="Unable to get a token we needed to connect to Gaijins servers")
        return

# router that provides an endpoint to get user stats directly from Gaijin
@router.get("/direct/{userid}", summary="Gets user info directly from Gaijin.")
async def get_user_direct(userid: Annotated[int, Path(title="The ID of the user to get information about", description="The ID of the user to get information about", gt=0)]):
    
    """
    This endpoint pulls information directly from Gaijin and the schema changes as Gaijin deems it necessary, it therefore isn't documented in depth.
    """
    
    # Get connection
    conn = dbcon()
    
    # Get database cursor
    cur = conn.cursor(dictionary=True)
    
    # Pull token information row if any tokens with more than 5 minutes left exist
    cur.execute("SELECT * FROM WarThunder.AccessToken WHERE WarThunder.AccessToken.LastRefresh > NOW() LIMIT 1")
    
    # Fetch results from select
    results = cur.fetchall()
    
    # Close the cursor after use
    cur.close()

    # Download BLK file
    if results:
        token = results[0]['Token']
        uidHint = results[0]['UidHint']

        # Calls the char server (Probably character server), to get public stats
        url = ['https://char-lw-nl-005-2.warthunder.com/char','https://char-lw-nl-005-3.warthunder.com/char','https://char-lw-nl-005-4.warthunder.com/char','https://char-lw-nl-005-5.warthunder.com/char']
        headers = {'token': token,'action': 'ano_get_public_userstat','User-Agent': 'wt','userid': str(userid),'uidHint': str(uidHint)}
        userStatsResponse = requests.post(random.choice(url), headers=headers, stream=True)

        binary = bytearray()
        for chunk in userStatsResponse.iter_content(chunk_size=128):
            binary.extend(chunk)
        
        if len(binary) < 3:
            raise HTTPException(status_code=500, detail="No data about user, feel free to try again later.")
            return
        
        try:
            decodedUserStats = parse_data(binary)
        except:
            raise HTTPException(status_code=500, detail="We failed to decode the information from the game api or there was no information about the user.")
            return
        
        response = {"timestamp": int(time.time())}
        response.update(decodedUserStats)
            
        return JSONResponse(response)
    else:
        raise HTTPException(status_code=500, detail="Unable to get a token we needed to connect to Gaijins servers")
        return

# router that provides an endpoint to get terse user information directly from Gaijin
@router.get("/direct/terse/", summary="Gets terse user info directly from Gaijin.")
async def get_user_terse(userid: Annotated[list[int], Query(title="The ID of the users to get information about", description="The ID of the users to get information about", min_length=1, max_length=50)]):
    
    """
    This endpoint pulls information directly from Gaijin and the schema changes as Gaijin deems it necessary, it therefore isn't documented in depth.
    """
    
    response = get_terse(userid)
            
    return JSONResponse(response)
    

# Class used to create the response objects from the search router below
class user_search_model(BaseModel):
    userid: int
    nick: str 
    icon_name: str | None = ""
    icon_path: str | None = ""
    clan_tag: str | None = ""
    clan_name: str | None = ""
    frame: str | None = ""
    frame_path: str | None = ""
    background: str | None = ""
    background_path: str | None = ""
    last_updated: int | None = None

# router that provides an endpoint to search for users directly from Gaijin
@router.get("/direct/search/", summary="Searches for users from War Thunder.")
async def get_users_search(
        nick: Annotated[str, Query(title="The nickname to search for", description="The nickname to search for")], 
        limit: Annotated[int, Query(title="How many users to retrieve", description="How many users to retrieve", ge=2, le=50)] = 10
    ) -> list[user_search_model]:
    
    """
    This endpoint searches for users from War Thunder.
    """
    
    # Get connection
    conn = dbcon()
    
    # Get database cursor
    cur = conn.cursor(dictionary=True)
    
    # Pull token information row if any tokens with more than 5 minutes left exist
    cur.execute("SELECT * FROM WarThunder.AccessToken WHERE WarThunder.AccessToken.LastRefresh > NOW() LIMIT 1")
    
    # Fetch results from select
    results = cur.fetchall()
    
    # Close the cursor after use
    cur.close()

    # Download BLK file
    if results:
        token = results[0]['Token']
        uidHint = results[0]['UidHint']

        # Calls the contact server, to get search for users
        url = 'https://contact-proxy-02.gaijin.net/json'
        headers = {'token': token,'action': 'cln_find_users_by_nick_prefix_json','User-Agent': 'wt'}
        data = {
            "ignoreCase": True,
            "maxCount": limit,
            "nick": nick,
            "specificAppId": 1067
        }
        userSearchResponse = (requests.post(url, headers=headers, json=data)).json()
        
        response = []
        
        userids = []
        
        for key, value in userSearchResponse.items():
            userids.append(key)
        
        terseInformation = get_terse(userids)
        
        for key, value in userSearchResponse.items():
            
            if 'pilotIcon' in terseInformation[key] and terseInformation[key]['pilotIcon'] != "":
                iconPath = "/static/avatars/" + str(terseInformation[key]['pilotIcon']).lower() + ".avif"
                pilotIcon = terseInformation[key]['pilotIcon']
            else: 
                iconPath = "/static/avatars/cardicon_bot.avif"
                pilotIcon = "cardicon_bot"
            
            if 'frame' in terseInformation[key] and terseInformation[key]['frame'] != "":
                framePath = "/static/avatars/frames/" + str(terseInformation[key]['frame']).lower() + ".avif"
                frame = terseInformation[key]['frame']
            else: 
                framePath = ""
                frame = ""
            
            if 'background' in terseInformation[key] and terseInformation[key]['background'] != "":
                backgroundPath = "/static/profile/headers/" + str(terseInformation[key]['background']).lower() + ".avif"
                background = terseInformation[key]['background']
            else: 
                backgroundPath = "/static/profile/headers/profile_header_default.avif"
                background = "profile_header_default"
            
            if 'clanName' in terseInformation[key] and terseInformation[key]['clanName'] != "":
                clanName = terseInformation[key]['clanName']
                clanTag = terseInformation[key]['clanTag']
            else: 
                clanName = ""
                clanTag = ""
                
            
            response.append(
                user_search_model(
                    userid=key, 
                    nick=value, 
                    clan_tag=clanTag, 
                    clan_name=clanName,
                    icon_name=pilotIcon, 
                    icon_path=iconPath, 
                    frame=frame, 
                    frame_path=framePath,
                    background=background,
                    background_path=backgroundPath
                )
            )
        
        return response
    else:
        raise HTTPException(status_code=500, detail="Unable to get a token we needed to connect to Gaijins servers")
        return
    
# Class used to create the response objects from the search router below
class user_titles_model(BaseModel):
    name: str
    translation: str | None = None
    description: str | None = None

# router that provides an endpoint to get the titles a user has obtained
@router.get("/titles/{userid}", summary="gets the titles that a user has obtained.")
async def get_users(
        userid: Annotated[int, Path(title="The ID of the user to get titles for", description="The ID of the user to get titles for", gt=0)],
        language: Annotated[str, Query(title="The language to receive translated information in", description="The language to receive translated information in")] = "English"
    ) -> list[user_titles_model]:
    
    """
    This endpoint gets a list of titles that a user has obtained.
    """
    
    # Get connection
    conn = dbcon()
    
    # Get database cursor
    cur = conn.cursor(dictionary=True)
    
    # Pull token information row if any tokens with more than 5 minutes left exist
    cur.execute("""SELECT
        name as name,
        translation as translation,
        NULLIF(description,'') as description
        FROM war_thunder_stats_v1.title_correlation
        INNER JOIN war_thunder_stats_v1.title ON title_correlation.title_id = title.id
        LEFT OUTER JOIN war_thunder_stats_v1.title_translation ON title.id = title_translation.title_id
        LEFT OUTER JOIN war_thunder_stats_v1.language ON title_translation.language_id = language.id
        WHERE (
            language.language = ? or 
            language.language IS NULL
        ) and user_id = ?;""",[language, userid])
    
    # Fetch results from select
    results = cur.fetchall()
    
    # Close the cursor after use
    cur.close()

    # Download BLK file
    if results:
        #for key, value in results.items():
        #    response.append(
        #        user_search_model(userid=key, nick=value, clanTag=terseInformation[key]['clanTag'], iconName=terseInformation[key]['pilotIcon'], frame=terseInformation[key]['frame'], background=terseInformation[key]['background'])
        #    )
        
        return results
    else:
        raise HTTPException(status_code=404, detail="Didn't find any titles for the user, you might want to refresh the user information first")
        return

   

# Class used to create the response objects from the search router below
class user_general_stats_model(BaseModel):
    userid: int
    nick: str
    title: str | None
    last_day: int
    register_day: int
    experience: int
    experience_converted: int
    icon_name: str
    icon_path: str
    frame_name: str
    frame_path: str
    background_name: str
    background_path: str
    clan_name: str | None
    clan_tag: str | None
    clan_type: int | None
    clan_role_name: str | None
    penalty_status: str | None
    last_update: int
        
# router that provides an endpoint to get general stats for a user
@router.get("/stats/{userid}", summary="gets general stats for a user.")
async def get_general_user_stats(
        userid: Annotated[int, Path(title="The ID of the user to get stats for", description="The ID of the user to get stats for", gt=0)]
    ) -> list[user_general_stats_model]:
    
    """
    This endpoint gets the general stats for a user.
    """
    
    # Get connection
    conn = dbcon()
    
    # Get database cursor
    cur = conn.cursor(dictionary=True)
    
    # Pull token information row if any tokens with more than 5 minutes left exist
    cur.execute("""
        SELECT
            user.id as userid,
            user.nickname as nick,
            title.name as title,
            UNIX_TIMESTAMP(user.last_day) as last_day,
            UNIX_TIMESTAMP(user.register_day) as register_day,
            general_stat.experience as experience,
            general_stat.experience_converted as experience_converted,
            icon.name as icon_name,
            frame.name as frame_name,
            background.name as background_name,
            clan.name as clan_name,
            clan.tag as clan_tag,
            clan.type as clan_type,
            clan_role.name as clan_role_name,
            user_penalty.status as penalty_status,
            UNIX_TIMESTAMP(general_stat.datetime) as last_update
        FROM war_thunder_stats_v1.user
        LEFT JOIN general_stat ON user.id = general_stat.user_id
        LEFT JOIN title ON user.selected_title_id = title.id
        LEFT JOIN icon ON user.icon_id = icon.id
        LEFT JOIN frame ON user.frame_id = frame.id
        LEFT JOIN background ON user.background_id = background.id
        LEFT JOIN clan ON user.clan_id = clan.id
        LEFT JOIN clan_role ON user.clan_member_role_id = clan_role.id
        LEFT JOIN (SELECT user_id, status FROM (SELECT t.*, ROW_NUMBER() OVER(PARTITION BY user_id ORDER BY datetime DESC) rn FROM (SELECT * FROM war_thunder_stats_v1.penalty_correlation INNER JOIN penalty_type ON penalty_correlation.penalty_id = penalty_type.id WHERE penalty_correlation.user_id = ?) t) t WHERE rn = 1) as user_penalty ON user.id = user_penalty.user_id
        WHERE user.id = ?
        ORDER BY general_stat.datetime DESC
        LIMIT 1;
        ;""",[userid,userid])
    
    # Fetch results from select
    results = cur.fetchall()
    
    # Close the cursor after use
    cur.close()

    # check if we got any data from the database
    if results:
        
        response = []
        
        if results[0]['icon_name'] != "":
            iconPath = "/static/avatars/" + str(results[0]['icon_name']).lower() + ".avif"
        else: 
            iconPath = "/static/avatars/cardicon_bot.avif"
        
        if results[0]['frame_name'] != "":
            framePath = "/static/avatars/frames/" + str(results[0]['frame_name']).lower() + ".avif"
        else: 
            framePath = ""
        
        if results[0]['background_name'] != "":
            backgroundPath = "/static/profile/headers/" + str(results[0]['background_name']).lower() + ".avif"
            background = results[0]['background_name']
        else: 
            backgroundPath = "/static/profile/headers/profile_header_default.avif"
            background = "profile_header_default"
            
        
        response.append(
            user_general_stats_model(
                userid=results[0]['userid'], 
                nick=results[0]['nick'], 
                title=results[0]['title'], 
                last_day=results[0]['last_day'], 
                register_day=results[0]['register_day'], 
                experience=results[0]['experience'], 
                experience_converted=results[0]['experience_converted'], 
                icon_name=results[0]['icon_name'], 
                icon_path=iconPath, 
                frame_name=results[0]['frame_name'], 
                frame_path=framePath, 
                background_name=background, 
                background_path=backgroundPath, 
                clan_name=results[0]['clan_name'], 
                clan_tag=results[0]['clan_tag'], 
                clan_type=results[0]['clan_type'], 
                clan_role_name=results[0]['clan_role_name'],
                penalty_status=results[0]['penalty_status'],
                last_update=results[0]['last_update']
            )
        )
    
        return response
    else:
        raise HTTPException(status_code=404, detail="Didn't find any general stats for the user, you might not have refreshed the profile yet or something else is wrong.")
        return
        
        
        
# Class used to create the response objects from the search router below
class user_historic_unit_count(BaseModel):
    timestamp: int
    unit_count: int

# router that provides an endpoint to get the total amount of units the user has owned over time
@router.get("/stats/{userid}/historical/unitcount", summary="gets total amount of units the user has owned over time.")
async def get_historic_user_unit_count(
        userid: Annotated[int, Path(title="The ID of the user to get unit count for", description="The ID of the user to get unit count for", gt=0)]
    ) -> list[user_historic_unit_count]:
    
    """
    This endpoint gets the total amount of units the user has owned over time.
    """
    
    # Get connection
    conn = dbcon()
    
    # Get database cursor
    cur = conn.cursor(dictionary=True)
    
    # Pull token information row if any tokens with more than 5 minutes left exist
    cur.execute("""SELECT 
                    UNIX_TIMESTAMP(datetime) as timestamp,
                    datetime,
                    max(unit_count) as unit_count
                FROM (
                    SELECT 
                        unit_count_total.timestamp, 
                        user_id,
                        MAX(unit_count_total.cumulative_total) as unit_count
                    FROM (
                        SELECT 
                            first_seen as timestamp,
                            user_id,
                           count(id) OVER (ORDER BY first_seen) AS cumulative_total
                        FROM (
                            SELECT 
                                min(datetime) as first_seen, 
                                user_id, 
                                unit.id 
                            FROM war_thunder_stats_v1.user_modification_status
                            INNER JOIN unit ON user_modification_status.unit_id = unit.id
                            INNER JOIN unit_type ON unit.type_id = unit_type.id
                            INNER JOIN country as country ON unit.country_id = country.id
                            INNER JOIN country_translation as country_translation ON country.id = country_translation.country_id
                            INNER JOIN language as country_translation_language ON country_translation.language_id = country_translation_language.id
                            INNER JOIN country as operator_country ON unit.operator_country_id = operator_country.id
                            INNER JOIN country_translation as operator_country_translation ON operator_country.id = operator_country_translation.country_id
                            INNER JOIN language as operator_country_translation_language ON operator_country_translation.language_id = operator_country_translation_language.id
                            WHERE 
                                operator_country_translation_language.language = 'English' AND 
                                country_translation_language.language = 'English' AND 
                                user_id = ?
                            GROUP BY 
                                user_id, 
                                unit.id
                        ) as units
                    ) as unit_count_total
                    GROUP BY unit_count_total.timestamp, user_id
                ) as unit_count_total
                RIGHT JOIN general_stat ON unit_count_total.user_id = general_stat.user_id
                WHERE general_stat.user_id = ? AND general_stat.datetime >= unit_count_total.timestamp
                GROUP BY datetime
                ORDER BY datetime
        ;""",[userid, userid])
    
    # Fetch results from select
    results = cur.fetchall()
    
    # Close the cursor after use
    cur.close()

    # check if we got any data from the database
    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail="Didn't find any information about how many units the user has, maybe try refreshing the profile")
        return

   
# Class used to create the response objects from the search router below
class user_unit_stat_model(BaseModel):
    name: str
    shop_name: str
    full_name: str
    short_name: str
    compressed_name: str
    type: str
    tags: list
    country: str
    operator_country: str
    tier: int
    tier_roman: str
    battlerating: str
    premium: int
    gift: int
    event: int
    clan: int
    modification_status: int
    modification_title: str
    gamemode: str | None
    spawns: int
    deaths: int
    experience_earned: int
    silver_lions_earned: int
    ground_kills: int
    air_kills: int
    naval_kills: int
    was_in_lineup: int
    defeats: int
    victories: int
    icon_path: str
    small_image_path: str
    image_path: str
    country_icon_path: str
    country_flag_path: str
    operator_country_icon_path: str
    operator_country_flag_path: str

# router that provides an endpoint to get stats for multiple units for a user
@router.get("/stats/{userid}/units/", summary="gets the stats for multiple units for a user.")
async def get_user_unit_stats(
        userid: Annotated[int, Path(title="The ID of the user to get stats for", description="The ID of the user to get stats for", gt=0)],
        language: Annotated[str, Query(title="The language to receive translated information in", description="The language to receive translated information in")] = "English",
        gamemode: Annotated[str | None, Query(title="The gamemode to get battlerating info for", description="The gamemode to get battlerating info for")] = None,
        premium: Annotated[bool | None, Query(title="Defines if the units returned should be premiums or not", description="Defines if the units returned should be premiums or not")] = None,
        gift: Annotated[bool | None, Query(title="Defines if the units returned should be gifts or not", description="Defines if the units returned should be gifts or not")] = None,
        event: Annotated[bool | None, Query(title="Defines if the units returned should be event units or not", description="Defines if the units returned should be event units or not")] = None,
        clan: Annotated[bool | None, Query(title="Defines if the units returned should be clan units or not", description="Defines if the units returned should be clan units or not")] = None
    ) -> list[user_unit_stat_model]:
    
    """
    This endpoint gets the stats for a multiple units for a user.
    """
    
    # Get connection
    conn = dbcon()
    
    # Get database cursor
    cur = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
            unit.name as name, 
            unit_translation.shop_name as shop_name, 
            unit_translation.full_name as full_name, 
            unit_translation.short_name as short_name, 
            unit_translation.compressed_name as compressed_name, 
            unit_type.type as type, 
            GROUP_CONCAT(DISTINCT COALESCE(unit_tag.translation,unit_tag.tag)) as tags, 
            COALESCE(country.translation, country.name) as country, 
            country.name as country_name,
            COALESCE(operator_country.translation, operator_country.name) as operator_country, 
            operator_country.name as operator_country_name,
            tier.id as tier, 
            tier.tier as tier_roman, 
            CAST(battlerating.battlerating as CHAR(4)) as battlerating, 
            unit.premium, 
            unit.gift, 
            unit.event, 
            unit.clan, 
            modification_status.id as modification_status, 
            modification_status.title as modification_title, 
            gamemode.name as gamemode, 
            COALESCE(unit_stat.spawns,0) as spawns, 
            COALESCE(unit_stat.deaths,0) as deaths, 
            COALESCE(experience_earned,0) as experience_earned, 
            COALESCE(silver_lions_earned,0) as silver_lions_earned, 
            COALESCE(unit_stat.ground_kills,0) as ground_kills, 
            COALESCE(unit_stat.air_kills,0) as air_kills, 
            COALESCE(unit_stat.naval_kills,0) as naval_kills, 
            COALESCE(unit_stat.was_in_lineup,0) as was_in_lineup, 
            COALESCE(unit_stat.defeats,0) as defeats, 
            COALESCE(unit_stat.victories,0) as victories
        FROM (
			SELECT datetime, 
            user_id, 
            unit_id, 
            modification_status_id 
            FROM (
				SELECT t.*, 
                ROW_NUMBER() OVER(PARTITION BY user_id, unit_id ORDER BY datetime DESC) rn 
                FROM (
					SELECT * 
                    FROM war_thunder_stats_v1.user_modification_status 
                    WHERE 
						user_modification_status.user_id = ?
				) t
			) t WHERE rn = 1
		) as user_modification_status
        LEFT OUTER JOIN (
			SELECT user_id, 
            unit_id, 
            gamemode_id, 
            max(silver_lions_earned) as silver_lions_earned, 
            max(experience_earned) as experience_earned, 
            max(unit_stat.spawns) as spawns, 
            max(unit_stat.deaths) as deaths, 
            max(unit_stat.ground_kills) as ground_kills, 
            max(unit_stat.air_kills) as air_kills, 
            max(unit_stat.naval_kills) as naval_kills, 
            max(unit_stat.was_in_lineup) as was_in_lineup, 
            max(unit_stat.defeats) as defeats, 
            max(unit_stat.victories) as victories 
            FROM war_thunder_stats_v1.unit_stat 
            WHERE unit_stat.user_id = ? 
            GROUP BY gamemode_id, unit_id
		) as unit_stat ON user_modification_status.unit_id = unit_stat.unit_id AND user_modification_status.user_id = unit_stat.user_id
        LEFT OUTER JOIN war_thunder_stats_v1.unit ON user_modification_status.unit_id = unit.id
        LEFT OUTER JOIN war_thunder_stats_v1.modification_status ON user_modification_status.modification_status_id = modification_status.id
        LEFT OUTER JOIN war_thunder_stats_v1.gamemode ON unit_stat.gamemode_id = gamemode.id
        LEFT OUTER JOIN (
			SELECT country.id, 
            country.name, 
            country_translation.translation 
            FROM war_thunder_stats_v1.country
			LEFT OUTER JOIN war_thunder_stats_v1.country_translation as country_translation ON country.id = country_translation.country_id
			INNER JOIN war_thunder_stats_v1.language as country_translation_language ON country_translation.language_id = country_translation_language.id AND country_translation_language.language = ?
		) as country ON unit.country_id = country.id
        LEFT OUTER JOIN (
			SELECT operator_country.id, 
            operator_country.name, 
            operator_country_translation.translation 
            FROM war_thunder_stats_v1.country as operator_country
			LEFT OUTER JOIN war_thunder_stats_v1.country_translation as operator_country_translation ON operator_country.id = operator_country_translation.country_id
			INNER JOIN war_thunder_stats_v1.language as operator_country_translation_language ON operator_country_translation.language_id = operator_country_translation_language.id AND operator_country_translation_language.language = ?
		) as operator_country ON unit.operator_country_id = operator_country.id
        LEFT OUTER JOIN (
			SELECT unit_translation.unit_id, 
            unit_translation.shop_name, 
            unit_translation.full_name, 
            unit_translation.short_name, 
            unit_translation.compressed_name 
            FROM war_thunder_stats_v1.unit_translation
			INNER JOIN war_thunder_stats_v1.language as unit_translation_language ON unit_translation.language_id = unit_translation_language.id AND unit_translation_language.language = ?
		) as unit_translation ON user_modification_status.unit_id = unit_translation.unit_id
        LEFT OUTER JOIN war_thunder_stats_v1.tier ON unit.tier_id = tier.id
        LEFT OUTER JOIN war_thunder_stats_v1.battlerating_correlation ON unit.id = battlerating_correlation.unit_id AND COALESCE(gamemode.id,1) = battlerating_correlation.gamemode_id
        LEFT OUTER JOIN war_thunder_stats_v1.battlerating ON battlerating_correlation.battlerating_id = battlerating.id
        LEFT OUTER JOIN war_thunder_stats_v1.unit_type ON unit.type_id = unit_type.id
        LEFT OUTER JOIN war_thunder_stats_v1.unit_tag_correlation ON unit.id = unit_tag_correlation.unit_id
        LEFT OUTER JOIN (
			SELECT unit_tag.id, unit_tag.tag, 
            unit_tag_translation.translation 
            FROM war_thunder_stats_v1.unit_tag
			LEFT OUTER JOIN war_thunder_stats_v1.unit_tag_translation ON unit_tag.id = unit_tag_translation.tag_id
			INNER JOIN war_thunder_stats_v1.language as unit_tag_translation_language ON unit_tag_translation.language_id = unit_tag_translation_language.id AND unit_tag_translation_language.language = ?
		) as unit_tag ON unit_tag_correlation.unit_tag_id = unit_tag.id
        WHERE 
            user_modification_status.user_id = ? 
            """
    
    queryParameters = [userid, userid, language, language, language, language, userid]
        
    if gamemode is not None:
        query = query + " AND gamemode.name = ? "
        queryParameters.append(gamemode)
    
    if premium is not None:
        query = query + " AND unit.premium = ? "
        queryParameters.append(premium)
        
    if gift is not None:
        query = query + " AND unit.gift = ? "
        queryParameters.append(gift)
        
    if event is not None:
        query = query + " AND unit.event = ? "
        queryParameters.append(event)
        
    if clan is not None:
        query = query + " AND unit.clan = ? "
        queryParameters.append(clan)
    
    query = query + """
        GROUP BY user_modification_status.unit_id, gamemode.name
        ;
    """
    
    # Pull units and stats
    cur.execute(query,queryParameters)
    
    # Fetch results from select
    results = cur.fetchall()
    
    # Close the cursor after use
    cur.close()
    
    response = []
    
    for result in results:
        response.append(
            user_unit_stat_model(
                name=result['name'],
                shop_name=result['shop_name'],
                full_name=result['full_name'],
                short_name=result['short_name'],
                compressed_name=result['compressed_name'],
                type=result['type'],
                tags=result['tags'].split(","),
                country=result['country'],
                operator_country=result['operator_country'],
                tier=result['tier'],
                tier_roman=result['tier_roman'],
                battlerating=result['battlerating'],
                premium=result['premium'],
                gift=result['gift'],
                event=result['event'],
                clan=result['clan'],
                modification_status=result['modification_status'],
                modification_title=result['modification_title'],
                gamemode=result['gamemode'],
                spawns=result['spawns'],
                deaths=result['deaths'],
                experience_earned=result['experience_earned'],
                silver_lions_earned=result['silver_lions_earned'],
                ground_kills=result['ground_kills'],
                air_kills=result['air_kills'],
                naval_kills=result['naval_kills'],
                was_in_lineup=result['was_in_lineup'],
                defeats=result['defeats'],
                victories=result['victories'],
                icon_path="/static/uielements/" + str(result['name']).lower() + "_ico.svg",
                small_image_path="/static/units/small/" + str(result['name']).lower() + ".png",
                image_path="/static/units/" + str(result['name']).lower() + ".avif",
                country_icon_path="/static/uielements/" + str(result['country_name']).lower() + ".svg",
                country_flag_path="/static/flags/" + str(result['country_name']).lower() + ".avif",
                operator_country_icon_path="/static/uielements/" + str(result['operator_country_name']).lower() + ".svg",
                operator_country_flag_path="/static/flags/" + str(result['operator_country_name']).lower() + ".avif"
            )
        )

    # check if we got any data from the database
    if results:
        return response
    else:
        raise HTTPException(status_code=404, detail="Didn't find any stats for the unit for the user, you might want to refresh the user information or refine your filters")
        return

# router that provides an endpoint to get stats for a specific unit for a user
@router.get("/stats/{userid}/units/{unitname}", summary="gets the stats for a specific unit for a user.")
async def get_user_unit_stats(
        userid: Annotated[int, Path(title="The ID of the user to get stats for", description="The ID of the user to get stats for", gt=0)],
        unitname: Annotated[str, Path(title="The name of the unit to get stats for", description="The name of the unit to get stats for")],
        language: Annotated[str, Query(title="The language to receive translated information in", description="The language to receive translated information in")] = "English",
        gamemode: Annotated[str | None, Query(title="The gamemode to get battlerating info for", description="The gamemode to get battlerating info for")] = None,
    ) -> list[user_unit_stat_model]:
    
    """
    This endpoint gets the stats for a specific unit for a user.
    """
    
    # Get connection
    conn = dbcon()
    
    # Get database cursor
    cur = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
            unit.name as name, 
            unit_translation.shop_name as shop_name, 
            unit_translation.full_name as full_name, 
            unit_translation.short_name as short_name, 
            unit_translation.compressed_name as compressed_name, 
            unit_type.type as type, 
            GROUP_CONCAT(DISTINCT COALESCE(unit_tag_translation.translation,unit_tag.tag)) as tags, 
            COALESCE(country_translation.translation, country.name) as country, 
            country.name as country_name,
            COALESCE(operator_country_translation.translation, operator_country.name) as operator_country, 
            operator_country.name as operator_country_name,
            tier.id as tier, 
            tier.tier as tier_roman, 
            CAST(battlerating.battlerating as CHAR(4)) as battlerating, 
            unit.premium, 
            unit.gift, 
            unit.event, 
            unit.clan, 
            modification_status.id as modification_status, 
            modification_status.title as modification_title, 
            gamemode.name as gamemode, 
            COALESCE(max(unit_stat.spawns),0) as spawns, 
            COALESCE(max(unit_stat.deaths),0) as deaths, 
            COALESCE(max(experience_earned),0) as experience_earned, 
            COALESCE(max(silver_lions_earned),0) as silver_lions_earned, 
            COALESCE(max(unit_stat.ground_kills),0) as ground_kills, 
            COALESCE(max(unit_stat.air_kills),0) as air_kills, 
            COALESCE(max(unit_stat.naval_kills),0) as naval_kills, 
            COALESCE(max(unit_stat.was_in_lineup),0) as was_in_lineup, 
            COALESCE(max(unit_stat.defeats),0) as defeats, 
            COALESCE(max(unit_stat.victories),0) as victories
        FROM war_thunder_stats_v1.general_stat
        LEFT OUTER JOIN (SELECT datetime, user_id, unit_id, modification_status_id FROM (SELECT t.*, ROW_NUMBER() OVER(PARTITION BY user_id, unit_id ORDER BY datetime DESC) rn FROM (SELECT * FROM war_thunder_stats_v1.user_modification_status WHERE user_modification_status.user_id = ?) t) t WHERE rn = 1) as user_modification_status ON general_stat.user_id = user_modification_status.user_id
        LEFT OUTER JOIN war_thunder_stats_v1.unit_stat ON user_modification_status.unit_id = unit_stat.unit_id AND general_stat.user_id = unit_stat.user_id
        LEFT OUTER JOIN war_thunder_stats_v1.unit ON user_modification_status.unit_id = unit.id
        LEFT OUTER JOIN war_thunder_stats_v1.modification_status ON user_modification_status.modification_status_id = modification_status.id
        LEFT OUTER JOIN war_thunder_stats_v1.gamemode ON unit_stat.gamemode_id = gamemode.id
        LEFT OUTER JOIN war_thunder_stats_v1.country ON unit.country_id = country.id
        LEFT OUTER JOIN war_thunder_stats_v1.country_translation as country_translation ON country.id = country_translation.country_id
        LEFT OUTER JOIN war_thunder_stats_v1.language as country_translation_language ON country_translation.language_id = country_translation_language.id
        LEFT OUTER JOIN war_thunder_stats_v1.country as operator_country ON unit.operator_country_id = operator_country.id
        LEFT OUTER JOIN war_thunder_stats_v1.country_translation as operator_country_translation ON operator_country.id = operator_country_translation.country_id
        LEFT OUTER JOIN war_thunder_stats_v1.language as operator_country_translation_language ON operator_country_translation.language_id = operator_country_translation_language.id
        LEFT OUTER JOIN war_thunder_stats_v1.unit_translation ON user_modification_status.unit_id = unit_translation.unit_id
        LEFT OUTER JOIN war_thunder_stats_v1.language as unit_translation_language ON unit_translation.language_id = unit_translation_language.id
        LEFT OUTER JOIN war_thunder_stats_v1.tier ON unit.tier_id = tier.id
        LEFT OUTER JOIN war_thunder_stats_v1.battlerating_correlation ON unit.id = battlerating_correlation.unit_id AND COALESCE(gamemode.id,1) = battlerating_correlation.gamemode_id
        LEFT OUTER JOIN war_thunder_stats_v1.battlerating ON battlerating_correlation.battlerating_id = battlerating.id
        LEFT OUTER JOIN war_thunder_stats_v1.unit_type ON unit.type_id = unit_type.id
        LEFT OUTER JOIN war_thunder_stats_v1.unit_tag_correlation ON unit.id = unit_tag_correlation.unit_id
        LEFT OUTER JOIN war_thunder_stats_v1.unit_tag ON unit_tag_correlation.unit_tag_id = unit_tag.id
        LEFT OUTER JOIN war_thunder_stats_v1.unit_tag_translation ON unit_tag.id = unit_tag_translation.tag_id
        LEFT OUTER JOIN war_thunder_stats_v1.language as unit_tag_translation_language ON unit_tag_translation.language_id = unit_tag_translation_language.id
        WHERE 
            user_modification_status.user_id = ? AND
            unit.name = ? AND 
            """
    
    queryParameters = [userid, userid, unitname]
        
    if gamemode is not None:
        query = query + " gamemode.name = ? AND "
        queryParameters.append(gamemode)
    
    query = query + """
            operator_country_translation_language.language = ? AND 
            country_translation_language.language = ? AND 
            unit_translation_language.language = ? AND 
            unit_tag_translation_language.language = ?
        GROUP BY user_modification_status.unit_id, gamemode.name
        ;
    """
    queryParameters.extend([language, language, language, language])
    
    # Pull units and stats
    cur.execute(query,queryParameters)
    
    # Fetch results from select
    results = cur.fetchall()
    
    # Close the cursor after use
    cur.close()
    
    response = []
    
    for result in results:
        response.append(
            user_unit_stat_model(
                name=result['name'],
                shop_name=result['shop_name'],
                full_name=result['full_name'],
                short_name=result['short_name'],
                compressed_name=result['compressed_name'],
                type=result['type'],
                tags=result['tags'].split(","),
                country=result['country'],
                operator_country=result['operator_country'],
                tier=result['tier'],
                tier_roman=result['tier_roman'],
                battlerating=result['battlerating'],
                premium=result['premium'],
                gift=result['gift'],
                event=result['event'],
                clan=result['clan'],
                modification_status=result['modification_status'],
                modification_title=result['modification_title'],
                gamemode=result['gamemode'],
                spawns=result['spawns'],
                deaths=result['deaths'],
                experience_earned=result['experience_earned'],
                silver_lions_earned=result['silver_lions_earned'],
                ground_kills=result['ground_kills'],
                air_kills=result['air_kills'],
                naval_kills=result['naval_kills'],
                was_in_lineup=result['was_in_lineup'],
                defeats=result['defeats'],
                victories=result['victories'],
                icon_path="/static/uielements/" + str(result['name']).lower() + "_ico.svg",
                small_image_path="/static/units/small/" + str(result['name']).lower() + ".png",
                image_path="/static/units/" + str(result['name']).lower() + ".avif",
                country_icon_path="/static/uielements/" + str(result['country_name']).lower() + ".svg",
                country_flag_path="/static/flags/" + str(result['country_name']).lower() + ".avif",
                operator_country_icon_path="/static/uielements/" + str(result['operator_country_name']).lower() + ".svg",
                operator_country_flag_path="/static/flags/" + str(result['operator_country_name']).lower() + ".avif"
            )
        )

    # check if we got any data from the database
    if results:
        return response
    else:
        raise HTTPException(status_code=404, detail="Didn't find any stats for the unit for the user, you might want to refresh the user information or refine your filters")
        return
        
        
# Class used to create the response objects from the search router below
class user_historic_unit_stat_model(BaseModel):
    timestamp: int
    type: str
    spawns: int
    deaths: int
    experience_earned: int
    silver_lions_earned: int
    ground_kills: int
    air_kills: int
    naval_kills: int
    was_in_lineup: int
    defeats: int
    victories: int

# router that provides an endpoint to get stats for a specific unit for a user
@router.get("/stats/{userid}/units/{unitname}/historical", summary="gets the historical stats for a specific unit for a user.")
async def get_historic_user_unit_stats(
        userid: Annotated[int, Path(title="The ID of the user to get stats for", description="The ID of the user to get stats for", gt=0)],
        unitname: Annotated[str, Path(title="The name of the unit to get stats for", description="The name of the unit to get stats for")],
        gamemode: Annotated[str, Query(title="The gamemode to get stats from", description="The gamemode to get stats from")] = "Realistic"
    ) -> list[user_historic_unit_stat_model]:
    
    """
    This endpoint gets the historical stats for a specific unit for a user.
    """
    
    # Get connection
    conn = dbcon()
    
    # Get database cursor
    cur = conn.cursor(dictionary=True)
    
    # Pull token information row if any tokens with more than 5 minutes left exist
    cur.execute("""-- SELECT unique fields and the highest value for the others
        SELECT 
            UNIX_TIMESTAMP(datetime) as timestamp, 
            type as type,
            max(spawns) as spawns, 
            max(deaths) as deaths, 
            max(experience_earned) as experience_earned, 
            max(silver_lions_earned) as silver_lions_earned, 
            max(ground_kills) as ground_kills, 
            max(air_kills) as air_kills, 
            max(naval_kills) as naval_kills, 
            max(was_in_lineup) as was_in_lineup, 
            max(defeats) as defeats, 
            max(victories) as victories
        FROM (
            -- SELECT unique fields and value fields
            SELECT 
                general_stat.user_id, 
                general_stat.datetime, 
                unit_id,
                unit_type.type as type,
                gamemode_id, 
                spawns, 
                deaths, 
                experience_earned, 
                silver_lions_earned, 
                ground_kills, 
                air_kills, 
                naval_kills, 
                was_in_lineup, 
                defeats, 
                victories
            FROM war_thunder_stats_v1.general_stat
            -- Make sure to keep all values from the general_stat table, and match them with user_id on the unit_stat table to make duplicates.
            LEFT OUTER JOIN war_thunder_stats_v1.unit_stat on general_stat.user_id = unit_stat.user_id
            -- add unit to allow for k/d calculation
            LEFT OUTER JOIN war_thunder_stats_v1.unit ON unit_stat.unit_id = unit.id
            -- add type to allow for k/d calculation
            LEFT OUTER JOIN war_thunder_stats_v1.unit_type ON unit.type_id = unit_type.id
            -- Only keep the entries that have a duplicate datetime that is greater than or equal to the unit_stat datetime it was matched against.
            WHERE 
                general_stat.datetime >= unit_stat.datetime AND
                general_stat.user_id = ? AND
                unit_id = (SELECT id FROM `war_thunder_stats_v1`.`unit` WHERE name = ?) AND
                gamemode_id = (SELECT id FROM `war_thunder_stats_v1`.`gamemode` WHERE name = ?)
        ) as db
        -- group the entries by user_id, datetime, unit_id and gamemode_id to make sure we keep atleast one pr day
        Group by 
            user_id, 
            datetime, 
            unit_id,
            type,
            gamemode_id
        -- order by the unit_id and then datetime afterwards
        ORDER BY 
            unit_id, 
            datetime
        ;""",[userid, unitname, gamemode])
    
    # Fetch results from select
    results = cur.fetchall()
    
    # Close the cursor after use
    cur.close()

    # check if we got any data from the database
    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail="Didn't find any stats for the unit for the user, you might want to refresh the user information or refine your filters")
        return

        
# Class used to create the response objects from the search router below
class user_historic_unit_modification_status_model(BaseModel):
    timestamp: int
    status: str      
        
# router that provides an endpoint to get the historical modification status for a specific unit for a user
@router.get("/stats/{userid}/units/{unitname}/historical/modification_status", summary="gets the historical modification status for a specific unit for a user.")
async def get_historic_user_unit_modification_status(
        userid: Annotated[int, Path(title="The ID of the user to get modification status for", description="The ID of the user to get modification status for", gt=0)],
        unitname: Annotated[str, Path(title="The name of the unit to get modification status for", description="The name of the unit to get modification status for")]
    ) -> list[user_historic_unit_modification_status_model]:
    
    """
    This endpoint gets the historical modification status for a specific unit for a user.
    """
    
    # Get connection
    conn = dbcon()
    
    # Get database cursor
    cur = conn.cursor(dictionary=True)
    
    # Pull token information row if any tokens with more than 5 minutes left exist
    cur.execute("""
        SELECT 
             UNIX_TIMESTAMP(user_modification_status.datetime) as timestamp,
             modification_status.title as status
        FROM war_thunder_stats_v1.user_modification_status
        INNER JOIN war_thunder_stats_v1.modification_status ON user_modification_status.modification_status_id = modification_status.id
        INNER JOIN war_thunder_stats_v1.unit ON user_modification_status.unit_id = unit.id
        WHERE 
            user_id = ? AND
            unit.name = ?
        ORDER BY timestamp DESC
        ;""",[userid, unitname])
    
    # Fetch results from select
    results = cur.fetchall()
    
    # Close the cursor after use
    cur.close()

    # check if we got any data from the database
    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail="Didn't find any modification status for the unit for the user, you might want to refresh the user information or verify if the user even has the unit")
        return