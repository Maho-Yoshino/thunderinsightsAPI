from __future__ import annotations
from asyncio import get_running_loop
from dataclasses import dataclass, asdict
from subprocess import run as sub_run
from enum import Enum
from logging import getLogger
from pathlib import Path
from datetime import datetime
from typing import TYPE_CHECKING, Any
from pandas import read_csv
from utils.vehicleParser.vehiclesProcessor import processor, get_vehicle_paths
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


class DatabasePaths:
	ROOT:Path = Path(__file__).parent

	@dataclass(frozen=True, slots=True)
	class _dbpaths:
		ROOT: Path
		VEHICLES: Path
		WEAPONS: Path
		SENSORS: Path
		ALL: Path

	DATABASE:_dbpaths = _dbpaths(
		ROOT / "database",
		ROOT / "database" / "units",
		ROOT / "database" / "weapons",
		ROOT / "database" / "sensors",
		ROOT / "database" / "all.json"
	)
	GAMEFILES:Path = ROOT / "gamefiles"

class Vehicles:
	def __init__(self):
		_logger.debug("Vehicles object created")

	async def setup(self):
		DatabasePaths.GAMEFILES.mkdir(mode=0o755, exist_ok=True)

		if not (DatabasePaths.GAMEFILES / ".git").exists():
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
				"/lang.vromfs.bin_u/lang/units_modifications.csv",
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
				cwd=DatabasePaths.GAMEFILES
			)
			_logger.info(f"Set up git repo in {DatabasePaths.GAMEFILES}")

		if (not DatabasePaths.DATABASE.ROOT.exists()):
			if (not DatabasePaths.DATABASE.ALL.exists()):
				DatabasePaths.DATABASE.ALL.write_text("{}")

	async def get(self, unit:str) -> dict[str, Any]|None:
		vehicles = await processor(unit)
		if len(vehicles < 1):
			return
		return vehicles[0]

	async def _write_vehicles(self, *vehicle_ids:str, get_all:bool = False):
		lang_vromf = DatabasePaths.GAMEFILES / "lang.vromfs.bin_u" / "lang"

		units_localization = read_csv(lang_vromf / "units.csv", delimiter=';', encoding='utf-8')
		units_localization.set_index("<ID|readonly|noverify>", inplace=True)

		weaponry_localization = read_csv(lang_vromf / "units_weaponry.csv", delimiter=";", encoding="utf-8")
		weaponry_localization.set_index("<ID|readonly|noverify>", inplace=True)

		modifications_localization = read_csv(lang_vromf / "units_modifications.csv", delimiter=";", encoding="utf-8")
		modifications_localization.set_index("<ID|readonly|noverify>", inplace=True)

		vehicles = await processor(*vehicle_ids, get_all=get_all)
		
		written_weapons:list[str] = []
		written_sensors:list[str] = []
		summaries: dict[str, dict[str, Any]] = {}
		for vehicle in vehicles:
			summary = {}
			obj = {}

			pass
