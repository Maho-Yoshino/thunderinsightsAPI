from fastapi import HTTPException
from enum import StrEnum, Enum
from datetime import datetime, UTC
from tools import Request
from utils.auth import UserTokenCache

class ReplayType(StrEnum):
    RANDOM_BATTLE = "randomBattle"
    SQUADRON_TOURNAMENT = "squadron_tournament"
    CLAN_BATTLE = "clanBattle"
    TOURNAMENTS = "tournaments"
class ReplayTechType(StrEnum):
    ALL = "all"
    AIRCRAFT = "aircraft"
    HELICOPTER = "helicopter"
    TANK = "tank"
    SHIP = "ship"
    MIXED = "mixed"
class ReplayMode(Enum):
    ARCADE = "arcade"
    REALISTIC = "realistic"
    SIMULATOR = "simulator"

async def search_replay(
    user: UserTokenCache.Entry,
    uid: int | None = None,
    nickname: str | None = None,
    gameType: ReplayType = ReplayType.RANDOM_BATTLE,
    techType: ReplayTechType = ReplayTechType.ALL,
    mode: ReplayMode | None = None,
    limit: int = 25,
    page: int = 0
):
    if user.sid is not None and user.sid.exp < datetime.now(UTC):
        raise HTTPException(401, "Identity SID expired. Please re-login to get a new one.")
    response = await Request.from_template(user, "replays_search")
    response["limit"] = limit
    response["page"] = page
    if uid is not None:
        response["findUserType"] = "ID"
        response["findUserValue"] = str(uid)
    elif nickname is not None:
        response["findUserType"] = "USERNAME"
        response["findUserValue"] = nickname
    else:
        response["findUserType"] = "USERNAME"
        response["findUserValue"] = ""

    response["gameType"] = gameType.value
    response["techType"] = techType.value
    if mode is not None:
        response["gameMode"] = [mode.value,]

    response.headers["cookie"] = f"identity_sid={user.sid.sid}"

    resp = await response.send()

    return resp