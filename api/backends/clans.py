from api.models import Clans
from fastapi import HTTPException
from typing import Any
from utils.auth import UserTokenCache
from tools import Request

async def searchClan(user: UserTokenCache.Entry, clanName: str | None = None, clanTag: str | None = None, limit: int = 10, page:int = 0) -> list[Clans.ClanModel]:
    response = await Request.from_template(
        user, 
        "clan_find_by_prefix",
        count=limit,
        start=limit*page
    )
    if clanName is None and clanTag is None: 
        raise HTTPException(400, "You must provide either a clanName or clanTag")
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

async def getClan(user: UserTokenCache.Entry, clanId: int) -> dict[str, Any]:
    data = await Request.send_template(
        user,
        "clan_get",
        clanId=clanId
    )

    candidates = data.get("candidates")
    if isinstance(candidates, dict):
        data["candidates"] = [candidates,]

    return data
