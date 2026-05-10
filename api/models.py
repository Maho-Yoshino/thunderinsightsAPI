from typing import Literal
from pydantic import BaseModel, Field
from .shared import IntString
from datetime import datetime
from enum import StrEnum

#region Clans router
class ClanActions(StrEnum):
    rem = "Kick user"
    add = "Accept membership request"
    role = "Role change"
    reject_candidate = "Rejected membership request"
    info = "Squadron info changed"

clanRoles = {
    1:"Commander",
    2:"Officer",
    3:"Private",
    5:"Deputy",
    6:"Sergeant"
}

clanPlatforms = {
    2:"pc",
    5:"psn transferred to pc",
    7:"psn",
    9:"xbox transferred to pc",
    12:"xbox"
}

class ClanLogsModel(BaseModel):
    time: int
    affectedId: int
    affectedNick: str
    action: str
    adminId: int
    adminNick: str
    oldRole: str | None = Field(default=None, description="Previous role. Only present for role-change log entries.")
    newRole: str | None = Field(default=None, description="New role. Only present for role-change log entries.")

class ClanEntry(BaseModel):
    class ClanSeasonRatingRewardsModel(BaseModel):
        t:int
        seasonId:int
        seasonStartTimestamp: int
        seasonEndTimestamp: int
        numInYear: int
        regaliaTags: str
    class MemberModel(BaseModel):
        uid: IntString
        nick: str
        role: int
        platform: int
        max_unit_rank: int
        initiator: IntString
        initiator_nick: str
        date: int
    class astatModel(BaseModel):
        deaths_hist: int
        ftime_hist: int
        akills_hist: int
        dr_era5_hist: int
        gkills_hist: int
        battles_hist: int
        wins_hist: int
        dr_era0_arc: int
        dr_era0_hist: int
        dr_era0_sim: int
        dr_era1_arc: int
        dr_era1_hist: int
        dr_era1_sim: int
        dr_era2_arc: int
        dr_era2_hist: int
        dr_era2_sim: int
        dr_era3_arc: int
        dr_era3_hist: int
        dr_era3_sim: int
        dr_era4_arc: int
        dr_era4_hist: int
        dr_era4_sim: int
        dr_era5_arc: int
        dr_era5_sim: int
        dr_era6_arc: int
        dr_era6_hist: int
        dr_era6_sim: int
        dr_era7_arc: int
        dr_era7_hist: int
        dr_era7_sim: int
        dr_era8_arc: int
        dr_era8_hist: int
        dr_era8_sim: int
        dr_era9_arc: int
        dr_era9_hist: int
        dr_era9_sim: int
        activity: int
        clan_activity_by_periods: int    
    pos: int
    _id: IntString
    announcement:str
    autoaccept:bool
    cdate: int
    changed_by_uid: IntString
    changed_time: int
    creator_uid: IntString
    currentTagRegalia: str
    desc: str
    interlockid: int
    lastPaidTag: str
    members_cnt: int
    name: str
    namel: str
    region: str
    region_last_updated: int
    regionl: str
    slogan: str
    status: str
    tag: str
    tagl: str
    transactions: list[str]
    type: str
    clanSeasonRatingRewards: ClanSeasonRatingRewardsModel
    members: list[MemberModel]
    membership_req: dict
    astat: astatModel
    clanRewardRatingPerUser_60: dict
#endregion
#region General router
class LoginResponse(BaseModel):
	session_token: str = "Used for accessing many of the `POST` endpoints. Changes with new logins"
	user_token: str = "Used for refreshing so the token stays alive. It is bound to the user, doesn't change."
	expires: int

class NewsResponse(BaseModel):
	class ImageModel(BaseModel):
		src:str
		width:int
		height:int
	id:int
	anons:str
	title:str
	link:str
	pinned:bool
	images:list[ImageModel]
	tags:list[Literal["Event", "Development", "Video", "Shop", "Fixed", "eSport", "Market", "Special", "Warbonds", "Fair Play", "Update"]]
	platforms:list[Literal["pc", "ps4", "ps5"]]
	type:Literal["News", "Changelog"]
	created:datetime
	importance:int
#endregion
#region Users router
class TerseReturnModel(BaseModel):
    background: str
    clanName: str
    clanTag: str
    frame: str
    nick: str
    pilotIcon: str
    pilotId: int
    shcType: str

COUNTRIES = Literal[
    "country_usa",
    "country_germany",
    "country_ussr",
    "country_britain",
    "country_japan",
    "country_china",
    "country_italy",
    "country_france",
    "country_sweden",
    "country_israel"
]
GAMEMODES = Literal[
    "arcade",
    "realistic",
    "hardcore"
]
VEHICLE_TYPES = Literal[
    "fighter",
    "bomber",
    "assault",
    "tank",
    "heavy_tank",
    "tank_destroyer",
    "SPAA",
    "ship",
    "torpedo_boat",
    "gun_boat",
    "torpedo_gun_boat",
    "submarine_chaser",
    "destroyer",
    "naval_ferry_barge",
    "helicopter",
    "cruiser",
    "human"
]

class getUserDirectModel(BaseModel):
    class summaryModel(BaseModel):
        class summaryGameModeModel(BaseModel):
            class vehicleModel(BaseModel):
                timePlayed: int
                air_kills: int
                ground_kills: int
                naval_kills: int
                respawns: int            
            missionsComplete: int
            victories: int
            fighter:vehicleModel
            bomber: vehicleModel
            assault: vehicleModel
            tank: vehicleModel
            heavy_tank: vehicleModel
            tank_destroyer: vehicleModel
            SPAA: vehicleModel
            ship: vehicleModel
            torpedo_boat: vehicleModel
            gun_boat: vehicleModel
            torpedo_gun_boat: vehicleModel
            submarine_chaser: vehicleModel
            destroyer: vehicleModel
            naval_ferry_barge: vehicleModel
            helicopter: vehicleModel
            cruiser: vehicleModel
            human: vehicleModel   
        single_played: dict[GAMEMODES, summaryGameModeModel]
        pvp_played: dict[GAMEMODES, summaryGameModeModel]
        skirmish_played: dict[GAMEMODES, summaryGameModeModel]
        campaign_played: dict[GAMEMODES, summaryGameModeModel]
        dynamic_played: dict[GAMEMODES, summaryGameModeModel]
        builder_played: dict[GAMEMODES, summaryGameModeModel]
        other_played: dict[GAMEMODES, summaryGameModeModel]

    nick: str
    lastDay: int
    registerDay: int
    userid: IntString
    exp: int
    expConverted: int
    numEliteUnits: int
    title: str
    icon: int
    iconName: str
    frame: str
    background: str
    shcType: str
    penaltyStatus: str
    era: dict[
       COUNTRIES, 
       dict[
            Literal[
                "Aircraft",
                "Tank",
                "Ship",
                "Helicopter",
                "Boat",
                "Human"
            ], int
        ]]
    unitsPerCountry: dict[COUNTRIES, dict[Literal["numUnits", "numEliteUnits"], int]]
    aircrafts: dict[COUNTRIES, dict[str, int]]
    slots: dict[COUNTRIES, dict[str, int]]
    summary: summaryModel
    unlocks: dict[str, dict[Literal["type"], Literal["achievement", "challenge"]]]
    closedUnlocks: dict
    titles: dict
    userstat: dict
    classinessAwards: dict
    leaderboard: dict[str, dict[str, dict]]
#endregion