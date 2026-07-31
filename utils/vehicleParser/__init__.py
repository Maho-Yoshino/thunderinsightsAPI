from __future__ import annotations
from asyncio import get_running_loop
from dataclasses import dataclass
from enum import Enum
from logging import getLogger
from pathlib import Path
from datetime import datetime
from typing import Any
from pandas import read_csv
from utils.vehicleParser.vehiclesProcessor import Vehicle, Weapon, Sensor, getAllVehicleIDs, processVehicles

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
			
			_logger.info(f"Set up git repo in {DatabasePaths.GAMEFILES}")

		if (not DatabasePaths.DATABASE.ROOT.exists()):
			if (not DatabasePaths.DATABASE.ALL.exists()):
				DatabasePaths.DATABASE.ALL.write_text("{}")

	async def getVehicle(self, unit:str) -> Vehicle|None:
		try:
			vehicle = await Vehicle.from_id(unit)
		except LookupError:
			return
		return vehicle

	async def getWeapon(self, weapon:str) -> Weapon|None:
		try:
			weapon = Weapon.from_id(weapon)
		except LookupError:
			return
		return weapon

	async def getSensor(self, sensor:str) -> Sensor|None:
		try:
			sensor = await Sensor.from_id(sensor)
		except LookupError:
			return
		return sensor