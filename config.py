from enum import Enum
from dataclasses import dataclass
from typing import Union

class Format(Enum):
    """Compression formats.
    Enum values correspond to the identifiers used within AEI files.
    Make sure you know what you're doing before editing.
    """
    Unknown =                   0b00000000
    Uncompressed_UI =           0b00000001
    PVRTCI2A =                  0b00001101
    PVRTCI4A =                  0b00010000
    ATC =                       0b00010001
    DXT1 =                      0b00100000
    DXT3 =                      0b00100001
    DXT5 =                      0b00100100
    ETC1 =                      0b01000000
    Uncompressed_CubeMap_PC =   0b10000001
    Uncompressed_CubeMap =      0b11000010


class Endianness(Enum):
    """Bit-endianness.
    AEI files ALWAYS use little endianness, hence why this class is not used as part of the public API of AEPi.
    """
    big = ">"
    little = "<"


@dataclass
class PlatformConfiguration:
    """All of the configuration which AEPi may use to represent a platform, such as PC or Android.
    """
    format: Format
    endianness: Endianness
    mipmapped: bool


class Platform(Enum):
    """A target platform for use of an AEI file. E.g, Galaxy on Fire 2 for PC uses DXT5 for compressing ship textures.
    """
    PC = PlatformConfiguration(Format.DXT5, Endianness.little, False)
    android = PlatformConfiguration(Format.ETC1, Endianness.little, False)


def mipmapped(f: Union[int, Format]) -> int:
    """Flag a compression format as using mipmapping.
    This is the flag used internally by AEI files. Make sure you know what you're doing before editing.
    Not currently supported by AEPi.

    :param f: The format to edit
    :type f: Format
    :return: `f`, but also marked with mipmapping
    :rtype: int
    """
    return (f if isinstance(f, int) else f.value) & 0b11111110


def noMipmap(f: Union[int, Format]) -> int:
    """Flag a compression format as not using mipmapping.
    This is the flag used internally by AEI files. Make sure you know what you're doing before editing.
    Not currently supported by AEPi.

    :param f: The format to edit
    :type f: Format
    :return: `f`, but also marked without mipmapping
    :rtype: int
    """
    return (f if isinstance(f, int) else f.value) & 0b11111101


def isMipmapped(f: Union[int, Format]) -> bool:
    """Get the value of the mipmapping flag fo a compression format.
    This is the flag used internally by AEI files. Make sure you know what you're doing before editing.
    Not currently supported by AEPi.

    :param f: The compression format
    :type f: Format
    :return: `True` if `f` is flagged for mipmapping, `False` otherwise
    :rtype: int
    """
    return bool(mipmapped(f))
