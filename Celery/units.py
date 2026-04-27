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

def get_units():
    
    # Get conn
    conn = dbcon()
    
    # Get Cursor
    cur = conn.cursor(dictionary=True)
    
    # set prefix
    prefix = "/code/app/gamefiles/"
    
    # Read JSON file containing translated unit names
    filecontent = open(prefix + "units.json",'r',encoding='utf-16')
    unitslist = json.load(filecontent)
                
    # create insert query for languages
    langaugeQuery = "INSERT INTO `war_thunder_stats_v1`.`language` (`language`) SELECT ? FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`language` WHERE language = ?);"
    
    # Extract languages from the first unit
    for language, translatedText in unitslist[0].items():
        # Try to remove anything that isn't a language
        if language not in ["ID", "Comments", "max_chars"]:
            cur.execute(langaugeQuery, [language,language])
    
    # Commit to database
    conn.commit()
    
    # Create a insert query for unit translations
    unitTranslationQuery = "INSERT IGNORE INTO `war_thunder_stats_v1`.`unit_translation` (`unit_id`,`language_id`,<nameType>) SELECT (SELECT id FROM `war_thunder_stats_v1`.`unit` WHERE name = ?),(SELECT id FROM `war_thunder_stats_v1`.`language` WHERE language = ?),? FROM DUAL WHERE EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`unit` WHERE name = ?) AND EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`language` WHERE language = ?) ON DUPLICATE KEY UPDATE <nameType> = ?;"
    
    # Create regex to match name type
    precompiled = re.compile(r'(?P<name>.*)_(?P<nameType>shop|0|1|2)$')
    
    # Go through every unit with a translated name
    for unit in unitslist:
        
        # Run regex on the unit id
        matches = precompiled.search(unit["ID"])
        
        # If we don't find a match then we probably aren't looking at a usable unit
        if matches is not None:
        
            # Get unit name from the regex matches
            unitName = matches.group('name')
            
            # Set the nameType variable in the query based on the return from the regex match
            match matches.group('nameType'):
                case "shop":
                    unitTranslationQueryTypeDependent = unitTranslationQuery.replace("<nameType>","`shop_name`")
                case "0":
                    unitTranslationQueryTypeDependent = unitTranslationQuery.replace("<nameType>","`full_name`")
                case "1":
                    unitTranslationQueryTypeDependent = unitTranslationQuery.replace("<nameType>","`short_name`")
                case "2":
                    unitTranslationQueryTypeDependent = unitTranslationQuery.replace("<nameType>","`compressed_name`")
            
            # Loop through the translations for the unit
            for language, translatedText in unit.items():
                # Try to remove anything that isn't a language
                if language not in ["ID", "Comments", "max_chars"]:
                    # Run query to insert the new translated name
                    cur.execute(unitTranslationQueryTypeDependent, [unitName,language,translatedText,unitName,language,translatedText])
                
    # Commit to database
    conn.commit()
    
    # Close the cursor after use
    cur.close()
    
    return "Probably done pulling information into database"