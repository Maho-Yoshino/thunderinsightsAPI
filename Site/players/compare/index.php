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
		<div class="row">
			<div class="mt-4 col-12">
				<div class="dropdown">
					<label for="filterButtonComparator1" class="me-2">Comparator 1:</label>
					<button id="filterButtonComparator1" class="btn btn-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
						stat source
					</button>
					<ul class="dropdown-menu">
						<li><a class="dropdown-item" onclick="addFilter('statSource1',this);addComparisonSelectors(this,1)">Player</a></li>
						<li><a class="dropdown-item" onclick="addFilter('statSource1',this);addComparisonSelectors(this,1)">Vehicle</a></li>
					</ul>
				</div>
			</div>
		</div>
		<div class="row">
			<div class="mt-4 col-12">
				<div class="dropdown">
					<label for="filterButtonComparator2" class="me-2">Comparator 2:</label>
					<button id="filterButtonComparator2" class="btn btn-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
						stat source
					</button>
					<ul class="dropdown-menu">
						<li><a class="dropdown-item" onclick="addFilter('statSource2',this);addComparisonSelectors(this,2)">Player</a></li>
						<li><a class="dropdown-item" onclick="addFilter('statSource2',this);addComparisonSelectors(this,2)">Vehicle</a></li>
					</ul>
				</div>
			</div>
		</div>
		<div class="row">
			<div class="mt-4 col-12">
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
		</div>
	</div>
	<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.js" crossorigin="anonymous"></script>
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
	<script src="/js/bootstrap-autocomplete.min.js"></script>
	<script src="/js/primary.js"></script> 
	<?php
	include_once('../../footer.php');
	?>
	<script>

	</script>
  </body>
</html>
