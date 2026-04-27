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

def get_rank():
    
    # Get conn
    conn = dbcon()
    
    # Get Cursor
    cur = conn.cursor(dictionary=True)
    
    # set prefix
    prefix = "/code/app/gamefiles/"
    
    # Read JSON file containing ranks
    filecontent = open(prefix + "rank.json",'r',encoding='utf-8')
    rankdict = json.load(filecontent)
    
    # move ranks into array for sql query
    ranks = []
    for key, value in rankdict["exp_for_playerRank"].items():
        rank = key.replace("rank","")
        ranks.append([int(rank),value,value])
    
    # create insert query
    query = "INSERT INTO `war_thunder_stats_v1`.`rank` (`rank`,`experience`) VALUES (?,?) ON DUPLICATE KEY UPDATE experience=?;"
    
    # execute many (might be faster for inserts)
    cur.executemany(query, ranks)
    
    conn.commit()
    
    # Close the cursor after use
    cur.close()
    
    return "Probably done pulling information into database"