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

def get_common_languages():
    
    # Get conn
    conn = dbcon()
    
    # Get Cursor
    cur = conn.cursor(dictionary=True)
    
    # set prefix
    prefix = "/code/app/gamefiles/"
    
    # Read JSON file containing translated unit names
    filecontent = open(prefix + "_common_languages.json",'r',encoding='utf-16')
    commonLanguagesList = json.load(filecontent)
    
    # Create a insert query for unit translations
    countryTranslationQuery = "INSERT IGNORE INTO `war_thunder_stats_v1`.`country_translation` (`country_id`,`language_id`,translation) SELECT (SELECT id FROM `war_thunder_stats_v1`.`country` WHERE name = ?),(SELECT id FROM `war_thunder_stats_v1`.`language` WHERE language = ?),? FROM DUAL WHERE EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`country` WHERE name = ?) AND EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`language` WHERE language = ?) ON DUPLICATE KEY UPDATE translation = ?;"
    
    # Create regex to match name type
    precompiled = re.compile(r'^country_(?P<country>[a-zA-Z]*)$')
    
    # Go through every unit with a translated name
    for commonLanguage in commonLanguagesList:
        
        # Run regex on the commonLanguage id
        matches = precompiled.search(commonLanguage["ID"])
        
        # If we don't find a match then we probably aren't looking at a country
        if matches is not None:
        
            # Save the country name
            country = commonLanguage["ID"]
            
            # Loop through the translations for the unit
            for language, translatedText in commonLanguage.items():
                # Try to remove anything that isn't a language
                if language not in ["ID", "Comments", "max_chars"]:
                    # Run query to insert the new translated name
                    cur.execute(countryTranslationQuery, [country,language,translatedText,country,language,translatedText])
                
    # Commit to database
    conn.commit()
    
    # Close the cursor after use
    cur.close()
    
    return "Probably done pulling information into database"