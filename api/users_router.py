from typing_extensions import Annotated
from fastapi import APIRouter, Path, Query
from fastapi.responses import JSONResponse
from urllib.parse import unquote
from api.shared import get_request
from api.models import Users
from api.shared import TokenString

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

async def get_terse(token:str, *userIds:int|str) -> dict[str, Users.TerseReturnModel]:
    return await (await get_request(
        token, 
        "get_users_terse_info",
        usersList = ";".join(str(i) for i in userIds)
    )).send()

@router.post("/terse", summary="Get several users by ID")
async def get_users_terse_info(
    token: TokenString,
    id: Annotated[list[int], Query(
        title="The ID of the users to get information about", 
        description="Provide multiple IDs to get information about multiple users at once",
        min_length=1, 
        max_length=50)
    ]
) -> dict[str, Users.TerseReturnModel]:
    """Get terse information about users by their IDs."""
    return JSONResponse(await get_terse(token, *id))

@router.post("/{userid}", summary="Get user by ID")
async def get_user_direct(
    token: TokenString,
    userid: Annotated[int, Path(title="The ID of the user to get information about", description="The ID of the user to get information about", gt=0)]
) -> Users.getUserDirectModel:
    response = await (await get_request(
        token, 
        "get_public_userstat",
        userId = userid
    )).send()
    return JSONResponse(response)

@router.post(
    "/search/{nick}", 
    summary="Get users by name",
    responses={}
)
async def get_users_search(
    token: TokenString,
    nick: Annotated[str, Path(title="The nickname to search for")], 
    limit: Annotated[int, Query(title="How many users to retrieve", ge=2, le=50)] = 10
) -> dict[str, Users.TerseReturnModel]:
    response = await (await get_request(
        token, 
        "find_users_by_nick_prefix",
        body={
            "nick": unquote(nick),
            "maxCount": limit
        }
    )).send()

    terseInfo = await get_terse(token, *list(response.keys()))
    return JSONResponse(terseInfo)
