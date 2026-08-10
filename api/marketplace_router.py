from os import getenv
from typing_extensions import Annotated
from typing import Literal, Any
from fastapi import APIRouter, Query, Path, Request, Depends
from fastapi.responses import JSONResponse
from utils import networkManager, users_cache
from api.backends.general import *
from api.models import Marketplace
from api.shared import limiter

router = APIRouter(
    prefix="/marketplace",
    tags=["marketplace"],
    responses={404: {"description": "Not found"}}
)

