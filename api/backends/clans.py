from api.models import Clans
from fastapi import HTTPException
from api.shared import get_request
from typing import Any
from api.users_router import get_terse
from utils import users_cache

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
        if userdata and userdata.get("clanName") is not None:
            squadronData = await searchClan(token, clanName=userdata["clanName"])
            for squadron in squadronData:
                for member in squadron["members"]:
                    if int(member["uid"]) == _.uidHint:
                        return int(squadron["_id"])
        return None
    else:
        raise HTTPException(401, "Invalid token provided")
