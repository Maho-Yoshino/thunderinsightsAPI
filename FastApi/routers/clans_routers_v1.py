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
from celery import Celery
from kombu import Exchange, Queue
from urllib3.exceptions import InsecureRequestWarning
from app.wt_bin_parser.wt_bin_parser import parse_file
from fastapi import APIRouter, Path, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import Annotated
from pydantic import BaseModel


router = APIRouter(
    prefix="/clans",
    tags=["clans"],
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

        
# router that provides an endpoint to get terse user information directly from Gaijin
@router.get("/direct/clan/search/", summary="Searches for clan/squadron directly from Gaijin.")
async def get_clan_search(
        clan: Annotated[str, Query(title="The clan/squadron to search for", description="The clan/squadron to search for")],
        limit: Annotated[int, Query(title="How many clans to retrieve", description="How many clans to retrieve", ge=1, le=25)] = 5
    ):
    
    """
    This endpoint pulls information directly from Gaijin and the schema changes as Gaijin deems it necessary, it therefore isn't documented in depth.
    """
    
    # Get connection
    conn = dbcon()
    
    # Get database cursor
    cur = conn.cursor(dictionary=True)
    
    # Pull token information row if any tokens with more than 5 minutes left exist
    cur.execute("SELECT * FROM WarThunder.AccessToken WHERE WarThunder.AccessToken.LastRefresh > NOW() LIMIT 1")
    
    # Fetch results from select
    results = cur.fetchall()
    
    # Close the cursor after use
    cur.close()

    # Download BLK file
    if results:
        token = results[0]['Token']
        uidHint = results[0]['UidHint']

        # Calls the char server (Probably character server), to get public stats
        url = ['https://char-lw-nl-005-2.warthunder.com/char','https://char-lw-nl-005-3.warthunder.com/char','https://char-lw-nl-005-4.warthunder.com/char','https://char-lw-nl-005-5.warthunder.com/char']
        headers = {'token': token,'action': 'cln_clan_find_by_prefix','User-Agent': 'wt','namePrefix': str(clan),'tagPrefix': str(clan),'uidHint': str(uidHint),'count': str(25)}
        clanSearchResponse = requests.post(random.choice(url), headers=headers, stream=True)

        # Write returned response to a file
        filename = '/code/app/wt_bin_parser/blk-files/' + str(clan) + '-search.blk'
        with open(filename, 'wb') as fd:
            for chunk in clanSearchResponse.iter_content(chunk_size=128):
                fd.write(chunk)

        with open(filename, 'rb') as fp:
            length = sum(1 for _ in fp)
        
        if length < 2:
            # Nuke file as we failed to grab items
            os.remove(filename)
            raise HTTPException(status_code=500, detail="No clan data returned, feel free to try again later.")
            return
            
        decodedClanSearch = parse_file(filename)
            
        os.remove(filename)
        
        response = {"timestamp": int(time.time())}
        response.update(decodedClanSearch)
            
        return JSONResponse(response)
    else:
        raise HTTPException(status_code=500, detail="Unable to get a token we needed to connect to Gaijins servers")
        return