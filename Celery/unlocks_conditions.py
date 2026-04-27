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

def get_unlocks_conditions():
    
    # Get conn
    conn = dbcon()
    
    # Get Cursor
    cur = conn.cursor(dictionary=True)
    
    # set prefix
    prefix = "/code/app/gamefiles/"
    
    # Read JSON file containing translated unit names
    filecontent = open(prefix + "unlocks_conditions.json",'r',encoding='utf-16')
    unlocksConditionsList = json.load(filecontent)
    
    # Create a insert query for tags
    tagQuery = "INSERT INTO `war_thunder_stats_v1`.`unit_tag` (`tag`) SELECT ? FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`unit_tag` WHERE tag = ?);"
    
    # Create a insert query for tag translations
    tagTranslationQuery = "INSERT IGNORE INTO `war_thunder_stats_v1`.`unit_tag_translation` (`tag_id`,`language_id`,translation) SELECT (SELECT id FROM `war_thunder_stats_v1`.`unit_tag` WHERE tag = ?),(SELECT id FROM `war_thunder_stats_v1`.`language` WHERE language = ?),? FROM DUAL WHERE EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`unit_tag` WHERE tag = ?) AND EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`language` WHERE language = ?) ON DUPLICATE KEY UPDATE translation = ?;"
    
    # Create regex to match name type
    precompiledTag = re.compile(r'^unlockTag\/(?P<tag>[a-zA-Z0-9_]*)$')
    
    # Go through every unlock with a translated name
    for unlocksCondition in unlocksConditionsList:
        
        # Run regex on the unlocksCondition id
        matches = precompiledTag.search(unlocksCondition["ID"])
        
        # If we don't find a match then we probably aren't looking at a country
        if matches is not None:
        
            # Save the country name
            tag = matches.group('tag')
            
            cur.execute(tagQuery, [tag,tag])
            
            # Loop through the translations for the unlock
            for language, translatedText in unlocksCondition.items():
                # Try to remove anything that isn't a language
                if language not in ["ID", "Comments", "max_chars"]:
                    # Run query to insert the new translated name
                    cur.execute(tagTranslationQuery, [tag,language,translatedText,tag,language,translatedText])
                
    # Commit to database
    conn.commit()
    
    # Close the cursor after use
    cur.close()
    
    return "Probably done pulling information into database"