from os import getenv
from typing_extensions import Annotated
from typing import Literal, Any
from fastapi import APIRouter, Query, Path, Request, Depends
from fastapi.responses import JSONResponse
from utils import users_cache, vehicle_cache
from utils.auth import UserTokenCache
from api.models import Units
from api.shared import IpString, limiter, get_auth

router = APIRouter(
	tags=["units"],
	responses={404: {"description": "Not found"}},
    prefix="/units"
)

@router.get(
    "/{vehicleId}",
    summary="Gets a specific vehicle's data",
    responses={
        200: {}
    }
)
@limiter.shared_limit("units", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def getVehicle(
    request: Request, 
    vehicleId: Annotated[str, Path(title="The vehicle's ID", examples=["saab_jas39e", "yak-7k"])],
    user: UserTokenCache.Entry = Depends(get_auth)
):
    await vehicle_cache.getVehicle(vehicleId)
    pass

