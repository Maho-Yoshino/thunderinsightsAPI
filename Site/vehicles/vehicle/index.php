<!doctype html>
<html lang="en" data-bs-theme="dark">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Thunder Insights vehicle details</title>
	<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.css" rel="stylesheet" crossorigin="anonymous">
  </head>
  <body>
  <?php
	include_once('../../header.php');
  ?>
    <div class="container-fluid">
		<div class="ml-2 mt-4 row justify-content-left">
			<div class="col-sm-12 col-md-3 col-xl-2 align-self-left" id="vehicleButtons">
				<button class="btn btn-primary" role="button" onclick='returnToSearch("/vehicles/search/")'>Return to search results</button>
			</div>
		</div>
		<div class="row">
			<div class="mt-4 col-lg-12 col-xl-6 col-xxl-5">
				<table class="table table-striped table-hover text-center" id="searchResponse">
					<tbody>
						<tr id="vehiclePicture">
							<!--<th scope="row">Profile Picture:</th>-->
							<td colspan="3"><img src="/images/avatars/cardicon_bot.avif" class="rounded" style="height:auto; max-height:20vh;" alt="vehicle picture"></img></td>
						</tr>
						<tr id="vehicleFullName">
							<th colspan="1" scope="row">Vehicle name:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="vehicleType">
							<th colspan="1" scope="row">Vehicle type:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="tier">
							<th colspan="1" scope="row">Tier:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="country">
							<th colspan="1" scope="row">Country:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="operatorNation">
							<th colspan="1" scope="row">Operator nation:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="ownedByUniqueUsers">
							<th colspan="1" scope="row">Players that own this vehicle:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="playedByUniqueUsers">
							<th colspan="1" scope="row">Players that have used this vehicle:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="spawns">
							<th colspan="1" scope="row">Total spawns:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="deaths">
							<th colspan="1" scope="row">Total deaths:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="experienceEarned">
							<th colspan="1" scope="row">Total experience earned:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="silverlionsEarned">
							<th colspan="1" scope="row">Total silverlions earned:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="groundKills">
							<th colspan="1" scope="row">Total ground kills:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="airKills">
							<th colspan="1" scope="row">Total air kills:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="navalKills">
							<th colspan="1" scope="row">Total naval kills:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="inLineup">
							<th colspan="1" scope="row">Total sessions with vehicle in lineup:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="defeats">
							<th colspan="1" scope="row">Total defeats:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="victories">
							<th colspan="1" scope="row">Total victories:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="winPercentage">
							<th colspan="1" scope="row">Win rate:</th>
							<td colspan="2"></td>
						</tr>
					</tbody>
				</table>
			</div>
			<div class="mt-4 col-lg-12 col-xl-6 col-xxl-7" id="vehicleStatsByUpdate">
				
			</div>
		</div>
	</div>
	<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.js" crossorigin="anonymous"></script>
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
	<script src="/js/primary.js"></script> 
	<?php
	include_once('../../footer.php');
	?>
	<script>
		let vehicleIdentifier = "<?php
			$firstLayer = filter_input(INPUT_GET, 'firstLayer', FILTER_UNSAFE_RAW);
			echo $firstLayer;
		?>";
		let PlayerVehicleStats;
		
		getVehicleDetails(vehicleIdentifier);
		getVehicleStatsByUpdate(vehicleIdentifier);
		getVehicleStatFilters();
	</script>
  </body>
</html>
