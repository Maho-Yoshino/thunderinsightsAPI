<?php
class Database
{
    protected $connection = null;
    public function __construct()
    {
        try {
			$this->connection = new PDO("mysql:host=".DB_HOST.";dbname=".DB_DATABASE_NAME.";port=".DB_PORT, DB_USERNAME, DB_PASSWORD);
			// set the PDO error mode to exception
			$this->connection->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_WARNING);
			$this->connection->setAttribute(PDO::ATTR_EMULATE_PREPARES, false);
        } catch (Exception $e) {
            throw new Exception($e->getMessage());   
        }			
    }
    public function select($query = "" , $params = [])
    {
        try {
			$stmt = $this->connection->prepare($query);
			if($stmt === false) {
                throw New Exception("Unable to do prepared statement: " . $query);
            }
			$stmt->execute($params);
            $result = $stmt->fetchAll($mode=PDO::FETCH_OBJ);
            $this->connection = null;
            return $result;
        } catch(Exception $e) {
            throw New Exception( $e->getMessage() );
        }
        return false;
    }
    protected function executeStatement($query = "" , $params = [])
    {
        try {
            $stmt = $this->connection->prepare($query);
            if($stmt === false) {
                throw New Exception("Unable to do prepared statement: " . $query);
            }
            $stmt->execute($params);
            return $stmt;
        } catch(Exception $e) {
            throw New Exception( $e->getMessage() );
        }	
    }
}
?>