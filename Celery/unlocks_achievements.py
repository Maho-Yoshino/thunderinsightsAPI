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

def get_unlocks_achievements():
    
    # Get conn
    conn = dbcon()
    
    # Get Cursor
    cur = conn.cursor(dictionary=True)
    
    # set prefix
    prefix = "/code/app/gamefiles/"
    
    # Read JSON file containing translated unit names
    filecontent = open(prefix + "unlocks_achievements.json",'r',encoding='utf-16')
    unlocksAchievementsList = json.load(filecontent)
    
    # Create a insert query for titles
    titleQuery = "INSERT INTO `war_thunder_stats_v1`.`title` (`name`) SELECT ? FROM DUAL WHERE NOT EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`title` WHERE name = ?);"
    
    # Create a insert query for title translations
    titleTranslationQuery = "INSERT IGNORE INTO `war_thunder_stats_v1`.`title_translation` (`title_id`,`language_id`,translation) SELECT (SELECT id FROM `war_thunder_stats_v1`.`title` WHERE name = ?),(SELECT id FROM `war_thunder_stats_v1`.`language` WHERE language = ?),? FROM DUAL WHERE EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`title` WHERE name = ?) AND EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`language` WHERE language = ?) ON DUPLICATE KEY UPDATE translation = ?;"
    
    # Create a insert query for title descriptions
    titleDescriptionQuery = "INSERT IGNORE INTO `war_thunder_stats_v1`.`title_translation` (`title_id`,`language_id`,description) SELECT (SELECT id FROM `war_thunder_stats_v1`.`title` WHERE name = ?),(SELECT id FROM `war_thunder_stats_v1`.`language` WHERE language = ?),? FROM DUAL WHERE EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`title` WHERE name = ?) AND EXISTS (SELECT NULL FROM `war_thunder_stats_v1`.`language` WHERE language = ?) ON DUPLICATE KEY UPDATE description = ?;"
    
    # Create regex to match name type
    precompiledTitle = re.compile(r'^title\/(?P<title>title_[a-zA-Z0-9_]*)$')
    precompiledDescription = re.compile(r'^(?P<title>title_[a-zA-Z0-9_]*)\/desc$')
    
    # Go through every unlock with a translated name
    for unlockAchievement in unlocksAchievementsList:
        
        # Run regex on the unlockAchievement id
        matches = precompiledTitle.search(unlockAchievement["ID"])
        
        # If we don't find a match then we probably aren't looking at a country
        if matches is not None:
        
            # Save the country name
            title = matches.group('title')
            
            cur.execute(titleQuery, [title,title])
            
            # Loop through the translations for the unlock
            for language, translatedText in unlockAchievement.items():
                # Try to remove anything that isn't a language
                if language not in ["ID", "Comments", "max_chars"]:
                    # Run query to insert the new translated name
                    cur.execute(titleTranslationQuery, [title,language,translatedText,title,language,translatedText])
    
    # Go through every unlock with a translated name
    for unlockAchievement in unlocksAchievementsList:
                    
        # Run regex on the unlockAchievement id
        matches = precompiledDescription.search(unlockAchievement["ID"])
        
        # If we don't find a match then we probably aren't looking at a country
        if matches is not None:
        
            # Save the country name
            title = matches.group('title')
            
            # Loop through the translations for the unlock
            for language, translatedText in unlockAchievement.items():
                # Try to remove anything that isn't a language
                if language not in ["ID", "Comments", "max_chars"]:
                    # Run query to insert the new translated name
                    cur.execute(titleDescriptionQuery, [title,language,translatedText,title,language,translatedText])
                
    # Commit to database
    conn.commit()
    
    # Close the cursor after use
    cur.close()
    
    return "Probably done pulling information into database"