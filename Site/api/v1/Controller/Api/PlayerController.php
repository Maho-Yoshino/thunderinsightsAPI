<?php
class PlayerController extends BaseController
{
    /**
* "/user/list" Endpoint - Get list of users
*/
    public function searchAction()
    {
        $strErrorDesc = '';
        $requestMethod = $_SERVER["REQUEST_METHOD"];
        $arrQueryStringParams = $this->getQueryStringParams();
        if (strtoupper($requestMethod) == 'GET') {
            try {
                $playerModel = new PlayerModel();
                $intLimit = 20;
                if (((isset($arrQueryStringParams['limit']) && $arrQueryStringParams['limit']) || $arrQueryStringParams['limit'] == 0) && is_numeric($arrQueryStringParams['limit'])) {
					if ($arrQueryStringParams['limit'] < 2) {
						$intLimit = 2;
					} elseif ($arrQueryStringParams['limit'] > 100) {
						$intLimit = 100;
					} else {
						$intLimit = $arrQueryStringParams['limit'];
					}
                }
				$userToSearchFor = "abc";
                if ((isset($arrQueryStringParams['userToSearchFor']) && $arrQueryStringParams['userToSearchFor'])) {
                    $userToSearchFor = $arrQueryStringParams['userToSearchFor'];
                }
				$inDatabase = 0;
				if ((isset($arrQueryStringParams['inDatabase']) && $arrQueryStringParams['inDatabase']) && is_numeric($arrQueryStringParams['inDatabase'])) {
					if ($arrQueryStringParams['inDatabase'] != 0 && $arrQueryStringParams['inDatabase'] != 1) {
						$inDatabase = 0;
					} else {
						$inDatabase = $arrQueryStringParams['inDatabase'];
					}
                }
                $arrPlayers = $playerModel->getPlayers($intLimit,$userToSearchFor,$inDatabase);
				if ($arrPlayers) {
					$responseData = json_encode($arrPlayers);
				} else {
					$responseData = $arrPlayers;
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
	
	public function detailsAction($userId = null)
    {
        $strErrorDesc = '';
        $requestMethod = $_SERVER["REQUEST_METHOD"];
        $arrQueryStringParams = $this->getQueryStringParams();
        if (strtoupper($requestMethod) == 'GET') {
            try {
                $playerModel = new PlayerModel();
				// If the timestamp parameter has been set use it
				$timestamp = 0;
                if (isset($arrQueryStringParams['timestamp']) && $arrQueryStringParams['timestamp'] && is_numeric($arrQueryStringParams['timestamp'])) {
					$timestamp = $arrQueryStringParams['timestamp'];
				}
                $playerDetails = $playerModel->getPlayer($userId,$timestamp);
				if ($playerDetails) {
					$responseData = json_encode($playerDetails);
				} else {
					$responseData = $playerDetails;
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
	
	public function updateAction($userId = null)
    {
        $strErrorDesc = '';
        $requestMethod = $_SERVER["REQUEST_METHOD"];
        $arrQueryStringParams = $this->getQueryStringParams();
        if (strtoupper($requestMethod) == 'GET') {
            try {
                $playerModel = new PlayerModel();
                $playerDetails = $playerModel->updatePlayer($userId);
				if ($playerDetails) {
					$responseData = json_encode($playerDetails);
				} else {
					$responseData = $playerDetails;
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
	
	public function vehicleStatsAction($userId = null)
    {
        $strErrorDesc = '';
        $requestMethod = $_SERVER["REQUEST_METHOD"];
        $arrQueryStringParams = $this->getQueryStringParams();
        if (strtoupper($requestMethod) == 'GET') {
            try {
                $playerModel = new PlayerModel();
				// If the timestamp parameter has been set use it
				$timestamp = 0;
                if (isset($arrQueryStringParams['timestamp']) && $arrQueryStringParams['timestamp'] && is_numeric($arrQueryStringParams['timestamp'])) {
					$timestamp = $arrQueryStringParams['timestamp'];
				}
				// If the country parameter has been set use it
				$country = "";
                if (isset($arrQueryStringParams['country']) && $arrQueryStringParams['country']) {
					$country = $arrQueryStringParams['country'];
				}
				// If the gamemode parameter has been set use it
				$gamemode = "";
                if (isset($arrQueryStringParams['gamemode']) && $arrQueryStringParams['gamemode']) {
					$gamemode = $arrQueryStringParams['gamemode'];
				}
				// If the language parameter has been set use it
				$language = "";
				if (isset($arrQueryStringParams['language']) && $arrQueryStringParams['language']) {
					$language = $arrQueryStringParams['language'];
				}
				// If the vehicletype parameter has been set use it
				$vehicleType = "";
				if (isset($arrQueryStringParams['vehicletype']) && $arrQueryStringParams['vehicletype']) {
					$vehicleType = $arrQueryStringParams['vehicletype'];
				}
				
				// If the min/max parameters have been set use them
				$minTier = 0;
				if (isset($arrQueryStringParams['mintier']) && $arrQueryStringParams['mintier']) {
					$minTier = $arrQueryStringParams['mintier'];
				}
				$maxTier = 100000000;
				if (isset($arrQueryStringParams['maxtier']) && $arrQueryStringParams['maxtier']) {
					$maxTier = $arrQueryStringParams['maxtier'];
				}
				$minBattlerating = 0;
				if (isset($arrQueryStringParams['minbattlerating']) && $arrQueryStringParams['minbattlerating']) {
					$minBattlerating = $arrQueryStringParams['minbattlerating'];
				}
				$maxBattlerating = 100000000;
				if (isset($arrQueryStringParams['maxbattlerating']) && $arrQueryStringParams['maxbattlerating']) {
					$maxBattlerating = $arrQueryStringParams['maxbattlerating'];
				}
				$minVictories = 0;
				if (isset($arrQueryStringParams['minvictories']) && $arrQueryStringParams['minvictories']) {
					$minVictories = $arrQueryStringParams['minvictories'];
				}
				$maxVictories = 100000000;
				if (isset($arrQueryStringParams['maxvictories']) && $arrQueryStringParams['maxvictories']) {
					$maxVictories = $arrQueryStringParams['maxvictories'];
				}
				$minDefeats = 0;
				if (isset($arrQueryStringParams['mindefeats']) && $arrQueryStringParams['mindefeats']) {
					$minDefeats = $arrQueryStringParams['mindefeats'];
				}
				$maxDefeats = 100000000;
				if (isset($arrQueryStringParams['maxdefeats']) && $arrQueryStringParams['maxdefeats']) {
					$maxDefeats = $arrQueryStringParams['maxdefeats'];
				}
				$minInSession = 0;
				if (isset($arrQueryStringParams['mininsession']) && $arrQueryStringParams['mininsession']) {
					$minInSession = $arrQueryStringParams['mininsession'];
				}
				$maxInSession = 100000000;
				if (isset($arrQueryStringParams['maxinsession']) && $arrQueryStringParams['maxinsession']) {
					$maxInSession = $arrQueryStringParams['maxinsession'];
				}
				$minSpawns = 0;
				if (isset($arrQueryStringParams['minspawns']) && $arrQueryStringParams['minspawns']) {
					$minSpawns = $arrQueryStringParams['minspawns'];
				}
				$maxSpawns = 100000000;
				if (isset($arrQueryStringParams['maxspawns']) && $arrQueryStringParams['maxspawns']) {
					$maxSpawns = $arrQueryStringParams['maxspawns'];
				}
				$minDeaths = 0;
				if (isset($arrQueryStringParams['mindeaths']) && $arrQueryStringParams['mindeaths']) {
					$minDeaths = $arrQueryStringParams['mindeaths'];
				}
				$maxDeaths = 100000000;
				if (isset($arrQueryStringParams['maxdeaths']) && $arrQueryStringParams['maxdeaths']) {
					$maxDeaths = $arrQueryStringParams['maxdeaths'];
				}
				$minGroundKills = 0;
				if (isset($arrQueryStringParams['mingroundkills']) && $arrQueryStringParams['mingroundkills']) {
					$minGroundKills = $arrQueryStringParams['mingroundkills'];
				}
				$maxGroundKills = 100000000;
				if (isset($arrQueryStringParams['maxgroundkills']) && $arrQueryStringParams['maxgroundkills']) {
					$maxGroundKills = $arrQueryStringParams['maxgroundkills'];
				}
				$minAirKills = 0;
				if (isset($arrQueryStringParams['minairkills']) && $arrQueryStringParams['minairkills']) {
					$minAirKills = $arrQueryStringParams['minairkills'];
				}
				$maxAirKills = 100000000;
				if (isset($arrQueryStringParams['maxairkills']) && $arrQueryStringParams['maxairkills']) {
					$maxAirKills = $arrQueryStringParams['maxairkills'];
				}
				$minNavalKills = 0;
				if (isset($arrQueryStringParams['minnavalkills']) && $arrQueryStringParams['minnavalkills']) {
					$minNavalKills = $arrQueryStringParams['minnavalkills'];
				}
				$maxNavalKills = 100000000;
				if (isset($arrQueryStringParams['maxnavalkills']) && $arrQueryStringParams['maxnavalkills']) {
					$maxNavalKills = $arrQueryStringParams['maxnavalkills'];
				}
				
                $playerVehicleStats = $playerModel->getPlayerVehicleStats($userId,$timestamp,$country,$gamemode,$language,$vehicleType,$minTier,$maxTier,$minBattlerating,$maxBattlerating,$minVictories,$maxVictories,$minDefeats,$maxDefeats,$minInSession,$maxInSession,$minSpawns,$maxSpawns,$minDeaths,$maxDeaths,$minGroundKills,$maxGroundKills,$minAirKills,$maxAirKills,$minNavalKills,$maxNavalKills);
				if ($playerVehicleStats) {
					$responseData = json_encode($playerVehicleStats);
				} else {
					$responseData = $playerVehicleStats;
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
	
	public function summaryStatsAction($userId = null)
    {
        $strErrorDesc = '';
        $requestMethod = $_SERVER["REQUEST_METHOD"];
        $arrQueryStringParams = $this->getQueryStringParams();
        if (strtoupper($requestMethod) == 'GET') {
            try {
                $playerModel = new PlayerModel();
                $playerDetails = $playerModel->getPlayer($userId);
				if ($playerDetails) {
					$responseData = json_encode($playerDetails);
				} else {
					$responseData = $playerDetails;
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
	
	public function rarestTitlesAction()
    {
        $strErrorDesc = '';
        $requestMethod = $_SERVER["REQUEST_METHOD"];
        $arrQueryStringParams = $this->getQueryStringParams();
        if (strtoupper($requestMethod) == 'GET') {
            try {
                $playerModel = new PlayerModel();
                $titlesByRarity = $playerModel->getTitlesByRarity();
				if ($titlesByRarity) {
					$responseData = json_encode($titlesByRarity);
				} else {
					$responseData = $titlesByRarity;
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
	
	public function playersWithTitleAction($titleIdentifier = null)
    {
        $strErrorDesc = '';
        $requestMethod = $_SERVER["REQUEST_METHOD"];
        $arrQueryStringParams = $this->getQueryStringParams();
        if (strtoupper($requestMethod) == 'GET') {
            try {
                $playerModel = new PlayerModel();
                $playersWithTitle = $playerModel->playersWithTitle($titleIdentifier);
				if ($playersWithTitle) {
					$responseData = json_encode($playersWithTitle);
				} else {
					$responseData = $playersWithTitle;
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