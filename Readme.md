# Celery:
The files in the Celery folder where used to run reoccuring tasks such as renewing the war thunder api token.

# Docker
Basic docker files used to make budget container for Celery and FastApi.

# FastApi:
The FastApi code used to run the public api for the war thunder website.

# FastApiRefresh
The FastApi code used to refresh the data for a user (This really just triggers a celery job)

# MariaDB
This should contain the database layout, can't remember which one of the 2 files were used.

# Powershell
This script runs local tasks on a pc with war thunder installed to get icons for the website. It makes use of other projects available on github.