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

# Function to database connection
def dbcon():
    # Connect to MariaDB  
    try:
        conn = mariadb.connect(
            user="<username>",
            password="<password>",
            host="<ip address>",
            port=13306,
            database="WarThunder"

        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        #sys.exit(1)
        return
    
    return conn