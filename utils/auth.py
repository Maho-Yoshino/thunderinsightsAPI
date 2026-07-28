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
from aiohttp import ClientSession, ClientResponse
from typing import Any
from fastapi import HTTPException
from hashlib import sha256
from secrets import token_urlsafe
from pathlib import Path
from enum import StrEnum
from contextlib import asynccontextmanager
from random import randint
from json import loads
from jwt import decode as jwt_decode
from dataclasses import dataclass

from utils.helper import StringTimeToTimedelta, dtToTimestamp

_logger = getLogger(__name__)

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

@dataclass(frozen=True, slots=True)
class jwtData:
	auth: str
	cntry: str
	exp: datetime
	fac: str
	iat: datetime
	lng: str
	loc: str
	nick: str
	slt: str
	tgs: tuple[str]
	uid: int
	extras: dict[str, Any]

def jwt_get_data(jwt:str) -> jwtData:
	data = jwt_decode(jwt, options={"verify_signature": False})
	return jwtData(
		data["auth"],
		data["cntry"],
		datetime.fromtimestamp(data["exp"], UTC),
		data["fac"],
		datetime.fromtimestamp(data["iat"], UTC),
		data["lng"],
		data["loc"],
		data["nick"],
		data["slt"],
		tuple(data["tgs"].split(",")),
		data["uid"],
		extras={k:v for k, v in data.items() if k not in ["auth","cntry","exp","fac","iat","lng","loc","nick","slt","tgs","uid"]}
	)
# region User Tokens Cache and refresh

class UserTokenCache:
	scheduler: AsyncIOScheduler
	class dbSchema(StrEnum):
		TABLE = "tokens"
		HASH = "hash_token"
		EMAIL = "email"
		JWT = "jwt"
		JWT_EXPIRES = "jwt_expires"
		USER_TOKEN = "token"
		UID = "uidHint"
		REQUESTS_CNT = "requests_count"
		LAST_USED = "last_used"
		CREATED = "created_at"

	class Entry: # Short lived data class with some helper methods
		hashed: str
		jwt: str # Session token
		jwt_expires: datetime # Inferred from jwt
		session_token_expires: datetime # Session token expiry
		user_token: str # User token
		last_used: datetime # Used for invalidating old tokens
		uidHint: int = -1 # uidHint value for refresh and other auth calls
		email:str # For contact purposes
		requests_count: int = 0 # For token statistics (and to find abuse)

		__saved:dict[str, str|int|datetime] # Saved to file state, used for comparing what to change
	
		def __init__(self, row:Row, parent:'UserTokenCache'):
			p = UserTokenCache.dbSchema
			self.hashed = str(row[p.HASH])
			self.jwt = str(row[p.JWT])
			self.jwt_expires = jwt_get_data(self.jwt)
			self.user_token = str(row[p.USER_TOKEN])
			self.last_used = datetime.fromtimestamp(int(row[p.LAST_USED]), UTC)
			self.requests_count = int(row[p.REQUESTS_CNT])
			self.uidHint = int(row[p.UID])
			self.email = str(row[p.EMAIL])

			self.__parent = parent
			self.__saved = self.to_json()

		async def refresh(self):
			if datetime.now(UTC) > self.jwt_expires:
				raise AuthenticationError(401, "Login expired. Please reauthenticate.")

			async with self.__parent.operation() as session:
				async with session.post(
					"https://auth.gaijinent.com/login_token.php", 
					data={"token": self.user_token}, 
					headers={
						"User-Agent": "ThunderAPI/1.0", 
						"Content-Type": "application/x-www-form-urlencoded"
					}
				) as r:
					content = await self.__parent._handle_response(r)

			if content.get("status") == "LOGINERROR":
				if content.get("error") == "Wrong token":
					self.expires = datetime.now(UTC)
					return
				raise AuthenticationError(400, f"An error occurred during authentication: {content}")

			if self.jwt_expires != content["jwt"]:
				self.jwt = content["jwt"]
				self.jwt_expires = jwt_get_data(self.jwt).exp
			await self._write_values()
		
		async def add_auth_headers(self, headerData: dict[str, Any]) -> dict[str, Any]:
			if self.timeLeft() <= timedelta(minutes=30):
				await self.refresh()
			if self.jwt:
				
				headerData["token"] = self.jwt
				headerData["uidHint"] = str(self.uidHint)
				headerData["transactid"] = str(randint(0, 999999999999))

				self.last_used = datetime.now(UTC) 
				self.requests_count += 1
				
				await self._write_values()
				
				return headerData
			else:
				raise AuthenticationError(403, "Authentication required for this request, but no token is available. Please ensure you have logged in successfully.")

		def timeLeft(self) -> timedelta:
			return self.jwt_expires - datetime.now(UTC)
		def usedWithin(self, minutes:int) -> bool:
			return self.last_used > (datetime.now(UTC) - timedelta(minutes=minutes)) 
		
		async def _write_values(self):
			changed:dict[str, int|str] = {}
			for key, value in self.to_json().items():
				if self.__saved[key] == value: continue
				if isinstance(value, datetime):
					value = dtToTimestamp(value)
				changed[key] = value
			
			if not changed: # No point running query, no changes made
				return

			async with self.__parent._transaction() as cur:
				p = self.__parent.dbSchema
				await cur.execute(f"""
					UPDATE {p.TABLE} 
					SET {", ".join([f"{k} = ?" for k in changed.keys()])}
					WHERE {p.EMAIL} = ?
				""",
				(
					*changed.values(),
					self.__saved[p.EMAIL]
				))

			self.__saved = self.to_json()
		
		def to_json(self) -> dict[str, str|int|datetime]:
			p = self.__parent.dbSchema
			return {
				p.HASH: self.hashed,
				p.JWT: self.jwt,
				p.JWT_EXPIRES: self.jwt_expires,
				p.USER_TOKEN: self.user_token,
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
		self.__db_path = Path(__file__).parent / "users.db"

		_logger.debug("User Token Cache initialized")

	async def get(self, token:str):
		schema = self.dbSchema
		hash = self._hash_token(token)
		async with self._transaction() as cur:
			row = await (await cur.execute(f"SELECT * FROM {schema.TABLE} WHERE {schema.HASH} = ? AND {schema.JWT_EXPIRES} > strftime('%s', 'now', '+5 minutes')", (hash,))).fetchone()
			if row:
				await cur.execute(f"UPDATE {schema.TABLE} SET {schema.REQUESTS_CNT} = {schema.REQUESTS_CNT} + 1, {schema.LAST_USED} = strftime('%s', 'now') WHERE {schema.HASH} = ?", (hash,))
				return self.Entry(row, self)
			return None
	
	async def login(self, email:str, password:str|None = None):
		"""Adds the user to the database if needed and returns the token for the user"""
		client_id = getenv("MACHINE_ID", "unknown")
		logindata = {
			"login": email,
			"password": password,
			"game": "wt",
			"client": client_id
		}
		
		async with self.operation() as session:
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

		if data["status"] == "LOGINERROR":
			raise HTTPException(400, f"Login failed: {data["error"]}")
		async with self._transaction() as cur:
			schema = self.dbSchema
			raw, hash = self._generate_hash()
			jwt_decoded = jwt_get_data(data["jwt"])
			if await (await cur.execute(f"SELECT 1 FROM {schema.TABLE} WHERE {schema.EMAIL} = ?", (email,))).fetchone() is not None:
				_logger.debug(f"Overwriting old loginentry for {email}")
				await cur.execute(f"""
					UPDATE {schema.TABLE} 
					SET 
						{schema.HASH} = ?, 
						{schema.JWT} = ?,
						{schema.JWT_EXPIRES} = ?, 
						{schema.USER_TOKEN} = ?, 
						{schema.UID} = ?,
						{schema.LAST_USED} = ?,
					WHERE {schema.EMAIL} = ?""", 
					(hash, data["jwt"], dtToTimestamp(jwt_decoded.exp), data["token"], data["user_id"], 0, email)
				)
			else:
				await cur.execute(f"""
					INSERT INTO {schema.TABLE} 
					({schema.HASH}, {schema.JWT}, {schema.JWT_EXPIRES}, {schema.USER_TOKEN}, {schema.UID}, {schema.EMAIL}, {schema.LAST_USED}) 
					VALUES ({', '.join(["?" for i in range(7)])})""", 
					(hash, data["jwt"], dtToTimestamp(jwt_decoded.exp), data["token"], data["user_id"], email, 0)
				)		
		return raw
	# region Helpers
	async def _refresh(self):
		self.__pending_2fa = {k:v for k,v in self.__pending_2fa.items() if v["expires"] > round(datetime.now(UTC).timestamp(), 0)}
		schema = self.dbSchema
		async with self._transaction() as cur:
			rows = await (await cur.execute(f"SELECT * FROM {schema.TABLE} WHERE {schema.JWT_EXPIRES} > strftime('%s', 'now')")).fetchall()
		for row in rows:
			entry = self.Entry(row, self)
			try:
				if entry.usedWithin(30):
					await entry.refresh()
			except AuthenticationError:
				await cur.execute(
					f"DELETE FROM {schema.TABLE} WHERE {schema.HASH} = ?", 
					(entry.hashed,)
				)
				_logger.info(f"Removed expired entry for {entry.email}")
		async with self._transaction() as cur:
			operation = await cur.execute(f"DELETE FROM {schema.TABLE} WHERE {schema.JWT_EXPIRES} <= strftime('%s', 'now')")
			if operation.rowcount > 0:
				_logger.info(f"Deleted {operation.rowcount} expired entries")
		
	def _generate_hash(self) -> tuple[str, str]:
		raw_token = token_urlsafe(32)
		return raw_token, sha256(raw_token.encode()).hexdigest()
	def _hash_token(self, raw_token:str) -> str:
		return sha256(raw_token.encode()).hexdigest()

	@asynccontextmanager
	async def operation(self):
		session = await self._enter_op()
		try:
			yield session
		finally:
			await self._exit_op()
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
			self.__session = ClientSession(headers={"User-Agent": "ThunderAPI/1.0"})

		await self._init_db(self.__db_path)
		await self._init_db(Path(__file__).parent / "vehicleParser" / "units.db")
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

	@staticmethod
	async def _handle_response(resp:ClientResponse) -> dict[str, Any]:
		text = await resp.text()

		if resp.status >= 400:
			raise AuthenticationError(400, f"Request failed: {resp.status} {text}")
		if text.startswith("!ERROR"):
			raise AuthenticationError(400, f"Request failed: {text}")

		return loads(text)

	@staticmethod
	async def _init_db(dbPath:Path):
		if dbPath.exists():
			return

		init_script = dbPath.parent / (".".join(dbPath.name.split(".")[:-1]) + "_create.sql")
		dbPath.touch()

		try:
			async with connect(dbPath) as con:
				lines = re_sub("--.*\n", "", init_script.read_text()).replace("\n", "").split(";")

				for line in lines:
					line = line.strip()
					if not line:
						continue

					await con.execute(line + ";")

				await con.commit()

			_logger.debug("Database successfully initialized")

		except OperationalError:
			dbPath.unlink()
			_logger.exception("An error occurred during database setup")
			raise
	#endregion