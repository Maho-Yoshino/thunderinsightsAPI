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
import re
from urllib3.exceptions import InsecureRequestWarning
from datetime import datetime
from celery import Celery
from celery.schedules import crontab
from kombu import Exchange, Queue
from database_connection import dbcon

# Function to get a value if the property exists, else return None
def getValueIfExists(objectToCheck,valueToFind):
    if valueToFind in objectToCheck:
        return objectToCheck[valueToFind]
    else:
        return None

def add_user(userid):

    # Get connection
    conn = dbcon()
    
    # Get database cursor
    cur = conn.cursor(dictionary=True)
    
    # Pull token information row if any tokens with more than 5 minutes left exist
    cur.execute("SELECT * FROM war_thunder_stats_v1.general_stat WHERE war_thunder_stats_v1.general_stat.datetime > TIMESTAMPADD(HOUR, -24, NOW()) AND war_thunder_stats_v1.general_stat.user_id = ? LIMIT 1",[userid])
    
    # Fetch results from select
    results = cur.fetchall()

    if not results:
        url = 'http://192.168.3.1:20080/v1/users/direct/' + str(userid)
        userInformation = requests.get(url, verify=False)
        
        userStatInformation = json.loads(userInformation.content)
        
        # Pull information in if it exists
        timestamp = getValueIfExists(userStatInformation,'timestamp')
        nickname = getValueIfExists(userStatInformation,'nick')
        clanid = getValueIfExists(userStatInformation,'clanId')
        clanMemberRole = getValueIfExists(userStatInformation,'clanMemberRole')
        clanTag = getValueIfExists(userStatInformation,'clanTag')
        clanName = getValueIfExists(userStatInformation,'clanName')
        clanType = getValueIfExists(userStatInformation,'clanType')
        lastDay = getValueIfExists(userStatInformation,'lastDay')
        registerDay = getValueIfExists(userStatInformation,'registerDay')
        exp = getValueIfExists(userStatInformation,'exp')
        expConverted = getValueIfExists(userStatInformation,'expConverted')
        selectedTitleName = getValueIfExists(userStatInformation,'title')
        iconid = getValueIfExists(userStatInformation,'icon')
        iconName = getValueIfExists(userStatInformation,'iconName')
        frame = getValueIfExists(userStatInformation,'frame')
        background = getValueIfExists(userStatInformation,'background')
        penaltyStatus = getValueIfExists(userStatInformation,'penaltyStatus')
        
        # Check if the user has played since last stat pull
        cur.execute(
        "SELECT * FROM war_thunder_stats_v1.general_stat WHERE experience=? AND user_id=?;", 
        ([exp, userid]))
        results = cur.fetchall()
        if results:
            # The user doesn't seem to have played since last check so we won't refresh their information, but we will still update the timestamp on the user
            
            # Insert a timestamp which we will use to keep track of when we last tried to refresh info for the user, even if it didn't work
            cur.execute(
            "INSERT INTO `war_thunder_stats_v1`.`user` (`id`,`datetime`) VALUES (?,FROM_UNIXTIME(?)) ON DUPLICATE KEY UPDATE `datetime`=FROM_UNIXTIME(?);", 
            ([userid, timestamp, timestamp]))
            
            # Commit to database
            conn.commit()
            
            return "user with ID: " + str(userid) + " returned the same RP/EXP as last pull, so profile wasn't updated"
            
        # If clanid has any other value than none, try to insert/update in the clan table
        if (clanid != None):
            cur.execute(
            "INSERT INTO `war_thunder_stats_v1`.`clan` (`id`,`name`,`tag`,`type`) VALUES (?, ?, ?, ?) ON DUPLICATE KEY UPDATE name=?,tag=?,type=?;", 
            ([clanid, clanName, clanTag, clanType, clanName, clanTag, clanType]))
            
            # Update the ClanRoles Table
            cur.execute(
            "INSERT IGNORE INTO `war_thunder_stats_v1`.`clan_role` (`id`) VALUES (?);", 
            ([clanMemberRole]))
            
        # Insert in the icon table
        cur.execute(
        "INSERT INTO `war_thunder_stats_v1`.`icon` (`id`,`name`) VALUES (?,?) ON DUPLICATE KEY UPDATE name=?;", 
        ([iconid, iconName, iconName]))
        
        # Insert in the penalty_type table
        cur.execute(
        "INSERT IGNORE INTO `war_thunder_stats_v1`.`penalty_type` (`status`) SELECT ? FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`penalty_type` WHERE status = ?);", 
        ([penaltyStatus,penaltyStatus]))
        
        # Insert in the frame table
        cur.execute(
        "INSERT IGNORE INTO `war_thunder_stats_v1`.`frame` (`name`) SELECT ? FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`frame` WHERE name = ?);", 
        ([frame,frame]))
        
        # Insert in the background table
        cur.execute(
        "INSERT IGNORE INTO `war_thunder_stats_v1`.`background` (`name`) SELECT ? FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`background` WHERE name = ?);", 
        ([background,background]))
        
        # Do preliminary insertion into the user table to allow for titles to be inserted below
        cur.execute(
        "INSERT IGNORE INTO `war_thunder_stats_v1`.`user` (`id`) VALUES (?);", 
        ([userid]))
        
        # Insert in the penalty_correlation table
        cur.execute(
        "INSERT IGNORE INTO `war_thunder_stats_v1`.`penalty_correlation` (`penalty_id`,`user_id`,`datetime`) SELECT (SELECT id FROM `war_thunder_stats_v1`.`penalty_type` WHERE `status` = ?),?,FROM_UNIXTIME(?) FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM (SELECT * FROM `war_thunder_stats_v1`.`penalty_correlation` WHERE `user_id` = ? ORDER BY datetime DESC LIMIT 1) as most_recent_user_penalty WHERE `penalty_id` = (SELECT id FROM `war_thunder_stats_v1`.`penalty_type` WHERE `status` = ?) AND `user_id` = ?);", 
        ([penaltyStatus, userid, timestamp, userid, penaltyStatus, userid]))
        
        # Commit to database
        conn.commit()
            
        # Insert/update in the Titles table
        if 'name' in userStatInformation['titles']:
            if isinstance(userStatInformation['titles']['name'], str):
                # Insert title in table if it doesn't already exist
                cur.execute(
                "INSERT INTO `war_thunder_stats_v1`.`title` (`name`) SELECT ? FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`title` WHERE name = ?);", 
                ([userStatInformation['titles']['name'], userStatInformation['titles']['name']]))
                
                # Insert a connection between the userid and titleid in the correlation table
                cur.execute(
                "INSERT IGNORE INTO `war_thunder_stats_v1`.`title_correlation` (`user_id`,`title_id`) VALUES (?,(SELECT id FROM `war_thunder_stats_v1`.`title` WHERE name = ?));", 
                ([userid, userStatInformation['titles']['name']]))
                
            else:
                for title in userStatInformation['titles']['name']:
                    # Insert title in table if it doesn't already exist
                    cur.execute(
                    "INSERT INTO `war_thunder_stats_v1`.`title` (`name`) SELECT ? FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`title` WHERE name = ?);", 
                    ([title, title]))
                    
                    # Insert a connection between the userid and titleid in the correlation table
                    cur.execute(
                    "INSERT IGNORE INTO `war_thunder_stats_v1`.`title_correlation` (`user_id`,`title_id`) VALUES (?,(SELECT id FROM `war_thunder_stats_v1`.`title` WHERE name = ?));", 
                    ([userid, title]))
                    
        # Commit to database
        conn.commit()
                    
        # do the actual insertion
        cur.execute(
        "INSERT INTO `war_thunder_stats_v1`.`user` (`id`,`clan_id`,`nickname`,`clan_member_role_id`,`last_day`,`register_day`,`selected_title_id`,`icon_id`,`frame_id`,`background_id`,`datetime`) VALUES (?,?,?,?,FROM_UNIXTIME(?),FROM_UNIXTIME(?),(SELECT id FROM `war_thunder_stats_v1`.`title` WHERE name = ?),?,(SELECT id FROM `war_thunder_stats_v1`.`frame` WHERE name = ?),(SELECT id FROM `war_thunder_stats_v1`.`background` WHERE name = ?),FROM_UNIXTIME(?)) ON DUPLICATE KEY UPDATE clan_id=?,nickname=?,clan_member_role_id=?,last_day=FROM_UNIXTIME(?),register_day=FROM_UNIXTIME(?),selected_title_id=(SELECT id FROM `war_thunder_stats_v1`.`title` WHERE name = ?),icon_id=?,frame_id=(SELECT id FROM `war_thunder_stats_v1`.`frame` WHERE name = ?),background_id=(SELECT id FROM `war_thunder_stats_v1`.`background` WHERE name = ?),datetime=FROM_UNIXTIME(?);", 
        ([userid, clanid, nickname, clanMemberRole, lastDay, registerDay, selectedTitleName, iconid, frame, background, timestamp, clanid, nickname, clanMemberRole, lastDay, registerDay, selectedTitleName, iconid, frame, background, timestamp]))
        
        # Insert in the general_stat table
        cur.execute(
        "INSERT INTO `war_thunder_stats_v1`.`general_stat` (`datetime`,`user_id`,`experience`,`experience_converted`) SELECT FROM_UNIXTIME(?),?,?,? FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`general_stat` WHERE user_id = ? AND experience = ? AND experience_converted = ?);", 
        ([timestamp, userid, exp, expConverted, userid, exp, expConverted]))
        
        # Commit to database
        conn.commit()
        
        # Insert/update the unit name in the VehicleInformation table, the country name in the country table, modificationStatus in the ModificationStatus table and ModificationStatusPerUser into the ModificationStatusPerUser table
        for country, vehicleArray in userStatInformation['aircrafts'].items():
            
            # insert country
            cur.execute(
            "INSERT INTO `war_thunder_stats_v1`.`country` (`name`) SELECT ? FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`country` WHERE name = ?);", 
            ([country, country]))
            
            for unit, modificationStatus in vehicleArray.items():
            
                # insert unit
                cur.execute(
                "INSERT INTO `war_thunder_stats_v1`.`unit` (`name`,`country_id`) SELECT ?,(SELECT id FROM `war_thunder_stats_v1`.`country` WHERE name = ?) FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`unit` WHERE name = ? AND country_id = (SELECT id FROM `war_thunder_stats_v1`.`country` WHERE name = ?));", 
                ([unit, country, unit, country]))
                
                # update the unit to make it available in search
                cur.execute(
                """UPDATE `war_thunder_stats_v1`.`unit`
                SET
                    `include_in_search` = 1
                WHERE 
                    `name` = ?;""", 
                ([unit]))
                
                # Insert in the modification_status Table
                cur.execute(
                "INSERT IGNORE INTO `war_thunder_stats_v1`.`modification_status` (`id`) VALUES (?);", 
                ([modificationStatus]))
                
                # Insert entry into user_modification_status Table
                cur.execute(
                "INSERT INTO `war_thunder_stats_v1`.`user_modification_status` (`datetime`,`user_id`,`unit_id`,`modification_status_id`) SELECT FROM_UNIXTIME(?),?,(SELECT id FROM `war_thunder_stats_v1`.`unit` WHERE name = ?),? FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM (SELECT modification_status_id FROM `war_thunder_stats_v1`.`user_modification_status` WHERE user_id = ? AND unit_id = (SELECT id FROM `war_thunder_stats_v1`.`unit` WHERE name = ?) ORDER BY datetime DESC LIMIT 1) as db WHERE modification_status_id = ?);", 
                ([timestamp, userid, unit, modificationStatus, userid, unit, modificationStatus]))
                
        # Commit to database
        conn.commit()
        
        # Insert/update the unit stats in the unit_stat table and the gamemode in the gamemode table
        for gamemode, gamemodeStats in userStatInformation['userstat'].items():

            # Skip if the property new exists or the gamemodestats is False
            if gamemode == 'new' or gamemode == None or gamemode == 'none' or gamemodeStats == False:
                continue
            
            # replace arcade with Arcade
            if gamemode == 'arcade':
                gamemode = 'Arcade'
            
            # replace historical with Realistic
            if gamemode == 'historical':
                gamemode = 'Realistic'
                
            # replace simulation with Simulator
            if gamemode == 'simulation':
                gamemode = 'Simulator'
            
            # Insert gamemode
            cur.execute(
            "INSERT INTO `war_thunder_stats_v1`.`gamemode` (`name`) SELECT ? FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`gamemode` WHERE name = ?);", 
            ([gamemode, gamemode]))
            
            for unit, unitStats in gamemodeStats['total'].items():
                
                # insert unit if it doesn't exist
                cur.execute(
                "INSERT INTO `war_thunder_stats_v1`.`unit` (`name`) SELECT ? FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`unit` WHERE name = ?);", 
                ([unit, unit]))
            
                # Get values and define others as 0 as they might not exist.
                if "flyouts" in unitStats:
                    spawns = unitStats['flyouts']
                else:
                    spawns = 0
                
                if "deaths" in unitStats:
                    deaths = unitStats['deaths']
                else:
                    deaths = 0
                
                if "wp_total" in unitStats:
                    silverLions = unitStats['wp_total']
                else:
                    silverLions = 0
                
                if "online_exp_total" in unitStats:
                    experience = unitStats['online_exp_total']
                else:
                    experience = 0
                
                if "defeats" in unitStats:
                    defeats = unitStats['defeats']
                else:
                    defeats = 0
                
                if "victories" in unitStats:
                    victories = unitStats['victories']
                else:
                    victories = 0
                
                if "was_in_session" in unitStats:
                    wasInLineup = unitStats['was_in_session']
                else:
                    wasInLineup = 0
                
                if "air_kills" in unitStats:
                    airKills = unitStats['air_kills']
                else:
                    airKills = 0
                
                if "ground_kills" in unitStats:
                    groundKills = unitStats['ground_kills']
                else:
                    groundKills = 0
                
                if "naval_kills" in unitStats:
                    navalKills = unitStats['naval_kills']
                else:
                    navalKills = 0
                
                # Insert entry into unit_stat Table
                cur.execute(
                """INSERT INTO `war_thunder_stats_v1`.`unit_stat` (
                    `datetime`,
                    `user_id`,
                    `unit_id`,
                    `gamemode_id`,
                    `spawns`,
                    `deaths`,
                    `experience_earned`,
                    `silver_lions_earned`,
                    `ground_kills`,
                    `air_kills`,
                    `naval_kills`,
                    `was_in_lineup`,
                    `defeats`,
                    `victories`
                ) SELECT 
                    FROM_UNIXTIME(?),
                    ?,
                    (SELECT id FROM `war_thunder_stats_v1`.`unit` WHERE name = ?),
                    (SELECT id FROM `war_thunder_stats_v1`.`gamemode` WHERE name = ?),
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ? 
                FROM DUAL 
                WHERE NOT EXISTS (
                    SELECT 
                        NULL 
                    FROM `war_thunder_stats_v1`.`unit_stat` 
                    WHERE 
                        user_id = ? AND 
                        unit_id = (SELECT id FROM `war_thunder_stats_v1`.`unit` WHERE name = ?) AND 
                        gamemode_id = (SELECT id FROM `war_thunder_stats_v1`.`gamemode` WHERE name = ?) AND 
                        was_in_lineup = ?
                );""", 
                ([timestamp, userid, unit, gamemode, spawns, deaths, experience, silverLions, groundKills, airKills, navalKills, wasInLineup, defeats, victories, userid, unit, gamemode, wasInLineup]))
                    
        # Commit to database
        conn.commit()
        
        # Insert/update the summary stats in the SummaryStatsGames and SummaryStats tables, the gamemode in the gamemode table, the game type in the GameType table and the VehicleClass in the VehicleClass table
        for gametype, gamemodeSummaryStats in userStatInformation['summary'].items():
            
            # Insert gameType
            cur.execute(
            "INSERT INTO `war_thunder_stats_v1`.`game_type` (`name`) SELECT ? FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`game_type` WHERE name = ?);",           
            ([gametype, gametype]))
            
            for gamemode, vehicleandmissions in gamemodeSummaryStats.items():
                
                # replace arcade with Arcade
                if gamemode == 'arcade':
                    gamemode = 'Arcade'
                
                # replace realistic with Realistic
                if gamemode == 'realistic':
                    gamemode = 'Realistic'
                
                # replace hardcore with Simulator
                if gamemode == 'hardcore':
                    gamemode = 'Simulator'
            
                # If gameMode doesn't exist insert it
                cur.execute(
                "INSERT INTO `war_thunder_stats_v1`.`gamemode` (`name`) SELECT ? FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`gamemode` WHERE name = ?);", 
                ([gamemode, gamemode]))
                    
                # Insert entry into summary_stats_game Table
                cur.execute(
                """INSERT INTO `war_thunder_stats_v1`.`summary_stats_game` (
                    `datetime`,
                    `user_id`,
                    `game_type_id`,
                    `gamemode_id`,
                    `missions_completed`,
                    `victories`
                ) SELECT
                    FROM_UNIXTIME(?),
                    ?,
                    (SELECT id FROM `war_thunder_stats_v1`.`game_type` WHERE name = ?),
                    (SELECT id FROM `war_thunder_stats_v1`.`gamemode` WHERE name = ?),
                    ?,
                    ?
                FROM DUAL 
                WHERE NOT EXISTS (
                    SELECT 
                        NULL 
                    FROM `war_thunder_stats_v1`.`summary_stats_game` 
                    WHERE 
                        user_id = ? AND 
                        game_type_id = (SELECT id FROM `war_thunder_stats_v1`.`game_type` WHERE name = ?) AND 
                        gamemode_id = (SELECT id FROM `war_thunder_stats_v1`.`gamemode` WHERE name = ?) AND 
                        missions_completed = ?
                );""", 
                ([timestamp, userid, gametype, gamemode, vehicleandmissions['missionsComplete'], vehicleandmissions['victories'], userid, gametype, gamemode, vehicleandmissions['missionsComplete']]))
                
                for unitClass, stats in vehicleandmissions.items():
                
                    # If the value isn't a vehicle class skip it
                    if unitClass == 'missionsComplete' or unitClass == 'victories':
                        continue
                    
                    # Insert unitClass
                    cur.execute(
                    "INSERT INTO `war_thunder_stats_v1`.`unit_class` (`class`) SELECT ? FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`unit_class` WHERE class = ?);", 
                    ([unitClass, unitClass]))
                        
                    # Get values and define others as 0 as they might not exist.
                    if "timePlayed" in stats:
                        timePlayed = stats['timePlayed']
                    else:
                        timePlayed = 0
                    
                    if "air_kills" in stats:
                        airKills = stats['air_kills']
                    else:
                        airKills = 0
                    
                    if "ground_kills" in stats:
                        groundKills = stats['ground_kills']
                    else:
                        groundKills = 0
                    
                    if "naval_kills" in stats:
                        navalKills = stats['naval_kills']
                    else:
                        navalKills = 0
                    
                    if "respawns" in stats:
                        spawns = stats['respawns']
                    else:
                        spawns = 0
                    
                    if "air_kills_ai" in stats:
                        airKillsAI = stats['air_kills_ai']
                    else:
                        airKillsAI = 0
                    
                    if "ground_kills_ai" in stats:
                        groundKillsAI = stats['ground_kills_ai']
                    else:
                        groundKillsAI = 0
                    
                    if "naval_kills_ai" in stats:
                        navalKillsAI = stats['naval_kills_ai']
                    else:
                        navalKillsAI = 0
                    
                    if "air_kills_bot" in stats:
                        airKillsBot = stats['air_kills_bot']
                    else:
                        airKillsBot = 0
                    
                    if "ground_kills_bot" in stats:
                        groundKillsBot = stats['ground_kills_bot']
                    else:
                        groundKillsBot = 0
                    
                    if "naval_kills_bot" in stats:
                        navalKillsBot = stats['naval_kills_bot']
                    else:
                        navalKillsBot = 0
                        
                    # Insert entry into SummaryStats Table
                    cur.execute(
                    """INSERT IGNORE INTO `war_thunder_stats_v1`.`summary_stat` (
                        `datetime`,
                        `user_id`,
                        `game_type_id`,
                        `gamemode_id`,
                        `unit_class_id`,
                        `time_played`,
                        `air_kills`,
                        `ground_kills`,
                        `naval_kills`,
                        `spawns`,
                        `air_kills_ai`,
                        `ground_kills_ai`,
                        `naval_kills_ai`,
                        `air_kills_bot`,
                        `ground_kills_bot`,
                        `naval_kills_bot`
                    ) SELECT 
                        FROM_UNIXTIME(?),
                        ?,
                        (SELECT id FROM `war_thunder_stats_v1`.`game_type` WHERE name = ?),
                        (SELECT id FROM `war_thunder_stats_v1`.`gamemode` WHERE name = ?),
                        (SELECT id FROM `war_thunder_stats_v1`.`unit_class` WHERE class = ?),
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?
                    FROM DUAL;""", 
                    ([timestamp, userid, gametype, gamemode, unitClass, timePlayed, airKills, groundKills, navalKills, spawns, airKillsAI, groundKillsAI, navalKillsAI, airKillsBot, groundKillsBot, navalKillsBot]))
                    
        # Commit to database
        conn.commit()
        
        # Insert/update the unlocks
        for unlock, unlockProperties in userStatInformation['unlocks'].items():
            
            # If it's not a medal we don't care
            if unlockProperties['type'] != 'medal':
                continue
            
            # Insert UnlockType
            cur.execute(
            "INSERT INTO `war_thunder_stats_v1`.`unlock_type` (`type`) SELECT ? FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`unlock_type` WHERE type = ?);",           
            ([unlockProperties['type'], unlockProperties['type']]))
            
            # Insert Unlock
            cur.execute(
            "INSERT INTO `war_thunder_stats_v1`.`unlock` (`name`,`type_id`) SELECT ?,(SELECT id FROM `war_thunder_stats_v1`.`unlock_type` WHERE type = ?) FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`unlock` WHERE name = ?);",           
            ([unlock, unlockProperties['type'], unlock]))
            
            # Insert UnlockCorrelation
            cur.execute(
            "INSERT INTO `war_thunder_stats_v1`.`unlock_correlation` (`datetime`,`user_id`,`unlock_id`) SELECT FROM_UNIXTIME(?),?,(SELECT id FROM `war_thunder_stats_v1`.`unlock` WHERE name = ?) FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`unlock_correlation` WHERE user_id = ? AND unlock_id = (SELECT id FROM `war_thunder_stats_v1`.`unlock` WHERE name = ?));",           
            ([timestamp, userid, unlock, userid, unlock]))
            
        # Commit to database
        conn.commit()
            
        # Close the cursor after use
        cur.close()
        
        return "Ingested user information for " + str(userid)
    else:
        return "userid: " + str(userid) + " has already been refreshed within the last 24 hours"
    