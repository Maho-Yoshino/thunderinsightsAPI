<?php
require_once PROJECT_ROOT_PATH . "Model/Database.php";
class VehicleModel extends Database
{	
	public function getPlayerVehicleFilters()
    {
		// Create basic parameters and query
		$parameters = [];
		$query = "SELECT distinct(coalesce(NationNameHumanReadable,NationName)) as Country FROM WarThunderStats.Country 
		INNER JOIN WarThunderStats.VehicleInformation
		ON Country.CountryID = VehicleInformation.VehicleCountryID;";
		// execute query
		$countries = $this->select($query, $parameters);
		
		$this->__construct();
		$query = "SELECT GamemodeName FROM WarThunderStats.Gamemode;";
		// execute query
		$gamemodes = $this->select($query, $parameters);
		
		$this->__construct();
		$query = "SELECT Language FROM WarThunderStats.Languages;";
		// execute query
		$languages = $this->select($query, $parameters);
		
		$this->__construct();
		$query = "SELECT VehicleTypeName FROM WarThunderStats.VehicleType;";
		// execute query
		$vehicleTypes = $this->select($query, $parameters);
		
		$data = (object)[];
		$data->Country = array_column($countries,'Country');
		$data->Gamemode = array_column($gamemodes,'GamemodeName');
		$data->Language = array_column($languages,'Language');
		$data->VehicleType = array_column($vehicleTypes,'VehicleTypeName');
		
		$result = $data;
		
		return $result;
    }
	
	public function getVehicles($language = "")
	{
		// Create basic parameters and query
		$parameters = [];
		$query = "SELECT VehicleInformation.VehicleID, VehicleTierID as Tier, VehicleInformation.VehicleName as VehicleIdentifiyingName, COALESCE(VehicleNames.ShopName, VehicleInformation.VehicleName) as VehicleName, FullName as VehicleFullName, ShortName as VehicleShortName, CompressedName as VehicleCompressedName, COALESCE(Country.NationNameHumanReadable, Country.NationName) as NationName, OperatorCountry.NationNameHumanReadable as OperatorName, OperatorCountry.NationName as OperatorCountry
			FROM WarThunderStats.VehicleInformation
			LEFT OUTER JOIN WarThunderStats.VehicleNames
			ON VehicleInformation.VehicleID = VehicleNames.VehicleID
			LEFT OUTER JOIN WarThunderStats.Languages
			ON VehicleNames.LanguageID = Languages.LanguageID
			LEFT OUTER JOIN WarThunderStats.Country
			ON VehicleInformation.VehicleCountryID = Country.CountryID
			LEFT OUTER JOIN WarThunderStats.Country as OperatorCountry
			ON VehicleInformation.OperatorCountryID = OperatorCountry.CountryID
			WHERE 1 = 1";
		// Add filter to query depending on if the language has been set
		if($language != "") {
			$query = $query . " AND Languages.Language = ?";
			array_push($parameters, $language);
		} else {
			$query = $query . " AND Languages.Language = ?";
			array_push($parameters, "English");
		}
		
		// execute query
		$data = $this->select($query, $parameters);
		
		$result = $data;
		
		return $result;
	}
	
	public function getVehicle($VehicleIdentifier = "",$gamemode = "",$gameUpdateID = "",$language = "")
	{
		// Create basic parameters and query
		$parameters = [$VehicleIdentifier];
		$query = "SELECT 
			COALESCE(VehicleOwnerCounts.UniqueOwners,0) as OwnedByUniqueUsers, 
			COALESCE(PlayedByUniqueUsers,0) as PlayedByUniqueUsers, 
			sum(COALESCE(Spawns,0)) as Spawns, 
			sum(COALESCE(Deaths,0)) as Deaths, 
			sum(COALESCE(ExperienceEarned,0)) as ExperienceEarned, 
			sum(COALESCE(SilverLionsEarned,0)) as SilverLionsEarned, 
			sum(COALESCE(GroundKills,0)) as GroundKills, 
			sum(COALESCE(AirKills,0)) as AirKills, 
			sum(COALESCE(NavalKills,0)) as NavalKills, 
			sum(COALESCE(WasInLineup,0)) as WasInLineup, 
			sum(COALESCE(Defeats,0)) as Defeats, 
			sum(COALESCE(Victories,0)) as Victories, 
			UpdateTitle, 
			UpdateVersion, 
			UpdateDate, 
			UpdateEOLDate, 
			VehicleInformation.VehicleID as VehicleID,
			VehicleName as VehicleIdentifiyingName,
			COALESCE(VehicleNames.ShopName, VehicleInformation.VehicleName) as VehicleName,
			FullName as VehicleFullName,
			ShortName as VehicleShortName,
			CompressedName as VehicleCompressedName,
			VehicleType.VehicleTypeName as VehicleType,
			GROUP_CONCAT(DISTINCT(COALESCE(VehicleTags.VehicleTagNameHumanReadable,VehicleTags.VehicleTagName))) as Tags,
			Country.NationName as Country,
			COALESCE(Country.NationNameHumanReadable, Country.NationName) as NationName,
			Operator.NationName as OperatorCountry,
			COALESCE(Operator.NationNameHumanReadable, Operator.NationName) as OperatorName,
			Tier.TierID as Tier, 
			Tier.TierRoman as TierRoman,
			GROUP_CONCAT(DISTINCT(Battlerating.BattleratingValue)) as Battlerating,
			VehicleInformation.Premium as Premium, 
			VehicleInformation.Gift as Gift, 
			VehicleInformation.Event as Event,
			VehicleInformation.Clan as Clan,
			GROUP_CONCAT(DISTINCT(Gamemode.GamemodeName)) as GamemodeName,
			VehicleCost.VehicleCost as SilverCost,
			Gold.VehicleCost as GoldCost,
			VehicleExperienceRequirement.VehicleExperience as ExperienceRequired
			FROM WarThunderStats.VehicleStatsByUpdate
			LEFT OUTER JOIN WarThunderStats.Updates ON VehicleStatsByUpdate.UpdateID = Updates.UpdateID
			LEFT OUTER JOIN WarThunderStats.VehicleInformation ON VehicleStatsByUpdate.VehicleID = VehicleInformation.VehicleID
			LEFT OUTER JOIN WarThunderStats.VehicleNames ON VehicleStatsByUpdate.VehicleID = VehicleNames.VehicleID
			LEFT OUTER JOIN WarThunderStats.Gamemode ON VehicleStatsByUpdate.GamemodeID = Gamemode.GamemodeID
			LEFT OUTER JOIN WarThunderStats.Country ON VehicleInformation.VehicleCountryID = Country.CountryID
			LEFT OUTER JOIN WarThunderStats.VehicleType ON VehicleInformation.VehicleTypeID = VehicleType.VehicleTypeID
			LEFT OUTER JOIN WarThunderStats.Tier ON VehicleInformation.VehicleTierID = Tier.TierID
			LEFT OUTER JOIN WarThunderStats.VehicleExperienceRequirement ON VehicleInformation.VehicleExperienceID = VehicleExperienceRequirement.VehicleExperienceID
			LEFT OUTER JOIN WarThunderStats.VehicleCost ON VehicleInformation.VehicleCostID = VehicleCost.VehicleCostID
			LEFT OUTER JOIN WarThunderStats.VehicleCost as Gold ON VehicleInformation.VehicleCostGoldID = Gold.VehicleCostID
			LEFT OUTER JOIN WarThunderStats.Country as Operator ON VehicleInformation.OperatorCountryID = Operator.CountryID
			LEFT OUTER JOIN WarThunderStats.VehicleTagCorrelations ON VehicleInformation.VehicleID = VehicleTagCorrelations.VehicleID
			LEFT OUTER JOIN WarThunderStats.VehicleTags ON VehicleTagCorrelations.VehicleTagID = VehicleTags.VehicleTagID
			LEFT OUTER JOIN WarThunderStats.BattleratingCorrelations ON VehicleInformation.VehicleID = BattleratingCorrelations.VehicleID AND COALESCE(Gamemode.GamemodeID,1) = BattleratingCorrelations.GamemodeID
			LEFT OUTER JOIN WarThunderStats.Battlerating ON BattleratingCorrelations.BatleratingID = Battlerating.BatleratingID
			LEFT OUTER JOIN WarThunderStats.Languages ON VehicleNames.LanguageID = Languages.LanguageID
			LEFT OUTER JOIN WarThunderStats.VehicleOwnerCounts ON VehicleInformation.VehicleID = VehicleOwnerCounts.VehicleID
			WHERE VehicleName = ?";
			
		// Add filter to query depending on if the gamemode has been set
		if($gamemode != "") {
			$query = $query . " AND Gamemode.GamemodeName = ?";
			array_push($parameters, $gamemode);
		} else {
			$query = $query . " AND Gamemode.GamemodeName = ?";
			array_push($parameters, "realistic");
		}
		// Add filter to query depending on if the gamemode has been set
		if($gameUpdateID != "") {
			$query = $query . " AND Updates.UpdateID = ?";
			array_push($parameters, $gameUpdateID);
		} else {
			$query = $query . " AND Updates.UpdateID = ?";
			array_push($parameters, "0");
		}
		// Add filter to query depending on if the language has been set
		if($language != "") {
			$query = $query . " AND Languages.Language = ?";
			array_push($parameters, $language);
		} else {
			$query = $query . " AND Languages.Language = ?";
			array_push($parameters, "English");
		}
		
		$query = $query . " GROUP BY VehicleStatsByUpdate.VehicleID, VehicleStatsByUpdate.UpdateID, VehicleStatsByUpdate.GamemodeID;";
		
		// execute query
		$data = $this->select($query, $parameters);
		
		$result = $data;
		
		return $result;
	}
	
	public function getVehicleStatsByUpdates($VehicleIdentifier = "",$gamemode = "")
	{
		// Create basic parameters and query
		$parameters = [$VehicleIdentifier];
		$query = "SELECT 
			COALESCE(PlayedByUniqueUsers,0) as PlayedByUniqueUsers, 
			sum(COALESCE(Spawns,0)) as Spawns, 
			sum(COALESCE(Deaths,0)) as Deaths, 
			sum(COALESCE(ExperienceEarned,0)) as ExperienceEarned, 
			sum(COALESCE(SilverLionsEarned,0)) as SilverLionsEarned, 
			sum(COALESCE(GroundKills,0)) as GroundKills, 
			sum(COALESCE(AirKills,0)) as AirKills, 
			sum(COALESCE(NavalKills,0)) as NavalKills, 
			sum(COALESCE(WasInLineup,0)) as WasInLineup, 
			sum(COALESCE(Defeats,0)) as Defeats, 
			sum(COALESCE(Victories,0)) as Victories, 
			UpdateTitle, 
			UpdateVersion, 
			UpdateDate, 
			UpdateEOLDate, 
			VehicleInformation.VehicleID as VehicleID,
			VehicleName as VehicleIdentifiyingName,
			GROUP_CONCAT(DISTINCT(Gamemode.GamemodeName)) as GamemodeName
			FROM WarThunderStats.VehicleStatsByUpdate
			LEFT OUTER JOIN WarThunderStats.Updates ON VehicleStatsByUpdate.UpdateID = Updates.UpdateID
			LEFT OUTER JOIN WarThunderStats.VehicleInformation ON VehicleStatsByUpdate.VehicleID = VehicleInformation.VehicleID
			LEFT OUTER JOIN WarThunderStats.Gamemode ON VehicleStatsByUpdate.GamemodeID = Gamemode.GamemodeID
			WHERE VehicleName = ? AND Updates.UpdateID != 0";
			
		// Add filter to query depending on if the gamemode has been set
		if($gamemode != "") {
			$query = $query . " AND Gamemode.GamemodeName = ?";
			array_push($parameters, $gamemode);
		} else {
			$query = $query . " AND Gamemode.GamemodeName = ?";
			array_push($parameters, "realistic");
		}
		
		$query = $query . " GROUP BY VehicleStatsByUpdate.VehicleID, VehicleStatsByUpdate.UpdateID, VehicleStatsByUpdate.GamemodeID;";
		
		// execute query
		$data = $this->select($query, $parameters);
		
		$result = $data;
		
		return $result;
	}
}
?>