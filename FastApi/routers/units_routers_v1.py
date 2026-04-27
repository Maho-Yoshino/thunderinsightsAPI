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
    prefix="/units",
    tags=["units"],
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
class units_model(BaseModel):
    unit_name: str
    shop_name: str
    full_name: str
    short_name: str
    compressed_name: str
    country: str
    type: str
    tier: int
    experience: int
    cost: int
    gold_cost: int
    operator_country: str
    premium: int
    gift: int
    event: int
    clan: int
    release_date: int
    battlerating: str
        
# router that provides an endpoint to get a list of units from the game war thunder
@router.get("/", summary="Gets a list of units from the game war thunder.")
async def get_units(
    language: Annotated[str, Query(title="The language to receive translated information in", description="The language to receive translated information in")] = "English",
    gamemode: Annotated[str, Query(title="The gamemode to get battlerating info for", description="The gamemode to get battlerating info for")] = "Realistic",
    premium: Annotated[bool | None, Query(title="Defines if the units returned should be premiums or not", description="Defines if the units returned should be premiums or not")] = None,
    gift: Annotated[bool | None, Query(title="Defines if the units returned should be gifts or not", description="Defines if the units returned should be gifts or not")] = None,
    event: Annotated[bool | None, Query(title="Defines if the units returned should be event units or not", description="Defines if the units returned should be event units or not")] = None,
    clan: Annotated[bool | None, Query(title="Defines if the units returned should be clan units or not", description="Defines if the units returned should be clan units or not")] = None
) -> list[units_model]:
    
    """
    This endpoint Gets a list of units from the game war thunder.
    """
    
    # Get connection
    conn = dbcon()
    
    # Get database cursor
    cur = conn.cursor(dictionary=True)
    
    query = """SELECT 
        unit.name as unit_name, 
        unit_translation.shop_name as shop_name, 
        unit_translation.full_name as full_name, 
        unit_translation.short_name as short_name, 
        unit_translation.compressed_name as compressed_name, 
        country_translation.translation as country, 
        unit_type.type as type, 
        tier_id as tier, 
        experience.value as experience, 
        cost.value as cost, 
        goldcost.value as gold_cost, 
        operator_country_translation.translation as operator_country, 
        premium, 
        gift, 
        event, 
        clan, 
        UNIX_TIMESTAMP(release_date) as release_date, 
        CAST(battlerating.battlerating as CHAR(4)) as battlerating 
        FROM war_thunder_stats_v1.unit
    INNER JOIN unit_type ON unit.type_id = unit_type.id
    INNER JOIN unit_value as experience ON unit.experience_id = experience.id
    INNER JOIN unit_value as cost ON unit.cost_id = cost.id
    INNER JOIN unit_value as goldcost ON unit.gold_cost_id = goldcost.id
    INNER JOIN country as country ON unit.country_id = country.id
    INNER JOIN country_translation as country_translation ON country.id = country_translation.country_id
    INNER JOIN language as country_translation_language ON country_translation.language_id = country_translation_language.id
    INNER JOIN country as operator_country ON unit.operator_country_id = operator_country.id
    INNER JOIN country_translation as operator_country_translation ON operator_country.id = operator_country_translation.country_id
    INNER JOIN language as operator_country_translation_language ON operator_country_translation.language_id = operator_country_translation_language.id
    INNER JOIN unit_translation ON unit.id = unit_translation.unit_id
    INNER JOIN language as unit_translation_language ON unit_translation.language_id = unit_translation_language.id
    INNER JOIN battlerating_correlation as battlerating_correlation ON unit.id = battlerating_correlation.unit_id
    INNER JOIN gamemode as battlerating_gamemode ON battlerating_correlation.gamemode_id = battlerating_gamemode.id
    INNER JOIN battlerating as battlerating ON battlerating_correlation.battlerating_id = battlerating.id
    WHERE 
        operator_country_translation_language.language = ? AND 
        country_translation_language.language = ? AND 
        unit_translation_language.language = ? AND
        battlerating_gamemode.name = ? AND
        unit.include_in_search = 1"""
        
    queryParameters = [language, language, language, gamemode]
        
    if premium is not None:
        query = query + " AND unit.premium = ?"
        queryParameters.append(premium)
        
    if gift is not None:
        query = query + " AND unit.gift = ?"
        queryParameters.append(gift)
        
    if event is not None:
        query = query + " AND unit.event = ?"
        queryParameters.append(event)
        
    if clan is not None:
        query = query + " AND unit.clan = ?"
        queryParameters.append(clan)
    
    query = query + ";"
    
    # Pull list of units
    cur.execute(query,queryParameters)
    
    # Fetch results from select
    results = cur.fetchall()
    
    # Close the cursor after use
    cur.close()

    # return results
    if results:
            
        return JSONResponse(results)
    else:
        raise HTTPException(status_code=500, detail="didn't find any information, either something is wrong with the api or you need to refine your search")
        return