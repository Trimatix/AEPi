from io import BytesIO
import struct
from config import *

def intbytes(x):
    return bytes((x,))


def uint16(x: int, endianness: Endianness):
    """A C unsigned short
    """
    return struct.pack(endianness.value + "H", x)

    
def uint32(x: int, endianness: Endianness):
    """A C unsigned int
    """
    return struct.pack(endianness.value + "I", x)


def makeSingleTextureAEI(format: Format, compressedImage: bytes, width: int, height: int, endianness: Endianness) -> BytesIO:
    out = BytesIO()
    # Write header meta
    out.write(bytes("AEImage\0", "utf-8"))
    out.write(intbytes(format.value))
    
    for item in (
        width, height, # image dimensions
        1, # number of textures
        0, # first texture x-coordinate
        0, # first texture y-coordinate
        width, height # first texture dimensions
    ):
        out.write(uint16(item, endianness))
    
    out.write(uint32(len(compressedImage), endianness)) # length of compressed image in bytes
    # end header meta

    # write image
    out.write(compressedImage)

    # write footer meta
    out.write(uint16(0, endianness)) # format symbol data
    out.write(intbytes(3)) # compression quality

    # done
    out.seek(0)
    return out
