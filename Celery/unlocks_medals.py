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

def get_unlocks_medals():
    
    # Get conn
    conn = dbcon()
    
    # Get Cursor
    cur = conn.cursor(dictionary=True)
    
    # set prefix
    prefix = "/code/app/gamefiles/"
    
    # Read JSON file containing translated unit names
    filecontent = open(prefix + "unlocks_medals.json",'r',encoding='utf-16')
    unlocksMedalsList = json.load(filecontent)
    
    # Create a insert query for medal type
    medalQuery = "INSERT INTO `war_thunder_stats_v1`.`unlock_type` (`type`) SELECT ? FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`unlock_type` WHERE type = ?);"
    
    # Run query to insert the unlock type into the database
    cur.execute(medalQuery, ['medal','medal'])
    
    # Commit to database
    conn.commit()
    
    # Create a insert query for medal unlock
    medalUnlockQuery = "INSERT INTO `war_thunder_stats_v1`.`unlock` (`name`,`type_id`) SELECT ?,(SELECT id FROM `war_thunder_stats_v1`.`unlock_type` WHERE type = ?) FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`unlock` WHERE name = ?);"
    
    # Create a insert query for title translations
    medalUnlockTranslationQuery = "INSERT IGNORE INTO `war_thunder_stats_v1`.`unlock_translation` (`unlock_id`,`language_id`,translation) SELECT (SELECT id FROM `war_thunder_stats_v1`.`unlock` WHERE name = ?),(SELECT id FROM `war_thunder_stats_v1`.`language` WHERE language = ?),? FROM DUAL WHERE EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`unlock` WHERE name = ?) AND EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`language` WHERE language = ?) ON DUPLICATE KEY UPDATE translation = ?;"
    
    # Create a insert query for title descriptions
    medalUnlockDescriptionQuery = "INSERT IGNORE INTO `war_thunder_stats_v1`.`unlock_translation` (`unlock_id`,`language_id`,description) SELECT (SELECT id FROM `war_thunder_stats_v1`.`unlock` WHERE name = ?),(SELECT id FROM `war_thunder_stats_v1`.`language` WHERE language = ?),? FROM DUAL WHERE EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`unlock` WHERE name = ?) AND EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`language` WHERE language = ?) ON DUPLICATE KEY UPDATE description = ?;"
    
    # Create regex to match name type
    precompiledTitle = re.compile(r'^(?P<unlockName>[a-zA-Z0-9_]*_medal)\/name$')
    precompiledDescription = re.compile(r'^(?P<unlockName>[a-zA-Z0-9_]*_medal)\/desc$')
    
    # Go through every unlock with a translated name
    for unlockMedal in unlocksMedalsList:
        
        # Run regex on the unlockMedal id
        matches = precompiledTitle.search(unlockMedal["ID"])
        
        # If we don't find a match then we probably aren't looking at a country
        if matches is not None:
        
            # Save the name of the medal unlock
            unlockName = matches.group('unlockName')
            
            cur.execute(medalUnlockQuery, [unlockName,'medal',unlockName])
            
            # Loop through the translations for the unlock
            for language, translatedText in unlockMedal.items():
                # Try to remove anything that isn't a language
                if language not in ["ID", "Comments", "max_chars"]:
                    # Run query to insert the new translated name
                    cur.execute(medalUnlockTranslationQuery, [unlockName,language,translatedText,unlockName,language,translatedText])
    
    # Go through every unlock with a translated name
    for unlockMedal in unlocksMedalsList:
                    
        # Run regex on the unlockMedal id
        matches = precompiledDescription.search(unlockMedal["ID"])
        
        # If we don't find a match then we probably aren't looking at a country
        if matches is not None:
        
            # Save the country name
            unlockName = matches.group('unlockName')
            
            # Loop through the translations for the unlock
            for language, translatedText in unlockMedal.items():
                # Try to remove anything that isn't a language
                if language not in ["ID", "Comments", "max_chars"]:
                    # Run query to insert the new translated name
                    cur.execute(medalUnlockDescriptionQuery, [unlockName,language,translatedText,unlockName,language,translatedText])
                
    # Commit to database
    conn.commit()
    
    # Close the cursor after use
    cur.close()
    
    return "Probably done pulling information into database"