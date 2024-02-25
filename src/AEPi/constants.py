from enum import Enum
from typing import Literal
from AEPi.lib.binaryio import Endianness

class CompressionFormat(Enum):
    """Compression formats.
    Enum values correspond to the identifiers used within AEI files.
    """
    Unknown =                   0b00000000
    Uncompressed_UI =           0b00000001
    Uncompressed_CubeMap_PC =   0b10000001
    Uncompressed_CubeMap =      0b11000010
    PVRTCI2A =                  0b00001101
    PVRTCI4A =                  0b00010000
    ATC =                       0b00010001
    DXT1 =                      0b00100000
    DXT3 =                      0b00100001
    DXT5 =                      0b00100100
    ETC1 =                      0b01000000

    @property
    def isCompressed(self):
        return self not in (
            CompressionFormat.Unknown,
            CompressionFormat.Uncompressed_UI,
            CompressionFormat.Uncompressed_CubeMap,
            CompressionFormat.Uncompressed_CubeMap_PC
        )

FILE_TYPE_HEADER = b"AEimage\x00"
ENDIANNESS = Endianness("little", "<")
CompressionQuality = Literal[1, 2, 3]
