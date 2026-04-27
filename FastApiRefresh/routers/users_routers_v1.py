import subprocess
import json
import mariadb
import time
import datetime
import socket
import sys
import requests
import os
import glob
import random
from datetime import datetime, timezone
from celery import Celery
from kombu import Exchange, Queue
from urllib3.exceptions import InsecureRequestWarning
from app.wt_bin_parser.wt_bin_parser import parse_file, parse_data
from fastapi import APIRouter, Path, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import Annotated
from pydantic import BaseModel


router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

# Stop Python from warning about the certificate
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Function to get api token from database
def dbcon():
    # Connect to MariaDB  
    try:
        conn = mariadb.connect(
            user="<username>",
            password="<password>",
            host="192.168.3.1",
            port=13306,
            database="war_thunder_stats_v1"

        )
    except mariadb.Error as e:
        #print(f"Error connecting to MariaDB Platform: {e}")
        #sys.exit(1)
        raise HTTPException(status_code=500, detail="Unable to connect to internal database")
        return
    
    return conn
       
# Class used to create the response objects from the search router below
class user_refresh_model(BaseModel):
    message: str
    iso_timestamp: str
    timestamp: int
       
# router that provides an endpoint to get user stats directly from Gaijin
@router.get("/refresh/{userid}", summary="Request to have information about a user saved into the database. (This endpoint should NOT be used for webscraping purposes, please analyze the direct endpoints instead.)")
async def refresh_user(userid: Annotated[int, Path(title="The ID of the user to be refreshed", description="The ID of the user to be refreshed", gt=0)]) -> list[user_refresh_model]:
    
    """
    This endpoint is used to refresh the data used for the main part of the api you see here.
    """
    
    # Get connection
    conn = dbcon()
    
    # Get database cursor
    cur = conn.cursor(dictionary=True)
    
    # Pull token information row if any tokens with more than 5 minutes left exist
    cur.execute("SELECT UNIX_TIMESTAMP(datetime) as timestamp FROM war_thunder_stats_v1.general_stat WHERE war_thunder_stats_v1.general_stat.datetime > TIMESTAMPADD(HOUR, -24, NOW()) AND war_thunder_stats_v1.general_stat.user_id = ? LIMIT 1",[userid])
    
    # Fetch results from select
    results = cur.fetchall()
    
    # Close the cursor after use
    cur.close()

    if not results:
    
        # Create celery application to be used
        # Start application
        application = Celery(
          'ThunderInsightsBackgroundTasksCelery',
          broker='redis://192.168.3.1:16379/0'
        )

        # set timezone
        application.conf.timezone = 'Europe/Copenhagen'

        # Create exchange
        default_exchange = Exchange('default', type='topic')

        # Create task queues
        application.conf.task_queues = (
            Queue('default', default_exchange, routing_key='default.#'),
            Queue('periodic', default_exchange, routing_key='periodic.#'),
        )

        # Configuring default queue, exchange and routing key
        application.conf.task_default_queue = 'default'
        application.conf.task_default_exchange = 'default'
        application.conf.task_default_routing_key = 'default'

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
        @application.task(name="default.user", bind=True)
        def user(self,userid):
            return
            
        user.delay(userid)
        
        
        timestamp = int(time.time())
        now = datetime.now(timezone.utc)
        iso_date = now.isoformat()
        
        response = [{
            "message": "Refresh queued. This response may have been cached, please check the timestamp to verify", 
            "iso_timestamp": str(iso_date), 
            "timestamp": timestamp
        }]
        return response
    
    else:
        nextRefresh = datetime.utcfromtimestamp(results[0]['timestamp'] + 24*60*60).isoformat() + 'Z'
        raise HTTPException(status_code=404, detail="User has already been refreshed within the last 24 hours and will be skipped. Next possible refresh at: " + str(nextRefresh))
        return