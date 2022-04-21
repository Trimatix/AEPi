from enum import Enum
from dataclasses import dataclass

class Format(Enum):
    DXT5 = 0b00100100
    ETC1 = 0b01000000


class Endianness(Enum):
    big = ">"
    little = "<"


@dataclass
class PlatformConfiguration:
    format: Format
    endianness: Endianness
    mipmapped: bool


class Platform(Enum):
    PC = PlatformConfiguration(Format.DXT5, Endianness.little, False)
    android = PlatformConfiguration(Format.ETC1, Endianness.little, False)


def mipmapped(f: Format):
    return f.value & 0b10
