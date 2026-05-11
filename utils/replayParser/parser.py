from dataclasses import dataclass
from typing import Any
from tools import blk_to_json

class _Difficulty:
    unk_nib: int # 4 bits
    difficulty: int # 4 bits
    def __init__(self, byte:int):
        self.unk_nib = byte >> 4
        self.difficulty = byte & 0x0F

@dataclass
class _ReplayHeader:
    magic: int
    version: int
    level: str
    levelSettings: str
    battleType: str
    environment: str
    visibility: str
    rezOffset: int 
    diff: _Difficulty
    sessionType: int
    sessionIdHex: int
    mSetSize: int
    locName: str
    startTime: int
    timeLimit: int
    scoreLimit: int
    battleClass: str
    battleKillStreak: str

class ReplayParser:
    header: _ReplayHeader
    body: bytes # blk
    def __init__(self, replay:bytes):
        self.header = _ReplayHeader(
            magic = int.from_bytes(replay[0:4], 'little'),
            version = int.from_bytes(replay[4:8], 'little'),
            level = replay[8:136].split(b'\x00')[0].decode('ascii'),
            levelSettings=replay[136:396].split(b'\x00')[0].decode('ascii'),
            battleType=replay[396:524].split(b'\x00')[0].decode('ascii'),
            environment=replay[524:652].split(b'\x00')[0].decode('ascii'),
            visibility=replay[652:684].split(b'\x00')[0].decode('ascii'),
            rezOffset=int.from_bytes(replay[684:688], 'little'),
            diff=_Difficulty(replay[688]),
            # 35 bytes of padding
            sessionType=int.from_bytes(replay[724:728], 'little'),
            # 4 bytes of padding
            sessionIdHex=int.from_bytes(replay[732:740], 'little'),
            # 4 bytes of padding
            mSetSize=int.from_bytes(replay[744:748], 'little'),
            # 32 bytes of padding
            locName=replay[780:908].split(b'\x00')[0].decode('ascii'),
            startTime=int.from_bytes(replay[908:912], 'little'),
            timeLimit=int.from_bytes(replay[912:916], 'little'),
            scoreLimit=int.from_bytes(replay[916:920], 'little'),
            # 48 bytes of padding
            battleClass=replay[968:1096].split(b'\x00')[0].decode('ascii'),
            battleKillStreak=replay[1096:1224].split(b'\x00')[0].decode('ascii')
        )
        self.body = replay[self.header.rezOffset:]
    def decode_body(self) -> dict[str, Any]:
        return blk_to_json(self.body)
