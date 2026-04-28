import sys
from enum import Enum


class BlockInfo:

    def __init__(self, params):
        self.id = -1
        self.name = ""
        self.block_offset = 0
        self.param_info = params
        self.block_info = None

    def __init__(self, id, name, block_offset, param_info_size, block_info_size):
        self.id = id
        self.name = name
        self.block_offset = block_offset
        self.param_info = [None] * param_info_size
        self.block_info = [None] * block_info_size

    def __str__(self):
        return f"BlockInfo(id={self.id}, name={self.name}, block_offset={self.block_offset}\n"


class ParamInfo:
    def __init__(self, id, name, type, value):
        self.id = id
        self.name = name
        self.type = type
        self.value = value

    def __str__(self):
        return f"ParamInfo(id={self.id}, name={self.name}, type={self.type}, value={self.value})\n"


class DataType(Enum):
    Size = 0x00
    Str = 0x01
    Int = 0x02
    Float = 0x03
    Vec2F = 0x04
    Vec3F = 0x05
    Vec4F = 0x06
    Vec2 = 0x07
    Vec3 = 0x08
    Bool = 0x09
    Color = 0x0A
    M4x3F = 0x0B
    Long = 0x0C
    Typex7 = 0x10
    Typex = 0x89
