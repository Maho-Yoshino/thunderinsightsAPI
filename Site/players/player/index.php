<!doctype html>
<html lang="en" data-bs-theme="dark">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Thunder Insights user details</title>
	<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.css" rel="stylesheet" crossorigin="anonymous">
  </head>
  <body>
  <?php
	include_once('../../header.php');
  ?>
    <div class="container-fluid">
		<div class="ml-2 mt-4 row justify-content-left">
			<div class="col-xs-6 col-md-6 col-xl-4 align-self-left">
				<button class="btn btn-primary" role="button" onclick='returnToSearch("/players/search/")'>Return to search results</button>
				<div class="dropdown m-2"><label for="timestampButton" class="me-2" id="userDetailsTimetampButton"></div>
			</div>
		</div>
		<div class="row">
			<div class="mt-4 col-lg-12 col-xl-4 col-xxl-3">
				<table class="table table-striped table-hover text-center" id="searchResponse">
					<tbody>
						<tr id="profilePicture">
							<!--<th scope="row">Profile Picture:</th>-->
							<td colspan="3"><img src="/images/avatars/cardicon_bot.avif" class="rounded" style="height:auto; max-height:20vh;" alt="profile picture"></img></td>
						</tr>
						<tr id="username">
							<th colspan="1" scope="row">Username:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="title">
							<th colspan="1" scope="row">Title:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="clan">
							<th colspan="1" scope="row">Clan:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="clanTag">
							<th colspan="1" scope="row">Clan Tag:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="clanRole">
							<th colspan="1" scope="row">Clan Role:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="experience">
							<th colspan="1" scope="row">Research points earned:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="experienceConverted">
							<th colspan="1" scope="row">Research points converted:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="premiumVehicleGoldenEagleCost">
							<th colspan="1" scope="row">Estimated GE cost of premium vehicles:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="spadedVehicles">
							<th colspan="1" scope="row">Spaded vehicles:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="lastActive">
							<th colspan="1" scope="row">Last Time Online:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="signupDate">
							<th colspan="1" scope="row">Sign up date:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="profileStatus">
							<th colspan="1" scope="row">Profile Status:</th>
							<td colspan="2"></td>
						</tr>
						<tr id="statsLastUpdated">
							<th colspan="1" scope="row">Stats last updated:</th>
							<td colspan="2"></td>
						</tr>
						<tr>
							<td colspan="3"><button class="btn btn-primary" role="button" onclick="requestStatRefresh(userID)">Request stat refresh</button></td>
						</tr>
					</tbody>
				</table>
			</div>
			<div class="mt-4 col-lg-12 col-xl-8 col-xxl-9" id="generalPlaySatisticsForPlayer">
				
			</div>
		</div>
		<div class="row">
			<div class="mt-4 col-lg-12 col-xl-12 col-xxl-12">
				<div class="btn-group" role="group" aria-label="Button group with nested dropdown">
					<div class="btn-group" role="group">
						<button id="sortPropertyButton" type="button" class="btn btn-primary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false">
							NationName
						</button>
						<ul class="dropdown-menu">
							
						</ul>
					</div>
					<button id="sortOrderButton" onclick="sortOrder()" type="button" class="btn btn-primary"><svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' class='bi bi-sort-up' viewBox='0 0 16 16'><path d='M3.5 12.5a.5.5 0 0 1-1 0V3.707L1.354 4.854a.5.5 0 1 1-.708-.708l2-1.999.007-.007a.5.5 0 0 1 .7.006l2 2a.5.5 0 1 1-.707.708L3.5 3.707zm3.5-9a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7a.5.5 0 0 1-.5-.5M7.5 6a.5.5 0 0 0 0 1h5a.5.5 0 0 0 0-1zm0 3a.5.5 0 0 0 0 1h3a.5.5 0 0 0 0-1zm0 3a.5.5 0 0 0 0 1h1a.5.5 0 0 0 0-1z'/></svg></button>
				</div>
				<button id="filterButton" type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#filterModal">Filters</button>
				<div class="row" id="playerVehicleStats">
				</div>
			</div>
		</div>
	</div>
	<!-- Basic Modal to tell user if their stat refresh was submitted -->
	<div class="modal fade" id="messageModal" tabindex="-1" aria-labelledby="messageModalLabel" aria-hidden="true">
	  <div class="modal-dialog">
		<div class="modal-content">
		  <div class="modal-header">
			<h1 class="modal-title fs-5" id="messageModalLabel"></h1>
			<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
		  </div>
		  <div class="modal-body">
		  </div>
		  <div class="modal-footer">
			<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
		  </div>
		</div>
	  </div>
	</div>
	<!-- Modal to filter results -->
	<div class="modal" id="filterModal" tabindex="-1" aria-labelledby="filterModalLabel" aria-hidden="true">
	  <div class="modal-dialog modal-xl">
		<div class="modal-content">
		  <div class="modal-header">
			<h1 class="modal-title fs-5" id="filterModalLabel">Filters</h1>
			<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
		  </div>
		  <div class="modal-body" id="filterModalBody">
		  </div>
		  <div class="modal-footer">
			<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
		  </div>
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
		let userID = Number("<?php
			$firstLayer = filter_input(INPUT_GET, 'firstLayer', FILTER_UNSAFE_RAW);
			echo $firstLayer;
		?>");
		let PlayerVehicleStats;
		
		if (!isNaN(userID)) {
			getUserDetails(userID);
			getPlayerVehicleStats(userID);
			getFilters();
		} else {
			$("#username td").html("UserID must be a numeric identifier")
		}
	</script>
  </body>
</html>
