<?php
require_once PROJECT_ROOT_PATH . "Model/Database.php";
class PlayerModel extends Database
{
    public function getPlayers($intLimit = 20, $userToSearchFor = "abc", $inDatabase = 0)
    {
        $data = $this->select("SELECT * FROM WarThunder.AccessToken WHERE WarThunder.AccessToken.LastRefresh > NOW() LIMIT 1");
		if($data){
			// data returned, use token and user_id from first one
			foreach ($data as $row) {
				$token = $row->Token;
				$userID = $row->UidHint;
			}
			
			// initiate the curl request
			$request = curl_init();
			curl_setopt($request, CURLOPT_URL,WarThunderAPI);
			curl_setopt($request, CURLOPT_POST, 1);
			curl_setopt($request, CURLOPT_HTTPHEADER, array("token: $token","action: cln_find_users_by_nick_prefix_json","User-Agent: wt"));
			curl_setopt($request, CURLOPT_POSTFIELDS,
			  json_encode(array("ignoreCase"=>true, "maxCount"=>$intLimit, "nick"=>$userToSearchFor, "specificAppId"=>1067)));

			// catch the response
			curl_setopt($request, CURLOPT_RETURNTRANSFER, true);

			$response = curl_exec($request);

			curl_close ($request);
			
			$response = json_decode($response, true);
		}
		  
		if(!$response or isset($response['result'])){
			$formatted = null;
		} else {
			$formatted = [];
			$query = "WITH ranked_messages AS (
			  SELECT Users.UserID, Users.Nickname, Icons.IconName, Clans.ClanTag, UNIX_TIMESTAMP(Timestamp) as LastUpdated, ROW_NUMBER() OVER (PARTITION BY UserID ORDER BY Timestamp DESC) AS rn
					FROM WarThunderStats.Users
					INNER JOIN WarThunderStats.GeneralStats
					ON Users.UserID = GeneralStats.UserID
					LEFT JOIN WarThunderStats.Clans
					ON Users.ClanID = Clans.ClanID
					INNER JOIN WarThunderStats.Icons
					ON Users.IconID = Icons.IconID
					WHERE Users.UserID IN (".implode(', ', array_fill(0, count($response), '?')).")
			)
			SELECT UserID, Nickname, IconName, ClanTag, LastUpdated FROM ranked_messages WHERE rn = 1;";
			$this->__construct();
			$data = $this->select($query, array_keys($response));
			foreach ($response as $key => $value) {
				$iconName = Null;
				$clanTag = Null;
				$lastUpdated = Null;
				foreach($data as $entry){
					if($key == $entry->UserID) {
						$iconName = $entry->IconName;
						$clanTag = $entry->ClanTag;
						$lastUpdated = $entry->LastUpdated;
						if ($inDatabase == 1) {
							$formatted[] = [
								"UserID" => $key,
								"Nickname" => $value,
								"IconName" => $iconName,
								"ClanTag" => $clanTag,
								"LastUpdated" => $lastUpdated
							];
						}
					}
				}
				if ($inDatabase == 0) {
					$formatted[] = [
						"UserID" => $key,
						"Nickname" => $value,
						"IconName" => $iconName,
						"ClanTag" => $clanTag,
						"LastUpdated" => $lastUpdated
					];
				}
			}
		}
		
		return $formatted;
    }
	
	public function getPlayer($userId,$timestamp = 0)
    {
		$parameters = [$userId];
		$query = "SELECT Users.UserID, Users.Nickname, UNIX_TIMESTAMP(Users.LastDay) as LastDay, UNIX_TIMESTAMP(Users.RegisterDay) as RegisterDay, GeneralStats.Experience, GeneralStats.ExperienceConverted, GeneralStats.NumberOfEliteUnits as SpadedVehicles, COALESCE(Titles.TitleNameHumanReadable, Titles.TitleName) as TitleName, Icons.IconName, Clans.ClanName, Clans.ClanTag, ClanRoles.ClanMemberRoleName as ClanRole, Users.PenaltyStatus, UNIX_TIMESTAMP(Timestamp) as LastUpdated 
		FROM WarThunderStats.Users
		INNER JOIN WarThunderStats.GeneralStats
		ON Users.UserID = GeneralStats.UserID
		LEFT JOIN WarThunderStats.Clans
		ON Users.ClanID = Clans.ClanID
		INNER JOIN WarThunderStats.Icons
		ON Users.IconID = Icons.IconID
		INNER JOIN WarThunderStats.Titles
		ON Users.SelectedTitleID = Titles.TitleID
		LEFT JOIN WarThunderStats.ClanRoles
		ON Users.ClanMemberRoleID = ClanRoles.ClanMemberRoleID
		WHERE Users.UserID = ?";
		// Add filter to query depending on if the timestamp has been set
		if($timestamp == 0) {
			$query = $query . " ORDER BY Timestamp DESC LIMIT 1";
		} else {
			$query = $query . " AND Timestamp = FROM_UNIXTIME(?) ORDER BY Timestamp DESC LIMIT 1";
			array_push($parameters, $timestamp);
		}
		
		// execute query
		$data = $this->select($query, $parameters);
		
		if($data){
			
			// Get the amount of golden eagles that is estimated to have been spent
			$this->__construct();
			$parameters = [$userId];
			$query = "SELECT 
				CAST(sum(cost.VehicleCost) as integer) as GoldVehicleCost,
				cost.Timestamp as Timestamp
			from (
				select 
					gold.VehicleCost,
					VehicleInformation.VehicleID,
					ModificationStatusPerUser.Timestamp
				FROM WarThunderStats.ModificationStatusPerUser
				LEFT OUTER JOIN WarThunderStats.VehicleStats
				ON ModificationStatusPerUser.VehicleID = VehicleStats.VehicleID AND ModificationStatusPerUser.UserID = VehicleStats.UserID AND ModificationStatusPerUser.Timestamp = VehicleStats.Timestamp
				LEFT OUTER JOIN WarThunderStats.VehicleInformation
				ON ModificationStatusPerUser.VehicleID = VehicleInformation.VehicleID
				LEFT OUTER JOIN WarThunderStats.VehicleCost as gold
				ON VehicleInformation.VehicleCostGoldID = gold.VehicleCostID
				WHERE ModificationStatusPerUser.UserID = ? AND VehicleInformation.Clan = 0";
			// Add filter to query depending on if the timestamp has been set
			if($timestamp == 0) {
				$query = $query . " AND ModificationStatusPerUser.Timestamp IN (SELECT * from (SELECT Timestamp FROM WarThunderStats.GeneralStats WHERE UserID = ? ORDER BY Timestamp DESC LIMIT 1) as temp)";
				array_push($parameters, $userId);
			} else {
				$query = $query . " AND ModificationStatusPerUser.Timestamp = FROM_UNIXTIME(?)";
				array_push($parameters, $timestamp);
			}
			$query = $query . "GROUP BY ModificationStatusPerUser.VehicleID, ModificationStatusPerUser.Timestamp
			) as cost 
			GROUP BY cost.Timestamp";
			
			$estimatedGoldenEagleCost = $this->select($query, $parameters);
			
			if($estimatedGoldenEagleCost){
				foreach($estimatedGoldenEagleCost as $estimatedGoldCost){
					$data[0]->{"EstimatedGoldCost"} = $estimatedGoldCost->GoldVehicleCost;
				}
			}
			
			if(!property_exists($data[0], "Vehicles")){
				$data[0]->{"Vehicles"} = new stdClass();
			}
			
			// Get the amount of vehicles per country and per vehicle type
			$this->__construct();
			$parameters = [$userId];
			$query = "SELECT COUNT(IF(ModificationStatusPerUser.ModificationStatusID = 0, 1, NULL)) AS ModificationStatus0, COUNT(IF(ModificationStatusPerUser.ModificationStatusID = 1, 1, NULL)) AS ModificationStatus1, COUNT(IF(ModificationStatusPerUser.ModificationStatusID = 2, 1, NULL)) AS ModificationStatus2, COUNT(IF(VehicleInformation.Premium = 1, 1, NULL)) AS PremiumVehicles, COUNT(IF(VehicleInformation.Gift = 1, 1, NULL)) AS GiftVehicles, COUNT(IF(VehicleInformation.Event = 1, 1, NULL)) AS EventVehicles, COUNT(IF(VehicleInformation.Clan = 1, 1, NULL)) AS ClanVehicles, COUNT(VehicleInformation.VehicleID) AS TotalVehicles, COALESCE(Country.NationNameHumanReadable, Country.NationName) as NationName, VehicleType.VehicleTypeName
			FROM WarThunderStats.ModificationStatusPerUser
			LEFT OUTER JOIN WarThunderStats.VehicleInformation
			ON ModificationStatusPerUser.VehicleID = VehicleInformation.VehicleID
			RIGHT OUTER JOIN WarThunderStats.Country
			ON VehicleInformation.VehicleCountryID = Country.CountryID
			LEFT OUTER JOIN WarThunderStats.VehicleType
			ON VehicleInformation.VehicleTypeID = VehicleType.VehicleTypeID
			WHERE ModificationStatusPerUser.UserID = ?";
			// Add filter to query depending on if the timestamp has been set
			if($timestamp == 0) {
				$query = $query . " AND ModificationStatusPerUser.Timestamp IN (SELECT * from (SELECT Timestamp FROM WarThunderStats.GeneralStats WHERE UserID = ? ORDER BY Timestamp DESC LIMIT 1) as temp)";
				array_push($parameters, $userId);
			} else {
				$query = $query . " AND ModificationStatusPerUser.Timestamp = FROM_UNIXTIME(?)";
				array_push($parameters, $timestamp);
			}
			$query = $query . "GROUP BY NationName, VehicleTypeName;";
			$vehicleCountsGroupedByTypeAndCountry = $this->select($query, $parameters);
			
			if($vehicleCountsGroupedByTypeAndCountry){
				foreach($vehicleCountsGroupedByTypeAndCountry as $vehicleCountGroupedByTypeAndCountry){
					if(!property_exists($data[0]->{"Vehicles"}, $vehicleCountGroupedByTypeAndCountry->NationName)){
						$data[0]->{"Vehicles"}->{$vehicleCountGroupedByTypeAndCountry->NationName} = new stdClass();
					}
					if ($vehicleCountGroupedByTypeAndCountry->VehicleTypeName != null){
						if(!property_exists($data[0]->{"Vehicles"}->{$vehicleCountGroupedByTypeAndCountry->NationName}, $vehicleCountGroupedByTypeAndCountry->VehicleTypeName)){
							$data[0]->{"Vehicles"}->{$vehicleCountGroupedByTypeAndCountry->NationName}->{$vehicleCountGroupedByTypeAndCountry->VehicleTypeName} = new stdClass();
						}
						$data[0]->{"Vehicles"}->{$vehicleCountGroupedByTypeAndCountry->NationName}->{$vehicleCountGroupedByTypeAndCountry->VehicleTypeName}->{"ModificationStatus0"} = $vehicleCountGroupedByTypeAndCountry->ModificationStatus0;
						$data[0]->{"Vehicles"}->{$vehicleCountGroupedByTypeAndCountry->NationName}->{$vehicleCountGroupedByTypeAndCountry->VehicleTypeName}->{"ModificationStatus1"} = $vehicleCountGroupedByTypeAndCountry->ModificationStatus1;
						$data[0]->{"Vehicles"}->{$vehicleCountGroupedByTypeAndCountry->NationName}->{$vehicleCountGroupedByTypeAndCountry->VehicleTypeName}->{"ModificationStatus2"} = $vehicleCountGroupedByTypeAndCountry->ModificationStatus2;
						$data[0]->{"Vehicles"}->{$vehicleCountGroupedByTypeAndCountry->NationName}->{$vehicleCountGroupedByTypeAndCountry->VehicleTypeName}->{"PremiumVehicles"} = $vehicleCountGroupedByTypeAndCountry->PremiumVehicles;
						$data[0]->{"Vehicles"}->{$vehicleCountGroupedByTypeAndCountry->NationName}->{$vehicleCountGroupedByTypeAndCountry->VehicleTypeName}->{"GiftVehicles"} = $vehicleCountGroupedByTypeAndCountry->GiftVehicles;
						$data[0]->{"Vehicles"}->{$vehicleCountGroupedByTypeAndCountry->NationName}->{$vehicleCountGroupedByTypeAndCountry->VehicleTypeName}->{"EventVehicles"} = $vehicleCountGroupedByTypeAndCountry->EventVehicles;
						$data[0]->{"Vehicles"}->{$vehicleCountGroupedByTypeAndCountry->NationName}->{$vehicleCountGroupedByTypeAndCountry->VehicleTypeName}->{"ClanVehicles"} = $vehicleCountGroupedByTypeAndCountry->ClanVehicles;
						$data[0]->{"Vehicles"}->{$vehicleCountGroupedByTypeAndCountry->NationName}->{$vehicleCountGroupedByTypeAndCountry->VehicleTypeName}->{"TotalVehicles"} = $vehicleCountGroupedByTypeAndCountry->TotalVehicles;
					}
				}
			}
			
			// Get the amount of missions played per gamemode and gametype
			$this->__construct();
			$parameters = [$userId];
			$query = "SELECT MissionsCompleted, Victories, GamemodeName, GameTypeName
			FROM WarThunderStats.SummaryStatsGames
			LEFT OUTER JOIN WarThunderStats.Gamemode
			ON SummaryStatsGames.GamemodeID = Gamemode.GamemodeID
			LEFT OUTER JOIN WarThunderStats.GameType
			ON SummaryStatsGames.GameTypeID = GameType.GameTypeID
			WHERE SummaryStatsGames.UserID = ?";
			// Add filter to query depending on if the timestamp has been set
			if($timestamp == 0) {
				$query = $query . " AND SummaryStatsGames.Timestamp IN (SELECT * from (SELECT Timestamp FROM WarThunderStats.GeneralStats WHERE UserID = ? ORDER BY Timestamp DESC LIMIT 1) as temp)";
				array_push($parameters, $userId);
			} else {
				$query = $query . " AND SummaryStatsGames.Timestamp = FROM_UNIXTIME(?)";
				array_push($parameters, $timestamp);
			}
			$missionsPlayed = $this->select($query, $parameters);
			
			if(!property_exists($data[0], "MissionsPlayed")){
				$data[0]->{"MissionsPlayed"} = new stdClass();
			}
			if($missionsPlayed){
				foreach($missionsPlayed as $missionPlayed){
					if(!property_exists($data[0]->{"MissionsPlayed"}, $missionPlayed->GameTypeName)){
						$data[0]->{"MissionsPlayed"}->{$missionPlayed->GameTypeName} = new stdClass();
					}
					if(!property_exists($data[0]->{"MissionsPlayed"}->{$missionPlayed->GameTypeName}, $missionPlayed->GamemodeName)){
						$data[0]->{"MissionsPlayed"}->{$missionPlayed->GameTypeName}->{$missionPlayed->GamemodeName} = new stdClass();
					}
					$data[0]->{"MissionsPlayed"}->{$missionPlayed->GameTypeName}->{$missionPlayed->GamemodeName}->{"MissionsCompleted"} = $missionPlayed->MissionsCompleted;
					$data[0]->{"MissionsPlayed"}->{$missionPlayed->GameTypeName}->{$missionPlayed->GamemodeName}->{"Victories"} = $missionPlayed->Victories;
				}
			}
			
			// Get the amount of kills, spawns and timeplayed played per gamemode, gametype and vehicletype
			$this->__construct();
			$parameters = [$userId];
			$query = "SELECT TimePlayed, AirKills, GroundKills, NavalKills, Spawns, AirKillsAI, GroundKillsAI, NavalKillsAI, AirKillsBot, GroundKillsBot, NavalKillsBot, GamemodeName, GameTypeName, VehicleClassName
			FROM WarThunderStats.SummaryStats
			LEFT OUTER JOIN WarThunderStats.Gamemode
			ON SummaryStats.GamemodeID = Gamemode.GamemodeID
			LEFT OUTER JOIN WarThunderStats.GameType
			ON SummaryStats.GameTypeID = GameType.GameTypeID
			LEFT OUTER JOIN WarThunderStats.VehicleClass
			ON SummaryStats.VehicleClassID = VehicleClass.VehicleClassID
			WHERE SummaryStats.UserID = ?";
			// Add filter to query depending on if the timestamp has been set
			if($timestamp == 0) {
				$query = $query . " AND SummaryStats.Timestamp IN (SELECT * from (SELECT Timestamp FROM WarThunderStats.GeneralStats WHERE UserID = ? ORDER BY Timestamp DESC LIMIT 1) as temp)";
				array_push($parameters, $userId);
			} else {
				$query = $query . " AND SummaryStats.Timestamp = FROM_UNIXTIME(?)";
				array_push($parameters, $timestamp);
			}
			$missionStats = $this->select($query, $parameters);
			
			if(!property_exists($data[0], "MissionsPlayed")){
				$data[0]->{"MissionsPlayed"} = new stdClass();
			}
			if($missionsPlayed){
				foreach($missionStats as $missionStat){
					if(!property_exists($data[0]->{"MissionsPlayed"}, $missionStat->GameTypeName)){
						$data[0]->{"MissionsPlayed"}->{$missionStat->GameTypeName} = new stdClass();
					}
					if(!property_exists($data[0]->{"MissionsPlayed"}->{$missionStat->GameTypeName}, $missionStat->GamemodeName)){
						$data[0]->{"MissionsPlayed"}->{$missionStat->GameTypeName}->{$missionStat->GamemodeName} = new stdClass();
					}
					if(!property_exists($data[0]->{"MissionsPlayed"}->{$missionStat->GameTypeName}->{$missionStat->GamemodeName}, $missionStat->VehicleClassName)){
						$data[0]->{"MissionsPlayed"}->{$missionStat->GameTypeName}->{$missionStat->GamemodeName}->{$missionStat->VehicleClassName} = new stdClass();
					}
					$data[0]->{"MissionsPlayed"}->{$missionStat->GameTypeName}->{$missionStat->GamemodeName}->{$missionStat->VehicleClassName}->{"TimePlayed"} = $missionStat->TimePlayed;
					$data[0]->{"MissionsPlayed"}->{$missionStat->GameTypeName}->{$missionStat->GamemodeName}->{$missionStat->VehicleClassName}->{"Spawns"} = $missionStat->Spawns;
					$data[0]->{"MissionsPlayed"}->{$missionStat->GameTypeName}->{$missionStat->GamemodeName}->{$missionStat->VehicleClassName}->{"AirKills"} = $missionStat->AirKills;
					$data[0]->{"MissionsPlayed"}->{$missionStat->GameTypeName}->{$missionStat->GamemodeName}->{$missionStat->VehicleClassName}->{"GroundKills"} = $missionStat->GroundKills;
					$data[0]->{"MissionsPlayed"}->{$missionStat->GameTypeName}->{$missionStat->GamemodeName}->{$missionStat->VehicleClassName}->{"NavalKills"} = $missionStat->NavalKills;
					$data[0]->{"MissionsPlayed"}->{$missionStat->GameTypeName}->{$missionStat->GamemodeName}->{$missionStat->VehicleClassName}->{"AirKillsAI"} = $missionStat->AirKillsAI;
					$data[0]->{"MissionsPlayed"}->{$missionStat->GameTypeName}->{$missionStat->GamemodeName}->{$missionStat->VehicleClassName}->{"GroundKillsAI"} = $missionStat->GroundKillsAI;
					$data[0]->{"MissionsPlayed"}->{$missionStat->GameTypeName}->{$missionStat->GamemodeName}->{$missionStat->VehicleClassName}->{"NavalKillsAI"} = $missionStat->NavalKillsAI;
					$data[0]->{"MissionsPlayed"}->{$missionStat->GameTypeName}->{$missionStat->GamemodeName}->{$missionStat->VehicleClassName}->{"AirKillsBot"} = $missionStat->AirKillsBot;
					$data[0]->{"MissionsPlayed"}->{$missionStat->GameTypeName}->{$missionStat->GamemodeName}->{$missionStat->VehicleClassName}->{"GroundKillsBot"} = $missionStat->GroundKillsBot;
					$data[0]->{"MissionsPlayed"}->{$missionStat->GameTypeName}->{$missionStat->GamemodeName}->{$missionStat->VehicleClassName}->{"NavalKillsBot"} = $missionStat->NavalKillsBot;
				}
			}
			
			// Get the users titles
			$this->__construct();
			$titles = $this->select("SELECT COALESCE(Titles.TitleNameHumanReadable, Titles.TitleName) as TitleName
			FROM WarThunderStats.Users
			INNER JOIN WarThunderStats.TitleCorrelations
			ON Users.UserID = TitleCorrelations.UserID
			INNER JOIN WarThunderStats.Titles
			ON TitleCorrelations.TitleID = Titles.TitleID
			WHERE Users.UserID = ?", [$userId]);
			
			$data[0]->{"Titles"} = [];
			if($titles){
				foreach($titles as $title){
					if($title->TitleName != null){
						array_push($data[0]->{"Titles"}, $title->TitleName);
					}
				}
			}
			
			// Get the users timestamps
			$this->__construct();
			$datesWithData = $this->select("SELECT UNIX_TIMESTAMP(GeneralStats.Timestamp) as timestamp
			FROM WarThunderStats.GeneralStats
			WHERE GeneralStats.UserID = ?
			ORDER BY timestamp desc", [$userId]);
			
			$data[0]->{"Timestamps"} = [];
			if($datesWithData){
				foreach($datesWithData as $dateWithData){
					if($dateWithData->timestamp != null){
						array_push($data[0]->{"Timestamps"}, $dateWithData->timestamp);
					}
				}
			}
			
			$result = $data;
		} else {
			$this->__construct();
			$result = $this->getPlayers(20,$userId);
		}
		
		return $result;
    }
	
	public function updatePlayer($userId)
    {
		$data = $this->select("SELECT * FROM WarThunder.UpdateQueue WHERE LastRefresh > DATE_SUB(now(), INTERVAL 7 DAY) AND Status = 1 AND userID = ?", [$userId]);
		if(!$data){
			$this->__construct();
			$update = $this->executeStatement("INSERT INTO `WarThunder`.`UpdateQueue` (`userID`,`Status`) VALUES (? ,'0') ON DUPLICATE KEY UPDATE userID=LAST_INSERT_ID(userID),Status=0", [$userId]);
			$result = [
				"InQueue" => true,
				"Text" => "Added to queue"
			];
			return $result;
		}
		
		$this->__construct();
		$data = $this->select("SELECT * FROM WarThunder.UpdateQueue WHERE LastRefresh < DATE_SUB(now(), INTERVAL 7 DAY) AND Status = 0 AND userID = ?", [$userId]);
		if($data){
			$result = [
				"InQueue" => true,
				"Text" => "Already in queue"
			];
		} else {
			$result = [
				"InQueue" => false,
				"Text" => "Already been refreshed within last 7 days"
			];
		}
		return $result;
    }
	
	public function getPlayerVehicleStats($userId,$timestamp = 0,$country = "",$gamemode = "",$language = "",$vehicleType = "",$minTier = 0,$maxTier = 100000000,$minBattlerating = 0,$maxBattlerating = 100000000,$minVictories = 0,$maxVictories = 100000000,$minDefeats = 0,$maxDefeats = 100000000,$minInSession = 0,$maxInSession = 100000000,$minSpawns = 0,$maxSpawns = 100000000,$minDeaths = 0,$maxDeaths = 100000000,$minGroundKills = 0,$maxGroundKills = 100000000,$minAirKills = 0,$maxAirKills = 100000000,$minNavalKills = 0,$maxNavalKills = 100000000)
    {
		// Create basic parameters and query
		$parameters = [$userId];
		$query = "SELECT ModificationStatusPerUser.VehicleID, VehicleInformation.VehicleName as VehicleIdentifiyingName, COALESCE(VehicleNames.ShopName, VehicleInformation.VehicleName) as VehicleName, FullName as VehicleFullName, ShortName as VehicleShortName, CompressedName as VehicleCompressedName, VehicleType.VehicleTypeName as VehicleType, GROUP_CONCAT(COALESCE(VehicleTags.VehicleTagNameHumanReadable,VehicleTags.VehicleTagName)) as Tags, COALESCE(Country.NationNameHumanReadable, Country.NationName) as NationName, OperatorCountry.NationName as OperatorCountry, Tier.TierID as Tier, Tier.TierRoman, Battlerating.BattleratingValue as Battlerating, VehicleInformation.Premium, VehicleInformation.Gift, VehicleInformation.Event, VehicleInformation.Clan, ModificationStatus.ModificationStatusID as ModificationStatus, ModificationStatus.ModificicationStatusText, Gamemode.GamemodeName, COALESCE(VehicleStats.Victories,0) as Victories, COALESCE(VehicleStats.Defeats,0) as Defeats, COALESCE(VehicleStats.WasInLineup,0) as WasInLineup, COALESCE(VehicleStats.Spawns,0) as Spawns, COALESCE(VehicleStats.Deaths,0) as Deaths, COALESCE(VehicleStats.GroundKills,0) as GroundKills, COALESCE(VehicleStats.AirKills,0) as AirKills, COALESCE(VehicleStats.NavalKills,0) as NavalKills
			FROM WarThunderStats.ModificationStatusPerUser
            LEFT OUTER JOIN WarThunderStats.VehicleStats
			ON ModificationStatusPerUser.VehicleID = VehicleStats.VehicleID AND ModificationStatusPerUser.UserID = VehicleStats.UserID AND ModificationStatusPerUser.Timestamp = VehicleStats.Timestamp
            LEFT OUTER JOIN WarThunderStats.VehicleInformation
			ON ModificationStatusPerUser.VehicleID = VehicleInformation.VehicleID
            LEFT OUTER JOIN WarThunderStats.ModificationStatus
			ON ModificationStatusPerUser.ModificationStatusID = ModificationStatus.ModificationStatusID
            LEFT OUTER JOIN WarThunderStats.Gamemode
			ON VehicleStats.GamemodeID = Gamemode.GamemodeID
            LEFT OUTER JOIN WarThunderStats.Country
			ON VehicleInformation.VehicleCountryID = Country.CountryID
			LEFT OUTER JOIN WarThunderStats.Country as OperatorCountry
			ON VehicleInformation.OperatorCountryID = OperatorCountry.CountryID
            LEFT OUTER JOIN WarThunderStats.VehicleNames
			ON ModificationStatusPerUser.VehicleID = VehicleNames.VehicleID
            LEFT OUTER JOIN WarThunderStats.Languages
			ON VehicleNames.LanguageID = Languages.LanguageID
            LEFT OUTER JOIN WarThunderStats.Tier
			ON VehicleInformation.VehicleTierID = Tier.TierID
            LEFT OUTER JOIN WarThunderStats.BattleratingCorrelations
			ON VehicleInformation.VehicleID = BattleratingCorrelations.VehicleID AND COALESCE(Gamemode.GamemodeID,1) = BattleratingCorrelations.GamemodeID
            LEFT OUTER JOIN WarThunderStats.Battlerating
			ON BattleratingCorrelations.BatleratingID = Battlerating.BatleratingID
            LEFT OUTER JOIN WarThunderStats.VehicleType
			ON VehicleInformation.VehicleTypeID = VehicleType.VehicleTypeID
			LEFT OUTER JOIN WarThunderStats.VehicleTagCorrelations
			ON VehicleInformation.VehicleID = VehicleTagCorrelations.VehicleID
            LEFT OUTER JOIN WarThunderStats.VehicleTags
			ON VehicleTagCorrelations.VehicleTagID = VehicleTags.VehicleTagID
			WHERE ModificationStatusPerUser.UserID = ?";
		// Add filter to query depending on if the timestamp has been set
		if($timestamp == 0) {
			$query = $query . " AND ModificationStatusPerUser.Timestamp IN (SELECT * from (SELECT Timestamp FROM WarThunderStats.GeneralStats WHERE UserID = ? ORDER BY Timestamp DESC LIMIT 1) as temp)";
			array_push($parameters, $userId);
		} else {
			$query = $query . " AND ModificationStatusPerUser.Timestamp = FROM_UNIXTIME(?)";
			array_push($parameters, $timestamp);
		}
		// Add filter to query depending on if the country has been set
		if($country != "") {
			$query = $query . " AND (Country.NationNameHumanReadable = ? OR Country.NationName = ?)";
			array_push($parameters, $country);
			array_push($parameters, $country);
		}
		// Add filter to query depending on if the gamemode has been set
		if($gamemode != "") {
			$query = $query . " AND Gamemode.GamemodeName = ?";
			array_push($parameters, $gamemode);
		}
		// Add filter to query depending on if the language has been set
		if($language != "") {
			$query = $query . " AND Languages.Language = ?";
			array_push($parameters, $language);
		} else {
			$query = $query . " AND Languages.Language = ?";
			array_push($parameters, "English");
		}
		// Add filter to query depending on if the vehicleType has been set
		if($vehicleType != "") {
			$query = $query . " AND VehicleType.VehicleTypeName = ?";
			array_push($parameters, $vehicleType);
		}
		
		// add filters based on max / min values
		if($minTier != 0 || $maxTier != 100000000) {
			$query = $query . " AND (Tier.TierID >= ? AND Tier.TierID <= ?)";
			array_push($parameters, $minTier);
			array_push($parameters, $maxTier);
		}
		if($minBattlerating != 0 || $maxBattlerating != 100000000) {
			$query = $query . " AND (Battlerating.BattleratingValue >= ? AND Battlerating.BattleratingValue <= ?)";
			array_push($parameters, $minBattlerating);
			array_push($parameters, $maxBattlerating);
		}
		if($minVictories != 0 || $maxVictories != 100000000) {
			$query = $query . " AND (COALESCE(VehicleStats.Victories,0) >= ? AND COALESCE(VehicleStats.Victories,0) <= ?)";
			array_push($parameters, $minVictories);
			array_push($parameters, $maxVictories);
		}
		if($minDefeats != 0 || $maxDefeats != 100000000) {
			$query = $query . " AND (COALESCE(VehicleStats.Defeats,0) >= ? AND COALESCE(VehicleStats.Defeats,0) <= ?)";
			array_push($parameters, $minDefeats);
			array_push($parameters, $maxDefeats);
		}
		if($minInSession != 0 || $maxInSession != 100000000) {
			$query = $query . " AND (COALESCE(VehicleStats.WasInLineup,0) >= ? AND COALESCE(VehicleStats.WasInLineup,0) <= ?)";
			array_push($parameters, $minInSession);
			array_push($parameters, $maxInSession);
		}
		if($minSpawns != 0 || $maxSpawns != 100000000) {
			$query = $query . " AND (COALESCE(VehicleStats.Spawns,0) >= ? AND COALESCE(VehicleStats.Spawns,0) <= ?)";
			array_push($parameters, $minSpawns);
			array_push($parameters, $maxSpawns);
		}
		if($minDeaths != 0 || $maxDeaths != 100000000) {
			$query = $query . " AND (COALESCE(VehicleStats.Deaths,0) >= ? AND COALESCE(VehicleStats.Deaths,0) <= ?)";
			array_push($parameters, $minDeaths);
			array_push($parameters, $maxDeaths);
		}
		if($minGroundKills != 0 || $maxGroundKills != 100000000) {
			$query = $query . " AND (COALESCE(VehicleStats.GroundKills,0) >= ? AND COALESCE(VehicleStats.GroundKills,0) <= ?)";
			array_push($parameters, $minGroundKills);
			array_push($parameters, $maxGroundKills);
		}
		if($minAirKills != 0 || $maxAirKills != 100000000) {
			$query = $query . " AND (COALESCE(VehicleStats.AirKills,0) >= ? AND COALESCE(VehicleStats.AirKills,0) <= ?)";
			array_push($parameters, $minAirKills);
			array_push($parameters, $maxAirKills);
		}
		if($minNavalKills != 0 || $maxNavalKills != 100000000) {
			$query = $query . " AND (COALESCE(VehicleStats.NavalKills,0) >= ? AND COALESCE(VehicleStats.NavalKills,0) <= ?)";
			array_push($parameters, $minNavalKills);
			array_push($parameters, $maxNavalKills);
		}
		
		
		$query = $query . " GROUP BY VehicleID, GamemodeName";
		
		// execute query
		$data = $this->select($query, $parameters);
		
		foreach($data as $entry){
			if ($entry->Tags != null) {
				$entry->Tags = explode(",",$entry->Tags);
			}
		}
		
		$result = $data;
		
		return $result;
    }
	
	public function getTitlesByRarity()
    {
		// Create basic parameters and query
		$parameters = [];
		$query = "SELECT TitleCorrelations.TitleID, (count(UserID) / c.users) as percentageOfPlayersWithTitle, TitleName as TitleIdentifier, COALESCE(TitleName, TitleNameHumanReadable) as TitleName
			FROM WarThunderStats.TitleCorrelations 
            CROSS JOIN (SELECT count(DISTINCT UserID) as users FROM WarThunderStats.GeneralStats) c
			Join WarThunderStats.Titles on TitleCorrelations.TitleID = Titles.TitleID
			GROUP BY TitleCorrelations.TitleID
			ORDER BY percentageOfPlayersWithTitle ASC, TitleName ASC;";
		
		// execute query
		$data = $this->select($query, $parameters);
		
		$result = $data;
		
		return $result;
    }
	
	public function playersWithTitle($titleIdentifier)
    {
		// Create basic parameters and query
		$parameters = [$titleIdentifier];
		$query = "SELECT TitleCorrelations.UserID as UserID, Nickname, IconName
			FROM WarThunderStats.TitleCorrelations 
			LEFT JOIN WarThunderStats.GeneralStats on TitleCorrelations.UserID = GeneralStats.UserID
			INNER JOIN
				(SELECT UserID, max(Timestamp) as Timestamp
				FROM WarThunderStats.GeneralStats
				GROUP BY UserID) grouped on grouped.UserID = GeneralStats.UserID AND grouped.Timestamp = GeneralStats.Timestamp
			LEFT Join WarThunderStats.Titles on TitleCorrelations.TitleID = Titles.TitleID
			LEFT Join WarThunderStats.Users on TitleCorrelations.UserID = Users.UserID
			LEFT JOIN WarThunderStats.Icons on Users.IconID = Icons.IconID
			WHERE Titles.TitleName = ?
			ORDER BY GeneralStats.Experience DESC
			LIMIT 20;";
		
		// execute query
		$data = $this->select($query, $parameters);
		
		$result = $data;
		
		return $result;
    }
}
?>