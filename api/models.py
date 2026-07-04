from typing import Literal
from pydantic import BaseModel, Field
from .shared import IntString, IpString
from datetime import datetime
from enum import Enum

class Base:
	class SuccessEmptyDict(BaseModel):
		status:Literal["success"] = "success"
	class GaijinResponse(BaseModel):
		detail:str
class Authentication:
	class Login: # /v1/login endpoint
		class LoginResponse(BaseModel):
			status: Literal["OK"] = "OK"
			token: str
		class Fail2FAResponse(BaseModel):
			types: set[Literal["GaijinPass", "Email", "WTR"]] = Field(description="The types of 2FA that the account has enabled.")
			status: Literal["2STEP"] = "2STEP"
			requestId: str = Field(description="The requestId to be used in the 2FA process")
			userId: int = Field(description="The userId of the account")
	class LoginToken: # /v1/login-token endpoint
		class LoginTokenResponse(BaseModel):
			expires: int = Field(description="UNIX timestamp of the new token expiry")
			status: Literal["OK"] = "OK"
		class LoginFailResponse(BaseModel):
			status: Literal["FAIL"] = "FAIL"
			detail: str

class Clans:
	class Actions(Enum):
		rem = (0, "Kick user")
		add = (1, "Accept membership request")
		role = (2, "Role change")
		reject_candidate = (3, "Rejected membership request")
		info = (4, "Squadron info changed")
		create = (5, "Squadron created")
	class Roles(Enum):
		COMMANDER = 1
		OFFICER = 2
		PRIVATE = 3
		NONE = 4
		DEPUTY = 5
		SERGEANT = 6
	class RolesDisplay(Enum):
		COMMANDER = "Commander"
		OFFICER = "Officer"
		PRIVATE = "Private"
		NONE = "Unknown"
		DEPUTY = "Deputy"
		SERGEANT = "Sergeant"
	class Platforms(Enum):
		PC = 2
		PSN_TRANSFER_PC = 5
		PSN = 7
		XBOX_TRANSFER_PC = 9
		XBOX = 12

	class ApplicantModel(BaseModel):
		uid: IntString
		nickname: str
		timestamp: int
		comment: str
		ip: IpString

	class LogsModel(BaseModel):
		lastLog: str
		logs: list[ClanLogs]
		class ClanLogs(BaseModel):
			class _affected(BaseModel):
				_id: int
				nickname: str
			class _action(BaseModel):
				value: int
				detail: str
			class _admin(BaseModel):
				_id: int
				nickname: str

			class _roleChange(BaseModel):
				old: str | None = Field(default=None, description="Previous role. Only present for role-change log entries.")
				new: str | None = Field(default=None, description="New role. Only present for role-change log entries.")


			timestamp: int
			affected: _affected
			action: _action
			admin: _admin
			roleChange: _roleChange | None = Field(default=None)

	class ClanModel(BaseModel):
		class ClanSeasonRatingRewardsModel(BaseModel):
			t: int | None = None
			seasonId: int | None = None
			seasonStartTimestamp: int | None = None
			seasonEndTimestamp: int | None = None
			numInYear: int | None = None
			regaliaTags: str | None = None
		class MemberModel(BaseModel):
			uid: IntString
			nick: str
			role: int
			platform: int
			max_unit_rank: int
			initiator: IntString | None = None
			initiator_nick: str | None = None
			date: int
		class astatModel(BaseModel):
			deaths_hist: int | None = None
			ftime_hist: int | None = None
			akills_hist: int | None = None
			dr_era5_hist: int | None = None
			gkills_hist: int | None = None
			battles_hist: int | None = None
			wins_hist: int | None = None
			dr_era0_arc: int | None = None
			dr_era0_hist: int | None = None
			dr_era0_sim: int | None = None
			dr_era1_arc: int | None = None
			dr_era1_hist: int | None = None
			dr_era1_sim: int | None = None
			dr_era2_arc: int | None = None
			dr_era2_hist: int | None = None
			dr_era2_sim: int | None = None
			dr_era3_arc: int | None = None
			dr_era3_hist: int | None = None
			dr_era3_sim: int | None = None
			dr_era4_arc: int | None = None
			dr_era4_hist: int | None = None
			dr_era4_sim: int | None = None
			dr_era5_arc: int | None = None
			dr_era5_sim: int | None = None
			dr_era6_arc: int | None = None
			dr_era6_hist: int | None = None
			dr_era6_sim: int | None = None
			dr_era7_arc: int | None = None
			dr_era7_hist: int | None = None
			dr_era7_sim: int | None = None
			dr_era8_arc: int | None = None
			dr_era8_hist: int | None = None
			dr_era8_sim: int | None = None
			dr_era9_arc: int | None = None
			dr_era9_hist: int | None = None
			dr_era9_sim: int | None = None
			activity: int
			clan_activity_by_periods: int    
		pos: int | None = None
		_id: IntString | None = None
		announcement: str | None = None
		autoaccept: bool | None = None
		cdate: int | None = None
		changed_by_uid: IntString | None = None
		changed_time: int | None = None
		creator_uid: IntString | None = None
		currentTagRegalia: str | None = None
		desc: str | None = None
		interlockid: int | None = None
		lastPaidTag: str | None = None
		members_cnt: int | None = None
		name: str | None = None
		namel: str | None = None
		region: str | None = None
		region_last_updated: int | None = None
		regionl: str | None = None
		slogan: str | None = None
		status: str | None = None
		tag: str | None = None
		tagl: str | None = None
		transactions: list[str] | None = None
		type: str | None = None
		clanSeasonRatingRewards: ClanSeasonRatingRewardsModel | dict | None = None
		members: list[MemberModel] | MemberModel | None = None
		membership_req: dict | None = None
		astat: astatModel | None = None
		clanRewardRatingPerUser_60: dict | None = None

		class Config:
			extra = "allow"
	class ClanPositionModel(BaseModel):
		pos: int
		rating: int

class General:
	class Replay: # /v1/replay endpoint
		class DataModel(BaseModel):
			status: Literal["OK"] = "OK"
			class MatchModel(BaseModel):
				version: int = Field(description="Game version of the match, represented as an integer.", examples=[101374])
				map: str = Field(description="Map of the match. Uses internal name", examples=["levels/avg_abandoned_factory.bin", "levels/avg_tunisia_desert.bin"])
				mapSettings: str = Field(description="Map settings of the match.", examples=["gamedata/missions/cta/tanks/abandoned_factory/abandoned_factory_dom.blk", "gamedata/missions/cta/tanks/tunisia/tunisia_02_bttl.blk"])
				type: str = Field(description="Gamemode of the match, seems to be derived from `mapSettings`", examples=["tunisia_02_Bttl", "abandoned_factory_dom"])
				difficulty: str = Field(description="Gamemode of the match, such as `Arcade`, `Realistic`, `Simulator`", examples=["Arcade", "Realistic", "Simulator"])
				sessionType: int = Field(description="Unknown integer", examples=[0])
				timeLimit: int = Field(description="Time limit in seconds", examples=[1500])
				scoreLimit: int
				battleClass: str
			class ResultsModel(BaseModel):
				class UserModel(BaseModel):
					class StatsModel(BaseModel):
						kills: int
						groundKills: int
						humanKills: int
						navalKills: int
						teamKills: int
						aiKills: int
						aiGroundKills: int
						aiNavalKills: int
						assists: int
						deaths: int
						captureZone: int
						damageZone: int
						score: int
						awardDamage: int
						missileEvades: int
						ammoInterceptions: int
					class LineupModel(BaseModel):
						class VehicleModel(BaseModel):
							rank: int
							battlerating: int
						vehicles: dict[str, VehicleModel] = Field(
							description="Vehicles in the lineup of the player. Key is the internal name of the vehicle, such as `germ_leopard_2pl`",
							examples=[
							{
								"ef_2000_block_10": {
								  "rank": 9,
								  "battlerating": 13.3
								},
							}, {
								"germ_leopard_2pl": {
								  "rank": 8,
								  "battlerating": 11.3
								},
							}, {
								"tiger_had_spain": {
								  "rank": 7,
								  "battlerating": 9.7
								}
							}]
						)
						max_br: float = Field(description="Maximum battle rating of the user's lineup", examples=[6.7, 8.0, 9.7])
					clanTag: str | None = Field(default=None, description="Clan tag of the user, if applicable. Includes border", examples=["┾PECK┿", ""])
					userId: int
					autosquad: bool = Field(description="Whether the user was assigned into a squad automatically")
					squadId: int = Field(description="Squad ID of the user. Number is still generated if not in a squad. Looks like 4000+ are players playing alone", examples=[1001, 1002, 1000, 4096, 4097, 4098])
					stats: StatsModel
					lineup: LineupModel

				team1: dict[str, UserModel]
				team2: dict[str, UserModel]

			matchId: int
			match: MatchModel
			results: ResultsModel
		class ReplayNotFoundModel(BaseModel):
			detail: str = "Replay could not be found"
			status: Literal["NOT_FOUND"] = "NOT_FOUND"
	class News: # /v1/news endpoint
		class NewsResponseModel(BaseModel):
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
class Users:
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
			single_played: dict[Users.GAMEMODES, summaryGameModeModel]
			pvp_played: dict[Users.GAMEMODES, summaryGameModeModel]
			skirmish_played: dict[Users.GAMEMODES, summaryGameModeModel]
			campaign_played: dict[Users.GAMEMODES, summaryGameModeModel]
			dynamic_played: dict[Users.GAMEMODES, summaryGameModeModel]
			builder_played: dict[Users.GAMEMODES, summaryGameModeModel]
			other_played: dict[Users.GAMEMODES, summaryGameModeModel]

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
		   Users.COUNTRIES, 
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
		unitsPerCountry: dict[Users.COUNTRIES, dict[Literal["numUnits", "numEliteUnits"], int]]
		aircrafts: dict[Users.COUNTRIES, dict[str, int]]
		slots: dict[Users.COUNTRIES, dict[str, int]]
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
			mode: Users.GAMEMODES
			modeValue: ModeStatsModel = Field(description="Key value is the value set for `mode`")
		class Showcase_BH_Model(BaseModel): # Battle-Hardened 
			class ModeStatsModel(BaseModel):
				average_score: float
				avg_rel_position: float
				each_player_session: int
				each_player_victories: int
				efficiency_vs_ai: float
				efficiency_vs_players: float
			h_mode: Users.GAMEMODES
			h_modeValue: ModeStatsModel = Field(description="Key value is the value set for `h_mode`")
		class Showcase_FavUnit_Model(BaseModel): # Favorite vehicle
			difficulty: Users.GAMEMODES
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
			counts: dict[Users.COUNTRIES, int] = Field(description="Number of vehicles collected per country")
		class Showcase_AceOfSpades_Model(BaseModel): # Ace of spades 
			class AcedUnitsModel(BaseModel):
				filteredTotal: int
				Aircraft: dict[Users.SIMPLE_COUNTRIES, int]
				Boat: dict[Users.SIMPLE_COUNTRIES, int]
				Helicopter: dict[Users.SIMPLE_COUNTRIES, int]
				Ship: dict[Users.SIMPLE_COUNTRIES, int]
				Tank: dict[Users.SIMPLE_COUNTRIES, int]
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