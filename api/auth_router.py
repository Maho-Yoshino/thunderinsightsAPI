from os import getenv
from typing_extensions import Annotated
from fastapi import APIRouter, Form, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from utils import users_cache
from pydantic import EmailStr
from utils.auth import UserTokenCache
from api.models import Authentication
from api.shared import limiter, get_auth
from utils.helper import dtToTimestamp

router = APIRouter(
	tags=["authentication"],
	responses={404: {"description": "Not found"}}
)

@router.post(
	"/login", 
	summary="Get a token to use in other endpoints", 
	description="You can use this token for the endpoints. If given user has 2FA enabled, they must provide the 2FA code along with their credentials through either `Gaijin pass` or the `/v1/answer-2fa` endpoint. If you generated a token that hasn't expired yet, the endpoint will just give back the cached token.",
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
    user: UserTokenCache.Entry = Depends(get_auth)
):
	await user.refresh()
	return {
		"expires": dtToTimestamp(user.expires),
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

@router.post(
	"/get-sid",
	summary="Gets an 'identifier_sid' value, used for replay searching. Value is not displayed, but will be used in the requests that require it. Has to be refreshed every 14 days",
	responses={
		200: {},
		400: {"description": "Generic fetch failure"},
		404: {"description": "User not found in database"}
	}
)
async def get_sid(
	request: Request,
	password: Annotated[str, Form(min_length=6, max_length=64, json_schema_extra={"format": "password"}, description="Must be given, as we do not store passwords")],
    user: UserTokenCache.Entry = Depends(get_auth)
):
	sid = await users_cache.get_sid(user.email, password)
	if sid == None:
		raise HTTPException(400, "Could not obtain sid value")
	return JSONResponse({"status": "success"}, 200)