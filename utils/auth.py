from __future__ import annotations
import asyncio
from re import sub as re_sub
from logging import getLogger
from asyncio import sleep
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.job import Job
from aiosqlite import connect, Row, OperationalError
from os import getenv
from datetime import UTC, datetime, timedelta
from aiohttp import ClientSession, ClientResponse, ClientTimeout
from typing import Any
from fastapi import HTTPException
from hashlib import sha256
from secrets import token_urlsafe
from pathlib import Path
from enum import StrEnum
from contextlib import asynccontextmanager
from random import randint
from json import loads

from utils.helper import StringTimeToTimedelta

_logger = getLogger(__name__)

deleteAfter = StringTimeToTimedelta(getenv("DELETE_AFTER"))
checkInterval = StringTimeToTimedelta(getenv("CHECK_INTERVAL"))
refreshIfLessMinutes = int(getenv("REFRESH_IF_LESS_MINS", 15))
if refreshIfLessMinutes > 60:
	raise AssertionError("The env variable REFRESH_IF_LESS_MINS cannot exceed 60 minutes")
if refreshIfLessMinutes <= 0:
	_logger.warning("The env variable REFRESH_IF_LESS_MINS is set to below 1, meaning it will basically never autorefresh the token")

class AuthenticationError(HTTPException):
	def __init__(self, status_code, detail = None, headers = None):
		super().__init__(status_code, detail, headers)
class TwoFactorRequired(AuthenticationError):
	def __init__(self, types: set[str], request_id: str, user_id: int):
		_ = {
			"status": "2STEP",
			"2fa_types": types,
			"details": "Two-factor authentication is required for this account. Please try logging in again, and provide a valid 2FA code, along with the 'requestId' value",
			"requestId": request_id,
			"userId": user_id
		}
		super().__init__(403, _)

# region User Tokens Cache and refresh

class UserTokenCache:
	scheduler: AsyncIOScheduler
	class dbSchema:
		TOKENS = "tokens"
		EXPIRED_TOKENS = "expired_tokens"
		TWO_FACTOR_TOKENS = "two_factor_tokens"
		class Tokens(StrEnum):			
			HASH = "hash_token"
			EMAIL = "email"
			SESSION_TOKEN = "session_token"
			USER_TOKEN = "user_token"
			EXPIRES = "expires"
			UID = "uidHint"
			REQUESTS_CNT = "requests_count"
			LAST_USED = "last_used"
			CREATED = "created_at"
		class ExpiredTokens(StrEnum):
			HASH = "hash_token"
			EMAIL = "email"
			REQUESTS_CNT = "requests_count"
			LAST_USED = "last_used"
			EXPIRED_AT = "expired_at"
		class TwoFactorTokens(StrEnum):
			EMAIL = "email"
			CLIENT_ID = "client_id"
			TRUSTED_AT = "trusted_at"

	class Entry: # Short lived data class with some helper methods
		hashed: str
		session_token: str # Session token
		user_token: str # User token
		expires: datetime # Token Expiration Timestamp
		last_used: datetime # Used for invalidating old tokens
		uidHint: int = -1 # uidHint value for refresh and other auth calls
		email:str # For contact purposes
		requests_count: int = 0 # For token statistics (and to find abuse)

		__saved:dict[str, str|int|datetime] # Saved to file state, used for comparing what to change
	
		def __init__(self, row:Row, parent:'UserTokenCache'):
			p = UserTokenCache.dbSchema.Tokens
			self.hashed = str(row[p.HASH])
			self.session_token = str(row[p.SESSION_TOKEN])
			self.user_token = str(row[p.USER_TOKEN])
			self.expires = datetime.fromtimestamp(int(row[p.EXPIRES]), UTC)
			self.last_used = datetime.fromtimestamp(int(row[p.LAST_USED]), UTC)
			self.requests_count = int(row[p.REQUESTS_CNT])
			self.uidHint = int(row[p.UID])
			self.email = str(row[p.EMAIL])

			self.__parent = parent
			self.__saved = self.to_json()

		async def refresh(self):
			if datetime.now(UTC) > self.expires:
				raise AuthenticationError(401, "Login expired. Please reauthenticate.")
			session = await self.__parent._enter_op()
			try:
				async with session.post(
					"https://auth.gaijinent.com/login_token.php", 
					data={"token": self.user_token}, 
					headers={
						"User-Agent": "ThunderAPI/1.0", 
						"Content-Type": "application/x-www-form-urlencoded"
					}
				) as r:
					content = await self.__parent._handle_response(r)
			finally:
				await self.__parent._exit_op()

			if content.get("status") == "LOGINERROR":
				if content.get("error") == "Wrong token":
					self.expires = datetime.now(UTC)
					return
				raise AuthenticationError(400, f"An error occurred during authentication: {content}")

			self.expires = datetime.now(UTC) + timedelta(seconds=content["token_exp"])
			await self._write_values()
		
		async def add_auth_headers(self, headerData: dict[str, Any]) -> dict[str, Any]:
			if self.timeLeft() <= timedelta(minutes=30):
				await self.refresh()
			if self.session_token:
				
				headerData["token"] = self.session_token
				headerData["uidHint"] = str(self.uidHint)
				headerData["transactid"] = str(randint(0, 999999999999))

				self.last_used = datetime.now(UTC) 
				self.requests_count += 1
				
				await self._write_values()
				
				return headerData
			else:
				raise AuthenticationError(403, "Authentication required for this request, but no token is available. Please ensure you have logged in successfully.")

		def timeLeft(self) -> timedelta:
			return self.expires - datetime.now(UTC)
		def usedWithin(self, minutes:int) -> bool:
			return self.last_used > (datetime.now(UTC) - timedelta(minutes=minutes)) 
		
		async def _write_values(self):
			changed:dict[str, int|str] = {}
			for key, value in self.to_json().items():
				if self.__saved[key] == value: continue
				if isinstance(value, datetime):
					value = round(value.timestamp(), None)
				changed[key] = value
			
			if not changed: # No point running query, no changes made
				return

			async with self.__parent._transaction() as cur:
				p = self.__parent.dbSchema
				await cur.execute(f"""
					UPDATE {p.TOKENS} 
					SET {", ".join([f"{k} = ?" for k in changed.keys()])}
					WHERE {p.Tokens.EMAIL} = ?
				""",
				(
					*changed.values(),
					self.__saved[p.Tokens.EMAIL]
				))

			self.__saved = self.to_json()
		
		def to_json(self) -> dict[str, str|int|datetime]:
			p = self.__parent.dbSchema.Tokens
			return {
				p.HASH: self.hashed,
				p.SESSION_TOKEN: self.session_token,
				p.USER_TOKEN: self.user_token,
				p.EXPIRES: self.expires,
				p.LAST_USED: self.last_used,
				p.UID:self.uidHint,
				p.EMAIL:self.email,
				p.REQUESTS_CNT:self.requests_count
			}
	
	__autorefresh_job:Job = None
	__db_path:Path = None
	__pending_2fa:dict[str, dict[str, int|str|list[str]]] # email -> {requestId, userId, types, code (after answering)}

	def __init__(self):
		self.scheduler = AsyncIOScheduler()
		#region Aiohttp session setup
		self.__session: ClientSession | None = None
		self.__closing = False
		self.__active_ops = 0
		self.__active_ops_done = asyncio.Event()
		self.__active_ops_done.set()
		self.__lock = asyncio.Lock()
		#endregion

		self.__pending_2fa = {}
		self.__db_path = Path(__file__).parent / "database.db"

		_logger.debug("User Token Cache initialized")

	async def get(self, token:str):
		hash = self._hash_token(token)
		async with self._transaction() as cur:
			row = await (await cur.execute(f"SELECT * FROM {self.dbSchema.TOKENS} WHERE {self.dbSchema.Tokens.HASH} = ? AND {self.dbSchema.Tokens.EXPIRES} > strftime('%s', 'now', '+5 minutes')", (hash,))).fetchone()
			if row:
				await cur.execute(f"UPDATE {self.dbSchema.TOKENS} SET {self.dbSchema.Tokens.REQUESTS_CNT} = {self.dbSchema.Tokens.REQUESTS_CNT} + 1, {self.dbSchema.Tokens.LAST_USED} = strftime('%s', 'now') WHERE {self.dbSchema.Tokens.HASH} = ?", (hash,))
				return self.Entry(row, self)
			return None
	async def exists(self, token:str) -> bool:
		hash = self._hash_token(token)
		async with self._transaction() as cur:
			row = await (await cur.execute(f"SELECT 1 FROM {self.dbSchema.TOKENS} WHERE {self.dbSchema.Tokens.HASH} = ? AND {self.dbSchema.Tokens.EXPIRES} > strftime('%s', 'now', '+5 minutes')", (hash,))).fetchone()
			return row is not None
	
	async def login(self, email:str, password:str|None = None):
		"""Adds the user to the database if needed and returns the token for the user"""
		client_id = getenv("MACHINE_ID", "unknown")
		logindata = {
			"login": email,
			"password": password,
			"game": "wt",
			"client": client_id
		}
		session = await self._enter_op()
		try:
			async with session.post(
				"https://auth.gaijinent.com/login.php", 
				data=logindata, 
				headers={
					"Content-Type": "application/x-www-form-urlencoded",
					"User-Agent": "ThunderAPI/1.0"
				}
			) as r:
				data = await self._handle_response(r)

			if data["status"] == "2STEP": # FIXME: Implement 2FA for logging in
				two_factor_types = set()
				if data.get("hasGjPass"): two_factor_types.add("GaijinPass")
				if data.get("hasTwoStepEmail"): two_factor_types.add("Email")
				if data.get("hasWTR"): two_factor_types.add("WTR")
				self.__pending_2fa[email] = {
					"requestId": data['requestId'],
					"userId": data["user_id"],
					"types": two_factor_types 
				}

				# TODO: Implement 2FA Loop for non gaijin pass
				tries = 0
				success = False
				while not success and tries < 10:
					async with session.get(f"https://auth.gaijinent.com/api/auth/requestTwoStep?requestId={data['requestId']}&userId={data['userId']}", timeout=60) as r:
						if "GaijinPass" in two_factor_types:
							try:
								data = await self._handle_response(r)
								success = True
							except AuthenticationError:
								async with session.post(
									"https://auth.gaijinent.com/login.php", 
									data=logindata, 
									headers={
										"Content-Type": "application/x-www-form-urlencoded",
										"User-Agent": "ThunderAPI/1.0"
									}
								) as r:
									data = await self._handle_response(r)
								tries += 1
								continue
						else: # UNTESTED PATH
							if self.__pending_2fa[email].get("code") is None:
								tries += 1
								await sleep(60)
								continue
							data = {
								"Message": self.__pending_2fa[email]["code"],
								"Request": self.__pending_2fa[email]["requestId"]
							}
							success = True
				if not success:
					raise AuthenticationError(403, "Could not get 2FA login in time")
				async with session.post(
					"https://auth.gaijinent.com/login.php",
					data={
						"login": email,
						"password": password,
						"game": "wt",
						"2step": data["Message"],
						"requestId": data["Request"],
						"client": client_id
					},
					headers={
						"Content-Type": "application/x-www-form-urlencoded",
						"User-Agent": "ThunderAPI/1.0"
					}
				) as r:
					data = await self._handle_response(r)

				if data["status"] == "2STEPERROR":
					self.__pending_2fa.pop(email, None)
					raise AuthenticationError(403, "Invalid 2FA code provided.")
		finally:
			await self._exit_op()
		if data["status"] == "LOGINERROR":
			raise HTTPException(400, f"Login failed: {data["error"]}")
		async with self._transaction() as cur:
			_ = self.dbSchema.Tokens
			raw, hash = self._generate_hash()
			rn_timestamp = round(datetime.now(UTC).timestamp())
			if await (await cur.execute(f"SELECT 1 FROM {self.dbSchema.TOKENS} WHERE {_.EMAIL} = ?", (email,))).fetchone() is not None:
				_logger.info(f"Overwriting old entry for {email}")
				await cur.execute(f"""
					UPDATE {self.dbSchema.TOKENS} 
					SET {_.HASH} = ?, {_.SESSION_TOKEN} = ?, {_.USER_TOKEN} = ?, {_.EXPIRES} = ?, {_.UID} = ?, {_.LAST_USED} = ? WHERE {_.EMAIL} = ?""", 
					(hash, data["jwt"], data["token"], rn_timestamp + data["token_exp"], data["user_id"], rn_timestamp, email)
				)
			else:
				await cur.execute(f"""
					INSERT INTO {self.dbSchema.TOKENS} ({_.HASH}, {_.SESSION_TOKEN}, {_.USER_TOKEN}, {_.EXPIRES}, {_.UID}, {_.EMAIL}, {_.LAST_USED}) 
					VALUES ({', '.join(["?" for i in range(7)])})""", 
					(hash, data["jwt"], data["token"], rn_timestamp + data["token_exp"], data["user_id"], email, rn_timestamp)
				)		
		return raw
	# region Helpers
	async def _refresh(self):
		self.__pending_2fa = {k:v for k,v in self.__pending_2fa.items() if v["expires"] > round(datetime.now(UTC).timestamp(), 0)}
		p = self.dbSchema
		async with self._transaction() as cur:
			rows = await (await cur.execute(f"SELECT * FROM {p.TOKENS} WHERE {p.Tokens.EXPIRES} > strftime('%s', 'now')")).fetchall()
		for row in rows:
			entry = self.Entry(row, self)
			try:
				if entry.usedWithin(30):
					await entry.refresh()
			except AuthenticationError:
				await cur.execute(
					f"DELETE FROM {p.TOKENS} WHERE {p.Tokens.HASH} = ?", 
					(entry.hashed,)
				)
				await cur.execute(
					f"""
					INSERT INTO {p.EXPIRED_TOKENS}
					({p.ExpiredTokens.EMAIL}, {p.ExpiredTokens.EXPIRED_AT}, {p.ExpiredTokens.HASH}, {p.ExpiredTokens.LAST_USED}, {p.ExpiredTokens.REQUESTS_CNT})
					VALUES (?, ?, ?, ?, ?)
					""",
					(
						entry.email,
						round(entry.expires.timestamp()),
						entry.hashed,
						round(entry.last_used.timestamp()),
						entry.requests_count
					)
				)
				_logger.info(f"Removed expired entry for {entry.email}")
		async with self._transaction() as cur:
			await cur.execute(f"DELETE FROM {p.TOKENS} WHERE {p.Tokens.EXPIRES} <= strftime('%s', 'now')")
		
	def _generate_hash(self) -> tuple[str, str]:
		raw_token = token_urlsafe(32)
		return raw_token, sha256(raw_token.encode()).hexdigest()
	def _hash_token(self, raw_token:str) -> str:
		return sha256(raw_token.encode()).hexdigest()

	@asynccontextmanager
	async def _transaction(self):
		con = await connect(self.__db_path)
		con.row_factory = Row
		try:
			cur = await con.cursor()
			try:
				yield cur
				await con.commit()
			except Exception:
				await con.rollback()
				raise
			finally:
				await cur.close()
		finally:
			await con.close()
	
	async def start(self):
		async with self.__lock:
			if self.__session is not None and not self.__session.closed:
				return
			self.__closing = False
			self.__session = ClientSession()

		await self._init_db()
		if self.__autorefresh_job is None:
			self.__autorefresh_job = self.scheduler.add_job(
				self._refresh,
				IntervalTrigger(minutes=10)
			)
		if not self.scheduler.running:
			self.scheduler.start()

	async def close(self):
		async with self.__lock:
			self.__closing = True

		if self.__autorefresh_job is not None:
			self.__autorefresh_job.remove()
			self.__autorefresh_job = None
		if self.scheduler.running:
			self.scheduler.shutdown(wait=True)

		await self.__active_ops_done.wait()

		async with self.__lock:
			if self.__session is not None and not self.__session.closed:
				await self.__session.close()
			self.__session = None

	async def _enter_op(self):
		async with self.__lock:
			if self.__closing:
				raise RuntimeError("UserTokenCache is shutting down")

			if self.__session is None or self.__session.closed:
				raise RuntimeError("UserTokenCache is not started")

			self.__active_ops += 1
			self.__active_ops_done.clear()

			return self.__session

	async def _exit_op(self):
		async with self.__lock:
			self.__active_ops -= 1

			if self.__active_ops <= 0:
				self.__active_ops = 0
				self.__active_ops_done.set()

	async def _handle_response(self, resp:ClientResponse) -> dict[str, Any]:
		text = await resp.text()

		if resp.status >= 400:
			raise AuthenticationError(400, f"Request failed: {resp.status} {text}")
		if text.startswith("!ERROR"):
			raise AuthenticationError(400, f"Request failed: {text}")

		return loads(text)

	async def _init_db(self):
		if self.__db_path.exists():
			return

		init_script = self.__db_path.parent / "db_create.sql"
		self.__db_path.touch()

		try:
			async with connect(self.__db_path) as con:
				lines = re_sub("--.*\n", "", init_script.read_text()).replace("\n", "").split(";")

				for line in lines:
					line = line.strip()
					if not line:
						continue

					await con.execute(line + ";")

				await con.commit()

			_logger.debug("Database successfully initialized")

		except OperationalError:
			self.__db_path.unlink()
			_logger.exception("An error occurred during database setup")
			raise
	#endregion

users_cache = UserTokenCache()