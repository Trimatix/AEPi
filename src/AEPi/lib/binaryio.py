import struct
from typing import Literal, NamedTuple, BinaryIO, Optional, TypeVar, Union

ShortEndianness = Literal["<", ">"]
NameEndianness = Literal["little", "big"]

class Endianness(NamedTuple):
    name: NameEndianness
    short: ShortEndianness


def uint8(x: int, endianness: Endianness) -> bytes:
    """Convert an integer to a C unsigned char.

    :param x: The integer to convert
    :type x: int
    :param endianness: The bit-endianness
    :type endianness: Endianness
    :return: `x` in C uint8-representation
    :rtype: bytes
    """
    return struct.pack(endianness.short + "B", x)


def uint16(x: int, endianness: Endianness) -> bytes:
    """Convert an integer to a C unsigned short.

    :param x: The integer to convert
    :type x: int
    :param endianness: The bit-endianness
    :type endianness: Endianness
    :return: `x` in C uint16-representation
    :rtype: bytes
    """
    return struct.pack(endianness.short + "H", x)

    
def uint32(x: int, endianness: Endianness) -> bytes:
    """Convert an integer to a C unsigned int.

    :param x: The integer to convert
    :type x: int
    :param endianness: The bit-endianness
    :type endianness: Endianness
    :return: `x` in C uint32-representation
    :rtype: bytes
    """
    return struct.pack(endianness.short + "I", x)


TDefault = TypeVar("TDefault", bound=Optional[int])

def intFromBytes(b: bytes, endianness: Endianness, default: TDefault = 0) -> Union[int, TDefault]:
    """Interpret `b` as a python integer.

    :param b: The bytes to interpret
    :type b: bytes
    :param endianness: The bit-endianness
    :type endianness: Endianness
    :return: `b` interpreted as a python int
    :rtype: bytes
    """
    if b == b'':
        return default
    return int.from_bytes(b, byteorder=endianness.name)


def readUInt8(fp: BinaryIO, endianness: Endianness, default: TDefault = 0) -> Union[int, TDefault]:
    """Read a C unsigned char into a python integer.

    :param x: The binary stream from which to read
    :type x: BinaryIO
    :param endianness: The bit-endianness
    :type endianness: Endianness
    :return: The next 1 byte from `fp` interpreted as a C uint8
    :rtype: bytes
    """
    return intFromBytes(fp.read(1), endianness, default)


def readUInt16(fp: BinaryIO, endianness: Endianness, default: TDefault = 0) -> Union[int, TDefault]:
    """Read a C unsigned short into a python integer.

    :param x: The binary stream from which to read
    :type x: BinaryIO
    :param endianness: The bit-endianness
    :type endianness: Endianness
    :return: The next 2 bytes from `fp` interpreted as a C uint16
    :rtype: bytes
    """
    return intFromBytes(fp.read(2), endianness, default)

    
def readUInt32(fp: BinaryIO, endianness: Endianness, default: TDefault = 0) -> Union[int, TDefault]:
    """Read a C unsigned int into a python integer.

    :param x: The binary stream from which to read
    :type x: BinaryIO
    :param endianness: The bit-endianness
    :type endianness: Endianness
    :return: The next 4 bytes from `fp` interpreted as a C uint32
    :rtype: bytes
    """
    return intFromBytes(fp.read(4), endianness, default)
