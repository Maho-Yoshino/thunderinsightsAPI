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
#region /v1/login
class LoginResponse(BaseModel):
	session_token: str = Field(description="Used for accessing many of the `POST` endpoints. Changes with new logins")
	user_token: str = Field(description="Used for refreshing so the token stays alive. It is bound to the user, doesn't change.")
	expires: int
	status: Literal["OK"] = "OK"

class LoginFail2FAResponse(BaseModel):
	types: set[Literal["GaijinPass", "Email", "WTR"]] = Field(description="The types of 2FA that the account has enabled.")
	status: Literal["2STEP"] = "2STEP"
	requestId: str = Field(description="The requestId to be used in the 2FA process")
	userId: int = Field(description="The userId of the account")
#endregion


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
SIMPLE_COUNTRIES = Literal[
	"usa",
	"germany",
	"ussr",
	"britain",
	"japan",
	"china",
	"italy",
	"france",
	"sweden",
]
GAMEMODES = Literal[
	"arcade",
	"realistic",
	"hardcore"
]
SPECIFIC_GAMEMODES = Literal[
	"air_arcade",
	"air_realistic",
	"air_simulation",
	"tank_arcade",
	"tank_realistic",
	"tank_simulation",
	"test_ship_arcade",
	"test_ship_realistic",
	"helicopter_arcade"
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

class TerseReturnModel(BaseModel):
	#region Showcase Models
	class Showcase_FavMode_Model(BaseModel): # Favorite Mode
		class ModeStatsModel(BaseModel): 
			each_player_session: int
			each_player_victories: int
			flyouts: int
			kills_ai: int
			kills_player_or_bot: int
			score: int
		mode: SPECIFIC_GAMEMODES
		modeValue: ModeStatsModel = Field(description="Key value is the value set for `mode`")
	class Showcase_BH_Model(BaseModel): # Battle-Hardened 
		class ModeStatsModel(BaseModel):
			average_score: float
			avg_rel_position: float
			each_player_session: int
			each_player_victories: int
			efficiency_vs_ai: float
			efficiency_vs_players: float
		h_mode: SPECIFIC_GAMEMODES
		h_modeValue: ModeStatsModel = Field(description="Key value is the value set for `h_mode`")
	class Showcase_FavUnit_Model(BaseModel): # Favorite vehicle
		difficulty: GAMEMODES
		vehicle: str = Field(
			description="Internal name of the vehicle", 
			examples=["saab_jas39e", "germ_leopard_2pl", "tiger_had_spain"]
		)
	class Showcase_NukeDrop_Model(BaseModel): # Atomic Ace
		atomic_ace__counter: int = Field(description="Number of times the user has dropped a nuke")
	class Showcase_NukeKill_Model(BaseModel): # Peacemaker
		peacemaker__counter: int = Field(description="Number of nuke carriers killed")
	class Showcase_unitCollector_Model(BaseModel): # Vehicle collector
		units: list[str] = Field(
			description="List of internal names of the vehicles showcased", 
			examples=[
				["ussr_object_279", "ussr_pt_76_57", "douglas_a_1h"], 
				["germ_panther_II","germ_pzkpfw_VI_ausf_b_tiger_IIh_kwk46","germ_flakpanzer_V_Coelian"]
				])
		counts: dict[COUNTRIES, int] = Field(description="Number of vehicles collected per country")
	class Showcase_AceOfSpades_Model(BaseModel): # Ace of spades 
		class AcedUnitsModel(BaseModel):
			filteredTotal: int
			Aircraft: dict[SIMPLE_COUNTRIES, int]
			Boat: dict[SIMPLE_COUNTRIES, int]
			Helicopter: dict[SIMPLE_COUNTRIES, int]
			Ship: dict[SIMPLE_COUNTRIES, int]
			Tank: dict[SIMPLE_COUNTRIES, int]
		aced_units: AcedUnitsModel
	class Showcase_Medalist_Model(BaseModel): # Medalist 
		medals: list[str]
		total_medals: int
	class Showcase_Achievement_Model(BaseModel): # Achievement Hunter 
		achievements: list[str]
		total_steam_achievements: int
	#endregion

	background: str
	clanName: str = Field(description="Name of the clan the user is in, if applicable", examples=["Order Of The Birb", ""])
	clanTag: str = Field(description="Clan tag of the clan the user is in, if applicable. Includes border. Key doesn't exist if user is not in a clan", examples=["┾PECK┿"])
	frame: str
	nick: str
	pilotIcon: str
	pilotId: int
	shcType: str
	title: str
	showcase: Showcase_FavMode_Model | Showcase_BH_Model | Showcase_FavUnit_Model | Showcase_NukeDrop_Model | Showcase_NukeKill_Model | Showcase_unitCollector_Model | Showcase_AceOfSpades_Model | Showcase_Medalist_Model | Showcase_Achievement_Model
#endregion