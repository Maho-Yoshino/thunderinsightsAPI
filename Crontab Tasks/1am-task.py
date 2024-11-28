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
port = 2002
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

# Get a list of vehicles
cur.execute(
"SELECT VehicleName, VehicleID FROM `WarThunderStats`.`VehicleInformation`;")
vehicles = cur.fetchall()

for vehicle in vehicles:

    vehicleName = str(vehicle['VehicleName'])

    # Read JSON file containing translations
    file = open(prefix + "dailyInfoUpdate/units.json",'r',encoding='utf-16')
    Translations = json.load(file)
    TranslationShopName = next((Translation for Translation in Translations if (Translation['ID'] == vehicleName + "_shop")),None)
    TranslationFullName = next((Translation for Translation in Translations if (Translation['ID'] == vehicleName + "_0")),None)
    TranslationShortName = next((Translation for Translation in Translations if (Translation['ID'] == vehicleName + "_1")),None)
    TranslationCompressedName = next((Translation for Translation in Translations if (Translation['ID'] == vehicleName + "_2")),None)

    if TranslationShopName != None:
        for language in TranslationShopName.keys():
            if language == "ID" or language == "Comments" or language == "max_chars":
                continue
            # Check if country already exists
            cur.execute(
            "SELECT * FROM `WarThunderStats`.`Languages` WHERE Language=?;", 
            ([language]))
            results = cur.fetchall()
            if not results:
                # If country doesn't exist insert it
                cur.execute(
                "INSERT INTO `WarThunderStats`.`Languages` (`Language`) VALUES (?) ON DUPLICATE KEY UPDATE LanguageID=LAST_INSERT_ID(LanguageID),Language=?;", 
                ([language, language]))
                languageID = cur.lastrowid
                conn.commit()
            else:
                languageID = results[0]['LanguageID']
            
            if TranslationFullName == None:
                TranslationFullNameLanguage = ""
            else:
                TranslationFullNameLanguage = TranslationFullName[language]
                
            if TranslationShortName == None:
                TranslationShortNameLanguage = ""
            else:
                TranslationShortNameLanguage = TranslationShortName[language]
                
            if TranslationCompressedName == None:
                TranslationCompressedNameLanguage = ""
            else:
                TranslationCompressedNameLanguage = TranslationCompressedName[language]
            
            # Insert vehicles Names in the VehicleNames Table
            cur.execute(
            "INSERT INTO `WarThunderStats`.`VehicleNames` (`VehicleID`,`LanguageID`,`ShopName`,`FullName`,`ShortName`,`CompressedName`) VALUES (?,?,?,?,?,?) ON DUPLICATE KEY UPDATE ShopName=?,FullName=?,ShortName=?,CompressedName=?;", 
            ([vehicle['VehicleID'], languageID, TranslationShopName[language], TranslationFullNameLanguage, TranslationShortNameLanguage, TranslationCompressedNameLanguage, TranslationShopName[language], TranslationFullNameLanguage, TranslationShortNameLanguage, TranslationCompressedNameLanguage]))
            conn.commit()
            
    # Read JSON file containing prices, ranks, battleratings, vehicle types and so on.
    file = open(prefix + "dailyInfoUpdate/wpcost.json",'r',encoding='utf-8')
    informationAboutAllVehicles = json.load(file)
    if vehicleName in informationAboutAllVehicles:
        informationAboutCurrentVehicle = informationAboutAllVehicles[vehicleName]
        if informationAboutCurrentVehicle:
            
            # Check if vehicle is a premium, event or squadron vehicle.
            if 'costGold' in informationAboutCurrentVehicle:
                costGold = informationAboutCurrentVehicle['costGold']
                premium = 1
                if 'gift' in informationAboutCurrentVehicle and not 'event' in informationAboutCurrentVehicle:
                    gift = 1
                else:
                    gift = 0
            else:
                costGold = 0
                premium = 0
                gift = 0
            if 'event' in informationAboutCurrentVehicle:
                event = 1
            else:
                event = 0
            if 'researchType' in informationAboutCurrentVehicle and informationAboutCurrentVehicle['researchType'] == "clanVehicle":
                clan = 1
                if costGold == 0:
                    costGold = informationAboutCurrentVehicle['openCostGold']
            else:
                clan = 0
            
            # Get the silver lion cost, Research points required, battlerating ID and Rank of the vehicle
            cost = informationAboutCurrentVehicle['value']
            if 'reqExp' in informationAboutCurrentVehicle:
                experience = informationAboutCurrentVehicle['reqExp']
            else:
                experience = 0
            battleratingArcade = informationAboutCurrentVehicle['economicRankArcade']
            battleratingRealistic = informationAboutCurrentVehicle['economicRankHistorical']
            battleratingSimulator = informationAboutCurrentVehicle['economicRankSimulation']
            rank = informationAboutCurrentVehicle['rank']
            
            # Check if battlerating for Arcade already exists
            cur.execute(
            "SELECT * FROM `WarThunderStats`.`Battlerating` WHERE BatleratingID=?;", 
            ([battleratingArcade]))
            results = cur.fetchall()
            if not results:
                # If battlerating doesn't exist insert it
                cur.execute(
                "INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`) VALUES (?) ON DUPLICATE KEY UPDATE BatleratingID=LAST_INSERT_ID(BatleratingID);", 
                ([battleratingArcade]))
                conn.commit()
            # Get Arcade gamemode ID
            cur.execute(
            "SELECT * FROM `WarThunderStats`.`Gamemode` WHERE GamemodeName=?;", 
            (["arcade"]))
            results = cur.fetchall()
            arcadeGamemodeID = results[0]['GamemodeID']
            # Insert combined value into the battleratingCorrelation table
            cur.execute(
            "INSERT INTO `WarThunderStats`.`BattleratingCorrelations` (`VehicleID`,`GamemodeID`,`BatleratingID`) VALUES (?,?,?) ON DUPLICATE KEY UPDATE BatleratingID=?;", 
            ([vehicle['VehicleID'], arcadeGamemodeID, battleratingArcade, battleratingArcade]))
            conn.commit()
            
                
            # Check if battlerating for Realistic already exists
            cur.execute(
            "SELECT * FROM `WarThunderStats`.`Battlerating` WHERE BatleratingID=?;", 
            ([battleratingRealistic]))
            results = cur.fetchall()
            if not results:
                # If battlerating doesn't exist insert it
                cur.execute(
                "INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`) VALUES (?) ON DUPLICATE KEY UPDATE BatleratingID=LAST_INSERT_ID(BatleratingID);", 
                ([battleratingRealistic]))
                conn.commit()
            # Get Realistic gamemode ID
            cur.execute(
            "SELECT * FROM `WarThunderStats`.`Gamemode` WHERE GamemodeName=?;", 
            (["realistic"]))
            results = cur.fetchall()
            realisticGamemodeID = results[0]['GamemodeID']
            # Insert combined value into the battleratingCorrelation table
            cur.execute(
            "INSERT INTO `WarThunderStats`.`BattleratingCorrelations` (`VehicleID`,`GamemodeID`,`BatleratingID`) VALUES (?,?,?) ON DUPLICATE KEY UPDATE BatleratingID=?;", 
            ([vehicle['VehicleID'], realisticGamemodeID, battleratingRealistic, battleratingRealistic]))
            conn.commit()
            
                
            # Check if battlerating for Simulator already exists
            cur.execute(
            "SELECT * FROM `WarThunderStats`.`Battlerating` WHERE BatleratingID=?;", 
            ([battleratingSimulator]))
            results = cur.fetchall()
            if not results:
                # If battlerating doesn't exist insert it
                cur.execute(
                "INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`) VALUES (?) ON DUPLICATE KEY UPDATE BatleratingID=LAST_INSERT_ID(BatleratingID);", 
                ([battleratingSimulator]))
                conn.commit()
            # Get Simulator gamemode ID
            cur.execute(
            "SELECT * FROM `WarThunderStats`.`Gamemode` WHERE GamemodeName=?;", 
            (["simulator"]))
            results = cur.fetchall()
            simulatorGamemodeID = results[0]['GamemodeID']
            # Insert combined value into the battleratingCorrelation table
            cur.execute(
            "INSERT INTO `WarThunderStats`.`BattleratingCorrelations` (`VehicleID`,`GamemodeID`,`BatleratingID`) VALUES (?,?,?) ON DUPLICATE KEY UPDATE BatleratingID=?;", 
            ([vehicle['VehicleID'], simulatorGamemodeID, battleratingSimulator, battleratingSimulator]))
            conn.commit()
            
            
            # Check if rank/tier already exists
            cur.execute(
            "SELECT * FROM `WarThunderStats`.`Tier` WHERE TierID=?;", 
            ([rank]))
            results = cur.fetchall()
            if not results:
                # If rank/tier doesn't exist insert it
                cur.execute(
                "INSERT INTO `WarThunderStats`.`Tier` (`TierID`) VALUES (?) ON DUPLICATE KEY UPDATE TierID=LAST_INSERT_ID(TierID);", 
                ([rank]))
                conn.commit()
                
            # Check if vehicle cost already exists for gold
            cur.execute(
            "SELECT * FROM `WarThunderStats`.`VehicleCost` WHERE VehicleCost=?;", 
            ([costGold]))
            results = cur.fetchall()
            if not results:
                # If cost doesn't exist insert it
                cur.execute(
                "INSERT INTO `WarThunderStats`.`VehicleCost` (`VehicleCost`) VALUES (?) ON DUPLICATE KEY UPDATE VehicleCostID=LAST_INSERT_ID(VehicleCostID),VehicleCost=?;", 
                ([costGold, costGold]))
                costGoldID = cur.lastrowid
                conn.commit()
            else:
                costGoldID = results[0]['VehicleCostID']
                
            # Check if vehicle cost already exists for silver lions
            cur.execute(
            "SELECT * FROM `WarThunderStats`.`VehicleCost` WHERE VehicleCost=?;", 
            ([cost]))
            results = cur.fetchall()
            if not results:
                # If cost doesn't exist insert it
                cur.execute(
                "INSERT INTO `WarThunderStats`.`VehicleCost` (`VehicleCost`) VALUES (?) ON DUPLICATE KEY UPDATE VehicleCostID=LAST_INSERT_ID(VehicleCostID),VehicleCost=?;", 
                ([cost, cost]))
                costID = cur.lastrowid
                conn.commit()
            else:
                costID = results[0]['VehicleCostID']
                
            # Check if vehicle experience required already exists
            cur.execute(
            "SELECT * FROM `WarThunderStats`.`VehicleExperienceRequirement` WHERE VehicleExperience=?;", 
            ([experience]))
            results = cur.fetchall()
            if not results:
                # If experience required doesn't exist insert it
                cur.execute(
                "INSERT INTO `WarThunderStats`.`VehicleExperienceRequirement` (`VehicleExperience`) VALUES (?) ON DUPLICATE KEY UPDATE VehicleExperienceID=LAST_INSERT_ID(VehicleExperienceID),VehicleExperience=?;", 
                ([experience, experience]))
                experienceID = cur.lastrowid
                conn.commit()
            else:
                experienceID = results[0]['VehicleExperienceID']
                
            # Check if country already exists
            cur.execute(
            "SELECT * FROM `WarThunderStats`.`Country` WHERE NationName=?;", 
            ([informationAboutCurrentVehicle['country']]))
            results = cur.fetchall()
            if not results:
                # If country doesn't exist insert it
                cur.execute(
                "INSERT INTO `WarThunderStats`.`Country` (`NationName`) VALUES (?) ON DUPLICATE KEY UPDATE CountryID=LAST_INSERT_ID(CountryID),NationName=?;", 
                ([informationAboutCurrentVehicle['country'], informationAboutCurrentVehicle['country']]))
                countryID = cur.lastrowid
                conn.commit()
            else:
                countryID = results[0]['CountryID']
                
            # Insert vehicle information in the VehicleInformation Table
            cur.execute(
            "INSERT INTO `WarThunderStats`.`VehicleInformation` (`VehicleID`,`VehicleCountryID`,`VehicleTierID`,`VehicleExperienceID`,`VehicleCostID`,`VehicleCostGoldID`,`Premium`,`Gift`,`Event`,`Clan`) VALUES (?,?,?,?,?,?,?,?,?,?) ON DUPLICATE KEY UPDATE VehicleCountryID=?,VehicleTierID=?,VehicleExperienceID=?,VehicleCostID=?,VehicleCostGoldID=?,Premium=?,Gift=?,Event=?,Clan=?;", 
            ([vehicle['VehicleID'], countryID, rank, experienceID, costID, costGoldID, premium, gift, event, clan, countryID, rank, experienceID, costID, costGoldID, premium, gift, event, clan]))
            conn.commit()

    # Read JSON file containing vehicle type and tags.
    file = open(prefix + "dailyInfoUpdate/unittags.json",'r',encoding='utf-8')
    vehiclesCountriesAndTags = json.load(file)
    if vehicleName in vehiclesCountriesAndTags:
        vehicleCountriesAndTags = vehiclesCountriesAndTags[vehicleName]
        if vehicleCountriesAndTags:
            
            # Check if vehicle type already exists
            cur.execute(
            "SELECT * FROM `WarThunderStats`.`VehicleType` WHERE VehicleTypeName=?;", 
            ([vehicleCountriesAndTags['type'].capitalize()]))
            results = cur.fetchall()
            if not results:
                # If vehicle type doesn't exist insert it
                cur.execute(
                "INSERT INTO `WarThunderStats`.`VehicleType` (`VehicleTypeName`) VALUES (?) ON DUPLICATE KEY UPDATE VehicleTypeID=LAST_INSERT_ID(VehicleTypeID),VehicleTypeName=?;", 
                ([vehicleCountriesAndTags['type'].capitalize(), vehicleCountriesAndTags['type'].capitalize()]))
                vehicleTypeID = cur.lastrowid
                conn.commit()
            else:
                vehicleTypeID = results[0]['VehicleTypeID']
            
            
            # Get the operator country and set it if it doesn't already exist
            if 'operatorCountry' in vehicleCountriesAndTags:
                operatorCountry = vehicleCountriesAndTags['operatorCountry']
            else:
                for tag in vehicleCountriesAndTags['tags'].keys():
                    if re.match('country_', tag): 
                        operatorCountry = tag
            
            # Get the id of the operator country or create it if it doesn't exist
            cur.execute(
            "SELECT * FROM `WarThunderStats`.`Country` WHERE NationName=?;", 
            ([operatorCountry]))
            results = cur.fetchall()
            if not results:
                # If operator country doesn't exist insert it
                cur.execute(
                "INSERT INTO `WarThunderStats`.`Country` (`NationName`) VALUES (?) ON DUPLICATE KEY UPDATE CountryID=LAST_INSERT_ID(CountryID),NationName=?;", 
                ([operatorCountry, operatorCountry]))
                countryID = cur.lastrowid
                conn.commit()
            else:
                countryID = results[0]['CountryID']
            
            # Go through the tags and combine them with the vehicles
            queryToRemoveOldTags = "DELETE FROM `WarThunderStats`.`VehicleTagCorrelations` WHERE VehicleID = ? AND VehicleTagID NOT IN ("
            valuesToKeepInTagCorrelation = [vehicle['VehicleID']]
            trackAmountOfQuestionMarksToUse = []
            for tag in vehicleCountriesAndTags['tags'].keys():
                if re.match('type_', tag): 
                    # Get the id of the tag or create it if it doesn't exist
                    cur.execute(
                    "SELECT * FROM `WarThunderStats`.`VehicleTags` WHERE VehicleTagName=?;", 
                    ([tag]))
                    results = cur.fetchall()
                    if not results:
                        # If tag doesn't exist insert it
                        cur.execute(
                        "INSERT INTO `WarThunderStats`.`VehicleTags` (`VehicleTagName`) VALUES (?) ON DUPLICATE KEY UPDATE VehicleTagID=LAST_INSERT_ID(VehicleTagID),VehicleTagName=?;", 
                        ([tag, tag]))
                        vehicleTagID = cur.lastrowid
                        conn.commit()
                    else:
                        vehicleTagID = results[0]['VehicleTagID']
                    
                    valuesToKeepInTagCorrelation.append(vehicleTagID)
                    trackAmountOfQuestionMarksToUse.append("?")
                        
                    # Insert into tag correlations table
                    cur.execute(
                    "INSERT INTO `WarThunderStats`.`VehicleTagCorrelations` (`VehicleID`,`VehicleTagID`) VALUES (?,?) ON DUPLICATE KEY UPDATE VehicleID=?,VehicleTagID=?;", 
                    ([vehicle['VehicleID'], vehicleTagID, vehicle['VehicleID'], vehicleTagID]))
                    conn.commit()
            queryToRemoveOldTags += ','.join(trackAmountOfQuestionMarksToUse)
            queryToRemoveOldTags += ");"
            # delete old tag correlations no longer related to vehicle
            cur.execute(
            queryToRemoveOldTags, 
            (valuesToKeepInTagCorrelation))
            conn.commit()
            
            
            # Insert vehicle information in the VehicleInformation Table
            cur.execute(
            "INSERT INTO `WarThunderStats`.`VehicleInformation` (`VehicleID`,`OperatorCountryID`,`VehicleTypeID`) VALUES (?,?,?) ON DUPLICATE KEY UPDATE OperatorCountryID=?,VehicleTypeID=?;", 
            ([vehicle['VehicleID'], countryID, vehicleTypeID, countryID, vehicleTypeID]))
            conn.commit()
            
cur.execute(
"SELECT p2.VehicleID as VehicleID, p2.GamemodeID as GamemodeID, COUNT(DISTINCT(p2.UserID)) as UniqueUsers, sum(p2.Spawns) as Spawns, sum(p2.Deaths) as Deaths, sum(p2.ExperienceEarned) as ExperienceEarned, sum(p2.SilverLionsEarned) as SilverLionsEarned, sum(p2.GroundKills) as GroundKills, sum(p2.AirKills) as AirKills, sum(p2.NavalKills) as NavalKills, sum(p2.WasInLineup) as WasInLineup, sum(p2.Defeats) as Defeats, sum(p2.Victories) as Victories FROM (SELECT UserID, VehicleID, GamemodeID, MAX(Timestamp) AS maxdate FROM WarThunderStats.VehicleStats GROUP BY UserID, VehicleID, GamemodeID) AS p1 LEFT JOIN WarThunderStats.VehicleStats p2 ON p1.UserID = p2.UserID AND p2.Timestamp = p1.maxdate AND p2.VehicleID = p1.VehicleID AND p2.GamemodeID = p1.GamemodeID GROUP BY p2.VehicleID, p2.GamemodeID;", 
())
results = cur.fetchall()

for vehicle in results:

    cur.execute(
    "INSERT INTO `WarThunderStats`.`VehicleStatsByUpdate` (`VehicleID`,`UpdateID`,`GamemodeID`,`PlayedByUniqueUsers`,`Spawns`,`Deaths`,`ExperienceEarned`,`SilverLionsEarned`,`GroundKills`,`AirKills`,`NavalKills`,`WasInLineup`,`Defeats`,`Victories`) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON DUPLICATE KEY UPDATE PlayedByUniqueUsers=?,Spawns=?,Deaths=?,ExperienceEarned=?,SilverLionsEarned=?,GroundKills=?,AirKills=?,NavalKills=?,WasInLineup=?,Defeats=?,Victories=?;", 
    ([vehicle['VehicleID'], 0, vehicle["GamemodeID"], vehicle["UniqueUsers"], vehicle["Spawns"], vehicle["Deaths"], vehicle["ExperienceEarned"], vehicle["SilverLionsEarned"], vehicle["GroundKills"], vehicle["AirKills"], vehicle["NavalKills"], vehicle["WasInLineup"], vehicle["Defeats"], vehicle["Victories"], vehicle["UniqueUsers"], vehicle["Spawns"], vehicle["Deaths"], vehicle["ExperienceEarned"], vehicle["SilverLionsEarned"], vehicle["GroundKills"], vehicle["AirKills"], vehicle["NavalKills"], vehicle["WasInLineup"], vehicle["Defeats"], vehicle["Victories"]]))
    conn.commit()
    
    cur.execute(
    "SELECT p2.VehicleID as VehicleID, COUNT(DISTINCT(p2.UserID)) as UniqueUsers FROM (SELECT VehicleID, UserID, MAX(Timestamp) AS maxdate FROM WarThunderStats.ModificationStatusPerUser GROUP BY UserID, VehicleID) as p1 LEFT JOIN WarThunderStats.ModificationStatusPerUser p2 ON p1.UserID = p2.UserID AND p2.Timestamp = p1.maxdate AND p2.VehicleID = p1.VehicleID WHERE p2.VehicleID = ? GROUP BY p2.VehicleID;", 
    ([vehicle['VehicleID']]))
    uniqueOwners = cur.fetchall()
    
    if uniqueOwners:

        cur.execute(
        "INSERT INTO `WarThunderStats`.`VehicleOwnerCounts` (`VehicleID`,`UniqueOwners`) VALUES (?,?) ON DUPLICATE KEY UPDATE UniqueOwners=?;", 
        ([vehicle['VehicleID'], uniqueOwners[0]["UniqueUsers"], uniqueOwners[0]["UniqueUsers"]]))
        conn.commit()
    
cur.execute(
"SELECT UpdateID, UpdateTitle, UpdateVersion, UpdateDate, COALESCE(UpdateEOLDate, now()) as UpdateEOLDate, StatsRefreshesEnabled FROM WarThunderStats.Updates WHERE StatsRefreshesEnabled=1 AND UpdateID!=0;", 
())
updates = cur.fetchall()

for update in updates:
    
    cur.execute(
    "SELECT VehicleID as VehicleID, GamemodeID as GamemodeID, COUNT(DISTINCT(UserID)) as UniqueUsers, sum(Spawns) as Spawns, sum(Deaths) as Deaths, sum(ExperienceEarned) as ExperienceEarned, sum(SilverLionsEarned) as SilverLionsEarned, sum(GroundKills) as GroundKills, sum(AirKills) as AirKills, sum(NavalKills) as NavalKills, sum(WasInLineup) as WasInLineup, sum(Defeats) as Defeats, sum(Victories) as Victories FROM (SELECT p2.VehicleID as VehicleID, p2.GamemodeID as GamemodeID, p2.UserID as UserID, max(p2.Spawns) - min(p2.Spawns) as Spawns, max(p2.Deaths) - min(p2.Deaths) as Deaths, max(p2.ExperienceEarned) - min(p2.ExperienceEarned) as ExperienceEarned, max(p2.SilverLionsEarned) - min(p2.SilverLionsEarned) as SilverLionsEarned, max(p2.GroundKills) - min(p2.GroundKills) as GroundKills, max(p2.AirKills) - min(p2.AirKills) as AirKills, max(p2.NavalKills) - min(p2.NavalKills) as NavalKills, max(p2.WasInLineup) - min(p2.WasInLineup) as WasInLineup, max(p2.Defeats) - min(p2.Defeats) as Defeats, max(p2.Victories) - min(p2.Victories) as Victories FROM (select UserID, VehicleID, GamemodeID, Timestamp from (SELECT UserID, VehicleID, GamemodeID, Timestamp, ROW_NUMBER() OVER(PARTITION BY UserID, VehicleID, GamemodeID ORDER BY timestamp asc) as r1, ROW_NUMBER() OVER(PARTITION BY UserID, VehicleID, GamemodeID ORDER BY timestamp desc) as r2 FROM WarThunderStats.VehicleStats WHERE Timestamp > ? AND Timestamp < ?) data WHERE 1 IN (r1,r2) AND r1 != r2) AS p1 LEFT JOIN WarThunderStats.VehicleStats p2 ON p1.UserID = p2.UserID AND p2.Timestamp = p1.Timestamp AND p2.VehicleID = p1.VehicleID AND p2.GamemodeID = p1.GamemodeID GROUP BY p2.UserID, p2.VehicleID, p2.GamemodeID) filtereddata WHERE WasInLineup > 0 GROUP BY VehicleID, GamemodeID;", 
    (update['UpdateDate'],update['UpdateEOLDate'],))
    vehicles = cur.fetchall()

    for vehicle in vehicles:
        
        cur.execute(
        "INSERT INTO `WarThunderStats`.`VehicleStatsByUpdate` (`VehicleID`,`UpdateID`,`GamemodeID`,`PlayedByUniqueUsers`,`Spawns`,`Deaths`,`ExperienceEarned`,`SilverLionsEarned`,`GroundKills`,`AirKills`,`NavalKills`,`WasInLineup`,`Defeats`,`Victories`) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON DUPLICATE KEY UPDATE PlayedByUniqueUsers=?,Spawns=?,Deaths=?,ExperienceEarned=?,SilverLionsEarned=?,GroundKills=?,AirKills=?,NavalKills=?,WasInLineup=?,Defeats=?,Victories=?;", 
        ([vehicle['VehicleID'], update["UpdateID"], vehicle["GamemodeID"], vehicle["UniqueUsers"], vehicle["Spawns"], vehicle["Deaths"], vehicle["ExperienceEarned"], vehicle["SilverLionsEarned"], vehicle["GroundKills"], vehicle["AirKills"], vehicle["NavalKills"], vehicle["WasInLineup"], vehicle["Defeats"], vehicle["Victories"], vehicle["UniqueUsers"], vehicle["Spawns"], vehicle["Deaths"], vehicle["ExperienceEarned"], vehicle["SilverLionsEarned"], vehicle["GroundKills"], vehicle["AirKills"], vehicle["NavalKills"], vehicle["WasInLineup"], vehicle["Defeats"], vehicle["Victories"]]))
        conn.commit()
            


cur.execute(
"SELECT * FROM `WarThunder`.`UpdateQueue` WHERE Status = 1 AND LastRefresh < DATE_SUB(now(), INTERVAL 30 DAY) AND (TimeSinceLastActivity < DATEDIFF(DATE_SUB(now(), INTERVAL 30 DAY), LastRefresh) AND TimeSinceLastActivity < 90);",
())
playersToRefresh = cur.fetchall()
for player in playersToRefresh:

    TimeSinceLastActivity = player['TimeSinceLastActivity'] + 30

    cur.execute(
    "UPDATE `WarThunder`.`UpdateQueue` SET `Status` = 0, `TimeSinceLastActivity` = ? WHERE `userID` = ?;",
    ([TimeSinceLastActivity, player['userID']]))
    conn.commit()

cur.close()