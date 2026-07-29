from logging import getLogger
from typing import Literal, Any
from pathlib import Path
from orjson import loads
from dataclasses import dataclass, asdict
from re import compile
from packaging.version import Version
from .constants import *
from requests import get
from subprocess import run as sub_run
from datetime import datetime
from time import perf_counter

_logger = getLogger(__name__)

def getMultipleKeys(obj:dict, *keys:str, default:Any = None, raise_on_missing:bool = False):
	for key in keys:
		if key in obj:
			return obj[key]
	if raise_on_missing:
		raise KeyError("Could not find any of the keys provided within the object")
	return default

gamefiles = Path(__file__).parent / "gamefiles"
@dataclass(frozen=True, init=False)
class DataLocations:
	@dataclass(frozen=True, slots=True)
	class VehicleData:
		DATA:Path
		IMAGE:Path
		PRESETS:Path
		SENSORS:Path

	TT_IMAGES:Path = gamefiles / "atlases.vromfs.bin_u" / "units"
	AIR_DATA: VehicleData = VehicleData(
		gamefiles / "aces.vromfs.bin_u" / "gamedata" / "flightmodels",
		gamefiles / "tex.vromfs.bin_u" / "aircrafts",
		gamefiles / "aces.vromfs.bin_u" / "gamedata" / "flightmodels" / "weaponpresets",
		gamefiles / "aces.vromfs.bin_u" / "gamedata" / "sensors"
	)
	GROUND_DATA: VehicleData = VehicleData(
		gamefiles / "aces.vromfs.bin_u" / "gamedata" / "units" / "tankmodels",
		gamefiles / "tex.vromfs.bin_u" / "tanks",
		gamefiles / "aces.vromfs.bin_u" / "gamedata" / "units" / "weaponpresets",
		gamefiles / "aces.vromfs.bin_u" / "gamedata" / "sensors"
	)
	NAVY_DATA: VehicleData = VehicleData(
		gamefiles / "aces.vromfs.bin_u" / "gamedata" / "units" / "ships",
		gamefiles / "tex.vromfs.bin_u" / "ships",
		gamefiles / "aces.vromfs.bin_u" / "gamedata" / "units" / "weaponpresets",
		gamefiles / "aces.vromfs.bin_u" / "gamedata" / "sensors" / "naval"
	)
	WEAPON_DATA: Path = gamefiles / "aces.vromfs.bin_u" / "gamedata" / "weapons"
	VEHICLE_DATA: Path = gamefiles / "char.vromfs.bin_u" / "config" / "unittags.blkx"
	TT_LINES: Path = gamefiles / "char.vromfs.bin_u" / "config" / "shop.blkx"
	WPCOST: Path = gamefiles / "char.vromfs.bin_u" / "config" / "wpcost.blkx"
	VEHICLE_LOC: Path = gamefiles / "lang.vromfs.bin_u" / "lang" / "units.csv"
	WEAPON_LOC: Path = gamefiles / "lang.vromfs.bin_u" / "lang" / "units_weaponry.csv"
	VERSION: Path = gamefiles / "version"
vehicle_data_loc = DataLocations()

csv_vehicle_pattern = compile(r"^(?P<base>[A-Za-z0-9_-]+?)(?:_(?P<variant>shop|[0-3]))?$")
@dataclass(frozen=True, slots=True)
class VehiclePaths:
	vehicle_id:str
	@dataclass(frozen=True, slots=True)
	class Images:
		techtree: Path
		statcard: Path
	images: Images
	vehicleData: Path
	presets: tuple[Path]
def referenceToPath(reference:str) -> Path:
	if not reference.endswith(".blk"): reference += ".blk"
	return gamefiles / "aces.vromfs.bin_u" / (reference.lower().replace("blk", "blkx"))
def get_vehicle_paths(vehicle_id:str) -> VehiclePaths|None:
	def ext(text:str, ext:Literal["png", "blkx"]): return text+"."+ext

	#region Vehicle type assessment
	vtype:DataLocations.VehicleData|None = None

	if ((vtype := vehicle_data_loc.AIR_DATA).DATA / ext(vehicle_id, "blkx")).exists(): pass
	elif ((vtype := vehicle_data_loc.GROUND_DATA).DATA / ext(vehicle_id, "blkx")).exists(): pass
	elif ((vtype := vehicle_data_loc.NAVY_DATA).DATA / ext(vehicle_id, "blkx")).exists(): pass
	else: return None
	vehiclePath = vtype.DATA / ext(vehicle_id, "blkx")
	#endregion

	return VehiclePaths(
		vehicle_id,
		VehiclePaths.Images(
			vehicle_data_loc.TT_IMAGES / ext(vehicle_id, "png"),
			vtype.IMAGE / ext(vehicle_id, "blkx")
		),
		vehiclePath,
		tuple(vtype.PRESETS.rglob(fr"{vehicle_id}_*.blkx"))
	)

@dataclass(frozen=True, slots=True)
class _limit:
	maxValue: int|float
	minValue: int|float

	@classmethod
	def from_values(cls, value1:int|float, value2:int|float):
		return cls(
			max(value1, value2),
			min(value1, value2)
		)
	@classmethod
	def from_list(cls, data:list[int|float]|None):
		if data is None:
			return
		return cls.from_values(max(data), min(data))

	def to_json(self):
		return asdict(self)

_sensor_data_cache: dict[Path, dict[str, Any]] = {}
_weapon_data_cache: dict[Path, dict[str, Any]] = {}

@dataclass(frozen=True, slots=True)
class Sensor:
	@dataclass(frozen=True, slots=True)
	class Antenna:
		angleHalfSens: float
		sideLobesSensitivity: float

		def to_json(self): 
			return asdict(self)
	@dataclass(slots=True)
	class _transiversEntry:
		type: str
		sideLobesAttenuation: float | None
		power: float
		pulseWidth: float | None
		bands: list[int]
		rcs: float
		ranges: dict[str, float]
		rangeMax: float
		multipathEffect: list[float]
		antenna: Sensor.Antenna | dict[str, Sensor.Antenna]
		visibilityType: Literal["infraRed", "radarIntercept", "optic"]
		@classmethod
		def from_json(cls, _type:str, data:dict[str, float|int]):
			if "power" in data:
				power = data["power"]
			elif "pulsePower" in data:
				power = data["pulsePower"]

			if "band" in data:
				if isinstance(data["band"], int):
					bands = [data["band"],]
				else:
					bands = data["band"]
			else:
				bands = []

			if ("receiver" in data):
				receiver:dict[str, float|dict] = data["receiver"]
				rcs = receiver.get("rcs", None)
				ranges = {}
				for k, v in receiver.items():
					if not k.startswith("range") and k != "rangeMax":
						continue
					ranges[k] = v
				rangeMax = receiver["rangeMax"]
			else:
				rcs = data.get("rcs", None)
				ranges = {}
				for k, v in data.items():
					if not k.startswith("range") and k != "rangeMax":
						continue
					ranges[k] = v
				rangeMax = data["rangeMax"]

			if "antenna" in data:
				if "sideLobesSensitivity" in data["antenna"]:
					antenna = Sensor.Antenna(
						data["antenna"]["angleHalfSens"],
						data["antenna"]["sideLobesSensitivity"]
					)
				elif "azimuth" in data["antenna"]:
					antenna = {
						"azimuth": Sensor.Antenna(
							data["antenna"]["azimuth"]["angleHalfSens"],
							data["antenna"]["azimuth"]["sideLobesSensitivity"]
						),
						"elevation": Sensor.Antenna(
							data["antenna"]["elevation"]["angleHalfSens"],
							data["antenna"]["elevation"]["sideLobesSensitivity"]
						),
					}
			
			return cls(
				_type,
				data.get("sideLobesAttenuation"),
				power,
				data.get("pulseWidth"),
				bands,
				rcs,
				ranges,
				rangeMax,
				[],
				antenna,
				data.get("visibilityType")
			)
		def to_json(self): 
			obj = asdict(self)
			for key, value in obj.items():
				if isinstance(value, Sensor.Antenna):
					obj[key] = value.to_json()
				elif isinstance(value, dict):
					for antenna, entry in value.items():
						if not isinstance(entry, Sensor.Antenna):
							continue
						obj[key][antenna] = entry.to_json()

			return obj
	@dataclass(frozen=True, slots=True)
	class _illuminationTransmitter:
		power: float
		antenna: Sensor.Antenna

		def to_json(self):
			obj = asdict(self)
			for key, value in obj.items():
				if isinstance(value, Sensor.Antenna):
					obj[key] = value.to_json()

			return obj
	@dataclass(frozen=True, slots=True)
	class _signalEntry:
		@dataclass(frozen=True, slots=True)
		class _distance:
			presents: bool
			minValue: float
			maxValue: float
			width: float | None

			@classmethod
			def from_json(cls, data:dict[str, Any]|None) -> Sensor._signalEntry._distance | None:
				if data is None:
					return
				return cls(
					data["presents"],
					data["minValue"],
					data["maxValue"],
					data.get("width")
				)
			def to_json(self): 
				return asdict(self)
		@dataclass(frozen=True, slots=True)
		class _dopplerSpeed:
			presents: bool
			minValue: float
			maxValue: float
			signalWidthMin: float # Yes i had to make a new dataclass for a single value
			width: float

			@classmethod
			def from_json(cls, data:dict[str, Any]|None) -> Sensor._signalEntry._dopplerSpeed | None:
				if data is None:
					return
				if not data["presents"]:
					return

				return cls(
					data["presents"],
					data["minValue"],
					data["maxValue"],
					data["signalWidthMin"],
					data["width"]
				)
			def to_json(self): 
				return asdict(self)
		type: str
		groundClutter: bool
		aircraftAsTarget: bool
		IFF: bool
		targetId: bool
		mainBeamNotchWidth: float
		mainBeamNotchMaxElevation: float
		distance: _distance | None
		dopplerSpeed: _dopplerSpeed | None
		extras: dict[str, Any]

		@classmethod
		def from_json(cls, _type:str, data:dict[str, Any]):
			cls(
				_type,
				data.get("groundClutter", True),
				data.get("aircraftAsTarget", True),
				data.get("friendFoeId", False),
				data.get("targetId", False),
				data.get("mainBeamNotchWidth"),
				data.get("mainBeamNotchMaxElevation"),
				cls._distance.from_json(data.get("distance")),
				cls._dopplerSpeed.from_json(data.get("dopplerSpeed")),
				{k:v for k, v in data.items() if k not in ["groundClutter", "aircraftAsTarget", "friendFoeId", "targetId", "mainBeamNotchWidth", "mainBeamNotchMaxElevation", "distance", "dopplerSpeed"]}
			)

		def to_json(self):
			obj = asdict(self)
			for key, value in obj.items():
				if isinstance(value, (self._distance, self._dopplerSpeed)):
					obj[key] = asdict(value)
			return obj
	@dataclass(frozen=True, slots=True)
	class _scanPattern:
		name: str
		scanPatternSet: str
		type: str
		azimuthLimits: _limit
		elevationLimits: _limit
		rollStabLimit: float
		pitchStabLimit: float
		period: float
		width: float
		barHeight: float
		barsCount: int
		rowMajor: bool

		@classmethod
		def from_data(cls, name: str, data:dict[str, Any], scanPatternSet:str):
			return cls(
				name,
				scanPatternSet,
				data.get("type"),
				_limit.from_list(data.get("azimuthLimits")),
				_limit.from_list(data.get("elevationLimits")),
				data.get("rollStabLimit"),
				data.get("pitchStabLimit"),
				data.get("period"),
				data.get("width"),
				data.get("barHeight"),
				data.get("barsCount"),
				data.get("rowMajor")
			)

		def to_json(self):
			obj = asdict(self)
			for key, value in obj.items():
				if isinstance(value, _limit):
					obj[key] = value.to_json()

			return obj
	@dataclass(frozen=True, slots=True)
	class _targetTypeId:
		name: str
		targetType: list[str]

		@classmethod
		def from_json(cls, data:dict[str, Any]):
			return cls(
				data.get("name"),
				data.get("targetType")
			)
		def to_json(self):
			return asdict(self)
	@dataclass(frozen=True, slots=True)
	class _vehicleTypeId:
		name: str
		propulsion: dict[str, str|int]

		@classmethod
		def from_json(cls, data:dict[str, Any]):
			return cls (
				data.get("name"),
				data.get("targetPropulsion")
			)

		def to_json(self):
			return asdict(self)

	type:str
	name:str
	displayName: str
	maxTargets:int
	transivers: tuple[_transiversEntry]
	illuminationTransmitter: _illuminationTransmitter | None
	signals: tuple[_signalEntry]
	signals_track:bool | None
	scopeRangeSets: dict[str, tuple[float]]
	scanPatterns: tuple[_scanPattern]
	targetTypeId: tuple[_targetTypeId]
	vehicleTypeId: tuple[_vehicleTypeId]
	sizeRanges: dict[str, _limit]


	@classmethod
	def from_id(cls, weapon:str, count: int = 1):
		for path in vehicle_data_loc.WEAPON_DATA.rglob(f"{weapon}.blkx"):
			return cls.from_path(path, count)
		_logger.error(f"Could not find sensor '{weapon}'")
		return None
	@classmethod
	def from_path(cls, sensor: Path):
		if not sensor.exists():
			raise LookupError(f"Sensor file not found at {sensor}")
		if sensor in _sensor_data_cache:
			data = _sensor_data_cache[sensor]
		else:
			data = loads(sensor.read_text())
			_sensor_data_cache[sensor] = data
		name = ".".join(sensor.name.split(".")[:-1])
		maxTargets = data.get("weaponTargetsMax", -1)

		transivers = []
		for k, v in data.get("transivers", {}).items():
			transivers.append(cls._transiversEntry.from_json(k, v))

		_ = data.get("illuminationTransmitter", {})
		if _:
			illuminationTransmitter = cls._illuminationTransmitter(
				_["power"],
				cls.Antenna(
					_["antenna"]["angleHalfSens"],
					_["antenna"]["sideLobesSensitivity"]
				)
			)
		else:
			illuminationTransmitter = None

		signals = []
		for k, v in data.get("signals", {}).items():
			if k.lower() == "track":
				track = v
				continue
			signals.append(cls._signalEntry.from_json(k, v))

		scopeRangeSets = {}
		for k, v in data.get("scopeRangeSets", {}).items():
			scopeRangeSets[k] = [i for i in v]

		tmp = {}
		for k, v in data.get("scanPatternSets", {}).items():
			tmp[k] = [i for i in v.values()]
		scanPatterns = []
		for k, v in data.get("scanPatterns", {}).items():
			patternSet = next((i for i, j in tmp.items() if k in j), None)
			scanPatterns.append(cls._scanPattern.from_data(k, v, patternSet))

		sizeRanges = {}
		vehicleTypeId = []
		targetTypeId = []
		for v in data.get("targetTypeId", []):
			name:str = v.get("name").removeprefix("hud/")
			if (_:=v.get("sizeRange", [])):
				sizeRanges[name] = _limit.from_list(_)
			elif name in ["helicopter", "single prop", "multi prop", "single jet", "multi jet", "rocket"]:
				vehicleTypeId.append(cls._vehicleTypeId.from_json(v))
			else:
				targetTypeId.append(cls._targetTypeId.from_json(v))

		return cls(
			data["type"],
			name,
			data.get("name"),
			maxTargets,
			tuple(transivers),
			illuminationTransmitter,
			tuple(signals),
			None,
			scopeRangeSets,
			tuple(scanPatterns),
			tuple(targetTypeId),
			tuple(vehicleTypeId),
			sizeRanges
		)

	def to_json(self):
		obj = asdict(self)
		for key, value in obj.items():
			if isinstance(value, self._illuminationTransmitter):
				obj[key] = value.to_json()
			elif isinstance(value, tuple):
				new = []
				for item in value:
					if isinstance(item, (self._transiversEntry, self._scanPattern, self._targetTypeId, self._targetTypeId, self._vehicleTypeId)):
						new.append(item.to_json())
					else:
						# Just in case
						new.append(item)
				obj[key] = tuple(new)
			elif isinstance(value, dict):
				for k, v in value.items():
					if isinstance(v, _limit):
						obj[key][k] = v.to_json()

		return obj

@dataclass(slots=True)
class Weapon:
	@dataclass(frozen=True, slots=True)
	class _ammo:
		name: str = None
		type: str = None
		caliber: float = 0.0
		mass: float = 0.0
		speed: float = 0.0
		max_distance: float = 0.0
		explosive_type: str | None = None
		explosive_mass: float | None = 0.0

		@classmethod
		def from_json(cls, data:dict[str, Any]) -> Weapon._ammo | None:
			if not data:
				return
			return cls(
				getMultipleKeys(data, "bombName", "bulletName"),
				getMultipleKeys(data, "bombType", "bulletType"),
				data.get("caliber"),
				_[0] if isinstance(_:=data.get("mass"), list) else _,
				getMultipleKeys(data, "maxSpeedInWater", "speed", "maxSpeed"),
				getMultipleKeys(data, "distToLive", "maxDistance"),
				data.get("explosiveType"),
				data.get("explosiveMass")
			)

	name: str = None
	type: str = None
	count: int = 1
	ammo: tuple[_ammo] = tuple()

	@classmethod
	def from_id(cls, weapon:str, count: int = 1):
		for path in vehicle_data_loc.WEAPON_DATA.rglob(f"{weapon}.blkx"):
			return cls.from_path(path, count)
		_logger.error(f"Could not find weapon '{weapon}'")
		return None

	@classmethod
	def from_path(cls, weapon:Path, count: int = 1):

		self = cls()
		self.count = count

		if not weapon.exists():
			raise LookupError(f"Weapon file not found at {weapon}")

		if weapon in _weapon_data_cache:
			weapon_blk = _weapon_data_cache[weapon]
		else:
			weapon_blk = loads(weapon.read_text())
			_weapon_data_cache[weapon] = weapon_blk
		
		self.name = ".".join(weapon.name.split(".")[:-1])
		if (self.name == "dummy_weapon"):
			return

		weapon_type = weapon_blk.get("weaponType")

		lowercase_keys = [i.lower() for i in weapon_blk.keys()]

		is_rocket: bool = weapon_blk.get(ROCKET_NAME) or ROCKET_TYPE in lowercase_keys or weapon_blk.get(ROCKET_TYPE)
		is_cannon: bool = weapon_blk.get(CANNON_NAME) or CANNON_TYPE in lowercase_keys or weapon_blk.get(CANNON_TYPE) or weapon_type == -1 or weapon_type == 1 or weapon_type == 3
		is_torpedo: bool = weapon_blk.get(TORPEDO_NAME) or TORPEDO_TYPE in lowercase_keys or weapon_blk.get(TORPEDO_TYPE) or weapon_type == 1
		is_bomb: bool = weapon_blk.get(BOMB_NAME) or BOMB_TYPE in lowercase_keys or weapon_blk.get(BOMB_TYPE)
		is_booster: bool = weapon_blk.get(BOOSTER_NAME) or BOOSTER_TYPE in lowercase_keys or weapon_blk.get(BOOSTER_TYPE)
		is_container: bool = weapon_blk.get(CONTAINER_NAME) or CONTAINER_TYPE in lowercase_keys or weapon_blk.get(CONTAINER_TYPE)
		is_extfueltank: bool = weapon_blk.get(EXTFUELTANK_NAME) or EXTFUELTANK_TYPE in lowercase_keys or weapon_blk.get(EXTFUELTANK_TYPE)
		
		valid = weapon_type is not None or is_rocket or is_torpedo or is_cannon or is_bomb or is_booster or is_container or is_extfueltank
		if not valid:
			_logger.error(f"Weapon {self.name}'s type is missing\n\n{weapon}\n\tType: {weapon_type}")
			return

		if is_cannon:
			self._get_ammo("bullet", weapon_blk)
			self.type = CANNON_NAME
		elif is_rocket:
			self._get_ammo("rocket", weapon_blk)
			self.type = ROCKET_NAME
		elif is_torpedo:
			self._get_ammo("torpedo", weapon_blk)
			self.type = TORPEDO_NAME
		elif is_bomb:
			self._get_ammo("bomb", weapon_blk)
			self.type = BOMB_NAME
		elif is_booster:
			self._get_ammo("payload", weapon_blk)
			self.type = BOOSTER_NAME
		elif is_container:
			self.type = CONTAINER_NAME
			return self.from_path(referenceToPath(weapon_blk["blk"]), weapon_blk["bullets"])
		elif is_extfueltank:
			self._get_ammo("payload", weapon_blk)
			self.type = EXTFUELTANK_NAME

		return self

	def _get_ammo(self, key:str, data:dict[str, Any]) -> set[Weapon._ammo]:
		ammo_list = []
		for k in data.keys():
			raw_ammo = None
			key_value = data.get(k)
			
			lowercase_keys = [i.lower() for i in data.keys()]

			if isinstance(key_value, dict) or isinstance(key_value, list) and k.lower() == key:
				raw_ammo = key_value
			elif isinstance(key_value, dict) and key in lowercase_keys:
				raw_ammo = key_value.get(key)
			
			if not raw_ammo: 
				continue

			raw_ammo = raw_ammo if isinstance(raw_ammo, list) else [raw_ammo,]

			for ammos in raw_ammo:
				if "bullet" in ammos and isinstance(ammos["bullet"], list):
					for ammo in ammos["bullet"]:
						_ammo = self._ammo.from_json(ammo)
						ammo_list.append(_ammo)
				else:
					_ammo = self._ammo.from_json(ammos)
					ammo_list.append(_ammo)
		self.ammo = tuple(ammo_list)

	def to_json(self):
		return {
			"weapon": self.name,
			"type": self.type,
			"count": self.count,
			"ammo": [asdict(i) for i in self.ammo]
		}

class Vehicle:
	version: Version
	identifier: str
	type: str
	subtypes: list[str]
	operator: str
	tags: list[str]
	vehicle_stats: dict[str, float]
	release_date:datetime
	sensors: list[str]

	@dataclass(frozen=True, slots=True)
	class _weapon:
		"""A shorter, less computationally intensive weapon class. Holds less data"""
		id: str
		totalMass: int
		totalCount: int
		damage: int|None
		weaponmask: int
		reqModification: str|None = None
		usedForCustomSlot: bool = False
		guidance: str|None = None

		@classmethod
		def from_json(cls, id:str, data:dict[str, Any]):
			guidance = getMultipleKeys(data, "aamGuidanceType", "atgmVisibilityType", "guidedBombVisibilityType")
			if guidance == "default":
				if "aamGuidanceType" in data:
					guidance = "infraRed"
				elif "atgmVisibilityType" in data:
					guidance = "laser"
				elif "guidedBombVisibilityType" in data:
					raise NotImplementedError("Didn't implement default for this one yet")
					guidance = ""
			return cls(
				id,
				getMultipleKeys(data, "totalGuidedBombMass", "totalBombRocketMass"),
				getMultipleKeys(data, "totalBombCount"),
				data.get("weaponDamage"),
				data.get("weaponmask"),
				data.get("reqModification"),
				data.get("isWeaponForCustomSlot", False),
				guidance
			)
		def to_json(self):
			return asdict(self)

	@dataclass(frozen=True, slots=True)
	class _defaultPreset:
		id: str
		totalDamage: int
		mass: int|None
		ammoCount: int|None
		hasCountermeasures: bool
		mass_per_sec: int
		weaponmask: int
		weapons: dict[str, dict[str, Vehicle._weapon|int]]

		@classmethod
		def from_json(cls, key:str, data:dict[str, Any], full_weapon_data:dict[str, dict[str, Any]]):
			if any(key.startswith(i) for i in ["rocketguns", "containers", "bombguns", "equipment", "drop_tank", "custom_presets"]):
				raise RuntimeError(f"Invalid key for default preset: {key}")
			weapons = {}
			for k,v in data.get("sum_weapons", {}).items():
				weapons[k] = {
					"weapon": Vehicle._weapon.from_json(k, full_weapon_data[k]),
					"count": v
				}
			
			return cls(
				key,
				data.get("weaponDamage"),
				getMultipleKeys(data, "totalGuidedBombMass", "totalBombRocketMass"),
				getMultipleKeys(data, "totalBombCount"),
				data.get("hasCountermeasures", False),
				data.get("mass_per_sec", 0),
				data.get("weaponmask"),
				weapons
			)
		def to_json(self):
			obj = asdict(self)
			for id, data in self.weapons.items():
				for key, value in data.items():
					if isinstance(value, Vehicle._weapon):
						obj["weapons"][id][key] = value.to_json()

			return obj
	default_presets: tuple[_defaultPreset] | None = None

	@dataclass(frozen=True, slots=True)
	class _pylonData:
		index: int
		weapons: tuple[dict[str, Vehicle._weapon|int|dict[str, int]]]

		@classmethod
		def from_json(cls, data:dict[str, int|dict[str, int]], all_data:dict[str, Any]):
			index = data.pop("index")

			weapons = []
			for k, v in data.items():
				entry = {}
				entry[k] = {}
				for key, value in v.items():
					if key == "DependentWeaponPreset":
						entry[k]["dependsOn"] = {}
						for name, idx in value.items():
							entry[k]["dependsOn"][name] = idx
					elif key == "BannedWeaponPreset":
						entry[k]["bannedPreset"] = {}
						for name, idx in value.items():
							entry[k]["bannedPreset"][name] = idx
					else:
						entry[k][key] = Vehicle._weapon.from_json(value, all_data[key])
				weapons.append(entry)
			return cls(index, tuple(weapons))
		def to_json(self):
			new_weapons = []
			for idx, weapon in enumerate(self.weapons):
				new_weapons.append({})
				for k, v in weapon.items():
					if k == "dependsOn":
						new_weapons[idx][k]["dependsOn"] = v
					elif k == "bannedPreset":
						new_weapons[idx][k]["bannedPreset"] = v
					elif isinstance(v, Vehicle._weapon):
						new_weapons[idx][k] = v.to_json()
					else:
						new_weapons[idx][k] = v

			return {
				"index": self.index,
				"weapons": tuple(new_weapons)
			}
	pylon_configurations: tuple[_pylonData]

	@dataclass(frozen=True, slots=True)
	class _computer:
		gun_ccip: bool
		turret_ccip: bool
		bombs_ccip: bool
		rocket_ccip: bool
		gun_ccrp: bool
		turret_ccrp: bool
		bombs_ccrp: bool
		rocket_ccrp: bool
		laser_designator: bool
		poi_designator: bool
		poi_memory: bool
		aiming_point_memory: bool
		gyro_sight: bool

		def to_json(self):
			return asdict(self)
	computer:_computer
	
	@dataclass(frozen=True, slots=True)
	class _nightvision:
		@dataclass(frozen=True, slots=True)
		class entry:
			resolution: tuple[int, int]
			generation: str
			noise: float
			index: int
			ghosting: float | None = None
			lightMult: float | None = None
		sightThermal: entry|None
		sightTgtPodThermal: entry|None
		gunnerIr: entry|None
		pilotIr: entry|None

		def to_json(self):
			obj = asdict(self)
			for key, value in obj.items():
				if isinstance(value, self.entry):
					obj[key] = asdict(value)
			return obj
	night_vision: _nightvision

	@dataclass(frozen=True, slots=True)
	class _preset:
		name: str = None
		weapons: tuple[Weapon] = ()

		def to_json(self):
			_ = asdict(self)
			_["weapons"] = tuple([i.to_json() for i in self.weapons])
			return _

	@dataclass(frozen=True, slots=True)
	class _modification:
		id: str
		prevModification: str | None
		reqModification: str | None
		tier: int | None
		effects: dict[str, float]
		modClass: str | None
		extras: dict[str, Any]
		@classmethod
		def from_json(cls, mod_id:str, data:dict[str, Any]):
			extras = {k:v for k, v in data.items() if k not in ["prevModification","reqModification","tier","effects","modClass"]}
			return cls(
				mod_id,
				data.get("prevModification"),
				data.get("reqModification"),
				data.get("tier"),
				data.get("effects", {}),
				data.get("modClass"),
				extras
			)
		def to_json(self):
			return asdict(self)
	modifications:tuple[_modification]

	@dataclass(frozen=True, slots=True)
	class _wpcost:
		@dataclass(frozen=True, slots=True)
		class _GamemodesSplit:
			arcade: float
			realistic: float
			simulator: float|None = None
			realistic_ground: float|None = None
			simulator_ground: float|None = None
			@classmethod
			def from_json(cls, data:dict[str, Any], base:str):
				return cls(
					float(data[f"{base}Arcade"]),
					float(data[f"{base}Historical"]),
					float(data[f"{base}Simulation"]) if f"{base}Simulation" in data else None,
					float(data[f"{base}TankHistorical"]) if f"{base}TankHistorical" in data else None,
					float(data[f"{base}TankSimulation"]) if f"{base}TankSimulation" in data else None
				)
		price: int
		requiredRP: int
		trainCost: int
		expertCost: int
		aceCostGE: int
		aceCostRP: int
		repairTimeHrs: _GamemodesSplit
		repairTimeHrsNoCrew: _GamemodesSplit
		repairCost: _GamemodesSplit
		repairCostPerMin: _GamemodesSplit
		repairCostFullUpgraded: _GamemodesSplit | None
		battleTimeAward: _GamemodesSplit
		avgAward: _GamemodesSplit
		rewardMultiplier: _GamemodesSplit
		RpMultiplier: float
		battleTime: _GamemodesSplit
		rank: int
		battleRating: _GamemodesSplit
		country: str
		unitClass: str
		speed: float | None
		maxAmmo: int | None
		maxFlightTimeMinutes: int | None
		requiredUnit: str | None
		crewCount: int | None
		givesNationBonus: bool
		has_customizable_weapons:bool
		turretSpeed: tuple[int, int] | None
		hideUnlessOwned: bool

		@classmethod
		def from_json(cls, data:dict[str, Any]):
			return cls(
				data["value"],
				data.get("reqExp", 0),
				data["trainCost"],
				data["train2Cost"],
				data["train3Cost_gold"],
				data["train3Cost_exp"],
				cls._GamemodesSplit.from_json(data, "repairTimeHrs"),
				cls._GamemodesSplit.from_json(data, "repairTimeHrsNoCrew"),
				cls._GamemodesSplit.from_json(data, "repairCost"),
				cls._GamemodesSplit.from_json(data, "repairCostPerMin"),
				cls._GamemodesSplit.from_json(data, "repairCostFullUpgraded") if "repairCostFullUpgradedArcade" in data else None,
				cls._GamemodesSplit.from_json(data, "battleTimeAward"),
				cls._GamemodesSplit.from_json(data, "avgAward"),
				cls._GamemodesSplit.from_json(data, "rewardMul"),
				data["expMul"],
				cls._GamemodesSplit.from_json(data, "battleTime"),
				data["rank"],
				cls._GamemodesSplit.from_json(data, "economicRank"),
				Vehicle.convert_country(data["country"]),
				data["unitClass"],
				data.get("speed"),
				data.get("maxAmmo"),
				data.get("maxFlightTimeMinutes"),
				data.get("reqAir"),
				data.get("crewTotalCount"),
				data.get("doesItGiveNationBonus", False),
				data.get("hasWeaponSlots", False),
				tuple(_) if (_:=data.get("turretSpeed")) is not None else None,
				data.get("showOnlyWhenBought", False)
			)

		def to_json(self):
			obj = asdict(self)

			for key, value in obj.items():
				if isinstance(value, self._GamemodesSplit):
					obj[key] = asdict(value)

			return obj
	economy: _wpcost
	statcard_image: Path
	techtree_image: Path

	def __init__(
		self, 
		vehicle_paths:VehiclePaths, 
		vehicleData:dict[str, Any], 
		wpCost: dict[str, Any],
		version: Version
	):
		self.__pathData = vehicle_paths
		self.__vehicleData = vehicleData
		self.__wpcost = wpCost
		self.identifier = vehicle_paths.vehicle_id
		self.version = version

		self.sensors = []
		self.tags = []
		self.subtypes = []
		self.modifications = []

		self._parse_economy()
		self._get_vehicle_data()

		self.statcard_image = vehicle_paths.images.statcard
		self.techtree_image = vehicle_paths.images.techtree

	@staticmethod
	def convert_country(country_code:str) -> str:
		return country_code.removeprefix("country_")

	def _parse_economy(self):
		# TODO: Add default preset parsing (wpcost.blkx 'unit_id > weapons')
		self.economy = self._wpcost.from_json(self.__wpcost[self.identifier])

		vehicleDataEntry:dict[str, str|dict] = self.__vehicleData.get(self.identifier)
		if (vehicleDataEntry is None):
			return
		self.vehicle_stats = vehicleDataEntry.get("Shop")
		tags:dict[str, bool] = vehicleDataEntry["tags"]

		self.type = vehicleDataEntry["type"]
		for tag in tags:
			if tag.startswith("country_") or tag == self.type:
				continue
			elif tag.startswith("type_"):
				self.subtypes.append(tag.removeprefix("type_"))
			else:
				self.tags.append(tag)

		release = vehicleDataEntry.get("releaseDate", "1970-01-01 00:00:00")
		if release == '':
			release = "1970-01-01 00:00:00"
		self.release_date = datetime.fromisoformat(release)

		if ("operatorCountry" in vehicleDataEntry):
			if isinstance(vehicleDataEntry["operatorCountry"], list):
				self.operator = [self.convert_country(i) for i in vehicleDataEntry["operatorCountry"]]
			else:
				self.operator = self.convert_country(vehicleDataEntry["operatorCountry"])
		else:
			self.operator = self.economy.country

		weaponry = self.__wpcost[self.identifier]["weapons"]
		def_presets = []
		pylons = []
		for k, v in weaponry.items():
			if (k.startswith(self.identifier)): # Default presets
				def_presets.append(self._defaultPreset.from_json(k, v, weaponry))
			elif (k == "custom_presets"): # Custom Presets
				if isinstance(v["slot"], dict):
					pylons.append(self._pylonData.from_json(v["slot"], weaponry))
				else:
					for pylon in v["slot"]:
						pylons.append(self._pylonData.from_json(pylon, weaponry))
		self.default_presets = tuple(def_presets)
		self.pylon_configurations = tuple(pylons)
		#endregion

	def _get_vehicle_data(self):
		data:dict[str, Any] = loads(self.__pathData.vehicleData.read_text())
		self.computer = self._computer(
			gun_ccip = data.get("haveCCIPForGun", False),
			turret_ccip = data.get("haveCCIPForTurret", False),
			bombs_ccip = data.get("haveCCIPForBombs", False),
			rocket_ccip = data.get("haveCCIPForRocket", False),
			gun_ccrp = data.get("haveCCRPForGun", False),
			turret_ccrp = data.get("haveCCRPForTurret", False),
			bombs_ccrp = data.get("haveCCRPForBombs", False),
			rocket_ccrp = data.get("haveCCRPForRocket", False),
			laser_designator = data.get("laserDesignator", False),
			poi_designator = data.get("havePointOfInterestDesignator", False),
			poi_memory = data.get("hasPointOfInterestMemory", False),
			aiming_point_memory = data.get("hasAimingPointsMemory", False),
			gyro_sight = data.get("gyroSight", False)
		)

		#region NVDs
		tmp:dict[str, list[dict[str, Any]]] = data.get("nightVision", {})
		for k, v in tmp.items():
			if "ir" in k.lower():
				tmp[k]["generation"] = IR_VISION_GENERATIONS.get(tuple(v["resolution"]), "Unknown") 
			elif "thermal" in k.lower():
				tmp[k]["generation"] = THERMAL_VISION_GENERATIONS.get(tuple(v["resolution"]), "Unknown") 
			elif "nightvisiondmpart" in k.lower():
				pass
			else:
				raise KeyError(f"Type of night vision '{k}' not found")
		
		self.night_vision = self._nightvision(
			self._nightvision.entry(
				tuple(tmp["sightThermal"]["resolution"]),
				tmp["sightThermal"]["generation"],
				tmp["sightThermal"]["noiseFactor"],
				tmp["sightThermal"].get("index", -1)
			) if tmp.get("sightThermal") is not None else None,
			self._nightvision.entry(
				tuple(tmp["sightTPodThermal"]["resolution"]),
				tmp["sightTPodThermal"]["generation"],
				tmp["sightTPodThermal"]["noiseFactor"],
				tmp["sightTPodThermal"].get("index", -1)
			) if tmp.get("sightTPodThermal") is not None else None,
			self._nightvision.entry(
				tuple(tmp["gunnerIr"]["resolution"]),
				tmp["gunnerIr"]["generation"],
				tmp["gunnerIr"]["noiseFactor"],
				-1,
				tmp["gunnerIr"]["ghosting"],
				tmp["gunnerIr"]["lightMult"]
			) if tmp.get("gunnerIr") is not None else None,
			self._nightvision.entry(
				tuple(tmp["pilotIr"]["resolution"]),
				tmp["pilotIr"]["generation"],
				tmp["pilotIr"]["noiseFactor"],
				-1,
				tmp["gunnerIr"]["ghosting"],
				tmp["gunnerIr"]["lightMult"]
			) if tmp.get("pilotIr") is not None else None
		)
		#endregion

		#region Sensors
		sensorsData = data.get("sensors", {"sensor":[]})
		if not isinstance(sensorsData, dict):
			raise RuntimeError("Sensors entry not a dict")
		if "sensor" in sensorsData:
			if isinstance(sensorsData["sensor"], dict):
				blkname = sensorsData["sensor"].get("blk")
				if blkname is not None:
					self.sensors.append(referenceToPath(blkname).name.removesuffix(".blkx"))
			else:
				for sensor in sensorsData["sensor"]:
					blkname:str = sensor.get("blk")
					if blkname is None:
						continue
					self.sensors.append(referenceToPath(blkname).name.removesuffix(".blkx"))
		elif "fireDirecting" in sensorsData:
			pass # TODO: Navy stuff, no data retrieved currently
		#endregion

		self.modifications = tuple([self._modification.from_json(k, v) for k,v in data.get("modifications", {}).items()])
		pass

	def to_json(self):
		obj = {
			"id": self.identifier,
			"data_version": self.version,
			"economy": self.economy.to_json(),
			"modifications": [i.to_json() for i in self.modifications],
			"nightvision": self.night_vision.to_json(),
			"computers": self.computer.to_json(),
			"release_date": self.release_date,
			"type": self.type,
			"subtypes": self.subtypes,
			"operator": self.operator,
			"tags": self.tags,
			"stats": self.vehicle_stats,
			"default_presets": tuple([i.to_json() for i in self.default_presets]) if self.default_presets else None,
			"pylon_configurations": tuple([i.to_json() for i in self.pylon_configurations]) if self.pylon_configurations else None
		}
		return obj

class UpdateAvailableError(Exception): 
	"""An exception class for when a git update is available"""
	def __init__(self, *args):
		super().__init__(*args)

async def processor(*vehicle_ids:str, get_all:bool = False, autoupdate_repo:bool = True) -> list[Vehicle]|None:
	#region Pre-run checks
	if not gamefiles.exists():
		_logger.error(f"Directory {gamefiles} could not be found")
		return None
	if not (gamefiles / ".git").exists():
		_logger.error(f"{gamefiles} doesn't have a git repository set up")
		return None
	version = Version(vehicle_data_loc.VERSION.read_text())
	git_version = Version(get("https://raw.githubusercontent.com/gszabi99/War-Thunder-Datamine/refs/heads/master/version").text)
	if (version < git_version):
		if not autoupdate_repo:
			raise UpdateAvailableError(f"Update available for repository: {version} -> {git_version}")
		sub_run("git pull", cwd=gamefiles, shell=True, check=True)
		return await processor(*vehicle_ids, get_all=get_all)
	#endregion

	wpCost: dict[str, dict[str, Any]] = loads(vehicle_data_loc.WPCOST.read_text())
	#region Path Obtaining
	if get_all:
		vehicle_ids = [k for k in wpCost.keys() if k != "economicRankMax"]
	#endregion
	vehicleData = loads(vehicle_data_loc.VEHICLE_DATA.read_text())
	#region Vehicle parsing
	start_time = perf_counter()
	vehicle_entries = []
	for id in vehicle_ids:
		if id not in wpCost:
			_logger.error(f"Invalid vehicle ID: '{id}'")
			continue
		paths = get_vehicle_paths(id)
		if paths is None:
			continue
		try:
			vehicle_entries.append(Vehicle(paths, vehicleData, wpCost, version))
		except LookupError:
			_logger.exception(f"Could not parse vehicle {id}")
	end_time = perf_counter()
	_logger.debug(f"Vehicle parsing took {round(end_time-start_time, 2)} seconds")
	#endregion

	return vehicle_entries


if __name__ == '__main__':
	from logging import DEBUG, basicConfig
	from asyncio import new_event_loop
	basicConfig(
		level=DEBUG, 
		format="%(asctime)s:%(name)-30s:%(funcName)-15s:%(lineno)-3d:%(levelname)-7s:%(message)s"
	)
	loop = new_event_loop()
	start_time = perf_counter()
	result = loop.run_until_complete(processor(get_all=True))
	#result = loop.run_until_complete(processor("saab_jas39e", "saab_j21a_2", "tiger_uht", "germ_leopard_2k", "ussr_battlecruiser_izmail", "it_gabbiano_class"))
	#result = loop.run_until_complete(processor("saab_jas39e"))
	end_time = perf_counter()
	_logger.debug(f"Fetching took {end_time-start_time} seconds to parse {len(result)} entries")

	start_time = perf_counter()
	results = [i.to_json() for i in result]
	end_time = perf_counter()
	_logger.debug(f"JSON conversion took {end_time-start_time} seconds to convert {len(result)} entries")
		
	pass