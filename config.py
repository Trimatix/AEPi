from enum import Enum
from dataclasses import dataclass

class Format(Enum):
    """Compression formats.
    Enum values correspond to the identifiers used within AEI files.
    Make sure you know what you're doing before editing.
    """
    DXT5 = 0b00100100
    ETC1 = 0b01000000


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


def mipmapped(f: Format) -> int:
    """Flag a compression format as using mipmapping.
    This is the flag used internally by AEI files. Make sure you know what you're doing before editing.
    Not currently supported by AEPi.

    :param f: The format to edit
    :type f: Format
    :return: `f`, but also marked with mipmapping
    :rtype: int
    """
    return f.value & 0b10
