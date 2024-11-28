<?php
require_once PROJECT_ROOT_PATH . "Model/Database.php";
class GeneralModel extends Database
{	
	public function getSiteInformation()
    {
		// Create basic parameters and query
		$parameters = [];
		$query = "SELECT count(DISTINCT UserID, Timestamp) as DataPoints FROM WarThunderStats.GeneralStats;";
		// execute query
		$dataPoints = $this->select($query, $parameters);
		
		$this->__construct();
		$query = "SELECT count(DISTINCT UserID) as Users FROM WarThunderStats.GeneralStats;";
		// execute query
		$users = $this->select($query, $parameters);
		
		$this->__construct();
		$query = 'SELECT table_schema "DBName",
			ROUND(SUM(data_length + index_length)) "Byte" 
			FROM information_schema.tables 
			GROUP BY table_schema;';
		// execute query
		$databaseSizes = $this->select($query, $parameters);
		
		$data = (object)[];
		$data->DataPoints = $dataPoints[0]->DataPoints;
		$data->Players = $users[0]->Users;
		$data->DataInBytes = 0;
		
		foreach($databaseSizes as $databaseSize){
			if ($databaseSize->DBName == "WarThunderStats") {
				$data->DataInBytes = $data->DataInBytes + $databaseSize->Byte;
			}
			if ($databaseSize->DBName == "WarThunder") {
				$data->DataInBytes = $data->DataInBytes + $databaseSize->Byte;
			}
		}
		
		$result = $data;
		
		return $result;
    }
}
?>