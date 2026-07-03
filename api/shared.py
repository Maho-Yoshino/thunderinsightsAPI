from fastapi import HTTPException, Form
from re import search as re_search
from tools import Request
from utils.auth import AuthenticationError, users_cache
from typing_extensions import Annotated
from pydantic import StringConstraints, Field
from datetime import timedelta
from typing import Any
from enum import StrEnum

async def get_request(token: str, template:str, **headers:str|dict[str, Any]):
	if (entry := await users_cache.get(token)) is None:
		raise HTTPException(status_code=403, detail="The given token is invalid")
	if entry.timeLeft() <= timedelta(minutes=30):
		await entry.refresh()
	try:
		request = await Request.from_template(entry, template)
	except AuthenticationError:
		raise HTTPException(status_code=500, detail="Unable to log into gaijin's systems")
	for key, value in headers.items():
		if key.lower() == "body":
			for k, v in value.items():
				request[k] = v
		else:
			request.headers[key] = str(value)
	entry.requests_count += 1
	await entry._write_values()
	return request

IntString = Annotated[
	str,
	StringConstraints(pattern=r"^\d+$"),
	Field(description="Integer value represented as a string", examples=["10016"]),
]
IpString = Annotated[
	str,
	StringConstraints(pattern=r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"),
	Field(description="IP address represented as a string", examples=["0.0.0.0"])
]
TokenString = Annotated[
	str,
	Form(description="Token obtained from the `login` endpoint.")
]

class RateLimitExceeded(HTTPException):
	def __init__(self, detail: str = "Rate limit exceeded"):
		super().__init__(status_code=429, detail=detail)

