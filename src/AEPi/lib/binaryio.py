import struct
from typing import Literal

Endianness = Literal["<", ">"]


def uint8(x: int, endianness: Endianness) -> bytes:
    """Convert an integer to a C unsigned char.

    :param x: The integer to convert
    :type x: int
    :param endianness: The bit-endianness
    :type endianness: Endianness
    :return: `x` in C uint8-representation
    :rtype: bytes
    """
    return struct.pack(endianness + "B", x)


def uint16(x: int, endianness: Endianness) -> bytes:
    """Convert an integer to a C unsigned short.

    :param x: The integer to convert
    :type x: int
    :param endianness: The bit-endianness
    :type endianness: Endianness
    :return: `x` in C uint16-representation
    :rtype: bytes
    """
    return struct.pack(endianness + "H", x)

    
def uint32(x: int, endianness: Endianness) -> bytes:
    """Convert an integer to a C unsigned int.

    :param x: The integer to convert
    :type x: int
    :param endianness: The bit-endianness
    :type endianness: Endianness
    :return: `x` in C uint32-representation
    :rtype: bytes
    """
    return struct.pack(endianness + "I", x)
