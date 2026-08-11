from os import getenv
from typing_extensions import Annotated
from fastapi import APIRouter, Path, Query, Form, HTTPException, Request as faRequest, Depends
from fastapi.responses import JSONResponse
from api.shared import limiter, get_auth
from tools import Request
from api.models import Clans, Base
from api.backends.clans import *

squadronId = Annotated[int, Path(title="The squadron's ID", gt=0)]
gaijinUserId = Annotated[int, Path(title="The user's ID", gt=0)]

router = APIRouter(
    prefix="/clans",
    tags=["clans"],
    responses={404: {"description": "Not found"}}
)

@router.post(
    "/{clanId}/apply", 
    summary="Sends an application to the squadron, if allowed"
)
@limiter.shared_limit("clans", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def send_application(
    request: faRequest,
    clanId: squadronId,
    user: str = Depends(get_auth),
) -> bool:
    response = await Request.send_template(
        user, 
        "clan_membership_request",
        body = {
            "_id": clanId
        }
    )
    return response.get("clanTag") is not None
@router.get(
    "/{clanId}/applicants", 
    summary="Gets the currently applying members"
)
@limiter.shared_limit("clans", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def get_applicants(
    request: faRequest,
    clanId: squadronId,
    user: str = Depends(get_auth)
) -> list[Clans.ApplicantModel]:
    clanData = await getClan(user, clanId)
    data = []
    candidates = clanData.get("candidates")
    if candidates is None:
        return []
    if isinstance(candidates, dict):
        return [
            Clans.ApplicantModel(
                uid=candidates["uid"],
                nickname=candidates["nick"],
                timestamp=candidates["date"],
                comment=candidates["comments"],
                ip=candidates["ip"]
            )
        ]
    for entry in clanData.get("candidates"):
        data.append({
            "uid": entry["uid"],
            "nickname": entry["nick"],
            "timestamp": entry["date"],
            "comment": entry["comments"],
            "ip": entry["ip"]
        })
    return data
@router.post(
    "/accept/{userId}",
    responses={
        200: {
            "model": Base.SuccessEmptyDict,
            "description": "Successfully accepted the applicant",
        },
        403: {
            "description": "You do not have permission to accept applicants"
        },
        404: {
            "description": "The given user is not an applicant"
        }
    }
)
@limiter.shared_limit("clans", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def accept_applicant(
    request: faRequest,
    userId: gaijinUserId,
    user: UserTokenCache.Entry = Depends(get_auth)
):
    return await Request.send_template(
        user, 
        "clan_accept_membership_request",
        userId=userId,
        body={
            "_id": await user.getSquadronId()
        }
    )

@router.post(
    "/reject/{userId}",
    responses={
        200: {"model": Base.SuccessEmptyDict, "description":"Successfully rejected user"},
        404: {"description":"Applicant could not be found"},
        403: {"description":"You do not have permission to reject applicants"}
    }
)
@limiter.shared_limit("clans", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def reject_applicant(
    request: faRequest,
    userId: gaijinUserId,
    message: Annotated[str, Query(title="Message to include alongside rejection")] = "",
    user: UserTokenCache.Entry = Depends(get_auth)
): 
    return await Request.send_template(
        user, 
        "clan_accept_membership_request",
        userId=userId,
        body={
            "_id": await user.getSquadronId(),
            "comments": message
        }
    )

@router.post(
    "/role/{userId}", 
    summary="Set a member's role", 
    description="Requires `Deputy` or `Commander` level in squadron",
    responses={
        200: {"model": Base.SuccessEmptyDict},
        403: {"description": "You do not have the required permissions"}
    }
)
@limiter.shared_limit("clans", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def change_role(
    request: faRequest,
    userId: gaijinUserId,
    role: Annotated[Clans.RolesDisplay, Query(title="The role to assign")],
    user: UserTokenCache.Entry = Depends(get_auth)
): 
    role = Clans.Roles[role.name]
    return await Request.send_template(
        user, 
        "clan_change_member_role",
        userid=userId,
        body={
            "role": role.value
        }
    )

@router.post(
    "/kick/{userId}",
    summary="Kicks the given user",
    description="Requires either `Officer`, `Deputy` or `Commander` rank to remove someone else"
)
@limiter.shared_limit("clans", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def kick_member(
    request: faRequest,
    userId: gaijinUserId,
    reason: Annotated[str, Form(title="The reason for kicking")] = "",
    user: UserTokenCache.Entry = Depends(get_auth)
):
    return await Request.send_template(
        user, 
        "clan_dismiss_member",
        userId=userId,
        body={
            "comments": reason
        }
    )

@router.post(
    "/leave",
    summary="Leaves the current squadron"
)
@limiter.shared_limit("clans", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def leave_squadron(
    request: faRequest,
    user: UserTokenCache.Entry = Depends(get_auth)
) -> bool:
    response = await Request.send_template(
        user, 
        "clan_leave"
    )
    return response.get("clanTag") is None

@router.get(
    "/{clanId}/logs", 
    summary="Gets the squadron logs"
)
@limiter.shared_limit("clans", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def get_clan_logs(
    request: faRequest,
    clanId: squadronId, 
    limit: Annotated[int, Query(title="The max ammount to get at once", gt=0, le=50)] = 10,
    fromEntry: Annotated[str, Query(title="The last call's 'lastLog' value to begin searching from")] = None,
    user: UserTokenCache.Entry = Depends(get_auth)
) -> Clans.LogsModel:
    allLogs = await user.getSquadronId() == clanId
    response = await Request.from_template(
        user, 
        "clan_get_log",
        body = {
            "_id":clanId,
            "count":limit,
            "events": "create;info"
        }
    )
    if (allLogs):
        response.pop("events")
    if fromEntry:
        response["last"] = fromEntry

    response = await response.send()

    logs:list[dict[str, int|str]] = []
    for item in response["log"]:
        item:dict[str, int|str]
        action = Clans.Actions[item["ev"]]
        logEntry = {
            "timestamp": item["time"],
            "action": {
                "value": action.value[0],
                "detail": action.value[1]
            }
        }
        if item.get("uId") is not None and not (action == Clans.Actions.rem and item.get("uid") is not None and item["uId"] == item["uid"]):
            logEntry["admin"] = {
                "_id": item["uId"],
                "nickname": item["uN"]
            }
        if item.get("uid") is not None:
            logEntry["affected"] = {
                "_id": item["uid"],
                "nickname": item["nick"],
            }
        match action:
            case Clans.Actions.role:
                logEntry.update({
                    "roleChange": {
                        "old": item["old"],
                        "new": item["new"]
                    }
                })
            case Clans.Actions.info:
                for i in ["tag", "desc", "region", "status"]: 
                    if (_ := item.get(i)):
                        logEntry[i] = _
            case Clans.Actions.create:
                logEntry["info"] = {}
                for i in ["type", "name", "tag", "slogan", "desc", "region", "announcement"]:
                    logEntry["info"][i] = item[i]
        logs.append(logEntry)

    return JSONResponse({
        "lastLog": response["lastMark"],
        "logs": logs
    })

@router.get("/search/", summary="Search for squadron")
@limiter.shared_limit("clans", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def get_clan_search(
    request: faRequest,
    clanName: Annotated[str, Query(title="Squadron name to look up")] = None,
    clanTag: Annotated[str, Query(title="Squadron tag to look up")] = None,
    limit: Annotated[int, Query(title="Amount of squadrons to return", gt=0, lt=50)] = 10,
    page: Annotated[int, Query(title="The page to display. Count starts from 0", ge=0)] = 0,
    user: UserTokenCache.Entry = Depends(get_auth)
) -> list[Clans.ClanModel]:
    return await searchClan(user, clanName=clanName, clanTag=clanTag, limit=limit, page=page)

@router.get(
    "/leaderboard",
    summary="Gets the leaderboard of squadrons. Position here is zero indexed, so the first squadron is at position 0",
)
@limiter.shared_limit("clans", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def get_clan_leaderboard(
    request: faRequest,
    limit: Annotated[int, Query(title="The max amount to get at once", gt=0, le=50)] = 20,
    page: Annotated[int, Query(title="The page to look up. Starts from 0.", ge=0)] = 0,
    user: UserTokenCache.Entry = Depends(get_auth)
) -> list[Clans.ClanModel]:
    response = await Request.send_template(
        user, 
        "clan_get_leaderboard",
        count=limit,
        start=limit*page
    )

    if response.get("clan") is None:
        raise HTTPException(500, "Could not obtain leaderboard data from Gaijin")
    return response["clan"]

@router.get(
    "/leaderboard/{clanId}",
    summary="Gets the leaderboard position of a given squadron. Position here is not zero indexed"
)
async def get_clan_leaderboard_position(
    request: faRequest,
    clanId: Annotated[int, Path(title="The squadron's ID")],
    user: UserTokenCache.Entry = Depends(get_auth)
) -> Clans.ClanPositionModel:
    response = await Request.send_template(
        user, 
        "clan_get_leaderboard",
        clanId=clanId
    )

    if response.get("clan") is None:
        raise HTTPException(404, "Could not obtain leaderboard position data from Gaijin")
    return {
        "pos": response["clan"]["pos"],
        "rating": response["clan"]["astat"]["dr_era5_hist"]
    }

@router.get(
    "/{clanId}/",
    summary="Gets data about the given squadron"
)
@limiter.shared_limit("clans", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def get_clan(
    request: faRequest,
    clanId: Annotated[int, Path(title="The squadron's ID")],
    user: UserTokenCache.Entry = Depends(get_auth)
) -> Clans.ClanModel:
    return await getClan(user, clanId)