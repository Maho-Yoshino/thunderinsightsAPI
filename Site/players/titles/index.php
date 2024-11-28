<!doctype html>
<html lang="en" data-bs-theme="dark">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Thunder Insights Players with Title</title>
	<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
  </head>
  <body>
  <?php
	include_once('../../header.php');
  ?>
    <div class="container-fluid">
		<div class="row justify-content-center">
			<div class="mt-4 col-xs-12 col-md-10 col-xl-8 align-self-center ">
				<h3 id="headerTitle">Top 20 Players with the title (Ordered by RP earned):</h3>
				<table class="table table-hover table-striped" id="playersWithTitle">
					<thead>
						<tr>
							<th scope="col">Profile Picture</th>
							<th scope="col">Username</th>
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
		let titleIdentifier = "<?php
			$firstLayer = filter_input(INPUT_GET, 'firstLayer', FILTER_UNSAFE_RAW);
			echo $firstLayer;
		?>";
		playersWithTitle(titleIdentifier)
	</script>
  </body>
</html>
