<!doctype html>
<html lang="en" data-bs-theme="dark">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Thunder Insights Vehicle Search</title>
	<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
	<script src="https://cdn.jsdelivr.net/npm/fuse.js@7.0.0"></script>
  </head>
  <body>
  <?php
	include_once('../../header.php');
  ?>
    <div class="container-fluid">
		<div class="row justify-content-center">
			<div class="mt-4 col-xs-12 col-md-10 col-xl-8 align-self-center">
				<div class="mb-3">
					<label for="vehicleSearchString" class="form-label">Search</label>
					<input type="search" class="form-control" id="vehicleSearchString" name="vehicleSearchString" onkeyup="vehicleSearch(this.value)">
				</div>
			</div>
			<div class="mt-4 col-xs-12 col-md-10 col-xl-8 align-self-center ">
				<table class="table table-hover table-striped" id="searchResponse">
					<thead>
						<tr>
							<th scope="col">Vehicle Image</th>
							<th scope="col">Vehicle Fullname</th>
							<th scope="col">Country</th>
							<th scope="col">Tier</th>
						</tr>
					</thead>
					<tbody>
					</tbody>
				</table>
			</div>
		</div>
	</div>
	<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-kenU1KFdBIe4zVF0s0G1M5b4hcpxyD9F7jL+jjXkk+Q2h455rYXK/7HAuoJl+0I4" crossorigin="anonymous"></script>
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
	<script src="/js/primary.js"></script> 
	<?php
	include_once('../../footer.php');
	?>
	<script>
		// I will need to go through this before releasing
		var fuse = null
		$.getJSON( "/api/v1/vehicles/list", function( data ) {
			fuse = new Fuse(data, {
			  keys: ['VehicleName', 'VehicleFullName', 'VehicleShortName', 'VehicleCompressedName', 'NationName', 'OperatorName'],
			  threshold: 0.2
			})
			let searchParams = new URLSearchParams(window.location.search);
			let searchString = null;
			if (searchParams.has('searchString')) {
				searchString = searchParams.get('searchString');
				vehicleSearch(searchString);
				document.getElementById("vehicleSearchString").value = searchString;
			}
		})
	</script>
  </body>
</html>
