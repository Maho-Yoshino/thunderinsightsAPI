<?php
class VehicleController extends BaseController
{
    /**
* "/user/list" Endpoint - Get list of users
*/
	
	public function vehicleFiltersAction()
    {
        $strErrorDesc = '';
        $requestMethod = $_SERVER["REQUEST_METHOD"];
        $arrQueryStringParams = $this->getQueryStringParams();
        if (strtoupper($requestMethod) == 'GET') {
            try {
                $vehicleModel = new VehicleModel();
                $vehicleFilters = $vehicleModel->getPlayerVehicleFilters();
				if ($vehicleFilters) {
					$responseData = json_encode($vehicleFilters);
				} else {
					$responseData = $vehicleFilters;
				}
            } catch (Error $e) {
                $strErrorDesc = $e->getMessage().'Something went wrong! Please contact support.';
                $strErrorHeader = 'HTTP/1.1 500 Internal Server Error';
            }
        } else {
            $strErrorDesc = 'Method not supported';
            $strErrorHeader = 'HTTP/1.1 422 Unprocessable Entity';
        }
        // send output
        if (!$strErrorDesc and $responseData != null) {
            $this->sendOutput(
                $responseData,
                array('Content-Type: application/json', 'Access-Control-Allow-Origin: *', 'Access-Control-Allow-Methods: GET, POST', 'HTTP/1.1 200 OK')
            );
        } elseif (!$strErrorDesc and $responseData == null) {
			$this->sendOutput(
                $responseData,
                array('Content-Type: application/json', 'Access-Control-Allow-Origin: *', 'Access-Control-Allow-Methods: GET, POST', 'HTTP/1.1 204 No Content')
            );
		} else {
            $this->sendOutput(json_encode(array('error' => $strErrorDesc)), 
                array('Content-Type: application/json', 'Access-Control-Allow-Origin: *', 'Access-Control-Allow-Methods: GET, POST', $strErrorHeader)
            );
        }
    }
	
	public function listAction()
    {
        $strErrorDesc = '';
        $requestMethod = $_SERVER["REQUEST_METHOD"];
        $arrQueryStringParams = $this->getQueryStringParams();
        if (strtoupper($requestMethod) == 'GET') {
            try {
                $vehicleModel = new VehicleModel();
				// If the language parameter has been set use it
				$language = "";
				if (isset($arrQueryStringParams['language']) && $arrQueryStringParams['language']) {
					$language = $arrQueryStringParams['language'];
				}
                $arrVehicles = $vehicleModel->getVehicles($language);
				if ($arrVehicles) {
					$responseData = json_encode($arrVehicles);
				} else {
					$responseData = $arrVehicles;
				}
                
            } catch (Error $e) {
                $strErrorDesc = $e->getMessage().'Something went wrong! Please contact support.';
                $strErrorHeader = 'HTTP/1.1 500 Internal Server Error';
            }
        } else {
            $strErrorDesc = 'Method not supported';
            $strErrorHeader = 'HTTP/1.1 422 Unprocessable Entity';
        }
        // send output
        if (!$strErrorDesc and $responseData != null) {
            $this->sendOutput(
                $responseData,
                array('Content-Type: application/json', 'Access-Control-Allow-Origin: *', 'Access-Control-Allow-Methods: GET, POST', 'HTTP/1.1 200 OK')
            );
        } elseif (!$strErrorDesc and $responseData == null) {
			$this->sendOutput(
                $responseData,
                array('Content-Type: application/json', 'Access-Control-Allow-Origin: *', 'Access-Control-Allow-Methods: GET, POST', 'HTTP/1.1 204 No Content')
            );
		} else {
            $this->sendOutput(json_encode(array('error' => $strErrorDesc)), 
                array('Content-Type: application/json', 'Access-Control-Allow-Origin: *', 'Access-Control-Allow-Methods: GET, POST', $strErrorHeader)
            );
        }
    }
	
	public function vehicleStatAction($vehicleIdentifier = null)
    {
        $strErrorDesc = '';
        $requestMethod = $_SERVER["REQUEST_METHOD"];
        $arrQueryStringParams = $this->getQueryStringParams();
        if (strtoupper($requestMethod) == 'GET') {
            try {
				$vehicleModel = new VehicleModel();
				// If the gamemode parameter has been set use it
				$gamemode = "";
                if (isset($arrQueryStringParams['gamemode']) && $arrQueryStringParams['gamemode']) {
					$gamemode = $arrQueryStringParams['gamemode'];
				}
				// If the gameupdateid parameter has been set use it
				$gameUpdateID = "";
                if (isset($arrQueryStringParams['gameupdateid']) && $arrQueryStringParams['gameupdateid']) {
					$gameUpdateID = $arrQueryStringParams['gameupdateid'];
				}
				// If the language parameter has been set use it
				$language = "";
				if (isset($arrQueryStringParams['language']) && $arrQueryStringParams['language']) {
					$language = $arrQueryStringParams['language'];
				}
				$arrVehicleStat = $vehicleModel->getVehicle($vehicleIdentifier,$gamemode,$gameUpdateID,$language);
				if ($arrVehicleStat) {
					$responseData = json_encode($arrVehicleStat);
				} else {
					$responseData = $arrVehicleStat;
				}
                
            } catch (Error $e) {
                $strErrorDesc = $e->getMessage().'Something went wrong! Please contact support.';
                $strErrorHeader = 'HTTP/1.1 500 Internal Server Error';
            }
        } else {
            $strErrorDesc = 'Method not supported';
            $strErrorHeader = 'HTTP/1.1 422 Unprocessable Entity';
        }
        // send output
        if (!$strErrorDesc and $responseData != null) {
            $this->sendOutput(
                $responseData,
                array('Content-Type: application/json', 'Access-Control-Allow-Origin: *', 'Access-Control-Allow-Methods: GET, POST', 'HTTP/1.1 200 OK')
            );
        } elseif (!$strErrorDesc and $responseData == null) {
			$this->sendOutput(
                $responseData,
                array('Content-Type: application/json', 'Access-Control-Allow-Origin: *', 'Access-Control-Allow-Methods: GET, POST', 'HTTP/1.1 204 No Content')
            );
		} else {
            $this->sendOutput(json_encode(array('error' => $strErrorDesc)), 
                array('Content-Type: application/json', 'Access-Control-Allow-Origin: *', 'Access-Control-Allow-Methods: GET, POST', $strErrorHeader)
            );
        }
    }
	
	public function vehicleStatsByUpdateAction($vehicleIdentifier = null)
    {
        $strErrorDesc = '';
        $requestMethod = $_SERVER["REQUEST_METHOD"];
        $arrQueryStringParams = $this->getQueryStringParams();
        if (strtoupper($requestMethod) == 'GET') {
            try {
				$vehicleModel = new VehicleModel();
				// If the gamemode parameter has been set use it
				$gamemode = "";
                if (isset($arrQueryStringParams['gamemode']) && $arrQueryStringParams['gamemode']) {
					$gamemode = $arrQueryStringParams['gamemode'];
				}
				$arrVehicleStat = $vehicleModel->getVehicleStatsByUpdates($vehicleIdentifier,$gamemode);
				if ($arrVehicleStat) {
					$responseData = json_encode($arrVehicleStat);
				} else {
					$responseData = $arrVehicleStat;
				}
                
            } catch (Error $e) {
                $strErrorDesc = $e->getMessage().'Something went wrong! Please contact support.';
                $strErrorHeader = 'HTTP/1.1 500 Internal Server Error';
            }
        } else {
            $strErrorDesc = 'Method not supported';
            $strErrorHeader = 'HTTP/1.1 422 Unprocessable Entity';
        }
        // send output
        if (!$strErrorDesc and $responseData != null) {
            $this->sendOutput(
                $responseData,
                array('Content-Type: application/json', 'Access-Control-Allow-Origin: *', 'Access-Control-Allow-Methods: GET, POST', 'HTTP/1.1 200 OK')
            );
        } elseif (!$strErrorDesc and $responseData == null) {
			$this->sendOutput(
                $responseData,
                array('Content-Type: application/json', 'Access-Control-Allow-Origin: *', 'Access-Control-Allow-Methods: GET, POST', 'HTTP/1.1 204 No Content')
            );
		} else {
            $this->sendOutput(json_encode(array('error' => $strErrorDesc)), 
                array('Content-Type: application/json', 'Access-Control-Allow-Origin: *', 'Access-Control-Allow-Methods: GET, POST', $strErrorHeader)
            );
        }
    }
}
?>