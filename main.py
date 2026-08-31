from dotenv import load_dotenv
if not load_dotenv(".env"):
	raise FileNotFoundError(".env file could not be loaded.")

import logging, asyncio
from logging.handlers import TimedRotatingFileHandler
from fastapi import FastAPI, status
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from slowapi.errors import RateLimitExceeded
from uvicorn import run as uvicorn_run
from os import getenv, path
from pathlib import Path
from contextlib import asynccontextmanager
from dataclasses import dataclass, asdict

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

from utils import users_cache, networkManager, newsManager
from api import users_router, clans_router, general_router, auth_router, units_router, replays_router, marketplace_router
from api.shared import limiter

logger = logging.getLogger()
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)

tags_metadata = [
	{
		"name": "authentication",
		"description": "Operations used to authenticate with the API, and get or refresh a token to use in other endpoints."
	},
	{
		"name": "clans",
		"description": "Operations correlating to clans/squadrons.",
	},
	{
		"name": "general",
		"description": "Operations to get general information.",
	},
	#{
	#    "name": "units",
	#    "description": "Operations correlating to getting information about the units of the game War Thunder.",
	#},
	{
		"name": "users",
		"description": "Operations to get information about the users/players.",
	},
	{
		"name": "replays",
		"description": "Operations to get information about replays.",
	},
	{
		"name": "marketplace",
		"description": "Operations to get information about the marketplace.",
	}
]

@asynccontextmanager
async def lifespan(app: FastAPI):
	await users_cache.start()
	await networkManager.start()
	newsManager.task = asyncio.create_task(newsManager.mainloop())

	try:
		yield
	finally:
		newsManager.task.cancel()
		try:
			await newsManager.task
		except asyncio.CancelledError:
			pass
		await users_cache.close()
		await networkManager.close()

app = FastAPI(
	title="ThunderAPI",
	description="API to retrieve War Thunder data.",
	version="1.0.0",
	openapi_tags=tags_metadata,
	lifespan=lifespan,
	redoc_url=None,
	docs_url=None
)

#region Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(
	RateLimitExceeded, 
	lambda request, exc: (
		logging.warning(f"Rate limit exceeded for {request.client.host}"), 
		JSONResponse({"detail": "Rate limit exceeded"}, status_code=status.HTTP_429_TOO_MANY_REQUESTS)
	)[1]
)
#endregion

#region Add routers
app.include_router(auth_router.router, prefix="/v1")
app.include_router(clans_router.router, prefix="/v1")
app.include_router(general_router.router, prefix="/v1")
#app.include_router(units_router.router, prefix="/v1")
app.include_router(users_router.router, prefix="/v1")
app.include_router(replays_router.router, prefix="/v1")
app.include_router(marketplace_router.router, prefix="/v1")
#endregion

#region Modify OpenAPI schema
@dataclass(slots=True)
class WebSocketInfo:
	tags: list[str]
	summary: str
	description: str

	def to_json(self):
		return asdict(self)
websockets: dict[str, WebSocketInfo] = {
	"/v1/news_ws": WebSocketInfo(
		tags = ["general"],
		summary = "Live news feed",
		description = "Sends the newest news article every time a new one is posted"
	)
}
def custom_openapi():
	if app.openapi_schema: # If already modified
		return app.openapi_schema

	openapi_schema = get_openapi(
		title=app.title,
		version=app.version,
		description=app.description,
		routes=app.routes,
		tags=app.openapi_tags,
	)

	for path in openapi_schema["paths"].values():
		for method in path.values():
			method["responses"].pop("422", None)

	for route in app.routes:
		ws_data = websockets.get(route.path)
		if ws_data is None:
			continue

		openapi_schema["paths"].setdefault(route.path, {})
		openapi_schema["paths"][route.path]["x-websocket"] = ws_data.to_json()

	app.openapi_schema = openapi_schema
	return app.openapi_schema

app.openapi = custom_openapi
#endregion

#region Modify Documentation page
swagger_docs = None
@app.get("/docs", include_in_schema=False)
@app.get("/", include_in_schema=False)
def custom_swagger_ui():
	global swagger_docs
	if swagger_docs:
		return HTMLResponse(swagger_docs)

	page = get_swagger_ui_html(
		openapi_url=app.openapi_url,
		title=f"{app.title} - Swagger UI",
		swagger_ui_parameters={"defaultModelsExpandDepth": -1},
	)

	html = page.body.decode("utf-8")

	websocket_script = (Path(__file__).parent / "swagger_ui_modify.js").read_text()
	html = html.replace("</body>", "<script>"+websocket_script+"</script></body>")

	websocket_css = (Path(__file__).parent / "swagger_ui_modify.css").read_text()
	html = html.replace("</head>", "<style>"+websocket_css+"</style></head>")

	swagger_docs = html
	return HTMLResponse(html)
#endregion
#region Privacy Policy
@app.get("/privacy")
def privacy_policy():
	return RedirectResponse("https://github.com/Order-Of-The-Birb/ThunderAPI/README.md#privacy-policy", status.HTTP_301_MOVED_PERMANENTLY)
#endregion

def main():

	debug = int(getenv("DEBUG_MODE", "0")) == 1
	# region Logging
	def log_namer(default_name:str):
		dirname = path.dirname(default_name)
		filename = path.basename(default_name)
		_, _, date = filename.rpartition(".")
		return path.join(dirname, f"{date}.log")

	logFolder = Path(__file__).parent / "logs"
	logFolder.mkdir(mode=0o755, exist_ok=True)

	handler = TimedRotatingFileHandler(logFolder / "latest.log", when="midnight", interval=1, utc=True, backupCount=5)
	handler.suffix = "%Y-%m-%d"
	formatter = logging.Formatter(f"%(asctime)s:%(name)-30s:%(funcName)-15s:%(lineno)-3d:%(levelname)-7s:%(message)s", datefmt="%Y-%m-%d %H:%M:%S")
	handler.setFormatter(formatter)
	handler.namer = log_namer
	logger.addHandler(handler)
	logger.setLevel(logging.DEBUG if debug else logging.INFO)
	# endregion

	logger.info("Starting up")
	try:
		uvicorn_run(app, host=getenv("HOST", "127.0.0.1"), port=int(getenv("PORT", "8001")))
	except Exception:
		logger.exception("An uncaught error occurred during runtime")
	finally:
		logger.info("Shutting down")

if __name__ == '__main__':
	main()