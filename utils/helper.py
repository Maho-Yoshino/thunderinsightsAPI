import re
from datetime import timedelta, datetime

_UNIT_MAP: dict[str, timedelta] = {
    "m": timedelta(days=30),
    "w": timedelta(days=7),
    "d": timedelta(days=1),
    "h": timedelta(hours=1),
    "M": timedelta(minutes=1)
}

def StringTimeToTimedelta(text:str) -> timedelta:
    """Converts strings like `3d12h` into a `timedelta` object"""
    total = timedelta()
    for result in re.finditer("(?:(\\d+)([mwdhM]))", text):
        val = int(result.group(1))
        unit = result.group(2)
        total += val * _UNIT_MAP[unit]
    return total

def RateLimitParse(text:str) -> tuple[int, timedelta]:
    # Example: "2/M" -> (2, timedelta(minutes=1))
    limit, period = text.split("/")
    return int(limit), StringTimeToTimedelta(f"1{period[0]}")
def dtToTimestamp(dt:datetime) -> int:
    return round(dt.timestamp(), 0)