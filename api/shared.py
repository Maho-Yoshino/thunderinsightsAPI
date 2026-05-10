from fastapi import HTTPException
from tools import Request
from utils.auth import AuthenticationError
from typing_extensions import Annotated
from pydantic import StringConstraints, Field
from datetime import datetime, UTC

token_cache:dict[str, dict[str, int|str]] = {}


def get_cached_entry(token:str) -> dict[str, str|int]:
	for _email, data in dict(token_cache).items():
		if datetime.now(UTC) >= datetime.fromtimestamp(data["expires"], UTC):
			token_cache.pop(_email)
	cachedTokenEntries = {i:j for i, j in token_cache.items() if j["session_token"] == token or j["user_token"] == token}
	if not cachedTokenEntries:
		raise HTTPException(404, detail="Cached token not found")
	email = next(cachedTokenEntries.keys())
	data = cachedTokenEntries[email]
	cachedTokenEntries["email"] = email
	return data

def get_request(template:str):
	try:
		request = Request.from_template(template)
	except AuthenticationError:
		raise HTTPException(status_code=500, detail="Unable to log into gaijin's systems")
	return request

IntString = Annotated[
	str,
	StringConstraints(pattern=r"^\d+$"),
	Field(description="Integer value represented as a string", examples=["10016"]),
]