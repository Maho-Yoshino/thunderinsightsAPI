from api.models import Users
from api.shared import get_request

async def get_terse(token:str, *userIds:int|str) -> dict[str, Users.TerseReturnModel]:
    return await (await get_request(
        token, 
        "get_users_terse_info",
        usersList = ";".join(str(i) for i in userIds)
    )).send()

