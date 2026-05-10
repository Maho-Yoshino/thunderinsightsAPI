from typing import Any
from typing_extensions import Annotated
from fastapi import APIRouter, Path, Query, Form, HTTPException
from fastapi.responses import JSONResponse
from enum import StrEnum
from .shared import get_request, IntString, token_cache, get_cached_entry
from api.users_router import get_terse
from .models import ClanActions, clanRoles, clanPlatforms, ClanLogsModel, ClanEntry

router = APIRouter(
    prefix="/clans",
    tags=["clans"],
    responses={404: {"description": "Not found"}}
)

@router.post("/{clanid}/logs", summary="Gets the squadron logs")
def get_clan_logs(
    clanid: Annotated[int, Path(title="The squadron to get the logs of", gt=0)], 
    token: Annotated[str, Form()],
    limit: Annotated[int, Query(title="", gt=0, lt=50)] = 10,
) -> list[ClanLogsModel]:
    request = get_request("clan_get_log")
    request["_id"] = clanid
    request["count"] = limit
    try:
        response = request.send(token)
    except Exception as e:
        pass
    logs:list[dict[str, int|str]] = []
    for item in response["log"]:
        _ = {
            "time": item["time"],
            "affectedId": item["uid"],
            "affectedNick": item["nick"],
            "action": ClanActions[item["ev"]],
            "adminId": item["uId"],
            "adminNick": item["uN"]
        }
        if _["action"] == ClanActions.role:
            _.update({
                "oldRole": item["old"],
                "newRole": item["new"]
            })
        elif _["action"] == ClanActions.info:
            if (_2 := _.get("tag")):
                _["NewTag"] = _2
            if (_2 := _.get("")): ...
        logs.append(_)

    return JSONResponse(logs)



@router.get("/search/{clanName}", summary="Search for squadron")
def get_clan_search(
    clanName: Annotated[str, Path(title="Squadron's name to look for")],
    limit: Annotated[int, Query(title="Amount of squadrons to return", gt=0, lt=50)] = 10
) -> list[ClanEntry]:
    request = get_request("clan_find_by_prefix")
    request.headers["clanPrefix"] = clanName
    request.headers["tagPrefix"] = clanName
    request.headers["count"] = limit

    response = request.send()

    return JSONResponse(response["clan"])

@router.get("/search/leaderboard/{clanId}", summary="")
def get_clan_placement(clanId: Annotated[int, Path(title="Clan's ID to look up")]):
    request = get_request("clan_get_leaderboard")
    request.headers["clanId"] = clanId
    response = request.send()

    return JSONResponse(response)

@router.get("/search/leaderboard/", summary="")
def get_clan_placement(
    start: Annotated[int, Query(title="Start placement", ge=0)] = 0,
    count: Annotated[int, Query(title="How many to get", gt=1)] = 20
):
    request = get_request("clan_get_leaderboard")
    request.headers["start"] = start
    request.headers["count"] = count

    response = request.send()

    return JSONResponse(response)

@router.post("/{clanId}/apply")
def apply_to_clan(
    session_token: Annotated[str, Form(title="The session token to the account")],
    clanId: Annotated[int, Path(title="The clan ID", gt=0)]
) -> bool:
    data = get_cached_entry(session_token)
    request = get_request("clan_membership_request")
    request["_id"] = clanId

    request.send(token_override=session_token, uid=data["uid"])
    return True

@router.post("/{clanId}/dismiss/{userId}", summary="Dismiss member")
def clan_dismiss_member(
    session_token: Annotated[str, Form(title="The session token to the account")],
    clanId: Annotated[int, Path(title="The squadron's ID")],
    userId: Annotated[int, Path(title="The user's ID to be kicked")],
    comment: Annotated[str, Form(title="The message to send alongside the kick")] = ""
):
    data = get_cached_entry(session_token)
    terse = get_terse(data["uid"])
    if terse["clanid"] != clanId:
        raise HTTPException(403, detail="Incorrect guild ID given")
    request = get_request("clan_dismiss_member")
    request.headers["userid"] = userId
    request["comment"] = comment

    request.send(token_override=session_token, uid=data["uid"])
    return