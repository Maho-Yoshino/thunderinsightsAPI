from dataclasses import dataclass
from typing import Any
from tools import blk_to_json
from enum import IntEnum, Enum

@dataclass
class _ReplayHeader:
    class ReplayStructure(Enum): # Based on the hexpat
        class ByteSizes(IntEnum):
            u32 = 4
            char = 1
            difficulty = 1
            padding = 1
            u64 = 8
        magic = (0, ByteSizes.u32 , int) # (index, size, type)
        version = (1, ByteSizes.u32, int)
        level = (2, ByteSizes.char * 128, str)
        levelSettings = (3, ByteSizes.char * 260, str)
        battleType = (4, ByteSizes.char * 128, str)
        environment = (5, ByteSizes.char * 128, str)
        visibility = (6, ByteSizes.char * 32, str)
        rezOffset = (7, ByteSizes.u32, int)
        diff = (8, ByteSizes.difficulty, '_Difficulty')
        _pad1 = (9, ByteSizes.padding * 35, None)
        sessionType = (10, ByteSizes.u32, int)
        _pad2 = (11, ByteSizes.padding * 4, None)
        sessionIdHex = (12, ByteSizes.u64, int)
        _pad3 = (13, ByteSizes.padding * 4, None)
        mSetSize = (14, ByteSizes.u32, int)
        _pad4 = (15, ByteSizes.padding * 32, None)
        locName = (16, ByteSizes.char * 128, str)
        startTime = (17, ByteSizes.u32, int)
        timeLimit = (18, ByteSizes.u32, int)
        scoreLimit = (19, ByteSizes.u32, int)
        _pad5 = (20, ByteSizes.padding * 48, None)
        battleClass = (21, ByteSizes.char * 128, str)
        battleKillStreak = (22, ByteSizes.char * 128, str)

    class _Difficulty:
        unk_nib: int # 4 bits
        difficulty: int # 4 bits
        def __init__(self, byte:int):
            self.unk_nib = byte >> 4
            self.difficulty = byte & 0x0F
    #region header fields
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
    #endregion
    def __init__(self, data:bytes):
        fields = sorted(self.ReplayStructure, key=lambda f: f.value[0]) # Sort by index
        offset = 0
        for field in fields:
            index, size, field_type = field.value

            if field_type == '_Difficulty':
                value = self._Difficulty(data[offset])
            elif field_type == str:
                value = data[offset:offset+size].split(b'\x00')[0].decode('ascii')
            elif field_type == int:
                value = int.from_bytes(data[offset:offset+size.value], 'little')
            elif field_type is None: # Padding
                offset += size
                continue

            setattr(self, field.name, value)
            offset += size

class ReplayParser:
    header: _ReplayHeader
    body: dict[str, Any]
    def __init__(self, replay:bytes):
        self.header = _ReplayHeader(replay)
        try:
            self.body = blk_to_json(replay[self.header.rezOffset:])
        except RuntimeError:
            self.body = {}
