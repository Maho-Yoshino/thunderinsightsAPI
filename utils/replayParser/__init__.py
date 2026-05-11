from utils.replayParser.parser import ReplayParser
from requests import get
from fastapi import HTTPException
from time import sleep
from re import search

difficultyDict = {
    0: "Arcade",
    5: "Realistic",
    10: "Simulator"
}
sessionTypeDict = {
    0: "SQB"
}

class Replay(dict):
    def __init__(self, replay_id:int|str):
        super().__init__({})
        if isinstance(replay_id, str): replay_id = int(replay_id, 16)
        replay_id = f"{replay_id:016x}"
        #region wrpl download (first and last)
        wrpl_num = 0
        r = get(f"https://wt-replays-cdnnow.cdn.gaijin.net/{replay_id}/0000.wrpl")
        if not r.ok:
            raise HTTPException(404, detail="Replay could not be found")
        wrpl_num += 1
        matchMetadata = r.content
        prev_resp = r.content
        while True:
            while True:
                r = get(f"https://wt-replays-cdnnow.cdn.gaijin.net/{replay_id}/{wrpl_num:04d}.wrpl")
                if r.status_code == 429:
                    sleep(1)
                else:
                    break
            if r.status_code == 404:
                break
            if not r.ok:
                raise HTTPException(500, detail="Replay server gave an error")
            wrpl_num += 1
            prev_resp = r.content
        resultsMetadata = prev_resp
        #endregion
        #region Parse gaijin JSON to proper JSON
        matchMetadata = ReplayParser(matchMetadata)
        resultsMetadata = ReplayParser(resultsMetadata)
        
        self["matchId"] = matchMetadata.header.sessionIdHex
        self["match"] = {}
        self["match"]["version"] = matchMetadata.header.version
        self["match"]["map"] = matchMetadata.header.level
        self["match"]["mapSettings"] = matchMetadata.header.levelSettings
        self["match"]["type"] = matchMetadata.header.battleType
        self["match"]["difficulty"] = difficultyDict[matchMetadata.header.diff.difficulty]
        self["match"]["sessionType"] = matchMetadata.header.sessionType
        self["match"]["timeLimit"] = matchMetadata.header.timeLimit * 60
        self["match"]["scoreLimit"] = matchMetadata.header.scoreLimit
        self["match"]["battleClass"] = matchMetadata.header.battleClass

        self["results"] = {}
        _ = resultsMetadata.decode_body()
        self["results"]["team1"] = {}
        self["results"]["team2"] = {}
        for user in _["player"]:
            user:dict[str, str|int|bool]
            add_obj = {
                "clanTag": user.get("clanTag", None),
                "userId": int(user["userId"]),
                "autosquad": user.get("autosquad", False),
                "squadId": user.get("squadId", None),
                "stats": {
                    "kills": user.get("kills", 0),
                    "groundKills": user.get("groundKills", 0),
                    "humanKills": user.get("humanKills", 0),
                    "navalKills": user.get("navalKills", 0),
                    "teamKills": user.get("teamKills", 0),
                    "aiKills": user.get("aiKills", 0),
                    "aiGroundKills": user.get("aiGroundKills", 0),
                    "aiNavalKills": user.get("aiNavalKills", 0),
                    "assists": user.get("assists", 0),
                    "deaths": user.get("deaths", 0),
                    "captureZone": user.get("captureZone", 0),
                    "damageZone": user.get("damageZone", 0),
                    "score": user.get("score", 0),
                    "awardDamage": user.get("awardDamage", 0),
                    "missileEvades": user.get("missileEvades", 0),
                    "ammoInterceptions": user.get("shellIntgerceptions", 0)
                },
                "lineup" : {}
            }
            lineupData = _["matchingInfo"].get(f"{add_obj["userId"]}")
            add_obj["lineup"]["vehicles"] = {}
            if lineupData is not None:
                for key, value in lineupData["crafts_info"].items():
                    if key == "__array": continue
                    add_obj["lineup"]["vehicles"][value["name"]] = {
                        "rank": value["rank"],
                        "battlerating": round(value["mrank"] / 3, 1) 
                    }
                try:
                    add_obj["lineup"]["maxBr"] = round(lineupData["mrank"] / 3, 1)
                except KeyError:
                    add_obj["lineup"]["maxBr"] = max(i["battlerating"] for i in add_obj["lineup"]["vehicles"].values())
            self["results"][f"team{user["team"]}"][user["name"]] = add_obj
        # endregion
        pass