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
    prefix="/general",
    tags=["general"],
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
        
    # Get Cursor
    cur = conn.cursor(dictionary=True)
    
    return cur

# Class used to create the rank response model
class rank_model(BaseModel):
    rank: int
    experience: int 

# router that provides an endpoint to get information about experience required to reach a ingame rank
@router.get("/rank/{rank}", summary="Gets the experience (research points) required to reach the defined rank.")
async def get_specific_rank(
        rank: Annotated[int, Path(title="The rank to get the experience (research points) required to reach", description="The rank to get the experience (research points) required to reach", ge=1, le=100)]
    ) -> rank_model:
    
    """
    This endpoint tells you how much experience (research points) is required to reach the rank mentioned.
    """
    
    # Get database cursor
    cur = dbcon()
    
    # Pull a rank and the experience required to reach it
    cur.execute("SELECT * FROM war_thunder_stats_v1.rank WHERE war_thunder_stats_v1.rank.rank = ? LIMIT 1",[rank])
    
    # Fetch results from select
    results = cur.fetchall()
    
    # Close the cursor after use
    cur.close()

    # Download BLK file
    if results:    
        return JSONResponse(results[0])
    else:
        raise HTTPException(status_code=500, detail="We didn't find anything, something is probably messed up in the api.")
        return

# Class used to create the rank response model
class rank_model(BaseModel):
    rank: int
    experience: int 

# router that provides an endpoint to get information about experience required to reach every rank ingame
@router.get("/rank/", summary="Gets the experience (research points) required to reach every rank.")
async def get_specific_rank() -> list[rank_model]:
    
    """
    This endpoint tells you how much experience (research points) is required to reach every rank in game.
    """
    
    # Get database cursor
    cur = dbcon()
    
    # Pull list of ranks and experience required to reach them
    cur.execute("SELECT * FROM war_thunder_stats_v1.rank")
    
    # Fetch results from select
    results = cur.fetchall()
    
    # Close the cursor after use
    cur.close()

    # Download BLK file
    if results:    
        return JSONResponse(results)
    else:
        raise HTTPException(status_code=500, detail="We didn't find anything, something is probably messed up in the api.")
        return
   
# Class used to create the rank response model
class language_model(BaseModel):
    language: str

# router that provides an endpoint to get a list of languages for translations
@router.get("/language/", summary="Gets list of available languages for translations.")
async def get_languages() -> list[language_model]:
    
    """
    This endpoint gets a list of the languages available for the endpoints offering translated information.
    """
    
    # Get database cursor
    cur = dbcon()
    
    # Pull list of languages
    cur.execute("SELECT language FROM war_thunder_stats_v1.language;")
    
    # Fetch results from select
    results = cur.fetchall()
    
    # Close the cursor after use
    cur.close()

    # Download BLK file
    if results:    
        return JSONResponse(results)
    else:
        raise HTTPException(status_code=500, detail="We didn't find anything, something is probably messed up in the api.")
        return
        
# Class used to create the rank response model
class gamemode_model(BaseModel):
    gamemode: str

# router that provides an endpoint to get a list of gamemodes
@router.get("/gamemode/", summary="Gets list of available gamemodes.")
async def get_gamemodes() -> list[gamemode_model]:
    
    """
    This endpoint gets a list of the gamemodes available for the endpoints offering filtering on these.
    """
    
    # Get database cursor
    cur = dbcon()
    
    # Pull list of gamemodes
    cur.execute("SELECT name as gamemode FROM war_thunder_stats_v1.gamemode;")
    
    # Fetch results from select
    results = cur.fetchall()
    
    # Close the cursor after use
    cur.close()

    # Download BLK file
    if results:    
        return JSONResponse(results)
    else:
        raise HTTPException(status_code=500, detail="We didn't find anything, something is probably messed up in the api.")
        return
        
# Class used to create the rank response model
class unit_type_model(BaseModel):
    unit_type: str

# router that provides an endpoint to get a list of unit types
@router.get("/unit/type/", summary="Gets list of unit types.")
async def get_unit_types() -> list[unit_type_model]:
    
    """
    This endpoint gets a list of the unit types in the database.
    """
    
    # Get database cursor
    cur = dbcon()
    
    # Pull list of unit types
    cur.execute("SELECT type FROM war_thunder_stats_v1.unit_type;")
    
    # Fetch results from select
    results = cur.fetchall()
    
    # Close the cursor after use
    cur.close()

    # Download BLK file
    if results:    
        return JSONResponse(results)
    else:
        raise HTTPException(status_code=500, detail="We didn't find anything, something is probably messed up in the api.")
        return