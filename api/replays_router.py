from os import getenv
from typing_extensions import Annotated
from fastapi import APIRouter, Path, Request as faRequest, Form, Depends
from utils.replayParser import Replay
from utils.auth import UserTokenCache
from api.backends.replay import *
from api.models import Replays
from api.shared import limiter, get_auth

router = APIRouter(
    prefix="/replay",
	tags=["replays"],
	responses={404: {"description": "Not found"}}
)

@router.get(
	"/search",
	summary="Searches for replays based on given parameters",
	responses={
		200: {"model": Replays.SearchModel},
		401: {"description": "The token has no associated `identity_sid` value associated, required for replay lookup. Get one from `/v1/get-sid`"},
	}
)
@limiter.shared_limit("replays", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def search_replays(
	request: faRequest,
	uid: Annotated[
		int, 
		Form(title="The UID of the user to search replays for")
	] = None,
	nickname: Annotated[
		str, 
		Form(title="The nickname of the user to search replays for")
	] = None,
	gameType: Annotated[
		ReplayType,
		Form(
			title="The type of game to search replays for",
			description="If not provided, will search for random battles",
			min_length=1
		)
	] = ReplayType.RANDOM_BATTLE,
	techType: Annotated[
		ReplayTechType,
		Form(
			title="The type of tech to search replays for",
			description="If not provided, will search for all tech types",
			min_length=1
		)
	] = ReplayTechType.ALL,
	mode: Annotated[
		ReplayMode,
		Form(
			title="The game modes to filter by",
			description="If not provided, will search for all game modes",
		)
	] | None = None,
	limit: Annotated[
		int, 
		Form(
			title="The maximum number of replays to return",
			description="Must be between 1 and 100",
			ge=1,
			le=100
		)
	] = 25,
	page: Annotated[
		int, 
		Form(
			title="The page of results to return",
			description="Must be 0 or greater",
			ge=0
		)
	] = 0,
    user: UserTokenCache.Entry = Depends(get_auth)
):
	return await search_replay(user, uid, nickname, gameType, techType, mode, limit, page)

@router.get(
	"/{replayId}", 
	summary="Gets data from a specified replay",
	responses={
		200: {"model": Replays.DataModel},
		404: {"model": Replays.ReplayNotFoundModel, "description": "Replay not found"}
	})
@limiter.shared_limit("replays", getenv("REGULAR_RATE_LIMIT", "30/minute"))
async def get_replay(
	request: faRequest,
	replayId: Annotated[
		str, 
		Path(
			title="The replay's ID to get",
			pattern=r"^#?[0-9a-fA-F]{1,16}$",
			description="Must be given in HEX format"
		),
	],
    user: UserTokenCache.Entry = Depends(get_auth)
):
	return await Replay.get(replayId)
