from enum import Enum
from typing import Literal, Dict
from AEPi.lib.binaryio import Endianness

FORMAT_PILLOW_MODES: Dict["CompressionFormat", str] = {}
FORMAT_BITCOUNTS: Dict["CompressionFormat", int] = {}

class CompressionFormat(Enum):
    """Compression formats.
    Enum values correspond to the identifiers used within AEI files.
    """
    Unknown =                   0b00000000
    Uncompressed_UI =           0b00000001
    Uncompressed_CubeMap_PC =   0b10000001
    Uncompressed_CubeMap =      0b11000010
    PVRTC12A =                  0b00001101
    PVRTC14A =                  0b00010000
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
    

    @property
    def pillowMode(self):
        return FORMAT_PILLOW_MODES[self]
    

    @property
    def bitcount(self):
        return FORMAT_BITCOUNTS[self]

FORMAT_PILLOW_MODES[CompressionFormat.Unknown] = "RGBA" # ?
FORMAT_PILLOW_MODES[CompressionFormat.Uncompressed_UI] = "RGBA" # ?
FORMAT_PILLOW_MODES[CompressionFormat.Uncompressed_CubeMap_PC] = "RGB" # ?
FORMAT_PILLOW_MODES[CompressionFormat.Uncompressed_CubeMap] = "RGB" # ?
FORMAT_PILLOW_MODES[CompressionFormat.PVRTC12A] = "RGBA"
FORMAT_PILLOW_MODES[CompressionFormat.PVRTC14A] = "RGBA"
FORMAT_PILLOW_MODES[CompressionFormat.ATC] = "RGBA"
FORMAT_PILLOW_MODES[CompressionFormat.DXT1] = "RGB"
FORMAT_PILLOW_MODES[CompressionFormat.DXT3] = "RGBA"
FORMAT_PILLOW_MODES[CompressionFormat.DXT5] = "RGBA"
FORMAT_PILLOW_MODES[CompressionFormat.ETC1] = "RGB"

FORMAT_BITCOUNTS[CompressionFormat.Unknown] = 8 # ?
FORMAT_BITCOUNTS[CompressionFormat.Uncompressed_UI] = 8 # ?
FORMAT_BITCOUNTS[CompressionFormat.Uncompressed_CubeMap_PC] = 8 # ?
FORMAT_BITCOUNTS[CompressionFormat.Uncompressed_CubeMap] = 8 # ?
FORMAT_BITCOUNTS[CompressionFormat.PVRTC12A] = 2
FORMAT_BITCOUNTS[CompressionFormat.PVRTC14A] = 4
FORMAT_BITCOUNTS[CompressionFormat.ATC] = 4
FORMAT_BITCOUNTS[CompressionFormat.DXT1] = 4
FORMAT_BITCOUNTS[CompressionFormat.DXT3] = 8
FORMAT_BITCOUNTS[CompressionFormat.DXT5] = 8
FORMAT_BITCOUNTS[CompressionFormat.ETC1] = 4

FILE_TYPE_HEADER = b"AEimage\x00"
ENDIANNESS = Endianness("little", "<")
CompressionQuality = Literal[1, 2, 3]
