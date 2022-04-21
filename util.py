from io import BytesIO
import struct
from .config import *

def intbytes(x: int) -> bytes:
    """Convert an integer to bytes

    :param x: The integer to convert
    :type x: int
    :return: `x` converted to bytes
    :rtype: bytes
    """
    return bytes((x,))


def uint16(x: int, endianness: Endianness) -> bytes:
    """Convert an integer to a C unsigned short.

    :param x: The integer to convert
    :type x: int
    :param endianness: The bit-endianness
    :type endianness: Endianness
    :return: `x` in C uint16-representation
    :rtype: bytes
    """
    return struct.pack(endianness.value + "H", x)

    
def uint32(x: int, endianness: Endianness) -> bytes:
    """Convert an integer to a C unsigned int.

    :param x: The integer to convert
    :type x: int
    :param endianness: The bit-endianness
    :type endianness: Endianness
    :return: `x` in C uint32-representation
    :rtype: bytes
    """
    return struct.pack(endianness.value + "I", x)


def makeSingleTextureAEI(format: Format, compressedImage: bytes, width: int, height: int, endianness: Endianness) -> BytesIO:
    """Convert a single, pre-compressed texture to an AEI file.
    No validation is performed on `compressedImage` or its format. `format`, `width` and `height` are assumed to be correct.

    :param format: The format that `compressedImage` was compressed into
    :type format: Format
    :param compressedImage: The compressed image to wrap in an AEI file
    :type compressedImage: bytes
    :param width: The width of `compressedImage` in pixels
    :type width: int
    :param height: The height of `compressedImage` in pixels
    :type height: int
    :param endianness: The bit-endianness
    :type endianness: Endianness
    :return: An AEI file wrapping `compressedImage`. These bytes can be written to a usable `.aei` file
    :rtype: BytesIO
    """
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
