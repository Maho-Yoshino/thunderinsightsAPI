<?php
class GeneralController extends BaseController
{
	
	public function siteInformationAction()
    {
        $strErrorDesc = '';
        $requestMethod = $_SERVER["REQUEST_METHOD"];
        $arrQueryStringParams = $this->getQueryStringParams();
        if (strtoupper($requestMethod) == 'GET') {
            try {
                $GeneralModel = new GeneralModel();
                $siteInformation = $GeneralModel->getSiteInformation();
				if ($siteInformation) {
					$responseData = json_encode($siteInformation);
				} else {
					$responseData = $siteInformation;
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