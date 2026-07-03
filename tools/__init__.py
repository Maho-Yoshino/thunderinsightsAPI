import json as _json
from os import getenv
from typing import Literal, Any
from logging import getLogger
from aiohttp import ClientResponse
from requests import get as req_get
from json import loads
from requests.exceptions import JSONDecodeError
from subprocess import run as _run
from random import choice
from fastapi import HTTPException
from utils.auth import UserTokenCache
from templates import TEMPLATES, load as load_template
from .json_to_blk import json_to_blkx, blkx_to_blk, compress_lz4hc, compress_bzip2, find_binblk
from .hex_to_json import lz4_decompress_try, bzip_decompress_try
from .const import Action, UserAction, ServerPool
from utils.auth import users_cache

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
_resp = req_get("https://public-configs-warthunder-gcore.cdn.gaijin.net/production/network.blk")
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
}
def get_server(action: str) -> str:
	try:
		action = Action[action].value
	except KeyError:
		action = UserAction[action].value
	return choice(SERVER_URLS[action[1]])
#endregion

class Request(dict):
	"""Dict-backed request with headers, wire-format encoding, and .request() shortcut."""
	response:dict[str, Any]|None
	login: UserTokenCache.Entry = None
	def __init__(
		self,
		body: dict[str, Any] | None = None,
		headers: dict[str, Any] | None = None,
		send_format: Literal["json", "blk"]|None = None,
		login: UserTokenCache.Entry = None
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
		self.action = self.headers.get("action", None)
		self.url = get_server(self.action)
		self.login = login
		self.response = None  # Placeholder for storing the response of a request if needed

	@classmethod
	async def from_template(cls, login:UserTokenCache.Entry, name: str) -> "Request":
		if name not in TEMPLATES:
			raise ValueError(f"Unknown template '{name}'. Available: {TEMPLATES}")
		tpl = load_template(name)
		headers = tpl.get("headers", {})
		if tpl.get("auth", False):
			headers = await login.add_auth_headers(headers)
		return cls(
			body=tpl.get("body"), 
			headers=tpl.get("headers"), 
			send_format=tpl.get("format", "json"),
			login=login
		)

	def _encode(self, compress: Literal["lz4hc", "bzip2"] | None = None) -> bytes:
		blkx = json_to_blkx(self)
		blk = blkx_to_blk(blkx.encode(), _binblk)
		if compress == "lz4hc":
			return compress_lz4hc(blk)
		if compress == "bzip2":
			return compress_bzip2(blk)
		return blk

	async def send(self) -> dict[str, Any]:
		if self.action is None and url is None: return
		kwargs: dict[str, Any] = {"headers": self.headers}
		for header, value in kwargs["headers"].items():
			if isinstance(value, (bytes, str)):
				continue
			kwargs["headers"][header] = str(value)
		url = get_server(self.action)
		if self.format == "json":
			kwargs["json"] = self
		elif self.format != None:
			compr = self.headers.get("compr", None)
			kwargs["data"] = self._encode(compress=compr)
			kwargs["headers"] = {**self.headers, "Content-Type": "application/octet-stream"}
			if compr:
				kwargs["headers"]["compr"] = compr
		kwargs["headers"]["token"] = self.login.session_token
		kwargs["headers"]["uidHint"] = str(self.login.uidHint)

		async with self.login.__parent.operation() as session:
			resp = await session.post(url, **kwargs)
			await self._decode(resp)

		return self.result

	async def _decode(self, response: ClientResponse) -> None:
		"""Decode from compressed or raw .blk binary to json."""
		content = await response.read()
		if content.startswith(b"!ERROR:"):
			raise HTTPException(status_code=500, detail=str(content))
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
