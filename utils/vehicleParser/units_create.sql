-- Versioning
CREATE TABLE git_versions (
	version TEXT PRIMARY KEY,
	git_hash TEXT NOT NULL
);
-- Weapon data
CREATE TABLE weapons (
	name TEXT PRIMARY KEY,
	type TEXT NOT NULL
);
CREATE TABLE ammo (
	weapon TEXT NOT NULL,
	ammo_index INTEGER NOT NULL,
	name TEXT,
	type TEXT, -- Projectile type (aphe, flr, aam, etc.)
	caliber REAL, -- Caliber in dm (why???)
	mass REAL, -- Projectile mass in kg
	speed INTEGER, -- Muzzle velocity in m/s
	max_distance INTEGER, -- Max range in meters
	explosive_type TEXT,
	explosive_mass REAL, -- Mass in kg (NOT TNT equivalent)

	PRIMARY KEY (weapon, ammo_index),
	FOREIGN KEY (weapon) REFERENCES weapons(name) ON DELETE CASCADE
);
-- Sensor data
CREATE TABLE sensors(
	name TEXT PRIMARY KEY,
	type TEXT NOT NULL,
	max_targets INTEGER,
	missile_aim_lead INTEGER NOT NULL CHECK (missile_aim_lead IN (0, 1))
);
CREATE TABLE sensor_signals(
	sensor TEXT NOT NULL,
	mode TEXT NOT NULL,
	ground_clutter INTEGER DEFAULT -1 CHECK (ground_clutter IN (0, 1)),
	aircraft_as_target INTEGER DEFAULT -1 CHECK (aircraft_as_target IN (0, 1)),
	iff INTEGER DEFAULT -1 CHECK (iff IN (0, 1)),
	target_id INTEGER DEFAULT -1 CHECK (target_id IN (0, 1)),
	min_distance INTEGER CHECK (min_distance IN (NULL, 0, 1)),
	max_distance INTEGER CHECK (max_distance IN (NULL, 0, 1)),
	min_doppler_speed INTEGER CHECK (min_doppler_speed IN (NULL, 0, 1)),
	max_doppler_speed INTEGER CHECK (max_doppler_speed IN (NULL, 0, 1)),
	rangefinder INTEGER DEFAULT 0 CHECK (rangefinder IN (0, 1)),


	PRIMARY KEY (sensor, mode),
	FOREIGN KEY (sensor) REFERENCES sensors(name) ON DELETE CASCADE
);
CREATE TABLE sensor_scan_patterns(
	sensor TEXT NOT NULL,
	name TEXT NOT NULL,
	type TEXT NOT NULL,
	azimuthMin REAL CHECK (azimuthMin = NULL OR azimuthMin < azimuthMax),
	azimuthMax REAL CHECK (azimuthMax = NULL OR azimuthMax > azimuthMin),
	elevationMin REAL CHECK (elevationMin = NULL OR elevationMin < elevationMax),
	elevationMax REAL CHECK (elevationMax = NULL OR elevationMax > elevationMin),
	roll_stab_limit REAL,
	pitch_stab_limit REAL,
	pattern TEXT NOT NULL,

	PRIMARY KEY (sensor, name),
	FOREIGN KEY (sensor) REFERENCES sensors(name) ON DELETE CASCADE
);
CREATE TABLE sensor_unit_id(
	sensor TEXT NOT NULL,
	target_name TEXT NOT NULL,

	PRIMARY KEY (sensor, target_name),
	FOREIGN KEY (sensor) REFERENCES sensors(name) ON DELETE CASCADE
);
-- Unit data
CREATE TABLE units (
	id TEXT PRIMARY KEY, -- Internal vehicle name (e.g. 'saab_jas39e')
	country TEXT NOT NULL, -- Internal country name (e.g 'country_sweden')
	type TEXT NOT NULL, -- Vehicle type (e.g. 'fighter')
	release_date INTEGER NOT NULL, -- Days since epoch. Logically x//60//60//24
	version TEXT NOT NULL, -- Last changed version
	rank INTEGER NOT NULL, -- The rank of the vehicle ingame (1-9 currently)
	event TEXT, -- Event name as a string if an event vehicle
	crew_count INTEGER NOT NULL,
	visibility INTEGER NOT NULL,
	hull_armor TEXT,
	turret_armor TEXT,
	mass INTEGER NOT NULL,
	required_vehicle TEXT,
	has_customizable_weapons INTEGER NOT NULL CHECK (has_customizable_weapons IN (0, 1)), -- Boolean
	data_version TEXT NOT NULL, -- The version this data was queried. If the data is not the current latest version, code will fetch new data on the vehicle

	FOREIGN KEY (required_vehicle) REFERENCES units(id) ON DELETE SET NULL,
	FOREIGN KEY (version) REFERENCES git_versions(version) ON DELETE SET NULL,
	FOREIGN KEY (data_version) REFERENCES git_versions(version) ON DELETE SET NULL
);
CREATE TABLE unit_subtypes (
	unit TEXT NOT NULL,
	type TEXT NOT NULL, -- e.g 'jet_fighter'

	PRIMARY KEY (unit, type),
	FOREIGN KEY (unit) REFERENCES units(id) ON DELETE CASCADE
);
CREATE TABLE unit_battleratings (
	unit TEXT PRIMARY KEY,
	arcade REAL NOT NULL,
	realistic REAL NOT NULL,
	realistic_ground REAL,
	simulator REAL, -- Nullable due to naval units
	simulator_ground REAL,

	FOREIGN KEY (unit) REFERENCES units(id) ON DELETE CASCADE
);
CREATE TABLE unit_economy (
	unit TEXT PRIMARY KEY,
	is_premium INTEGER NOT NULL CHECK (is_premium IN (0, 1)),
	is_pack INTEGER NOT NULL CHECK (is_pack IN (0, 1)),
	is_marketplace INTEGER NOT NULL CHECK (is_marketplace IN (0, 1)),
	is_squadron INTEGER NOT NULL CHECK (is_squadron IN (0, 1)),
	price INTEGER NOT NULL,
	rp_cost INTEGER NOT NULL,
	ge_cost INTEGER NOT NULL,
	train_cost INTEGER NOT NULL,
	expert_cost INTEGER NOT NULL,
	ace_cost_ge INTEGER NOT NULL,
	ace_cost_rp INTEGER NOT NULL,
	sl_mul_arcade REAL NOT NULL,
	sl_mul_realistic REAL NOT NULL,
	sl_mul_simulator REAL, -- Nullable due to naval units
	exp_mult REAL NOT NULL,
	repair_time_arcade REAL NOT NULL,
	repair_time_realistic REAL NOT NULL,
	repair_time_simulator REAL NOT NULL,
	repair_time_no_crew_arcade REAL NOT NULL,
	repair_time_no_crew_realistic REAL NOT NULL,
	repair_time_no_crew_simulator REAL,
	repair_cost_arcade INTEGER NOT NULL,
	repair_cost_realistic INTEGER NOT NULL,
	repair_cost_simulator INTEGER,
	repair_cost_per_min_arcade INTEGER NOT NULL,
	repair_cost_per_min_realistic INTEGER NOT NULL,
	repair_cost_per_min_simulator INTEGER,
	repair_cost_full_upgraded_arcade INTEGER NOT NULL,
	repair_cost_full_upgraded_realistic INTEGER NOT NULL,
	repair_cost_full_upgraded_simulator INTEGER,

	FOREIGN KEY (unit) REFERENCES units(id) ON DELETE CASCADE
);
CREATE TABLE unit_engines (
	unit TEXT PRIMARY KEY,
	hp_ab INTEGER NOT NULL,
	hp_rb_sb INTEGER NOT NULL,
	max_rpm INTEGER NOT NULL,
	min_rpm INTEGER NOT NULL,
	max_speed_ab INTEGER NOT NULL,
	max_reverse_speed_ab INTEGER NOT NULL,
	max_speed_rb_sb INTEGER NOT NULL,
	max_reverse_speed_rb_sb INTEGER NOT NULL,

	FOREIGN KEY (unit) REFERENCES units(id) ON DELETE CASCADE
);
CREATE TABLE unit_modifications (
	unit TEXT NOT NULL,
	name TEXT NOT NULL,
	tier INTEGER NOT NULL,
	repair_coeff REAL NOT NULL,
	price INTEGER NOT NULL,
	rp_cost INTEGER NOT NULL,
	ge_cost INTEGER NOT NULL,
	required_modification TEXT,
	mod_class TEXT NOT NULL,
	icon TEXT NOT NULL,

	PRIMARY KEY (unit, name),
	FOREIGN KEY (unit) REFERENCES units(id) ON DELETE CASCADE
);
CREATE TABLE unit_nv (
	unit TEXT PRIMARY KEY,
	commander INTEGER NOT NULL CHECK (commander IN (0, 1)),
	driver INTEGER NOT NULL CHECK (driver IN (0, 1)),
	pilot INTEGER NOT NULL CHECK (pilot IN (0, 1)),
	sight INTEGER NOT NULL CHECK (sight IN (0, 1)),
	tgt_pod INTEGER NOT NULL CHECK (tgt_pod IN (0, 1)),
	gunner INTEGER NOT NULL CHECK (gunner IN (0, 1)),

	FOREIGN KEY (unit) REFERENCES units(id) ON DELETE CASCADE
);
CREATE TABLE unit_thermal (
	unit TEXT PRIMARY KEY,
	commander INTEGER NOT NULL CHECK (commander IN (0, 1)),
	driver INTEGER NOT NULL CHECK (driver IN (0, 1)),
	pilot INTEGER NOT NULL CHECK (pilot IN (0, 1)),
	sight INTEGER NOT NULL CHECK (sight IN (0, 1)),
	tgt_pod INTEGER NOT NULL CHECK (tgt_pod IN (0, 1)),
	gunner INTEGER NOT NULL CHECK (gunner IN (0, 1)),

	FOREIGN KEY (unit) REFERENCES units(id) ON DELETE CASCADE
);
CREATE TABLE unit_computer (
	unit TEXT PRIMARY KEY,
	gun_ccip INTEGER NOT NULL CHECK (gun_ccip IN (0, 1)),
	turret_ccip INTEGER NOT NULL CHECK (turret_ccip IN (0, 1)),
	bombs_ccip INTEGER NOT NULL CHECK (bombs_ccip IN (0, 1)),
	rocket_ccip INTEGER NOT NULL CHECK (rocket_ccip IN (0, 1)),
	gun_ccrp INTEGER NOT NULL CHECK (gun_ccrp IN (0, 1)),
	turret_ccrp INTEGER NOT NULL CHECK (turret_ccrp IN (0, 1)),
	bombs_ccrp INTEGER NOT NULL CHECK (bombs_ccrp IN (0, 1)),
	rocket_ccrp INTEGER NOT NULL CHECK (rocket_ccrp IN (0, 1)),
	laser_designator INTEGER NOT NULL CHECK (laser_designator IN (0, 1)),
	poi_designator INTEGER NOT NULL CHECK (poi_designator IN (0, 1)),
	poi_memory INTEGER NOT NULL CHECK (poi_memory IN (0, 1)),
	aiming_point_memory INTEGER NOT NULL CHECK (aiming_point_memory IN (0, 1)),
	gyro_sight INTEGER NOT NULL CHECK (gyro_sight IN (0, 1)),

	FOREIGN KEY (unit) REFERENCES units(id) ON DELETE CASCADE
);
CREATE TABLE unit_aerodynamics (
	unit TEXT PRIMARY KEY,
	length INTEGER NOT NULL,
	wingspan INTEGER NOT NULL,
	wing_area INTEGER NOT NULL,
	empty_weight INTEGER NOT NULL,
	max_takeoff_weight INTEGER NOT NULL,
	max_altitude INTEGER NOT NULL,
	turn_time REAL NOT NULL,
	runway_length_req INTEGER NOT NULL,
	max_speed_at_altitude INTEGER NOT NULL,

	FOREIGN KEY (unit) REFERENCES units(id) ON DELETE CASCADE
);
CREATE TABLE unit_presets(
	unit TEXT NOT NULL,
	name TEXT PRIMARY KEY, -- Name usually contains the unit's name

	FOREIGN KEY (unit) REFERENCES units(id) ON DELETE CASCADE
);
CREATE TABLE unit_presets_weapons(
	preset TEXT NOT NULL,
	weapon TEXT NOT NULL,
	count INTEGER NOT NULL,

	PRIMARY KEY (preset, weapon),
	FOREIGN KEY (preset) REFERENCES unit_presets(name) ON DELETE CASCADE,
	FOREIGN KEY (weapon) REFERENCES weapons(name)
);
CREATE TABLE unit_customizable_presets_meta(
	unit TEXT PRIMARY KEY,
	max_load INTEGER NOT NULL,
	max_load_left_wing INTEGER NOT NULL,
	max_load_right_wing INTEGER NOT NULL,
	max_disbalance INTEGER NOT NULL,

	FOREIGN KEY (unit) REFERENCES units(id) ON DELETE CASCADE
);
CREATE TABLE unit_customizable_presets_pylons(
	unit TEXT NOT NULL,
	pylon_index INTEGER NOT NULL,
	used_for_disbalance INTEGER NOT NULL CHECK (used_for_disbalance IN (0, 1)), -- Boolean

	PRIMARY KEY (unit, pylon_index),
	FOREIGN KEY (unit) REFERENCES units(id) ON DELETE CASCADE
);
CREATE TABLE unit_customizable_presets_pylons_weapons(
	unit TEXT NOT NULL,
	pylon_index INTEGER NOT NULL,
	weapon TEXT NOT NULL,
	count INTEGER NOT NULL,

	PRIMARY KEY (unit, pylon_index, weapon),
	FOREIGN KEY (unit, pylon_index) REFERENCES unit_customizable_presets_pylons(unit, pylon_index) ON DELETE CASCADE,
	FOREIGN KEY (weapon) REFERENCES weapons(name)
);
CREATE TABLE unit_sensors(
	unit TEXT NOT NULL,
	sensor TEXT NOT NULL,

	PRIMARY KEY (unit, sensor),
	FOREIGN KEY (unit) REFERENCES units(id) ON DELETE CASCADE,
	FOREIGN KEY (sensor) REFERENCES sensors(name) ON DELETE CASCADE
);
-- Localizations
CREATE TABLE unit_localization(
	unit TEXT NOT NULL,
	lang TEXT NOT NULL,
	value TEXT NOT NULL,

	PRIMARY KEY (unit, lang),
	FOREIGN KEY (unit) REFERENCES units(id) ON DELETE CASCADE
);
CREATE TABLE weapon_localization(
	weapon TEXT NOT NULL,
	lang TEXT NOT NULL,
	value TEXT NOT NULL,

	PRIMARY KEY (weapon, lang),
	FOREIGN KEY (weapon) REFERENCES weapons(name) ON DELETE CASCADE
);
CREATE TABLE ammo_localization(
	ammo TEXT NOT NULL,
	lang TEXT NOT NULL,
	value TEXT NOT NULL,

	PRIMARY KEY (ammo, lang)
);
CREATE TABLE explosives_localization(
	explosive TEXT NOT NULL,
	lang TEXT NOT NULL,
	value TEXT NOT NULL,

	PRIMARY KEY (explosive, lang)
);