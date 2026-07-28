from __future__ import annotations
from asyncio import run as asyncio_run
from utils import users_cache
from apscheduler.triggers.interval import IntervalTrigger
from dataclasses import dataclass
from aiosqlite import Row, connect
from contextlib import asynccontextmanager
from subprocess import run as sub_run
from enum import Enum
from logging import getLogger
from packaging.version import Version
from pathlib import Path
from datetime import datetime
from typing import TYPE_CHECKING
from utils.vehicleParser.schema import *
from utils.vehicleParser.vehiclesProcessor import processor
if TYPE_CHECKING:
	from utils.vehicleParser.vehiclesProcessor import Vehicle

_logger = getLogger(__name__)

class VehicleDataTypes(Enum):
	META = 0
	SUBTYPES = 1
	BATTLERATINGS = 2
	ECONOMY = 3
	ENGINES = 4
	MODIFICATIONS = 5
	NIGHT_VISION = 6
	THERMAL = 7
	COMPUTER = 8
	AERO = 9
	PRESETS = 10
	IMAGES = 11
	SENSORS = 12
	LOCALIZATION = 13

class Vehicles:
	@dataclass(frozen=True, slots=True)
	class Weapon:
		@dataclass(frozen=True, slots=True)
		class _Ammo:
			name: str|None
			type: str|None
			caliber: float
			mass: float
			speed: int
			max_distance: int
			explosive_type: str
			explosive_mass: float
		name: str
		type: str
		ammo: tuple[_Ammo]
		count: int
	class Unit: # Short lived data class
		@dataclass(frozen=True, slots=True)
		class _Gamemodes:
			arcade: int|float
			realistic: int|float
			simulator: int|float|None
		@dataclass(frozen=True, slots=True)
		class _GamemodesSplit(_Gamemodes):
			realistic_ground: int|float|None
			simulator_ground: int|float|None
		@dataclass(frozen=True, slots=True)
		class _Economy:
			is_premium:bool
			is_pack:bool
			is_marketplace:bool
			is_squadron:bool
			price: int
			rp_cost: int
			ge_cost: int
			train_cost: int
			expert_cost: int
			ace_cost_ge: int
			ace_cost_rp: int
			repair_times: "Vehicles.Unit._Gamemodes"
			repair_times_no_crew: "Vehicles.Unit._Gamemodes"
			repair_cost: "Vehicles.Unit._Gamemodes"
			repair_cpm: "Vehicles.Unit._Gamemodes"
			repair_cost_full_upgraded: "Vehicles.Unit._Gamemodes"
		@dataclass(frozen=True, slots=True)
		class _Modification:
			name: str
			tier: int
			repair_coefficient: float
			price: int
			rp_cost: int
			ge_cost: int
			required_modification: "Vehicles.Unit._Modification"|None
			mod_class: str
			icon: str
		@dataclass(frozen=True, slots=True)
		class _Devices:
			commander: bool
			driver: bool
			pilot: bool
			sight: bool
			tgt_pod: bool
			gunner: bool
		@dataclass(frozen=True, slots=True)
		class _Ballistic:
			gun_ccip: bool
			turret_ccip: bool
			bombs_ccip: bool
			rocket_ccip: bool
			gun_ccrp: bool
			turret_ccrp: bool
			bombs_ccrp: bool
			rocket_ccrp: bool
		@dataclass(frozen=True, slots=True)
		class _Aerodynamics:
			length: int
			wingspan: int
			wing_area: int
			empty_weight: int
			max_takeoff_weight: int
			max_altitude: int
			turn_time: float
			runway_length_req: int
			max_speed_at_altitude: int
		@dataclass(frozen=True, slots=True)
		class _Preset:
			name: str
			weapons: tuple[Vehicles.Weapon]
		@dataclass(frozen=True, slots=True)
		class _CustomizablePresets:
			@dataclass(slots=True)
			class PylonData:
				idx: int
				used_for_disbalance: bool
				selectable_weapons: tuple[Vehicles.Weapon]
			max_load: int
			max_load_left_wing: int
			max_load_right_wing: int
			max_disbalance: int
			pylons: tuple[PylonData]
		@dataclass(frozen=True, slots=True)
		class _Images:
			image: str
			techtree: str
		id: str
		country: str
		type: str
		subtypes: tuple[str]
		release_date: datetime
		version: Version
		rank: int
		event: str|None
		battleratings: _GamemodesSplit
		economy: _Economy
		modifications: tuple[_Modification]
		nightvision: _Devices
		thermals: _Devices
		ballistic_computer: _Ballistic
		aerodynamics: _Aerodynamics
		presets: tuple[_Preset]
		has_customizable_weapons: bool
		customizable_presets: _CustomizablePresets

	__db_path: Path
	_gamefilesPath: Path
	currentVer: Version
	def __init__(self):
		root = Path(__file__).parent
		self.__db_path = root / "units.db"
		self._gamefilesPath = root / "gamefiles"
		
		try:
			asyncio_run(self.setup())
		except RuntimeError:
			_logger.warning("Skipped initialization due to no running event loop")

	async def setup(self):
		self._gamefilesPath.mkdir(mode=0o755, exist_ok=True)

		if not (self._gamefilesPath / ".git").exists():
			tracked_paths = [ # Put a / before single files
				"aces.vromfs.bin_u/gamedata/flightmodels",
				"aces.vromfs.bin_u/gamedata/units/tankmodels",
				"aces.vromfs.bin_u/gamedata/units/ships",
				"aces.vromfs.bin_u/gamedata/sensors",
				"aces.vromfs.bin_u/gamedata/weapons",
				"atlases.vromfs.bin_u/units",
				"/char.vromfs.bin_u/config/shop.blkx",
				"/char.vromfs.bin_u/config/unittags.blkx",
				"/char.vromfs.bin_u/config/wpcost.blkx",
				"/lang.vromfs.bin_u/lang/units.csv",
				"/lang.vromfs.bin_u/lang/units_weaponry.csv",
				"tex.vromfs.bin_u/aircrafts",
				"tex.vromfs.bin_u/ships",
				"tex.vromfs.bin_u/tanks",
				"/version"
			]

			sub_run(
		   		"git clone --filter=blob:none --sparse https://github.com/gszabi99/War-Thunder-Datamine.git ./ &&" +
		   		f"git sparse-checkout set --no-cone {" ".join(tracked_paths)}", 
				check=True,
				shell=True,
				cwd=self._gamefilesPath
			)
			_logger.info(f"Set up git repo in {self._gamefilesPath}")
		
		if not self.__db_path.exists():
			await users_cache._init_db(self.__db_path)

	async def get(self, unit:str, data:VehicleDataTypes = VehicleDataTypes.META) -> Vehicles.Unit|None:
		
		found = len(
			list( (self._gamefilesPath / "aces.vromfs.bin_u").rglob(f"{unit}.png") )
		) > 0
		if not found:
			return None # No point querying, the vehicle doesn't exist

		async with self._transaction() as cur:
			exists = await (await cur.execute(f"SELECT 1 FROM {Units.t()} WHERE {Units.UNIT} = ?", (unit,))).fetchone()
			if exists is None:
				await self._write_vehicles(unit)
			match data:
				case VehicleDataTypes.META:
					metaRow = await (await cur.execute(f"""
						SELECT * FROM {Units.t()} WHERE {Units.UNIT} = ?
					""", (unit,))).fetchone()
			if not metaRow:
				return
			subtypesRow = await (await cur.execute(f"""
				SELECT * FROM {UnitSubtypes.t()} WHERE {UnitSubtypes.UNIT} = ?
			""", (unit,))).fetchall()
			pass
		...

	async def _write_vehicles(self, *vehicle_ids:str, get_all:bool = False):
		vehicles = await processor(*vehicle_ids, get_all)
		lang_vromf = self._gamefilesPath / "lang.vromfs.bin_u"
		units_localization = lang_vromf / "units.csv"
		weaponry_localization = lang_vromf / "units_weaponry.csv"
		pass
		...
	def _getVersion(self):
		if (verPath := self._gamefilesPath / "version").exists():
			return Version(verPath.read_text("utf-8").strip())
		raise LookupError(f"Could not find version file at {verPath}")
	@asynccontextmanager
	async def _transaction(self):
		con = await connect(self.__db_path)
		con.row_factory = Row
		try:
			cur = await con.cursor()
			try:
				yield cur
				await con.commit()
			except Exception:
				await con.rollback()
				raise
			finally:
				await cur.close()
		finally:
			await con.close()
