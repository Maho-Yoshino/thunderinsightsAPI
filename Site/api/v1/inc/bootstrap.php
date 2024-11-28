<?php
define("PROJECT_ROOT_PATH", __DIR__ . "/../");
// include main configuration file
require_once PROJECT_ROOT_PATH . "inc/config.php";
// include the base controller file
require_once PROJECT_ROOT_PATH . "Controller/Api/BaseController.php";
// include the Player model file
require_once PROJECT_ROOT_PATH . "Model/PlayerModel.php";
// include the Vehicle model file
require_once PROJECT_ROOT_PATH . "Model/VehicleModel.php";
// include the General model file
require_once PROJECT_ROOT_PATH . "Model/GeneralModel.php";
?>
