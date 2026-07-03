from logging import getLogger
from typing import Any, Literal
from typing_extensions import Annotated
from fastapi import APIRouter, Path, Query, Form, HTTPException
from fastapi.responses import JSONResponse
from api.shared import get_request, TokenString
from api.users_router import get_terse
from api.models import Clans
from utils.auth import users_cache

_logger = getLogger(__name__)

squadronId = Annotated[int, Path(title="The squadron's ID", gt=0)]
gaijinUserId = Annotated[int, Path(title="The user's ID", gt=0)]

router = APIRouter(
    prefix="/clans",
    tags=["clans"],
    responses={404: {"description": "Not found"}}
)

async def tokenSquadronId(token:str) -> int|None:
    if (_ := await users_cache.get(token)) is not None:
        userdata = (await get_terse(token, *(_.uidHint,))).get(str(_.uidHint))
        if userdata.get("clanName") is not None:
            squadronData = await get_clan_search(token, clanName=userdata["clanName"])
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
async def send_application(
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
async def get_applicants(
    token: TokenString,
    clanId: squadronId
) -> list[Clans.ApplicantModel]:
    clanData = await get_clan(token, clanId)
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
            "description": "Successfully accepted the applicant",
            "content": {}
        },
        403: {
            "description": "You do not have permission to accept applicants",
            "content": {}
        },
        404: {
            "description": "The given user is not an applicant",
            "content": {}
        }
    }
)
async def accept_applicant(
    token: TokenString,
    userId: gaijinUserId
) -> dict[Literal["status"], Literal["success"]]: 
    try:
        response = await (await get_request(
            token, 
            "clan_accept_membership_request",
            userId=userId,
            body={
                "_id": await tokenSquadronId(token)
            }
        )).send()
        return response
    except HTTPException as e:
        if e.detail == "b'!ERROR:CLAN_YOU_HAVE_NO_RIGHT'":
            raise HTTPException(403, "You do not have permission to accept applicants.")
        if e.detail == "b'!ERROR:CLAN_USER_IS_NOT_CANDIDATE'":
            raise HTTPException(404, "The given user is not an applicant.")
        _logger.exception("An exception occurred in accept applicant endpoint")
        raise

@router.post(
    "/reject/{userId}"
)
async def reject_applicant(
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
    description="Getting a member's role can be done by anyone, however setting requires deputy or commander"
)
async def change_role(
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
async def kick_member(
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
async def leave_squadron(
    token: TokenString
):
    response = await (await get_request(
        token, 
        "clan_leave"
    )).send()
    return response.get("clanTag") is None

@router.post(
    "/{clanId}/logs", 
    summary="Gets the squadron logs"
)
async def get_clan_logs(
    clanId: squadronId, 
    token: TokenString,
    limit: Annotated[int, Query(title="The max ammount to get at once", gt=0, le=50)] = 10,
    fromEntry: Annotated[str, Query(title="The last call's 'lastLog' value to begin searching from")] = None
) -> Clans.LogsModel:
    allLogs = (await tokenSquadronId(token)) == clanId
    try:
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
    except HTTPException as e:
        if e.detail == "b'!ERROR:CLAN_YOU_HAVE_NO_RIGHT'":
            raise HTTPException(403, "You do not have permission to view this squadron's logs.")
        _logger.exception("An exception occurred in squadron logs endpoint")
        raise

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
async def get_clan_search(
    token: TokenString,
    clanName: Annotated[str, Query(title="Squadron name to look up")] = None,
    clanTag: Annotated[str, Query(title="Squadron tag to look up")] = None,
    limit: Annotated[int, Query(title="Amount of squadrons to return", gt=0, lt=50)] = 10
) -> list[Clans.ClanModel]:
    if clanName is None and clanTag is None:
        raise HTTPException(400, "You must provide either a clanName or clanTag")
    response = await get_request(
        token, 
        "clan_find_by_prefix",
        count = limit
    )
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

@router.post(
    "/{clanId}/",
    summary="Gets data about the given squadron"
)
async def get_clan(
    token: TokenString,
    clanId: Annotated[int, Path(title="The squadron's ID")]
):
    data = await (
        await get_request(
            token,
            "clan_get",
            clanId=clanId
        )
    ).send()

    candidates = data.get("candidates")
    if isinstance(candidates, dict):
        data["candidates"] = [candidates]

    return data