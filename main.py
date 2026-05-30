from dotenv import load_dotenv
from logging import getLogger
from fastapi import FastAPI
from uvicorn import run as uvicorn_run
from os import getenv

from utils.auth import login
from api import users_router, clans_router, general_router

logger = getLogger()

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
app = FastAPI(
    title="ThunderAPI",
    description="API to retrieve War Thunder data.",
    version="0.0.1",
    openapi_tags=tags_metadata,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)
app.include_router(users_router.router, prefix="/v1")
app.include_router(clans_router.router, prefix="/v1")
app.include_router(general_router.router, prefix="/v1")

def main():
    if not load_dotenv(".env"):
        logger.error("Failed to load .env file.")
        return
    login()
    uvicorn_run(app, host=getenv("HOST", "127.0.0.1"), port=int(getenv("PORT", "8001")))

if __name__ == '__main__':
    main()