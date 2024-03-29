from enum import Enum
from typing import Literal, Dict, Set, Tuple
from .lib.binaryio import Endianness
from . import exceptions 

FORMAT_PILLOW_MODES: Dict["CompressionFormat", str] = {}
FORMAT_BITCOUNTS: Dict["CompressionFormat", int] = {}
BGRA_FORMATS: Set["CompressionFormat"] = set()
MASK_MIPMAPPED_FLAG = 0b00000010
MASK_FORMAT_ID = 0b11111101

class CompressionFormat(Enum):
    """Compression formats.
    Enum values correspond to the identifiers used within AEI files.
    """
    Unknown =                   0b00000000
    Uncompressed =              0b00000011
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


    @classmethod
    def fromBinary(cls, rawId: int) -> Tuple["CompressionFormat", bool]:
        # Some non-mipmappable formats (uncompressed) have the mipmapping flag as 1, just as part of their ID
        if any(f.value == rawId for f in CompressionFormat):
            return CompressionFormat(rawId), False
        
        mipmapped = rawId & MASK_MIPMAPPED_FLAG == 2
        id = rawId & MASK_FORMAT_ID
        
        if not any(f.value == id for f in CompressionFormat):
            raise exceptions.InvalidCompressionFormatException(rawId)
        
        return CompressionFormat(id), mipmapped


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
    
    
    @property
    def supportsMipmapping(self):
        # This will need some more testing to validate
        return self.isCompressed
    
    
    @property
    def isBgra(self):
        return self in BGRA_FORMATS


FORMAT_PILLOW_MODES[CompressionFormat.Uncompressed] = "RGBA" # ?
FORMAT_PILLOW_MODES[CompressionFormat.Uncompressed_UI] = "RGBA"
FORMAT_PILLOW_MODES[CompressionFormat.Uncompressed_CubeMap_PC] = "RGBA" # ?
FORMAT_PILLOW_MODES[CompressionFormat.Uncompressed_CubeMap] = "RGBA" # ?
FORMAT_PILLOW_MODES[CompressionFormat.PVRTC12A] = "RGBA"
FORMAT_PILLOW_MODES[CompressionFormat.PVRTC14A] = "RGBA"
FORMAT_PILLOW_MODES[CompressionFormat.ATC] = "RGBA"
FORMAT_PILLOW_MODES[CompressionFormat.DXT1] = "RGB"
FORMAT_PILLOW_MODES[CompressionFormat.DXT3] = "RGBA"
FORMAT_PILLOW_MODES[CompressionFormat.DXT5] = "RGBA"
FORMAT_PILLOW_MODES[CompressionFormat.ETC1] = "RGB"

FORMAT_BITCOUNTS[CompressionFormat.Uncompressed] = 8 # ?
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

BGRA_FORMATS.add(CompressionFormat.ETC1)

FILE_TYPE_HEADER = b"AEimage\x00"
ENDIANNESS = Endianness("little", "<")
CompressionQuality = Literal[1, 2, 3]
