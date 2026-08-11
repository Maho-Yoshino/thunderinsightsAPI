import json as _json
from os import getenv
from typing import Literal, Any, TYPE_CHECKING
from fastapi import HTTPException
from logging import getLogger
from aiohttp import ClientResponse, ClientSession
from requests import get as req_get
from json import loads
from requests.exceptions import JSONDecodeError, SSLError
from datetime import timedelta
from subprocess import run as _run
from random import choice
from templates import TEMPLATES, load as load_template
from .json_to_blk import json_to_blkx, blkx_to_blk, compress_lz4hc, compress_bzip2, find_binblk
from json import dumps
from .hex_to_json import lz4_decompress_try, bzip_decompress_try
from .const import Action, UserAction, ServerPool, GaijinErrorCodes, getAction
from utils import networkManager
if TYPE_CHECKING:
	from utils import UserTokenCache

_logger = getLogger(__name__)

_binblk = find_binblk(getenv("BINBLK_PATH", None))

def blk_to_json(data: bytes) -> dict[str, Any]:
	"""Decode binary .blk (compressed or raw) to a JSON dict via wt_ext_cli."""
	result = _run(
		["wt_ext_cli", "unpack_raw_blk", "--stdin", "--stdout", "--format", "Json"],
		input=data, capture_output=True,
	)
	if result.returncode != 0:
		raise RuntimeError(f"wt_ext_cli failed: {result.stderr.decode()}")
	return _json.loads(result.stdout)

#region Fetch server list once at import
try:
	_resp = req_get("https://public-configs-warthunder-gcore.cdn.gaijin.net/production/network.blk")
except SSLError:
	_resp = req_get("https://public-configs.warthunder.com/production/network.blk")
if not _resp.ok:
	raise RuntimeError(f"Failed to fetch server list: {_resp.status_code}")
_cfg = blk_to_json(_resp.content)["production"]
char_servers: list[str] = _cfg["charServer"]
inv_proxies: list[str] = _cfg["inventory"]["servers"]["url"]
userstat_proxies: list[str] = _cfg["userstat"]["servers"]["url"]
contacts_proxies: list[str] = _cfg["contacts"]["servers"]["url"]
ugc_servers: list[str] = _cfg["ugc_settings"]["ugcServerUrl"]
del _resp, _cfg
if any(len(i) == 0 for i in [char_servers, inv_proxies, userstat_proxies, contacts_proxies, ugc_servers]):
	raise RuntimeError("Server URL lists did not get populated properly")
SERVER_URLS: dict[ServerPool, list[str]] = {
	ServerPool.CHAR: char_servers,
	ServerPool.INVENTORY: inv_proxies,
	ServerPool.USERSTAT: userstat_proxies,
	ServerPool.CONTACTS: contacts_proxies,
	ServerPool.UGC: ugc_servers,
	ServerPool.MARKET_JSON: ["https://market-proxy.gaijin.net/json"],
	ServerPool.MARKET_WEB: ["https://market-proxy.gaijin.net/web"],
	ServerPool.MARKET_CHAR: ["https://market-proxy.gaijin.net/char"],
	ServerPool.MARKET: ["https://market-proxy.gaijin.net/market"],
	ServerPool.MARKET_ASSET: ["https://market-proxy.gaijin.net/assetAPI"],
	ServerPool.VIEW_VEHICLE_PROXY: ["https://login.gaijin.net/proxy/api/matching/notifyClient"],
	ServerPool.WALLET: ["https://wallet.gaijin.net/GetBalance"]
}
def get_server(action: Action|UserAction) -> str:
	return choice(SERVER_URLS[action.value[1]])
#endregion

class Request(dict):
	"""Dict-backed request with headers, wire-format encoding, and .request() shortcut."""
	response:dict[str, Any]|None
	login: UserTokenCache.Entry = None
	session = None
	def __init__(
		self,
		action: Action|UserAction, 
		body: dict[str, Any] | None = None,
		headers: dict[str, Any] | None = None,
		send_format: Literal["json", "blk", "form"]|None = None,
		login: UserTokenCache.Entry = None,
		host:str|None = None,
		method:str = "POST",
		session:ClientSession|None=None
	):
		super().__init__(body if body is not None else {})
		self.headers = {
			"Accept": "*/*",
			"Accept-Encoding": "deflate, gzip, br, zstd",
			"User-Agent": "ThunderAPI/1.0",
			"transactid": "1",
			"platform": "PC",
			"platform_id": "9",
			"comprTypes": "lz4hc;lz4;snappy;bzip2;gzip;vromfs;zstd;zlib"
		}
		if headers:
			self.headers.update(headers)
		self.format = send_format

		if action is None:
			raise RuntimeError("No action provided")
		self.action = action

		if host is not None:
			self.url = host
		else:
			self.url = get_server(self.action)
		self.method = method
		self.login = login
		self.response = None  # Placeholder for storing the response of a request if needed
		self.session = session

	@classmethod
	async def from_template(cls, user:UserTokenCache.Entry, template: str, session:ClientSession|None=None, **data:str|dict[str, Any]) -> "Request":
		if user.timeLeft() <= timedelta(minutes=30):
			await user.refresh()
		if template not in TEMPLATES:
			raise ValueError(f"Unknown template '{template}'. Available: {TEMPLATES}")
		tpl = load_template(template)
		headers = tpl.get("headers", {})
		body = tpl.get("body", {})

		if auth := tpl.get("auth", None):
			if auth == "header":
				headers = await user.add_auth_headers(headers)
			elif auth == "body":
				body = await user.add_auth_headers(body)
			elif auth == "bearer":
				headers = await user.add_auth_headers(headers, True)
		if "action" in tpl:
			action = getAction(tpl["action"])
		elif "action" in headers:
			action = getAction(headers["action"])
		elif "action" in body:
			action = getAction(body["action"])
		else:
			raise RuntimeError(f"No action provided for template {template}")

		self = cls(
			body=body, 
			headers=headers, 
			send_format=tpl.get("format", "json"),
			login=user,
			host=tpl.get("host", None),
			method=tpl.get("method", "POST"),
			action=action,
			session=session
		)
		for key, value in data.items():
			if key.lower() == "body":
				for k, v in value.items():
					self[k] = v
			else:
				self.headers[key] = str(value)
		return self

	@staticmethod
	async def send_template(user:UserTokenCache.Entry, template: str, session:ClientSession|None=None, **data:str|dict[str, Any]) -> dict:
		cls = await Request.from_template(user, template, session=session, **data)
		return await cls.send()

	def _encode(self, compress: Literal["lz4hc", "bzip2"] | None = None) -> bytes:
		blkx = json_to_blkx(self)
		blk = blkx_to_blk(blkx.encode(), _binblk)
		if compress == "lz4hc":
			return compress_lz4hc(blk)
		if compress == "bzip2":
			return compress_bzip2(blk)
		return blk

	async def send(self) -> dict[str, Any]:
		if self.action is None and self.url is None: return
		kwargs: dict[str, Any] = {"headers": self.headers}
		for k, v in self.items():
			if v == "<replace>":
				raise HTTPException(500, f"[{self.action.name}] Body value `{k}` is not replaced by code")
		for header, value in kwargs["headers"].items():
			if value == "<replace>":
				raise HTTPException(500, f"[{self.action.name}] Header value `{k}` is not replaced by code")
			if isinstance(value, (bytes, str)):
				continue
			elif isinstance(value, dict):
				kwargs["headers"][header] = "; ".join(f"{k}={v}" for k, v in value.items())
			else:
				kwargs["headers"][header] = str(value)
		if self.format == "json":
			kwargs["json"] = self
		elif self.format == "form":
			kwargs["headers"]["Content-Type"] = "application/x-www-form-urlencoded"
			if self.url == SERVER_URLS[ServerPool.VIEW_VEHICLE_PROXY][0]:
				kwargs["data"] = dumps(dict(self))
			else:
				kwargs["data"] = dict(self) # TODO: New code
		elif self.format != None:
			compr = self.headers.get("compr", None)
			kwargs["data"] = self._encode(compress=compr)
			kwargs["headers"] = {**self.headers, "Content-Type": "application/octet-stream"}
			if compr:
				kwargs["headers"]["compr"] = compr

		if self.session is None:
			async with networkManager.request(self.method.upper(), self.url, **kwargs) as resp:
				await self._decode(resp)
		else:
			async with self.session.request(self.method.upper(), self.url, **kwargs) as resp:
				await self._decode(resp)
	
		return self.result

	async def _decode(self, response: ClientResponse) -> None:
		"""Decode from compressed or raw .blk binary to json."""
		content = await response.read()
		if content == b"":
			self.result = {}
			return
		if content.startswith(b"!ERROR:"):
			GaijinErrorCodes.parse(content) # Throws an HTTPException
		if content.startswith(b"!OK"):
			self.result = {
				"status": "success"
			}
			return # Nothing to parse
		try:
			self.result = loads(content.decode("utf-8"))
			return # If valid JSON, do not convert
		except (JSONDecodeError, UnicodeDecodeError):
			pass # Not valid JSON, continue on to decompressing and decoding
		except Exception:
			_logger.exception("An exception occurred while decoding the returned binary")
			raise

		# Try lz4hc decompress first, then bzip2
		# if neither worked, it assumes the data is raw blk
		if content[:1] != b"\x01" and len(content) > 4:
			_ = lz4_decompress_try(content)
			if _ is None:
				_ = bzip_decompress_try(content)
			if _ is not None:
				content = _	
		self.result = blk_to_json(content)

	def to_json(self, indent: int | None = 2) -> str:
		return _json.dumps(self, indent=indent, ensure_ascii=False)
