from os import getenv
from typing_extensions import Annotated
from fastapi import APIRouter, Path, Query, Request as faRequest, Depends
from fastapi.responses import JSONResponse
from urllib.parse import unquote
from tools import Request
from utils.auth import UserTokenCache
from api.models import Users
from api.shared import limiter, get_auth
from api.backends.users import *

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

@router.get("/terse", summary="Get several users by ID")
@limiter.shared_limit("users", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def get_users_terse_info(
    request: faRequest,
    id: Annotated[list[int], Query(
        title="The ID of the users to get information about", 
        description="Provide multiple IDs to get information about multiple users at once",
        min_length=1, 
        max_length=50)
    ],
    user: UserTokenCache.Entry = Depends(get_auth)
) -> dict[str, Users.TerseReturnModel]:
    """Get terse information about users by their IDs."""
    return JSONResponse(await get_terse(user, *id))

@router.get("/{userid}", summary="Get user by ID")
@limiter.shared_limit("users", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def get_user_direct(
    request: faRequest,
    userid: Annotated[int, Path(title="The ID of the user to get information about", description="The ID of the user to get information about", gt=0)],
    user: UserTokenCache.Entry = Depends(get_auth)
) -> Users.getUserDirectModel:
    return JSONResponse(
        await Request.send_template(
            user, 
            "get_public_userstat",
            userId = userid
        )
    )

@router.get(
    "/search/{nick}", 
    summary="Get users by name",
    responses={}
)
@limiter.shared_limit("users", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def get_users_search(
    request: faRequest,
    nick: Annotated[str, Path(title="The nickname to search for")], 
    limit: Annotated[int, Query(title="How many users to retrieve", ge=2, le=50)] = 10,
    user: UserTokenCache.Entry = Depends(get_auth)
) -> dict[str, Users.TerseReturnModel]:
    response = await Request.send_template(
        user, 
        "find_users_by_nick_prefix",
        nick = unquote(nick),
        maxCount = limit
    )

    terseInfo = await get_terse(user, *list(response.keys()))
    return JSONResponse(terseInfo)
