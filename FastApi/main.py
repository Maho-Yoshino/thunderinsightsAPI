from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import users_routers_v1
from app.routers import general_routers_v1
from app.routers import clans_routers_v1
from app.routers import units_routers_v1

description = """
Thunderinsights API can help you create basic websites for the game War Thunder.

All endpoints are currently cached for 20 hours every time they are called, so once called you will have to wait 20 hours to be able to get new data.

Please note that this project is not affiliated with War Thunder or Gaijin.

## Limitations
If you wish to webscrape, please only use the 'direct' endpoints as far as possible, use of the /v1/users/refresh/* endpoint for webscraping might lead to the project being shut down for good if too much data is ingested.

## Users

You will be able to:

* **Search for users** (_implemented_).
* **Get user information directly from Gaijin** (_implemented_).
* **request to have user information stored in the database and be monitored** (_implemented_).
"""

tags_metadata = [
    {
        "name": "clans",
        "description": "Operations correlating to getting information about the clans/squadrons of the game War Thunder.",
    },
    {
        "name": "general",
        "description": "Operations correlating to getting general information about the game War Thunder.",
    },
    {
        "name": "units",
        "description": "Operations correlating to getting information about the units of the game War Thunder.",
    },
    {
        "name": "users",
        "description": "Operations correlating to getting information about the users/players of the game War Thunder.",
    }
]

def create_app():
    app = FastAPI(
        title="Thunderinsights API",
        description=description,
        summary="API to retrieve War Thunder player data.",
        version="0.0.1",
        openapi_tags=tags_metadata,
    )

    app.include_router(clans_routers_v1.router, prefix="/v1")
    #app.include_router(clans_routers_v1.router, prefix="/latest")
    app.include_router(general_routers_v1.router, prefix="/v1")
    #app.include_router(general_routers_v1.router, prefix="/latest")
    app.include_router(users_routers_v1.router, prefix="/v1")
    #app.include_router(users_routers_v1.router, prefix="/latest")
    app.include_router(units_routers_v1.router, prefix="/v1")
    #app.include_router(users_routers_v1.router, prefix="/latest")

    return app


app = create_app()

app.mount("/static", StaticFiles(directory="/code/app/static"), name="static")