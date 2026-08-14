from os import getenv
from typing_extensions import Annotated
from typing import Literal
from fastapi import APIRouter, Query, Request, Depends, WebSocket
from utils import newsManager
from utils.auth import UserTokenCache
from utils.news import NewsEntry
from api.backends.general import *
from api.models import General
from api.shared import IpString, limiter, get_auth

router = APIRouter(
	tags=["general"],
	responses={404: {"description": "Not found"}}
)

@router.get("/latestGameVersion", summary="Get latest game version")
@limiter.shared_limit("general", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def get_latest_game_ver(
	request: Request,
	branch: Annotated[Literal["dev", "dev-stable"], Query(title="The game version to get")] = None,
	user: UserTokenCache.Entry = Depends(get_auth)
) -> IpString:
	return await getLatestGameVer(branch)

@router.get(
	"/news", 
	summary="Gets the latest news from gaijin", 
	description="Puts the pinned news first (Current update changelog + latest big news). There is additionally a `/v1/news_ws` websocket, that doesn't require any authentication, and provides the news through there. This websocket is the single exception to the 'token auth everywhere' rule. Websocket returns the same format for an entry like this endpoint"
)
@limiter.shared_limit("general", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def get_news(request: Request, user: UserTokenCache.Entry = Depends(get_auth)) -> list[NewsEntry]:
	return await newsManager.fetch()

@router.websocket(
	"/news_ws",
	name="News stream"
)
async def news_ws(websocket: WebSocket):
	await newsManager.websocket_mgr.connect(websocket)