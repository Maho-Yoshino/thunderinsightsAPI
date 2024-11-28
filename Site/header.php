<nav class="navbar navbar-expand-lg">
  <div class="container-fluid">
    <a class="navbar-brand" href="/">Thunder Insights</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarSupportedContent">
      <ul class="navbar-nav me-auto mb-2 mb-lg-0">
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
            Players
          </a>
          <ul class="dropdown-menu">
            <li><a class="dropdown-item" href="/players">General Stats</a></li>
            <li><a class="dropdown-item" href="/players/search">Search</a></li>
          </ul>
        </li>
		<li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
            Vehicles
          </a>
          <ul class="dropdown-menu">
            <li><a class="dropdown-item disabled" href="/vehicles">General Stats</a></li>
            <li><a class="dropdown-item" href="/vehicles/search">Search</a></li>
          </ul>
        </li>
      </ul>
	  <?php
	  $url = 'http://' . $_SERVER['SERVER_NAME'] . $_SERVER['REQUEST_URI'];
	  if (strpos(parse_url($url, PHP_URL_PATH),'players/search') == false) { ?>
      <form class="d-flex" role="search" action="/players/search" method="get">
        <input class="form-control me-2" type="search" placeholder="Search for player" aria-label="Search" id="searchString" name="searchString">
        <button class="btn btn-outline-success" type="submit">Search</button>
      </form>
	  <?php }
	  ?>
    </div>
  </div>
</nav>