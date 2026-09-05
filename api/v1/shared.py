from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils import users_cache
from utils.auth import UserTokenCache
from typing_extensions import Annotated
from pydantic import StringConstraints, Field
from datetime import datetime, UTC

security = HTTPBearer(description="Get the token from `POST /v1/login`")

async def get_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
	token = credentials.credentials
	user = await users_cache.get(token)
	if not user:
		raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
	user.requests_count += 1
	user.last_used = datetime.now(UTC)
	await user._write_values()
	return user

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
TokenBearer = Annotated[
	UserTokenCache.Entry,
	Depends(get_auth),
]
