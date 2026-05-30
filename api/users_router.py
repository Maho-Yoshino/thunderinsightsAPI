from typing_extensions import Annotated
from fastapi import APIRouter, Path, Query
from fastapi.responses import JSONResponse
from urllib.parse import unquote
from .shared import get_request
from .models import TerseReturnModel, getUserDirectModel

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

def get_terse(*userIds:int|str) -> dict[str, TerseReturnModel]:
    request = get_request("get_users_terse_info")
    request.headers["usersList"] = ";".join(str(i) for i in userIds)
    return request.send()

@router.get("/terse", summary="Get several users by ID")
def get_users_terse_info(
    id: Annotated[list[int], Query(
        title="The ID of the users to get information about", 
        description="Provide multiple IDs to get information about multiple users at once",
        min_length=1, 
        max_length=50)
    ]) -> dict[str, TerseReturnModel]:
    """Get terse information about users by their IDs."""
    return JSONResponse(get_terse(*id))

@router.get("/{userid}", summary="Get user by ID")
def get_user_direct(userid: Annotated[int, Path(title="The ID of the user to get information about", description="The ID of the user to get information about", gt=0)]) -> getUserDirectModel:
    request = get_request("get_public_userstat")
    request.headers["userId"] = userid
    result = request.send()
    return JSONResponse(result)

@router.get(
    "/search/{nick}", 
    summary="Get users by name",
    responses={}
)
def get_users_search(nick: Annotated[str, Path(title="The nickname to search for")], limit: Annotated[int, Query(title="How many users to retrieve", ge=2, le=50)] = 10) -> dict[str, TerseReturnModel]:
    request = get_request("find_users_by_nick_prefix")
    request["nick"] = unquote(nick)
    request["maxCount"] = limit
    result = request.send()

    userids:list[str] = []
    for key, value in result.items():
        userids.append(key)

    terseInfo = get_terse(*userids)
    return JSONResponse(terseInfo)
