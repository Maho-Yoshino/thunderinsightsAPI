from api.models import Users
from tools import Request

async def get_terse(token:str, *userIds:int|str) -> dict[str, Users.TerseReturnModel]:
    return await Request.send_template(
        token, 
        "get_users_terse_info",
        usersList = ";".join(str(i) for i in userIds)
    )

