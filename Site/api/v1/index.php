<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);
require __DIR__ . "/inc/bootstrap.php";
$firstLayer  = filter_input(INPUT_GET, 'firstLayer',  FILTER_UNSAFE_RAW);
$secondLayer = filter_input(INPUT_GET, 'secondLayer', FILTER_UNSAFE_RAW);
$thirdLayer = filter_input(INPUT_GET, 'thirdLayer', FILTER_UNSAFE_RAW);
$fourthLayer = filter_input(INPUT_GET, 'fourthLayer', FILTER_UNSAFE_RAW);
$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$uri = explode( '/', $uri );
if (isset($firstLayer) && isset($secondLayer) && isset($thirdLayer)) {
	if ($firstLayer == 'players' && $secondLayer == 'details' && is_numeric($thirdLayer)) {
		require PROJECT_ROOT_PATH . "Controller/Api/PlayerController.php";
		$objFeedController = new PlayerController();
	} elseif ($firstLayer == 'players' && $secondLayer == 'update' && is_numeric($thirdLayer)) {
		require PROJECT_ROOT_PATH . "Controller/Api/PlayerController.php";
		$objFeedController = new PlayerController();
	} elseif ($firstLayer == 'players' && $secondLayer == 'vehicleStats' && is_numeric($thirdLayer)) {
		require PROJECT_ROOT_PATH . "Controller/Api/PlayerController.php";
		$objFeedController = new PlayerController();
	} elseif ($firstLayer == 'players' && $secondLayer == 'summaryStats' && is_numeric($thirdLayer)) {
		require PROJECT_ROOT_PATH . "Controller/Api/PlayerController.php";
		$objFeedController = new PlayerController();
	} elseif ($firstLayer == 'players' && $secondLayer == 'playersWithTitle' && isset($thirdLayer)) {
		require PROJECT_ROOT_PATH . "Controller/Api/PlayerController.php";
		$objFeedController = new PlayerController();
	} elseif ($firstLayer == 'vehicles' && $secondLayer == 'vehicleStat' && isset($thirdLayer)) {
		require PROJECT_ROOT_PATH . "Controller/Api/VehicleController.php";
		$objFeedController = new VehicleController();
	} elseif ($firstLayer == 'vehicles' && $secondLayer == 'vehicleStatsByUpdate' && isset($thirdLayer)) {
		require PROJECT_ROOT_PATH . "Controller/Api/VehicleController.php";
		$objFeedController = new VehicleController();
	} else {
		header("HTTP/1.1 404 Not Found");
		header('Access-Control-Allow-Origin: *');
		header('Access-Control-Allow-Methods: GET, POST');
		exit();
	}
} elseif (isset($firstLayer) && isset($secondLayer) && !isset($thirdLayer)) {
	if ($firstLayer == 'players' && $secondLayer == 'search') {
		require PROJECT_ROOT_PATH . "Controller/Api/PlayerController.php";
		$objFeedController = new PlayerController();
	} elseif ($firstLayer == 'vehicles' && $secondLayer == 'vehicleFilters') {
		require PROJECT_ROOT_PATH . "Controller/Api/VehicleController.php";
		$objFeedController = new VehicleController();
	} elseif ($firstLayer == 'general' && $secondLayer == 'siteInformation') {
		require PROJECT_ROOT_PATH . "Controller/Api/GeneralController.php";
		$objFeedController = new GeneralController();
	} elseif ($firstLayer == 'vehicles' && $secondLayer == 'list') {
		require PROJECT_ROOT_PATH . "Controller/Api/VehicleController.php";
		$objFeedController = new VehicleController(); 
	} elseif ($firstLayer == 'players' && $secondLayer == 'rarestTitles') {
		require PROJECT_ROOT_PATH . "Controller/Api/PlayerController.php";
		$objFeedController = new PlayerController();
	} else {
		header("HTTP/1.1 404 Not Found");
		header('Access-Control-Allow-Origin: *');
		header('Access-Control-Allow-Methods: GET, POST');
		exit();
	}
} elseif (isset($firstLayer) && !isset($secondLayer) && !isset($thirdLayer)) {
	if ($firstLayer == 'players') {
		require PROJECT_ROOT_PATH . "Controller/Api/PlayerController.php";
		$objFeedController = new PlayerController();
	} else {
		header("HTTP/1.1 404 Not Found");
		header('Access-Control-Allow-Origin: *');
		header('Access-Control-Allow-Methods: GET, POST');
		exit();
	}
} else {
    header("HTTP/1.1 404 Not Found");
	header('Access-Control-Allow-Origin: *');
	header('Access-Control-Allow-Methods: GET, POST');
    exit();
}
$strMethodName = $secondLayer . 'Action';
$objFeedController->{$strMethodName}($thirdLayer);
?>