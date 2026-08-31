from fastapi import HTTPException, status
from typing import Any

from tools import Request
from utils.auth import UserTokenCache
from utils.geo import lookup_city
from api.models.clans import ClanModel, ApplicantModel

async def searchClan(user: UserTokenCache.Entry, clanName: str | None = None, clanTag: str | None = None, limit: int = 10, page:int = 0) -> list[ClanModel]:
	response = await Request.from_template(
		user, 
		"clan_find_by_prefix",
		count=limit,
		start=limit*page
	)
	if clanName is None and clanTag is None: 
		raise HTTPException(status.HTTP_400_BAD_REQUEST, "You must provide either a clanName or clanTag")
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
