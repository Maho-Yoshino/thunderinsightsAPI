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

def get_menu():
    
    # Get conn
    conn = dbcon()
    
    # Get Cursor
    cur = conn.cursor(dictionary=True)
    
    # set prefix
    prefix = "/code/app/gamefiles/"
    
    # Read JSON file containing translated unit names
    filecontent = open(prefix + "menu.json",'r',encoding='utf-16')
    menuList = json.load(filecontent)
    
    # Create a insert query for unit class
    unitClassQuery = "INSERT INTO `war_thunder_stats_v1`.`unit_class` (`class`) SELECT ? FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`unit_class` WHERE class = ?);"
    
    # Create a insert query for unit class translations
    unitClassTranslationQuery = "INSERT IGNORE INTO `war_thunder_stats_v1`.`unit_class_translation` (`class_id`,`language_id`,translation) SELECT (SELECT id FROM `war_thunder_stats_v1`.`unit_class` WHERE class = ?),(SELECT id FROM `war_thunder_stats_v1`.`language` WHERE language = ?),? FROM DUAL WHERE EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`unit_class` WHERE class = ?) AND EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`language` WHERE language = ?) ON DUPLICATE KEY UPDATE translation = ?;"
    
    # Create regex to match name type
    precompiledUnitClass = re.compile(r'^mainmenu\/type_(?P<unitClass>[a-zA-Z0-9_]*)$')
    
    # Go through every unlock with a translated name
    for menuItem in menuList:
        
        # Run regex on the menuItem id
        matches = precompiledUnitClass.search(menuItem["ID"])
        
        # If we don't find a match then we probably aren't looking at a country
        if matches is not None:
        
            # Save the country name
            unitClass = matches.group('unitClass')
            
            cur.execute(unitClassQuery, [unitClass,unitClass])
            
            # Loop through the translations for the unlock
            for language, translatedText in menuItem.items():
                # Try to remove anything that isn't a language
                if language not in ["ID", "Comments", "max_chars"]:
                    # Run query to insert the new translated name
                    cur.execute(unitClassTranslationQuery, [unitClass,language,translatedText,unitClass,language,translatedText])
                
    # Commit to database
    conn.commit()
    
    # Close the cursor after use
    cur.close()
    
    return "Probably done pulling information into database"