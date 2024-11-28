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
from urllib3.exceptions import InsecureRequestWarning

# Stop Python from warning about the certificate on ip 185.253.20.200
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Switch depending on windows or Linux
#prefix = "" # windows
prefix = "/tasks/" # linux

# Function to get a value if the property exists, else return None
def getValueIfExists(objectToCheck,valueToFind):
    if valueToFind in objectToCheck:
        return objectToCheck[valueToFind]
    else:
        return None

# Use a socket to prevent multiple instances of script running at once
s = socket.socket()
host = socket.gethostname()
port = 2001
s.bind((host, port))

# Connect to MariaDB  
try:
    conn = mariadb.connect(
        user="StatsSiteBatchJobs",
        password="UUo**wF4%Xb7cTuSY88@6Xu@!",
        host="192.168.3.1",
        port=13306,
        database="WarThunder"

    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)
    
# Get Cursor
cur = conn.cursor(dictionary=True)

# Pull list of users to update information for
cur.execute("SELECT * FROM WarThunder.UpdateQueue WHERE LastRefresh < DATE_SUB(now(), INTERVAL 7 DAY) AND Status = 0;")

users = cur.fetchall()

#users = [{'userID':5924642,'userID':15471872}]

for user in users:

    # Pull token information row if any tokens with more than 5 minutes left exist
    cur.execute("SELECT * FROM WarThunder.AccessToken WHERE WarThunder.AccessToken.LastRefresh > NOW() LIMIT 1")

    results = cur.fetchall()

    # Download BLK file
    if results:
        token = results[0]['Token']
        uidHint = results[0]['UidHint']
    
        userID = str(user['userID'])
        
        # Call the contact server to get a list of users matching the searched for username
        url = 'https://contact-proxy-02.gaijin.net/json'
        headers = {'token': token,'action': 'cln_find_users_by_nick_prefix_json','User-Agent': 'wt'}
        data = json.dumps({'ignoreCase': 'true','maxCount': '20','nick': userID,'specificAppId': '1067'})
        userListResponse = requests.post(url, data=data, headers=headers, verify=False)
        userList = json.loads(userListResponse.content)

        if userList:

            # Get the first userid returned
            userId = next(iter(userList))
            
            
            
            # get a timestamp, which will be used for the timestamp fields
            timestamp = int(time.time())
            
            tries = 0
            length = 0
            while tries < 4 and length < 3:
        
                # Calls the char server (Probably character server), to get public stats
                url = 'https://char-lw-nl-005-2.warthunder.com/char'
                headers = {'token': token,'action': 'ano_get_public_userstat','User-Agent': 'wt','userid': userID,'uidHint': str(uidHint)}
                userStatsResponse = requests.post(url, headers=headers, stream=True)

                # Write returned response to a file
                filename = prefix + 'blk-files/' + userID + '.blk'
                with open(filename, 'wb') as fd:
                    for chunk in userStatsResponse.iter_content(chunk_size=128):
                        fd.write(chunk)

                with open(filename, 'rb') as fp:
                    length = sum(1 for _ in fp)
                
                if length < 3:
                    # Wait a little before trying again
                    time.sleep(3)
                tries = tries + 1
                    
            if length < 3:
                # Update the LastRefresh time in the Update Queue
                cur.execute(
                "UPDATE `WarThunder`.`UpdateQueue` SET `Status` = 1 WHERE `userID` = ?;", 
                ([userID]))
                conn.commit()
                
                print("user with ID: " + userID + " returned invalid data 3 times in a row and was removed from queue")
                continue

            # Decode BLK file
            fileToDecode = prefix + "blk-files/" + userID + ".blk"
            fileToOutput = prefix + "json-files/" + userID + ".json"
            subprocess.Popen("python " + prefix + "wt_bin_parser/wt_bin_parser.py" + " -i " + fileToDecode + " -o " + fileToOutput, shell=True).wait()

            # Read JSON file
            file = open(fileToOutput)
            statInformation = json.load(file)

            # Pull information in if it exists
            userid = getValueIfExists(statInformation,'userid')
            nickname = getValueIfExists(statInformation,'nick')
            clanid = getValueIfExists(statInformation,'clanId')
            clanMemberRole = getValueIfExists(statInformation,'clanMemberRole')
            clanTag = getValueIfExists(statInformation,'clanTag')
            clanName = getValueIfExists(statInformation,'clanName')
            clanType = getValueIfExists(statInformation,'clanType')
            lastDay = getValueIfExists(statInformation,'lastDay')
            registerDay = getValueIfExists(statInformation,'registerDay')
            exp = getValueIfExists(statInformation,'exp')
            expConverted = getValueIfExists(statInformation,'expConverted')
            numEliteUnits = getValueIfExists(statInformation,'numEliteUnits')
            selectedTitleName = getValueIfExists(statInformation,'title')
            iconid = getValueIfExists(statInformation,'icon')
            iconName = getValueIfExists(statInformation,'iconName')
            penaltyStatus = getValueIfExists(statInformation,'penaltyStatus')
            
            # Check if the user has played since last stat pull
            cur.execute(
            "SELECT * FROM `WarThunderStats`.`GeneralStats` WHERE Experience=? AND UserID=?;", 
            ([exp, userID]))
            results = cur.fetchall()
            if results:
                # Update the LastRefresh time in the Update Queue
                cur.execute(
                "UPDATE `WarThunder`.`UpdateQueue` SET `Status` = 1 WHERE `userID` = ?;", 
                ([userID]))
                conn.commit()
            
                print("user with ID: " + userID + " returned the same RP/EXP as last pull, so profile wasn't updated")
                continue

            # If clanid has any other value than none, try to insert/update in the clan table
            if (clanid != None):
                cur.execute(
                "INSERT INTO `WarThunderStats`.`Clans` (`ClanID`,`ClanName`,`ClanTag`,`ClanType`) VALUES (?, ?, ?, ?) ON DUPLICATE KEY UPDATE ClanID=LAST_INSERT_ID(ClanID),ClanName=?,ClanTag=?,ClanType=?;", 
                ([clanid, clanName, clanTag, clanType, clanName, clanTag, clanType]))
                conn.commit()
                
                # Update the ClanRoles Table
                cur.execute(
                "INSERT IGNORE INTO `WarThunderStats`.`ClanRoles` (`ClanMemberRoleID`) VALUES (?);", 
                ([clanMemberRole]))
                conn.commit()
                
            # Insert/update in the Titles table
            if 'name' in statInformation['titles']:
                if isinstance(statInformation['titles']['name'], str):
                    cur.execute(
                    "SELECT * FROM `WarThunderStats`.`Titles` WHERE TitleName=?;", 
                    ([statInformation['titles']['name']]))
                    results = cur.fetchall()
                    if not results:
                        cur.execute(
                        "INSERT INTO `WarThunderStats`.`Titles` (`TitleName`) VALUES (?) ON DUPLICATE KEY UPDATE TitleID=LAST_INSERT_ID(TitleID),TitleName=?;", 
                        ([statInformation['titles']['name'], statInformation['titles']['name']]))
                        conn.commit()
                else:
                    for title in statInformation['titles']['name']:
                        cur.execute(
                        "SELECT * FROM `WarThunderStats`.`Titles` WHERE TitleName=?;", 
                        ([title]))
                        results = cur.fetchall()
                        if not results:
                            cur.execute(
                            "INSERT INTO `WarThunderStats`.`Titles` (`TitleName`) VALUES (?) ON DUPLICATE KEY UPDATE TitleID=LAST_INSERT_ID(TitleID),TitleName=?;", 
                            ([title, title]))
                            conn.commit()

            # Insert in the iconoid table
            cur.execute(
            "INSERT INTO `WarThunderStats`.`Icons` (`IconID`,`IconName`) VALUES (?,?) ON DUPLICATE KEY UPDATE IconID=LAST_INSERT_ID(IconID),IconName=?;", 
            ([iconid, iconName, iconName]))
            conn.commit()
            
            # Insert/update in the user table
            # Pull the the line containing the current title
            cur.execute(
            "SELECT * FROM `WarThunderStats`.`Titles` WHERE TitleName=?;", 
            ([selectedTitleName]))
            results = cur.fetchall()

            # do the actual insertion
            cur.execute(
            "INSERT INTO `WarThunderStats`.`Users` (`UserID`,`ClanID`,`Nickname`,`ClanMemberRoleID`,`LastDay`,`RegisterDay`,`SelectedTitleID`,`IconID`,`PenaltyStatus`) VALUES (?,?,?,?,FROM_UNIXTIME(?),FROM_UNIXTIME(?),?,?,?) ON DUPLICATE KEY UPDATE UserID=LAST_INSERT_ID(UserID),ClanID=?,Nickname=?,ClanMemberRoleID=?,LastDay=FROM_UNIXTIME(?),RegisterDay=FROM_UNIXTIME(?),SelectedTitleID=?,IconID=?,PenaltyStatus=?;", 
            ([userID, clanid, nickname, clanMemberRole, lastDay, registerDay, results[0]['TitleID'], iconid, penaltyStatus, clanid, nickname, clanMemberRole, lastDay, registerDay, results[0]['TitleID'], iconid, penaltyStatus]))
            conn.commit()
            
            # Insert/update in the TitleCorrelations table
            if 'name' in statInformation['titles']:
                if isinstance(statInformation['titles']['name'], str):
                    # Pull the the line containing the current title
                    cur.execute(
                    "SELECT * FROM `WarThunderStats`.`Titles` WHERE TitleName=?;", 
                    ([statInformation['titles']['name']]))
                    results = cur.fetchall()

                    # Insert a connection between the userid and titleid in the correlation table
                    cur.execute(
                    "INSERT IGNORE INTO `WarThunderStats`.`TitleCorrelations` (`UserID`,`TitleID`) VALUES (?,?);", 
                    ([userID, results[0]['TitleID']]))
                    conn.commit()
                else:
                    for title in statInformation['titles']['name']:
                        # Pull the the line containing the current title
                        cur.execute(
                        "SELECT * FROM `WarThunderStats`.`Titles` WHERE TitleName=?;", 
                        ([title]))
                        results = cur.fetchall()

                        # Insert a connection between the userid and titleid in the correlation table
                        cur.execute(
                        "INSERT IGNORE INTO `WarThunderStats`.`TitleCorrelations` (`UserID`,`TitleID`) VALUES (?,?);", 
                        ([userID, results[0]['TitleID']]))
                        conn.commit()

            # Insert in the generalstats table
            cur.execute(
            "INSERT INTO `WarThunderStats`.`GeneralStats` (`Timestamp`,`UserID`,`Experience`,`ExperienceConverted`,`NumberOfEliteUnits`) VALUES (FROM_UNIXTIME(?),?,?,?,?);", 
            ([timestamp, userID, exp, expConverted, numEliteUnits]))
            conn.commit()
            
            
            # Insert/update the vehicle name in the VehicleInformation table, the country name in the country table, modificationStatus in the ModificationStatus table and ModificationStatusPerUser into the ModificationStatusPerUser table
            for country, vehicleArray in statInformation['aircrafts'].items():
                
                countryID = 0
                vehicleID = 0
                
                # Check if country already exists
                cur.execute(
                "SELECT * FROM `WarThunderStats`.`Country` WHERE NationName=?;", 
                ([country]))
                results = cur.fetchall()
                if not results:
                    # If country doesn't exist insert it
                    cur.execute(
                    "INSERT INTO `WarThunderStats`.`Country` (`NationName`) VALUES (?) ON DUPLICATE KEY UPDATE CountryID=LAST_INSERT_ID(CountryID),NationName=?;", 
                    ([country, country]))
                    countryID = cur.lastrowid
                    conn.commit()
                else:
                    countryID = results[0]['CountryID']
                
                for vehicle, modificationStatus in vehicleArray.items():
                
                    # Check if vehicle already exists
                    cur.execute(
                    "SELECT * FROM `WarThunderStats`.`VehicleInformation` WHERE VehicleName=?;", 
                    ([vehicle]))
                    results = cur.fetchall()
                    if not results:
                        # If vehicle doesn't exist insert it
                        cur.execute(
                        "INSERT INTO `WarThunderStats`.`VehicleInformation` (`VehicleName`,`VehicleCountryID`) VALUES (?,?) ON DUPLICATE KEY UPDATE VehicleID=LAST_INSERT_ID(VehicleID),VehicleName=?,VehicleCountryID=?;", 
                        ([vehicle, countryID, vehicle, countryID]))
                        vehicleID = cur.lastrowid
                        conn.commit()
                    else:
                        vehicleID = results[0]['VehicleID']
                    
                    # Insert/update in the ModificationStatus Table
                    # Check if ModificationStatus already exists
                    cur.execute(
                    "SELECT * FROM `WarThunderStats`.`ModificationStatus` WHERE ModificationStatusID=?;", 
                    ([modificationStatus]))
                    results = cur.fetchall()
                    if not results:
                        # If ModificationStatus doesn't exist insert it
                        cur.execute(
                        "INSERT INTO `WarThunderStats`.`ModificationStatus` (`ModificationStatusID`) VALUES (?) ON DUPLICATE KEY UPDATE ModificationStatusID=?;", 
                        ([modificationStatus, modificationStatus]))
                        conn.commit()
                    
                    # Insert entry into ModificationStatusPerUser Table
                    cur.execute(
                    "INSERT INTO `WarThunderStats`.`ModificationStatusPerUser` (`Timestamp`,`UserID`,`VehicleID`,`ModificationStatusID`) VALUES (FROM_UNIXTIME(?),?,?,?) ON DUPLICATE KEY UPDATE Timestamp=FROM_UNIXTIME(?),UserID=?,VehicleID=?,ModificationStatusID=?;", 
                    ([timestamp, userID, vehicleID, modificationStatus, timestamp, userID, vehicleID, modificationStatus]))
                    conn.commit()
                    
            # Insert/update the vehicle stats in the VehicleStats table and the gamemode in the gamemode table
            for gamemode, gamemodeStats in statInformation['userstat'].items():
                gamemodeID = 0
                vehicleID = 0
                vehicleClassID = 0
                
                # Skip if the property new exists or the gamemodestats is False
                if gamemode == 'new' or gamemode == None or gamemode == 'none' or gamemodeStats == False:
                    continue
                
                # replace historical with realistic
                if gamemode == 'historical':
                    gamemode = 'realistic'
                    
                # replace historical with realistic
                if gamemode == 'simulation':
                    gamemode = 'simulator'
                
                # Check if gamemode already exists
                cur.execute(
                "SELECT * FROM `WarThunderStats`.`Gamemode` WHERE GamemodeName=?;", 
                ([gamemode]))
                results = cur.fetchall()
                if not results:
                    # If gamemode doesn't exist insert it
                    cur.execute(
                    "INSERT INTO `WarThunderStats`.`Gamemode` (`GamemodeName`) VALUES (?) ON DUPLICATE KEY UPDATE GamemodeID=LAST_INSERT_ID(GamemodeID),GamemodeName=?;", 
                    ([gamemode, gamemode]))
                    gamemodeID = cur.lastrowid
                    conn.commit()
                else:
                    gamemodeID = results[0]['GamemodeID']
                
                for vehicle, vehicleStats in gamemodeStats['total'].items():
                    
                    # Get vehicleID
                    cur.execute(
                    "SELECT * FROM `WarThunderStats`.`VehicleInformation` WHERE VehicleName=?;", 
                    ([vehicle]))
                    results = cur.fetchall()
                    if not results:
                        # If vehicle doesn't exist insert it
                        cur.execute(
                        "INSERT INTO `WarThunderStats`.`VehicleInformation` (`VehicleName`) VALUES (?) ON DUPLICATE KEY UPDATE VehicleID=LAST_INSERT_ID(VehicleID),VehicleName=?;", 
                        ([vehicle, vehicle]))
                        vehicleID = cur.lastrowid
                        conn.commit()
                    else:
                        vehicleID = results[0]['VehicleID']
                
                    # Get values and define others as 0 as they might not exist.
                    if "flyouts" in vehicleStats:
                        spawns = vehicleStats['flyouts']
                    else:
                        spawns = 0
                    if "deaths" in vehicleStats:
                        deaths = vehicleStats['deaths']
                    else:
                        deaths = 0
                    if "wp_total" in vehicleStats:
                        silverLions = vehicleStats['wp_total']
                    else:
                        silverLions = 0
                    if "online_exp_total" in vehicleStats:
                        experience = vehicleStats['online_exp_total']
                    else:
                        experience = 0
                    if "defeats" in vehicleStats:
                        defeats = vehicleStats['defeats']
                    else:
                        defeats = 0
                    if "victories" in vehicleStats:
                        victories = vehicleStats['victories']
                    else:
                        victories = 0
                    if "was_in_session" in vehicleStats:
                        wasInLineup = vehicleStats['was_in_session']
                    else:
                        wasInLineup = 0
                    if "air_kills" in vehicleStats:
                        airKills = vehicleStats['air_kills']
                    else:
                        airKills = 0
                    if "ground_kills" in vehicleStats:
                        groundKills = vehicleStats['ground_kills']
                    else:
                        groundKills = 0
                    if "naval_kills" in vehicleStats:
                        navalKills = vehicleStats['naval_kills']
                    else:
                        navalKills = 0
                        
                    # Insert entry into VehicleStats Table
                    cur.execute(
                    "INSERT INTO `WarThunderStats`.`VehicleStats` (`Timestamp`,`UserID`,`VehicleID`,`GamemodeID`,`Spawns`,`Deaths`,`ExperienceEarned`,`SilverLionsEarned`,`GroundKills`,`AirKills`,`NavalKills`,`WasInLineup`,`Defeats`,`Victories`) VALUES (FROM_UNIXTIME(?),?,?,?,?,?,?,?,?,?,?,?,?,?) ON DUPLICATE KEY UPDATE Timestamp=FROM_UNIXTIME(?),UserID=?,VehicleID=?,GamemodeID=?,Spawns=?,Deaths=?,ExperienceEarned=?,SilverLionsEarned=?,GroundKills=?,AirKills=?,NavalKills=?,WasInLineup=?,Defeats=?,Victories=?;", 
                    ([timestamp, userID, vehicleID, gamemodeID, spawns, deaths, experience, silverLions, groundKills, airKills, navalKills, wasInLineup, defeats, victories, timestamp, userID, vehicleID, gamemodeID, spawns, deaths, experience, silverLions, groundKills, airKills, navalKills, wasInLineup, defeats, victories]))
                    conn.commit()
                    
            
            # Insert/update the summary stats in the SummaryStatsGames and SummaryStats tables, the gamemode in the gamemode table, the game type in the GameType table and the VehicleClass in the VehicleClass table
            for gametype, gamemodeSummaryStats in statInformation['summary'].items():
                gameTypeID = 0
                gameModeID = 0
                
                # Get gameType
                cur.execute(
                "SELECT * FROM `WarThunderStats`.`GameType` WHERE GameTypeName=?;", 
                ([gametype]))
                results = cur.fetchall()
                if not results:
                    # If gameType doesn't exist insert it
                    cur.execute(
                    "INSERT INTO `WarThunderStats`.`GameType` (`GameTypeName`) VALUES (?) ON DUPLICATE KEY UPDATE GameTypeID=LAST_INSERT_ID(GameTypeID),GameTypeName=?;", 
                    ([gametype, gametype]))
                    gameTypeID = cur.lastrowid
                    conn.commit()
                else:
                    gameTypeID = results[0]['GameTypeID']
                
                for gamemode, vehicleandmissions in gamemodeSummaryStats.items():
                
                    # Change hardcore to simulator
                    if gamemode == 'hardcore':
                        gamemode = 'simulator'
                
                    # Get gameMode
                    cur.execute(
                    "SELECT * FROM `WarThunderStats`.`Gamemode` WHERE GamemodeName=?;", 
                    ([gamemode]))
                    results = cur.fetchall()
                    if not results:
                        # If gameMode doesn't exist insert it
                        cur.execute(
                        "INSERT INTO `WarThunderStats`.`Gamemode` (`GamemodeName`) VALUES (?) ON DUPLICATE KEY UPDATE GamemodeID=LAST_INSERT_ID(GamemodeID),GamemodeName=?;", 
                        ([gamemode, gamemode]))
                        gameModeID = cur.lastrowid
                        conn.commit()
                    else:
                        gameModeID = results[0]['GamemodeID']
                        
                    # Insert entry into SummaryStatsGames Table
                    cur.execute(
                    "INSERT INTO `WarThunderStats`.`SummaryStatsGames` (`Timestamp`,`UserID`,`GameTypeID`,`GamemodeID`,`MissionsCompleted`,`Victories`) VALUES (FROM_UNIXTIME(?),?,?,?,?,?) ON DUPLICATE KEY UPDATE Timestamp=FROM_UNIXTIME(?),UserID=?,GameTypeID=?,GamemodeID=?,MissionsCompleted=?,Victories=?;", 
                    ([timestamp, userID, gameTypeID, gameModeID, vehicleandmissions['missionsComplete'], vehicleandmissions['victories'], timestamp, userID, gameTypeID, gameModeID, vehicleandmissions['missionsComplete'], vehicleandmissions['victories']]))
                    conn.commit()
                    
                    for vehicleClass, stats in vehicleandmissions.items():
                    
                        # If the value isn't a vehicle class skip it
                        if vehicleClass == 'missionsComplete' or vehicleClass == 'victories':
                            continue
                        
                        # Get vehicleClass
                        cur.execute(
                        "SELECT * FROM `WarThunderStats`.`VehicleClass` WHERE VehicleClassName=?;", 
                        ([vehicleClass]))
                        results = cur.fetchall()
                        if not results:
                            # If vehicleClass doesn't exist insert it
                            cur.execute(
                            "INSERT INTO `WarThunderStats`.`VehicleClass` (`VehicleClassName`) VALUES (?) ON DUPLICATE KEY UPDATE VehicleClassID=LAST_INSERT_ID(VehicleClassID),VehicleClassName=?;", 
                            ([vehicleClass, vehicleClass]))
                            vehicleClassID = cur.lastrowid
                            conn.commit()
                        else:
                            vehicleClassID = results[0]['VehicleClassID']
                            
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
                        "INSERT INTO `WarThunderStats`.`SummaryStats` (`Timestamp`,`UserID`,`GameTypeID`,`GamemodeID`,`VehicleClassID`,`TimePlayed`,`AirKills`,`GroundKills`,`NavalKills`,`Spawns`,`AirKillsAI`,`GroundKillsAI`,`NavalKillsAI`,`AirKillsBot`,`GroundKillsBot`,`NavalKillsBot`) VALUES (FROM_UNIXTIME(?),?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON DUPLICATE KEY UPDATE Timestamp=FROM_UNIXTIME(?),UserID=?,GameTypeID=?,GamemodeID=?,VehicleClassID=?,TimePlayed=?,AirKills=?,GroundKills=?,NavalKills=?,Spawns=?,AirKillsAI=?,GroundKillsAI=?,NavalKillsAI=?,AirKillsBot=?,GroundKillsBot=?,NavalKillsBot=?;", 
                        ([timestamp, userID, gameTypeID, gameModeID, vehicleClassID, timePlayed, airKills, groundKills, navalKills, spawns, airKillsAI, groundKillsAI, navalKillsAI, airKillsBot, groundKillsBot, navalKillsBot, timestamp, userID, gameTypeID, gameModeID, vehicleClassID, timePlayed, airKills, groundKills, navalKills, spawns, airKillsAI, groundKillsAI, navalKillsAI, airKillsBot, groundKillsBot, navalKillsBot]))
                        conn.commit()
            
            # Update the LastRefresh time in the Update Queue
            cur.execute(
            "UPDATE `WarThunder`.`UpdateQueue` SET `LastRefresh` = FROM_UNIXTIME(?), `Status` = 1, `TimeSinceLastActivity` = 0 WHERE `userID` = ?;", 
            ([timestamp, userID]))
            conn.commit()
            
            print("Updated stats for: " + userID + " - " + nickname)
        else:
            # Update the LastRefresh time in the Update Queue
            cur.execute(
            "UPDATE `WarThunder`.`UpdateQueue` SET `Status` = 1, `TimeSinceLastActivity` = 0 WHERE `userID` = ?;", 
            ([userID]))
            conn.commit()
            
            print("Didn't find a user matching ID: " + userID + " So it was removed from queue")
cur.close()

time.sleep(3)

files = glob.glob(prefix + 'json-files/*')
for f in files:
    os.remove(f)
    
files = glob.glob(prefix + 'blk-files/*')
for f in files:
    os.remove(f)