import logging, asyncio
from logging.handlers import TimedRotatingFileHandler
from dotenv import load_dotenv
from fastapi import FastAPI
from uvicorn import run as uvicorn_run
from os import getenv, chdir, path
from pathlib import Path
from contextlib import asynccontextmanager
from utils.auth import users_cache

from api import users_router
from api import clans_router, general_router 

logger = logging.getLogger()

tags_metadata = [
	{
		"name": "clans",
		"description": "Operations correlating to getting information about the clans/squadrons of the game War Thunder.",
	},
	{
		"name": "general",
		"description": "Operations correlating to getting general information about the game War Thunder.",
	},
	#{ # TODO: Implement unit information pulling
	#    "name": "units",
	#    "description": "Operations correlating to getting information about the units of the game War Thunder.",
	#}, # Shall be implemented *eventually*, not an urgent job though
	{
		"name": "users",
		"description": "Operations correlating to getting information about the users/players of the game War Thunder.",
	}
]

@asynccontextmanager
async def lifespan(app: FastAPI):
	await users_cache.start()
	try:
		yield
	finally:
		await users_cache.close()

app = FastAPI(
	title="ThunderAPI",
	description="API to retrieve War Thunder data.",
	version="0.0.1",
	openapi_tags=tags_metadata,
	swagger_ui_parameters={"defaultModelsExpandDepth": -1},
	lifespan=lifespan
)
app.include_router(clans_router.router, prefix="/v1")
app.include_router(general_router.router, prefix="/v1")
#app.include_router(units_router.router, prefix="/v1")
app.include_router(users_router.router, prefix="/v1")

def main():

	debug:bool
	# region Debug mode setup
	chdir(path.dirname(path.abspath(__file__)))
	if not load_dotenv(".env"):
		raise FileNotFoundError(".env file could not be loaded.")
	debug = int(getenv("DEBUG_MODE", "0")) == 1
	# endregion
	# region Logging
	def log_namer(default_name:str):
		dirname = path.dirname(default_name)
		filename = path.basename(default_name)
		_, _, date = filename.rpartition(".")
		return path.join(dirname, f"{date}.log")

	logFolder = Path(__file__).parent / "logs"
	logFolder.mkdir(mode=0o755, exist_ok=True)

	logger = logging.getLogger()
	handler = TimedRotatingFileHandler(logFolder / "latest.log", when="midnight", interval=1, utc=True, backupCount=5)
	handler.suffix = "%Y-%m-%d"
	formatter = logging.Formatter(f"%(asctime)s:%(name)-30s:%(funcName)-15s:%(lineno)-3d:%(levelname)-7s:%(message)s", datefmt="%Y-%m-%d %H:%M:%S")
	handler.setFormatter(formatter)
	handler.namer = log_namer
	logger.addHandler(handler)
	logger.setLevel(logging.DEBUG if debug else logging.INFO)
	# endregion

	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)

	logger.info("Starting up")
	try:
		uvicorn_run(app, host=getenv("HOST", "127.0.0.1"), port=int(getenv("PORT", "8001")))
	except:
		logger.exception("An uncaught error occurred during runtime")
	finally:
		logger.info("Shutting down")

if __name__ == '__main__':
	main()