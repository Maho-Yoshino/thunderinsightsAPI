from typing_extensions import Annotated
from typing import Literal, Any
from fastapi import APIRouter, Query, Form, Path, HTTPException
from fastapi.responses import JSONResponse
from utils.auth import users_cache
from utils.replayParser import Replay
from datetime import datetime, UTC
from pydantic import EmailStr
from bs4 import BeautifulSoup, Tag
from enum import IntEnum
from api.models import NewsResponse, LoginResponse, LoginFail2FAResponse, ReplayDataModel, ReplayNotFoundModel
from api.shared import TokenString 
from utils.helper import dtToTimestamp

router = APIRouter(
	tags=["general"],
	responses={404: {"description": "Not found"}}
)

@router.post(
	"/login", 
	summary="Get a token to use in other endpoints", 
	description="You can use this token for the `POST` endpoints, which are user-specific. If given user has 2FA enabled, they must provide the 2FA code along with their credentials. If you generated a token that hasn't expired yet, the endpoint will just give back the cached token.",
	responses={
		200: {"model": LoginResponse},
		403: {"model": LoginFail2FAResponse, "description": "Unauthorized. Account has 2FA enabled, and needs to go through the 2FA process."}
	}
)
async def login_post(
	email: Annotated[EmailStr, Form()],
	password: Annotated[str, Form(min_length=6, max_length=64)]
):
	token = await users_cache.login(email, password)

	return JSONResponse({
		"status": "OK",
		"token": token
	}, status_code=200)

@router.post(
	"/refresh-token", 
	summary="Refresh your token so it stays alive for longer. This is essentially a 'No op', just to keep the token active.",
	description="If you are cached it will refresh the token. The game generally refreshes the token every 30 minutes. Returns an UNIX timestamp of the new token expiry"
)
async def login_token(token: TokenString) -> int:
	entry = await users_cache.get(token)
	await entry.refresh()
	return dtToTimestamp(entry.expires)

@router.post(
	"/answer-2fa"
)
async def answer_2fa(
	email: EmailStr,
	code: Annotated[int, Form(title="The 2FA code")]
):
	if email not in users_cache:
		raise HTTPException(401, "You are not pending ")
	users_cache.__pending_2fa[email]["code"] = code
	... # TODO: Implement

@router.get("/latestGameVersion", summary="Get latest game version")
async def get_latest_game_ver(
	branch: Annotated[Literal["dev", "dev-stable"], Query(title="The game version to get")] = None
) -> str:
	if branch is None: branch = ""
	session = await users_cache._enter_op()
	try:
		_ = await session.get(f"https://yupmaster.gaijinent.com/yuitem/get_version.php?proj=warthunder&tag={branch}")
		_ = await _.text()
	finally:
		await users_cache._exit_op()
	return _

#region /v1/news
class NewsObj:
	"""
	# Example Input dictionary with required elements
	```
	{
			   "id": 9862,
			   "anons": "...",
			   "title": "...",
			   "link": "https://warthunder.com/en/news/9862-planned-technical-works-on-16122025-en",
			   "images": [
				   {
					   "src": "https://staticfiles.warthunder.com/upload/image/0_2022_Anons/Ground/tank13_TW_Anons_831ad679a7237ed6886bfc1267b44e51.png",
					   "width": 0,
					   "height": 0
				   }
			   ],
			   "type": "news",
			   "created": "2025-12-15T17:21:00+0000"
		   }
	```
	"""
	id:int
	anons:str # Short description
	title:str # Title
	link:str # URL
	pinned:bool
	images:list['Image'] # Attached images
	tags:list[Literal["Event", "Development", "Video", "Shop", "Fixed", "eSport", "Market", "Special", "Warbonds", "Fair Play", "Update"]] # Attached tags
	platforms:list[str] # Affected platforms
	project:str # Game (100% of the time War Thunder with different version numbers) 
	type:Literal["news", "changelog"] # Article Type
	created:datetime # Article Creation Time
	importance:ImportanceLevel
	class ImportanceLevel(IntEnum):
		REGULAR = 0
		MINOR = 1
		EVENT = 2
		MAJOR = 3
	class Image:
		def __init__(self, item:dict):
			self.src:str = item['src']
			self.width:int = int(item['width'])
			self.height:int = int(item['height'])
		def to_json(self) -> dict[str, str|int]:
			return {
				"src": self.src,
				"width": self.width,
				"height": self.height
			}
	def __init__(self, item:dict[str, Any]):
		self.id = int(item['id'])
		self.anons = item['anons'] 
		self.title = item['title']
		self.link = item['link']
		self.pinned = item.get('pinned', False)
		self.images = [self.Image(i) for i in item['images']]
		self.tags = item.get('tags', [])
		self.platforms = item.get('platforms', [])
		self.project = item.get('project', "warthunder_en")
		self.type = item['type']
		self.created = datetime.strptime(item['created'], "%Y-%m-%dT%H:%M:%S%z")
		self.importance = self._getImportant()
	def _getImportant(self) -> ImportanceLevel:
		title = self.title.lower()
		if (
				(
					"Video" in self.tags and 
					(
						"trailer" in title or 
						"teaser" in title
					) 
				) or 
				(
					("Shop" in self.tags or "Event" in self.tags) and
					(
						(
							(
								any(i in title for i in ["winter", "summer", "may", "holiday"]) or 
								("war thunder" in title and "birthday" in title)
							) and
							any(i in title for i in ["sale", "discount", "celebrate"])  
						) or
						"black friday" in title
					)
				)
			):
			return self.ImportanceLevel.MAJOR
		if ("Event" in self.tags and "pages" not in title):
			return self.ImportanceLevel.EVENT
		if ("discount" in title and ("Shop" in self.tags or "Special" in self.tags)):
			return self.ImportanceLevel.MINOR
		return self.ImportanceLevel.REGULAR
	@classmethod
	def from_changelog(self, chlog:Tag) -> "NewsObj":
		ChLogURL:str = chlog.select_one("a.widget__link")["href"]
		content = chlog.select_one("div.widget__content")
		title = content.select_one("div.widget__title").get_text(strip=True)
		anons = content.select_one("div.widget__comment").get_text(strip=True)
		datetext = content.select_one("ul.widget__meta.widget-meta").select_one("li.widget-meta__item.widget-meta__item--right").get_text(strip=True)
		date = datetime.strptime(datetext, "%d %B %Y").replace(tzinfo=UTC).strftime("%Y-%m-%dT%H:%M:%S%z")
		del datetext
		src = chlog.select_one("div.widget__poster>img").attrs["data-src"]
		pinned = chlog.select_one("div.widget__pin") is not None
		return NewsObj({
			"id":int(ChLogURL.split("/")[-1]),
			"anons":anons,
			"title":title,
			"link":f"https://warthunder.com{ChLogURL}",
			"tags":["Update"],
			"images":[{
				"src":src,
				"width": 0,
				"height": 0
			}],
			"type":"Changelog",
			"created":date,
			"pinned": pinned
		})
	def to_json(self):
		return {
			"id": self.id,
			"anons": self.anons,
			"title": self.title,
			"link": self.link,
			"pinned": self.pinned,
			"images": [i.to_json() for i in self.images],
			"tags": self.tags,
			"platforms": self.platforms,
			"project": self.project,
			"type": self.type,
			"created": self.created.strftime("%Y-%m-%dT%H:%M"),
			"importance": self.importance,
		}

@router.get("/news", summary="Gets the latest news from gaijin", description="Puts the pinned news first (Current update changelog + latest big news)")
async def get_news() -> list[NewsResponse]:
	session = await users_cache._enter_op() 
	r1 = await session.get("http://newslist.gaijin.net:8080/news/warthunder/en/js")
	r1_news:list[NewsObj] = []
	for news in r1.json()["items"]:
		r1_news.append(NewsObj(news))

	r2 = await session.get("https://warthunder.com/en/game/changelog/")
	changelogs = BeautifulSoup(r2.text(), 'html.parser').select("div.showcase__content-wrapper>div.showcase__item.widget")
	await users_cache._exit_op()
	r2_news:list[NewsObj] = []
	for news in changelogs:
		r2_news.append(NewsObj.from_changelog(news))

	pinned:list[NewsObj] = []
	unpinned:list[NewsObj] = []
	for news in r1_news:
		if news.pinned:
			pinned.append(news)
		else:
			unpinned.append(news)
	for news in r2_news:
		if news.pinned:
			pinned.append(news)
		else:
			unpinned.append(news)

	pinned.sort(key=lambda x: x.created, reverse=True)
	unpinned.sort(key=lambda x: x.created, reverse=True)
	combined = pinned + unpinned
	return JSONResponse([i.to_json() for i in combined])
#endregion

@router.get(
	"/replay/{replayId}", 
	summary="Gets data from a specified replay",
	responses={
		200: {"model": ReplayDataModel},
		404: {"model": ReplayNotFoundModel, "description": "Replay not found"}
	})
async def get_replay(
	replayId: Annotated[
		str, 
		Path(
			title="The replay's ID to get",
			pattern=r"^#?[0-9a-fA-F]{1,16}$",
			description="Must be given in HEX format"
		)
]):
	return await Replay.get(replayId)