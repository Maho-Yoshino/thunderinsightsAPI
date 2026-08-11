from api.models import Users
from utils.auth import UserTokenCache
from tools import Request

async def get_terse(user:UserTokenCache.Entry, *userIds:int|str) -> dict[str, Users.TerseReturnModel]:
    return await Request.send_template(
        user, 
        "get_users_terse_info",
        usersList = ";".join(str(i) for i in userIds)
    )

