"""Library code for geolocation"""
from os import replace as file_replace
from asyncio import to_thread
from geoip2.database import Reader
from geoip2.models import City
from geoip2.errors import AddressNotFoundError
from pathlib import Path
from asyncio import sleep
from github import Github
from datetime import datetime, UTC
from zoneinfo import ZoneInfo
from threading import Lock

_db = Path(__file__).parent / "GeoLite2-City.mmdb"
_db_tmp = _db.parent / "GeoLite2-City.mmdb.tmp"
_db_id = _db.parent / "GeoLite2-City.hash"
_reader = None
_lock = Lock()

def lookup_city(ip: str) -> City | None:
    global _reader
    with _lock:
        if _reader is None:
            if not _db.exists():
                return None
            _reader = Reader(str(_db))
        try:
            return _reader.city(ip)
        except AddressNotFoundError:
            return None
def lookup_utc_offset(zone: str) -> int | None:
    """Converts an IANA spec timezone into an UTC offset"""
    rn = datetime.now(UTC)
    utcdiff = ZoneInfo(zone).utcoffset(rn)
    return utcdiff.total_seconds() // (60*60)

async def update_db():
    global _reader, _lock
    github_repo = Github().get_repo("P3TERX/GeoLite.mmdb")
    if not _db.exists():
        latest = github_repo.get_latest_release()
        for asset in latest.assets:
            if asset.name != "GeoLite2-City.mmdb":
                continue
            with _lock:
                await to_thread(lambda: asset.download_asset(_db_tmp))
                file_replace(_db_tmp, _db)
                _db_id.write_text(str(latest.id))
                if _reader is not None:
                    _reader.close()
                    _reader = None
            break
        else:
            raise RuntimeError(f"No file under the name 'GeoLite2-City.mmdb' found under the latest release ({latest.url})")
        await sleep(12*60*60)
    while True:
        latest = github_repo.get_latest_release()
        if latest.id != int(_db_id.read_text()):
            for asset in latest.assets:
                if asset.name != "GeoLite2-City.mmdb":
                    continue
                with _lock:
                    await to_thread(asset.download_asset(_db_tmp))
                    file_replace(_db_tmp, _db)
                    _db_id.write_text(str(latest.id))
                    if _reader is not None:
                        _reader.close()
                        _reader = None
                break
            else:
                raise RuntimeError(f"No file under the name 'GeoLite2-City.mmdb' found under the latest release ({latest.url})")
        await sleep(12*60*60)
