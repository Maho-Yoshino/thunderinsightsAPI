from typing_extensions import Annotated

from fastapi import APIRouter, Path, Query, HTTPException
from fastapi.responses import JSONResponse
from tools import Request
from utils.auth import AuthenticationError

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

@router.get("/v1/terse")
def get_users_terse_info(id: Annotated[list[int], Query(title="The ID of the users to get information about", description="Provide multiple IDs to get information about multiple users at once")]):
    """Get terse information about users by their IDs."""
    try:
        request = Request.from_template("get_users_terse_info")
    except AuthenticationError:
        raise HTTPException(status_code=500, detail="Unable to log into gaijin's systems")
    request.headers["usersList"] = ";".join(str(i) for i in id)
    request.request()
    return JSONResponse(request.result)

