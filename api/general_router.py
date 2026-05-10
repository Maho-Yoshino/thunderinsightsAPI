from typing_extensions import Annotated
from typing import Literal, Any
from fastapi import APIRouter, Path, Query, Form, HTTPException
from fastapi.responses import JSONResponse
from .shared import get_request, token_cache, get_cached_entry
from requests import get as requests_get
from utils.auth import login, __refresh_token
from datetime import datetime, timedelta, UTC
from pydantic import EmailStr
from bs4 import BeautifulSoup, Tag
from enum import IntEnum
from .models import LoginResponse, NewsResponse

router = APIRouter(
	tags=["general"],
	responses={404: {"description": "Not found"}}
)


@router.post(
	"/login", 
	summary="Get token from War Thunder directly", 
	description="You can use this token for the `POST` endpoints, which are user-specific. Given user must not have 2FA enabled, because it is not supported as of now. If you generated a token that hasn't expired yet, the endpoint will just give back the cached token."
)
def login_post(
	email: Annotated[EmailStr, Form()],
	password: Annotated[str, Form(min_length=6, max_length=64)],
	#two_factor_code: Annotated[int, Form(min_length=6, max_digits=6)] = None
) -> LoginResponse:
	for _email, data in dict(token_cache).items():
		if datetime.now(UTC) >= datetime.fromtimestamp(token_cache[_email]["expires"], UTC):
			token_cache.pop(_email)
	if email in token_cache:
		return JSONResponse(token_cache[email])
	data = login(email, password)
	token_cache[email] = {
		"session_token": data["jwt"],
		"user_token": data["token"],
		"expires": round((datetime.now(UTC) + timedelta(seconds=data["expires"])).timestamp(), 0),
		"uidHint": data["uid"]
	}
	return JSONResponse(token_cache[email])

@router.post(
	"/refresh-token", 
	summary="Refresh your token so it stays alive for longer.",
	description="If you are cached it will use the email to find the token. The game generally refreshes the token every 30 minutes."
)
def login_token(
	user_token: Annotated[str, Form()]
) -> None|LoginResponse:
	email = get_cached_entry(user_token)["email"]
	data = __refresh_token(token_cache[email])
	token_cache[email]["expires"] = round((datetime.now(UTC) + timedelta(seconds=data["expires"])).timestamp(), 0) 
	return token_cache[email]
@router.get("/latestGameVersion", summary="Get latest game version")
def get_latest_game_ver(
	branch: Annotated[Literal["dev", "dev-stable"], Query(title="The game version to get")] = None
) -> str:
	if branch is None: branch = ""
	_ = requests_get(f"https://yupmaster.gaijinent.com/yuitem/get_version.php?proj=warthunder&tag={branch}")
	return _.text 

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
def get_news() -> list[NewsResponse]:
	r1 = requests_get("http://newslist.gaijin.net:8080/news/warthunder/en/js")
	r1_news:list[NewsObj] = []
	for news in r1.json()["items"]:
		r1_news.append(NewsObj(news))

	r2 = requests_get("https://warthunder.com/en/game/changelog/")
	changelogs = BeautifulSoup(r2.text, 'html.parser').select("div.showcase__content-wrapper>div.showcase__item.widget")
	r2_news:list[NewsObj] = []
	for news in changelogs:
		r2_news.append(NewsObj.from_changelog(news))

	pinned:list[NewsObj] = [i for i in r1_news if i.pinned] + [i for i in r2_news if i.pinned]
	unpinned:list[NewsObj] = [i for i in r1_news if not i.pinned] + [i for i in r2_news if not i.pinned]
	pinned.sort(key=lambda x: x.created, reverse=True)
	unpinned.sort(key=lambda x: x.created, reverse=True)
	combined = pinned + unpinned
	return JSONResponse([i.to_json() for i in combined])
#endregion