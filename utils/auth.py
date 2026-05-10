from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv
from os import getenv
from datetime import UTC, timedelta, datetime
from requests import post
from typing import Any

token: str | None = None
token_expiry: datetime | None = None
actual_token: str | None = None
uidHint: int = -1  # Placeholder for UID hint, which may be required for certain requests.

#region Login
def __load_credentials() -> tuple[str, str]:
    if not load_dotenv(".env"):
        raise RuntimeError("Failed to load .env file.")
    
    email = getenv("WT_EMAIL")
    password = getenv("WT_PASS")
    if not email or not password:
        raise ValueError("WT_EMAIL and WT_PASS must be set in the .env file.")
    
    return email, password

def __2fa_login():
    raise NotImplementedError("Not yet figured out. Please consider using an account without 2FA")

def login():
    email, password = __load_credentials()
    r = post(
        "https://auth.gaijinent.com/login.php", 
        data={
            "login": email,
            "password": password,
            "game": "wt"
        }, 
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "ThunderAPI/1.0"
        })
    if not r.ok:
        raise AuthenticationError(f"Login failed: {r.status_code} {r.text}")
    if r.content.startswith(b"!ERROR"):
        raise AuthenticationError(f"Login failed: {r.text}")
    data:dict[str, Any] = r.json()
    if data["status"] == "2STEP":
        two_factor_types = []
        if data.get("hasGjPass"): two_factor_types.append("GaijinPass")
        if data.get("hasTwoStepEmail"): two_factor_types.append("Email")
        if data.get("hasWTR"): two_factor_types.append("WTR")
        __2fa_login()
    global token, token_expiry, actual_token, uidHint
    token = data.get("jwt")
    token_expiry = datetime.now(UTC) + timedelta(seconds=data.get("token_exp", 3600))
    actual_token = token  # Store the actual token for refreshing
    uidHint = data.get("uid")  # Store the UID hint for use in authenticated requests
    if not scheduler.running:
        scheduler.start()  # Start the token refresh scheduler
#endregion

#region Token Refresh
scheduler = BackgroundScheduler()
def __refresh_token():
    if token is None or token_expiry is not None and datetime.now(UTC) >= token_expiry: 
        login() # Re-login to refresh the token if it's expired or not set
        return
    r = post(
        "https://auth.gaijinent.com/login_token.php", 
        data={"token": actual_token}, 
        headers={
            "User-Agent": "ThunderAPI/1.0", 
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )
    if not r.ok:
        raise AuthenticationError(f"Token refresh failed: {r.status_code} {r.text}")
scheduler.add_job(__refresh_token, IntervalTrigger(minutes=30)) # Refresh token every 30 minutes

def add_auth_headers(headerData: dict[str, Any]) -> dict[str, Any]:
    if token:
        headerData["token"] = token
        headerData["uidHint"] = str(uidHint)
        headerData["transactid"] = str(6942067)
        return headerData
    else:
        raise AuthenticationError("Authentication required for this request, but no token is available. Please ensure you have logged in successfully.")

class AuthenticationError(Exception):
    pass