from os import getenv
from typing_extensions import Annotated
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from utils import users_cache
from pydantic import EmailStr
from api.models import Authentication
from api.shared import TokenString, limiter
from utils.helper import dtToTimestamp

router = APIRouter(
	tags=["authentication"],
	responses={404: {"description": "Not found"}}
)

@router.post(
	"/login", 
	summary="Get a token to use in other endpoints", 
	description="You can use this token for the `POST` endpoints, which are user-specific. If given user has 2FA enabled, they must provide the 2FA code along with their credentials. If you generated a token that hasn't expired yet, the endpoint will just give back the cached token.",
	responses={
		200: {"model": Authentication.Login.LoginResponse},
		403: {"model": Authentication.Login.Fail2FAResponse, "description": "Unauthorized. Account has 2FA enabled, and needs to go through the 2FA process."},
		429: {"description": "Rate limit exceeded. Please wait a bit before trying again."},
	}
)
@limiter.limit(getenv("LOGIN_RATE_LIMIT", "5/minute"))
async def login_post(
	request: Request,
	email: Annotated[EmailStr, Form()],
	password: Annotated[str, Form(min_length=6, max_length=64, json_schema_extra={"format": "password"})]
):
	token = await users_cache.login(email, password)

	return JSONResponse({
		"status": "OK",
		"token": token
	}, status_code=200)

@router.post(
	"/refresh-token", 
	summary="Refresh your token so it stays alive for longer. This is essentially a 'No op', just to keep the token active.",
	description="If you are cached it will refresh the token. The game generally refreshes the token every 30 minutes. Returns an UNIX timestamp of the new token expiry",
	responses={
		200: {"model": Authentication.LoginToken.LoginTokenResponse, "description": "Token refreshed successfully"},
		404: {"model": Authentication.LoginToken.LoginFailResponse, "description": "Invalid token provided. The token is either expired or invalid."},
		429: {"description": "Rate limit exceeded. Please wait a bit before trying again."}
	}
)
@limiter.limit(getenv("LOGIN_RATE_LIMIT", "5/minute"))
async def login_token(
	request: Request, 
	token: TokenString
):
	entry = await users_cache.get(token)
	if entry is None:
		return JSONResponse(status_code=404, content={"status": "FAIL", "detail": "Invalid token provided"})
	await entry.refresh()
	return {
		"expires": dtToTimestamp(entry.expires),
		"status": "OK"
	}

@router.post(
	"/answer-2fa",
	summary="Provide 2FA code to finish login in case of a 2FA account without gaijin pass"
)
@limiter.limit(getenv("LOGIN_RATE_LIMIT", "5/minute"))
async def answer_2fa(
	request: Request,
	email: EmailStr,
	code: Annotated[int, Form(title="The 2FA code")]
):
	if email not in users_cache:
		raise HTTPException(401, "You are not pending 2FA verification. Please try to log in first.")
	users_cache.__pending_2fa[email]["code"] = code
	... # TODO: Implement