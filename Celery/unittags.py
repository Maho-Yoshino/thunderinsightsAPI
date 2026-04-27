import requests
import json
import mariadb
import sys
import os
import glob
import re
import time
import datetime
from celery import Celery
from celery.schedules import crontab
from kombu import Exchange, Queue
from urllib3.exceptions import InsecureRequestWarning
from database_connection import dbcon

def get_unittags():
    
    # Get conn
    conn = dbcon()
    
    # Get Cursor
    cur = conn.cursor(dictionary=True)
    
    # set prefix
    prefix = "/code/app/gamefiles/"
    
    # Read JSON file containing unit cost, battle rating and rank
    filecontent = open(prefix + "unittags.json",'r',encoding='utf-8')
    unittagsdict = json.load(filecontent)
    
    # prepare some lists for later sql inserts
    tags = []
    types = []
    units = []
    countries = []
    
    # Extract some information about units from the wpcost.json file
    for unitName, value in unittagsdict.items():
        
        # get unit type
        unitType = value['type']
        
        # add type to the types list
        types.append([unitType,unitType])
        
        # create list to store unit tags in
        unitTags = []
        
        # Pull the active tags for the unit
        for key, tagValue in value['tags'].items():
            if tagValue == True:
                tags.append([key,key])
                unitTags.append(key)
        
        # Set default
        operatorCountry = None
        
        # Get the operator country either from the tags or from the operator country field
        if 'operatorCountry' in value:
            if isinstance(value['operatorCountry'], list):
                countryInvisibleRemoved = [x for x in value['operatorCountry'] if x != "country_invisible"]
                operatorCountry = countryInvisibleRemoved[0]
            else:
                operatorCountry = value['operatorCountry']
        else:
            for key, tagValue in value['tags'].items():
                if re.match('country_', key): 
                    operatorCountry = key
        
        countries.append([operatorCountry,operatorCountry])
        
        # Get the release date or set it to null
        if 'releaseDate' in value:
            releaseDate = int(time.mktime(datetime.datetime.strptime(value['releaseDate'], "%Y-%m-%d %H:%M:%S").timetuple()))
        else:
            releaseDate = None
        
        units.append([unitType, operatorCountry, releaseDate, unitTags, unitName])
    
    # create insert query for unit values
    countriesQuery = "INSERT INTO `war_thunder_stats_v1`.`country` (`name`) SELECT ? FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`country` WHERE name = ?);"
    
    # loop through and execute
    for country in countries:
        if country[0]:
            cur.execute(countriesQuery, country)
    
    # Commit to database
    conn.commit()
    
    # create insert query for unit values
    typeQuery = "INSERT INTO `war_thunder_stats_v1`.`unit_type` (`type`) SELECT ? FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`unit_type` WHERE type = ?);"
    
    # loop through and execute
    for singleType in types:
        cur.execute(typeQuery, singleType)
    
    # Commit to database
    conn.commit()
    
    # create insert query for unit tags
    tagQuery = "INSERT INTO `war_thunder_stats_v1`.`unit_tag` (`tag`) SELECT ? FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`unit_tag` WHERE tag = ?);"
    
    # loop through and execute
    for tag in tags:
        cur.execute(tagQuery, tag)
    
    # create insert query for unit tag correlations
    unitTagQuery = "INSERT IGNORE INTO `war_thunder_stats_v1`.`unit_tag_correlation` (`unit_id`,`unit_tag_id`) VALUES ((SELECT id FROM `war_thunder_stats_v1`.`unit` WHERE name = ?),(SELECT id FROM `war_thunder_stats_v1`.`unit_tag` WHERE tag = ?));"
    
    # loop through and execute
    for unit in units:
        if unit[3]:
            # we need a dynamic length query to remove the old tag correlations
            removeOldTagsQuery = "DELETE FROM `war_thunder_stats_v1`.`unit_tag_correlation` WHERE unit_id = (SELECT id FROM `war_thunder_stats_v1`.`unit` WHERE name = ?) AND unit_tag_id NOT IN (SELECT id from `war_thunder_stats_v1`.`unit_tag` WHERE tag IN ("
            trackAmountOfQuestionMarksToUse = []
            valuesToKeepInTagCorrelation = [unit[4]]
            
            # Add new tags to tag correlation table
            for tag in unit[3]:
                cur.execute(unitTagQuery, [unit[4],tag])
                valuesToKeepInTagCorrelation.append(tag)
                trackAmountOfQuestionMarksToUse.append("?")
                
            # delete old tag correlations no longer related to unit
            removeOldTagsQuery += ','.join(trackAmountOfQuestionMarksToUse)
            removeOldTagsQuery += "));"
            cur.execute(removeOldTagsQuery, (valuesToKeepInTagCorrelation))
    
    # Commit to database
    conn.commit()
    
    # create update query for unit (here we insert the actual data)
    unitsUpdateQuery = "UPDATE `war_thunder_stats_v1`.`unit` SET type_id = (SELECT id FROM `war_thunder_stats_v1`.`unit_type` WHERE type = ?), operator_country_id = (SELECT id FROM `war_thunder_stats_v1`.`country` WHERE name = ?), release_date = FROM_UNIXTIME(?) WHERE name = ?;"
    
    # loop through and execute
    for unit in units:
        cur.execute(unitsUpdateQuery, [unit[0], unit[1], unit[2], unit[4]])
        
    # Commit to database
    conn.commit()
    
    # Close the cursor after use
    cur.close()
    
    return "Probably done pulling information into database"