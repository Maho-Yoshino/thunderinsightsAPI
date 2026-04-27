import requests
import json
import mariadb
import sys
import os
import glob
import re
from datetime import datetime
from celery import Celery
from celery.schedules import crontab
from kombu import Exchange, Queue
from urllib3.exceptions import InsecureRequestWarning
from database_connection import dbcon

def get_wpcost():
    
    # Get conn
    conn = dbcon()
    
    # Get Cursor
    cur = conn.cursor(dictionary=True)
    
    # set prefix
    prefix = "/code/app/gamefiles/"
    
    # Read JSON file containing unit cost, battle rating and rank
    filecontent = open(prefix + "wpcost.json",'r',encoding='utf-8')
    wpcostdict = json.load(filecontent)
    
    # prepare some lists for later sql inserts
    battleratingCorrelations = []
    countries = []
    gamemodeValues = [["Arcade","Arcade"],["Realistic","Realistic"],["Simulator","Simulator"]]
    unitValues = []
    units = []
    
    # create insert query
    gamemodeQuery = "INSERT INTO `war_thunder_stats_v1`.`gamemode` (`name`) SELECT ? FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`gamemode` WHERE name = ?);"
    
    # loop through and execute
    for gamemodeValue in gamemodeValues:
        cur.execute(gamemodeQuery, gamemodeValue)
    
    # Commit to database
    conn.commit()
    
    # Extract some information about units from the wpcost.json file
    for key, value in wpcostdict.items():
        if key not in ["economicRankMax"]:
            
            # Check if unit is premium
            if 'costGold' in value:
                costGold = value['costGold']
                premium = 1
                if 'gift' in value and not 'event' in value:
                    gift = 1
                else:
                    gift = 0
            else:
                costGold = 0
                premium = 0
                gift = 0
            
            # Check if unit is from an event
            if 'event' in value:
                event = 1
            else:
                event = 0
            
            # Check if the unit is a squadron unit
            if 'researchType' in value and value['researchType'] == "clanVehicle":
                clan = 1
                if costGold == 0:
                    costGold = value['openCostGold']
            else:
                clan = 0
            
            # add the gold cost to the unit values list
            unitValues.append([costGold,costGold])
            
            # Get the silver lion cost
            cost = value['value']
            
            # add the silver lion cost to the unit values list
            unitValues.append([cost,cost])
            
            # Get the research points required to unlock
            if 'reqExp' in value:
                experience = value['reqExp']
            else:
                experience = 0
                
            # add the research points required to the unit values list
            unitValues.append([experience,experience])
                
            # Get the battlerating
            battleratingArcade = value['economicRankArcade']
            battleratingRealistic = value['economicRankHistorical']
            battleratingSimulator = value['economicRankSimulation']
            
            # Add the battlerating to the battleratingCorrelations list to later be inserted in the database
            battleratingCorrelations.append([key,"Arcade",battleratingArcade,battleratingArcade])
            battleratingCorrelations.append([key,"Realistic",battleratingRealistic,battleratingRealistic])
            battleratingCorrelations.append([key,"Simulator",battleratingSimulator,battleratingSimulator])
            
            # Get the country
            country = value['country']
            
            # Add the country to the countries list
            countries.append([country,country])
            
            # Get the rank
            rank = value['rank']
            
            units.append([experience, cost, costGold, rank, country, premium, gift, event, clan, key])
            
    # create insert query for unit values
    unitValueQuery = "INSERT INTO `war_thunder_stats_v1`.`unit_value` (`value`) SELECT ? FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`unit_value` WHERE value = ?);"
    
    # loop through and execute
    for unitValue in unitValues:
        cur.execute(unitValueQuery, unitValue)
    
    # create insert query for unit values
    countriesQuery = "INSERT INTO `war_thunder_stats_v1`.`country` (`name`) SELECT ? FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`country` WHERE name = ?);"
    
    # loop through and execute
    for country in countries:
        cur.execute(countriesQuery, country)
    
    # Commit to database
    conn.commit()
    
    # create insert query for unit (mainly to create the unit id)
    unitsInsertQuery = "INSERT INTO `war_thunder_stats_v1`.`unit` (`name`) SELECT ? FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`unit` WHERE name = ?);"
    
    # loop through and execute
    for unit in units:
        cur.execute(unitsInsertQuery, [unit[9],unit[9]])
        
    # Commit to database
    conn.commit()
    
    # create update query for unit (here we insert the actual data)
    unitsUpdateQuery = "UPDATE `war_thunder_stats_v1`.`unit` SET experience_id = (SELECT id FROM `war_thunder_stats_v1`.`unit_value` WHERE value = ?), cost_id = (SELECT id FROM `war_thunder_stats_v1`.`unit_value` WHERE value = ?), gold_cost_id = (SELECT id FROM `war_thunder_stats_v1`.`unit_value` WHERE value = ?), tier_id = ?, country_id = (SELECT id FROM `war_thunder_stats_v1`.`country` WHERE name = ?), premium = ?, gift = ?, event = ?, clan = ? WHERE name = ?;"
    
    # loop through and execute
    for unit in units:
        cur.execute(unitsUpdateQuery, unit)
        
    # Commit to database
    conn.commit()
    
    # create insert query for battlerating correlations
    battleratingCorrelationQuery = "INSERT INTO `war_thunder_stats_v1`.`battlerating_correlation` (`unit_id`,`gamemode_id`,`battlerating_id`) VALUES ((SELECT id FROM `war_thunder_stats_v1`.`unit` WHERE name = ?),(SELECT id FROM `war_thunder_stats_v1`.`gamemode` WHERE name = ?),?) ON DUPLICATE KEY UPDATE battlerating_id = ?;"
    
    # loop through and execute
    for battleratingCorrelation in battleratingCorrelations:
        cur.execute(battleratingCorrelationQuery, battleratingCorrelation)
    
    # Commit to database
    conn.commit()
    
    # Close the cursor after use
    cur.close()
    
    return "Probably done pulling information into database"