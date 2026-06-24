from fastapi import HTTPException, Form
from tools import Request
from utils.auth import AuthenticationError, users_cache
from typing_extensions import Annotated
from pydantic import StringConstraints, Field
from datetime import timedelta
from typing import Any

async def get_request(token: str, template:str, **headers:str|dict[str, Any]):
	if (_ := await users_cache.get(token)) is None:
		raise HTTPException(status_code=403, detail="The given token is invalid")
	if _.timeLeft() <= timedelta(minutes=30):
		await _.refresh()
	try:
		request = await Request.from_template(_, template)
	except AuthenticationError:
		raise HTTPException(status_code=500, detail="Unable to log into gaijin's systems")
	for key, value in headers.items():
		if key.lower() == "body":
			for k, v in value.items():
				request[k] = v
		else:
			request.headers[key] = str(value)
	_.requests_count += 1
	await _._write_values()
	return request

IntString = Annotated[
	str,
	StringConstraints(pattern=r"^\d+$"),
	Field(description="Integer value represented as a string", examples=["10016"]),
]
TokenString = Annotated[
	str,
	Form(description="Token obtained from the `login` endpoint.")
]
