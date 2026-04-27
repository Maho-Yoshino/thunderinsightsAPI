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
from rank import get_rank
from units import get_units
from wpcost import get_wpcost
from unittags import get_unittags
from common_languages import get_common_languages
from menu_options import get_menu_options
from unlocks_achievements import get_unlocks_achievements
from unlocks_conditions import get_unlocks_conditions
from menu import get_menu
from unlocks_medals import get_unlocks_medals
from useringest import add_user

# Stop Python from warning about the certificates when using requests
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Start application
app = Celery(
  'ThunderInsightsBackgroundTasksCelery',
  broker='redis://192.168.3.1:16379/0'
)

# set timezone
app.conf.timezone = 'Europe/Copenhagen'

# Create exchange
default_exchange = Exchange('default', type='topic')

# Create task queues
app.conf.task_queues = (
    Queue('default', default_exchange, routing_key='default.#'),
    Queue('periodic', default_exchange, routing_key='periodic.#'),
)

# Configuring default queue, exchange and routing key
app.conf.task_default_queue = 'default'
app.conf.task_default_exchange = 'default'
app.conf.task_default_routing_key = 'default'

# Configuring tasks routes
CELERY_TASK_ROUTES = {
    'default.*': {
        'queue': 'default',
        'routing_key': 'default.#',
    },
    'periodic.*': {
        'queue': 'periodic',
        'routing_key': 'periodic.#',
    }
}

# Tasks
@app.task(name="default.user", bind=True)
def user(self,userid):
    
    # Pull and ingest user information into the database
    return add_user(userid)

@app.task(name="periodic.gamefiles", bind=True)
def gamefiles(self):
    
    # Pull rank information from the rank.json file
    response = get_rank()
    
    # Pull unit information from the wpcost.json file
    response = get_wpcost()
    
    # Pull additional unit information from the unittags.json file
    response = get_unittags()
    
    # Pull translated unit names from the units.json file
    response = get_units()
    
    # Pull translated country names from the _common_languages.json file
    response = get_common_languages()
    
    # Pull translated country names from the menu_options.json file
    response = get_menu_options()
    
    # Pull translated titles from the unlocks_achievements.json file
    response = get_unlocks_achievements()
    
    # Pull translated unlocks from the unlocks_achievements.json file
    response = get_unlocks_conditions()
    
    # Pull translated unit classes from the menu.json file
    response = get_menu()
    
    # Pull translated medal information from the unlocks_medals.json file
    response = get_unlocks_medals()
    
    return response
    
@app.task(name="periodic.token_pull", bind=True)
def token_pull(self):
    
    # Get conn
    conn = dbcon()
    
    # Get Cursor
    cur = conn.cursor(dictionary=True)
    
    # Pull token information row to check if any tokens with more than 5 minutes left exist
    cur.execute("SELECT * FROM WarThunder.AccessToken WHERE WarThunder.AccessToken.LastRefresh > TIMESTAMPADD(MINUTE, 5, NOW()) LIMIT 1")
    
    # Fetch results from select
    results = cur.fetchall()
    
    if not results:
        # Set credentials of a war thunder account without 2fa
        email = '<war thunder email>'
        password = '<war thunder password>'

        # Call suspicious endpoint to get a login token
        url = 'https://185.253.20.200/login.php'
        data = {'client': 'win_72ba0e93-a10f-421b-8a6b-16dc182652d5','game': 'wt','gapp_id': '79','login': email,'meta': '1','password': password,'v': '2'}
        loginInformationResponse = requests.post(url, data=data, verify=False)

        # Pull the login token and user id into seperate variables
        loginInformation = json.loads(loginInformationResponse.content)
        token = loginInformation['jwt']
        uidHint = loginInformation['user_id']
        
        # Insert the new token into the database
        cur.execute("INSERT INTO WarThunder.AccessToken (Token, UidHint) VALUES (?, ?)",(token, uidHint))
        
        # Remove any expired or soon to expire tokens
        cur.execute("DELETE FROM WarThunder.AccessToken WHERE WarThunder.AccessToken.LastRefresh < TIMESTAMPADD(MINUTE, 5, NOW())")
        
        # commit changes
        conn.commit()
        
        # Close the cursor after use
        cur.close()
        
        return "Pulled new api token"
    else:
        return "Api token is still valid for 5+ minutes"
        
@app.task(name="periodic.auto_user_refresh", bind=True)
def auto_user_refresh(self):
    
    # Get conn
    conn = dbcon()
    
    # Get Cursor
    cur = conn.cursor(dictionary=True)
    
    # Pull list of users we haven't tried to refresh in 7 days and whose information is atleast 14 days old, but also no older than 56 days
    cur.execute("""SELECT 
            user_id 
        FROM (
            SELECT 
                min(general_stat.datetime) as min_datetime, 
                max(general_stat.datetime) as max_datetime, 
                user_id 
            FROM war_thunder_stats_v1.general_stat 
            INNER JOIN war_thunder_stats_v1.user ON general_stat.user_id = user.id 
            WHERE 
                general_stat.datetime > DATE_SUB(NOW(), INTERVAL 56 DAY) AND (user.datetime < DATE_SUB(NOW(), INTERVAL 7 DAY) OR user.datetime IS NULL)
            GROUP BY 
                user_id
            ) as potential_users 
        WHERE 
            max_datetime < DATE_SUB(NOW(), INTERVAL 14 DAY);""")
    
    # Fetch results from select
    results = cur.fetchall()
    
    # Close the cursor after use
    cur.close()
    
    if results:
        
        for result in results:
            user.delay(result['user_id'])
        
        return "Queued " + str(len(results)) + " users for stats refresh"
    else:
        return "no users to refresh for now"

# Schedules 
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Executes every day at 00:00.
    sender.add_periodic_task(
        crontab(hour=00, minute=00),
        gamefiles.s(),
        name='Pull info from game files at midnight every day'
    )
    sender.add_periodic_task(
        120.0, 
        token_pull.s(), 
        name='Pull new api token if necessary'
    )
    sender.add_periodic_task(
        3600.0, 
        auto_user_refresh.s(), 
        name='Refresh profiles automatically'
    )