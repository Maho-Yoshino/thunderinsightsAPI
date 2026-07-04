from os import getenv
from logging import getLogger
from typing import Literal, Any
from typing_extensions import Annotated
from fastapi import APIRouter, Path, Query, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from api.shared import get_request, TokenString, limiter
from api.users_router import get_terse
from api.models import Clans, Base
from utils.auth import users_cache

_logger = getLogger(__name__)

squadronId = Annotated[int, Path(title="The squadron's ID", gt=0)]
gaijinUserId = Annotated[int, Path(title="The user's ID", gt=0)]

router = APIRouter(
    prefix="/clans",
    tags=["clans"],
    responses={404: {"description": "Not found"}}
)

async def searchClan(token: str, clanName: str | None = None, clanTag: str | None = None, limit: int = 10) -> list[Clans.ClanModel]:
    response = await get_request(
        token, 
        "clan_find_by_prefix"
    )
    if clanName is None and clanTag is None: 
        raise HTTPException(500, "You must provide either a clanName or clanTag")
    if clanName:
        response.headers["namePrefix"] = clanName
    else:
        del response.headers["namePrefix"]
    if clanTag:
        response.headers["tagPrefix"] = clanTag
    else:
        del response.headers["tagPrefix"]
    response = await response.send()
    if isinstance(response["clan"], dict):
        response["clan"] = [response["clan"],]
    return response["clan"]
async def getClan(token: str, clanId: int) -> dict[str, Any]:
    data = await (
        await get_request(
            token,
            "clan_get",
            clanId=clanId
        )
    ).send()

    candidates = data.get("candidates")
    if isinstance(candidates, dict):
        data["candidates"] = [candidates,]

    return data
async def tokenSquadronId(token:str) -> int|None:
    if (_ := await users_cache.get(token)) is not None:
        userdata = (await get_terse(token, *(_.uidHint,))).get(str(_.uidHint))
        if userdata.get("clanName") is not None:
            squadronData = await searchClan(token, clanName=userdata["clanName"])
            for squadron in squadronData:
                for member in squadron["members"]:
                    if int(member["uid"]) == _.uidHint:
                        return int(squadron["_id"])
        return None
    else:
        raise HTTPException(401, "Invalid token provided")

@router.post(
    "/{clanId}/apply", 
    summary="Sends an application to the squadron, if allowed"
)
@limiter.shared_limit("clans", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def send_application(
    request: Request,
    clanId: squadronId,
    token: TokenString
) -> bool:
    response = await (await get_request(
        token, 
        "clan_membership_request", 
        body = {
            "_id": clanId
        }
    )).send()
    return response.get("clanTag") is not None
@router.post(
    "/{clanId}/applicants", 
    summary="Gets the currently applying members"
)
@limiter.shared_limit("clans", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def get_applicants(
    request: Request,
    token: TokenString,
    clanId: squadronId
) -> list[Clans.ApplicantModel]:
    clanData = await getClan(token, clanId)
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
    request: Request,
    token: TokenString,
    userId: gaijinUserId
): 
    response = await (await get_request(
        token, 
        "clan_accept_membership_request",
        userId=userId,
        body={
            "_id": await tokenSquadronId(token)
        }
    )).send()
    return response

@router.post(
    "/reject/{userId}",
    responses={
        200: {"model": Base.SuccessEmptyDict, "description":"Successfully rejected user"},
        404: {"model": Base.GaijinResponse, "description":"Applicant could not be found"},
        403: {"model": Base.GaijinResponse, "description":"You do not have permission to reject applicants"}
    }
)
@limiter.shared_limit("clans", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def reject_applicant(
    request: Request,
    token: TokenString,
    userId: gaijinUserId,
    message: Annotated[str, Query(title="Message to include alongside rejection")] = ""
): 
    response = await (await get_request(
        token, 
        "clan_accept_membership_request",
        userId=userId,
        body={
            "_id": await tokenSquadronId(token),
            "comments": message
        }
    )).send()

    return response

@router.post(
    "/role/{userId}", 
    summary="Get or set a member's role", 
    description="Setting an user's role requires `Deputy` or `Commander`",
    responses={
        200: {"model": Base.SuccessEmptyDict},
        403: {"model": Base.GaijinResponse, "description": "You do not have the required permissions"}
    }
)
@limiter.shared_limit("clans", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def change_role(
    request: Request,
    token: TokenString,
    userId: gaijinUserId,
    role: Annotated[Clans.RolesDisplay, Query(title="The role to assign")]
): 
    role = Clans.Roles[role.name]
    return await (await get_request(
        token, 
        "clan_change_member_role",
        userid=userId,
        body={
            "role": role.value
        }
    )).send()

@router.post(
    "/kick/{userId}",
    summary="Kicks the given user",
    description="Requires either `Officer`, `Deputy` or `Commander` rank to remove someone else"
)
@limiter.shared_limit("clans", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def kick_member(
    request: Request,
    token: TokenString,
    userId: gaijinUserId,
    reason: Annotated[str, Form(title="The reason for kicking")] = ""
):
    return await (await get_request(
        token, 
        "clan_dismiss_member",
        userId=userId,
        body={
            "comments": reason
        }
    )).send()

@router.post(
    "/leave",
    summary="Leaves the current squadron"
)
@limiter.shared_limit("clans", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def leave_squadron(
    request: Request,
    token: TokenString
) -> bool:
    response = await (await get_request(
        token, 
        "clan_leave"
    )).send()
    return response.get("clanTag") is None

@router.post(
    "/{clanId}/logs", 
    summary="Gets the squadron logs"
)
@limiter.shared_limit("clans", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def get_clan_logs(
    request: Request,
    clanId: squadronId, 
    token: TokenString,
    limit: Annotated[int, Query(title="The max ammount to get at once", gt=0, le=50)] = 10,
    fromEntry: Annotated[str, Query(title="The last call's 'lastLog' value to begin searching from")] = None
) -> Clans.LogsModel:
    allLogs = (await tokenSquadronId(token)) == clanId
    response = await get_request(
        token, 
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
        if item.get("uId") is not None:
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

@router.post("/search/", summary="Search for squadron")
@limiter.shared_limit("clans", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def get_clan_search(
    request: Request,
    token: TokenString,
    clanName: Annotated[str, Query(title="Squadron name to look up")] = None,
    clanTag: Annotated[str, Query(title="Squadron tag to look up")] = None,
    limit: Annotated[int, Query(title="Amount of squadrons to return", gt=0, lt=50)] = 10
) -> list[Clans.ClanModel]:
    return await searchClan(token, clanName=clanName, clanTag=clanTag, limit=limit)

@router.post(
    "/leaderboard",
    summary="Gets the leaderboard of squadrons. Position here is zero indexed, so the first squadron is at position 0",
)
@limiter.shared_limit("clans", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def get_clan_leaderboard(
    request: Request,
    token: TokenString,
    limit: Annotated[int, Query(title="The max ammount to get at once", gt=0, le=50)] = 20,
    start: Annotated[int, Query(title="The index to start lookup from")] = 0
) -> list[Clans.ClanModel]:
    response = await get_request(
        token, 
        "clan_get_leaderboard",
        count=limit,
        start=start
    )

    response = await response.send()
    if response.get("clan") is None:
        raise HTTPException(500, "Could not obtain leaderboard data from Gaijin")
    return response["clan"]

@router.post(
    "/leaderboard/{clanId}",
    summary="Gets the leaderboard position of a given squadron. Position here is not zero indexed"
)
async def get_clan_leaderboard_position(
    request: Request,
    token: TokenString,
    clanId: Annotated[int, Path(title="The squadron's ID")]
) -> Clans.ClanPositionModel:
    response = await get_request(
        token, 
        "clan_get_leaderboard",
        clanId=clanId
    )
    response = await response.send()
    if response.get("clan") is None:
        raise HTTPException(404, "Could not obtain leaderboard position data from Gaijin")
    return {
        "pos": response["clan"]["pos"],
        "rating": response["clan"]["astat"]["dr_era5_hist"]
    }

@router.post(
    "/{clanId}/",
    summary="Gets data about the given squadron"
)
@limiter.shared_limit("clans", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def get_clan(
    request: Request,
    token: TokenString,
    clanId: Annotated[int, Path(title="The squadron's ID")]
) -> Clans.ClanModel:
    return await getClan(token, clanId)