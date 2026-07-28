from typing import Literal
from utils import users_cache

async def getLatestGameVer(branch: Literal["dev", "dev-stable"]|None):
	if branch is None: branch = ""
	async with users_cache.operation() as session:
		_ = await session.get(f"https://yupmaster.gaijinent.com/yuitem/get_version.php?proj=warthunder&tag={branch}")
		_ = await _.text()
	return _