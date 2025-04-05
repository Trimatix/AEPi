from abc import ABC
from dataclasses import dataclass
from typing import BinaryIO, Dict, List, Optional, Type, TypeVar, Iterable
from PIL.Image import Image
import os

from .constants import CompressionFormat, CompressionQuality
from .exceptions import UnsupportedCompressionFormatException

class ImageCodecAdaptor(ABC):
    @classmethod
    def compress(cls, im: Image, format: CompressionFormat, quality: Optional[CompressionQuality]) -> bytes:
        """Compress an RGB(A) image into format `format`, with quality `quality`

        :param im: The image to compress
        :type im: Image
        :param format: The compression format
        :type format: CompressionFormat
        :param quality: The compression quality
        :type quality: CompressionQuality
        :return: `im`, compressed into format `format`
        :rtype: bytes
        """
        raise NotImplementedError(f"Codec {cls.__name__} is not capable of compression")


    @classmethod
    def decompress(cls, fp: bytes, format: CompressionFormat, width: int, height: int, quality: Optional[CompressionQuality]) -> Image:
        """Decompress a `format`-compressed RGB(A) image into a RGB(A) Image.

        :param fp: The compressed image to decompress
        :type im: bytes
        :param format: The compression format
        :type format: CompressionFormat
        :param width: The width of the image
        :type width: int
        :param height: The height of the image
        :type height: int
        :return: `fp`, decompressed into a RGB(A) image
        :rtype: Image
        """
        raise NotImplementedError(f"Codec {cls.__name__} is not capable of decompression")
    

    @classmethod
    def getCompressedImageLength(
        cls,
        readLength: int,
        fp: BinaryIO,
        format: CompressionFormat,
        mipmapped: bool,
        width: int,
        height: int
    ) -> int:
        """When reading an AEI file, override the compressed image length to read, in bytes, from `fp`.

        :param readLength: The length defined by the file
        :type readLength: int
        :param fp: The AEI file, with the cursor at the start position of the compressed image content
        :type fp: BinaryIO
        :param format: The compression format
        :type format: CompressionFormat
        :param mipmapped: Whether the image contains mipmaps
        :type mipmapped: bool
        :param width: The width of the image
        :type width: int
        :param height: The height of the image
        :type height: int
        :return: The full length in bytes of the compressed image content
        :rtype: int
        """
        return readLength


@dataclass
class CodecRegistration:
    codec: Type[ImageCodecAdaptor]
    notOnPlatforms: Optional[List[str]]


compressors: Dict[CompressionFormat, List[CodecRegistration]] = {}
decompressors: Dict[CompressionFormat, List[CodecRegistration]] = {}

TCodec = TypeVar("TCodec", bound=ImageCodecAdaptor)

def supportsFormats(
        compresses: Optional[Iterable[CompressionFormat]] = None,
        decompresses: Optional[Iterable[CompressionFormat]] = None,
        both: Optional[Iterable[CompressionFormat]] = None,
        notOnPlatforms: Optional[Iterable[str]] = None,
    ):
    """Class decorator marking an image codec as able to compress/decompress images into the given compression formats.
    The codec class must assume that RGB(A) is passed, and return RGB(A).

    ```py
    supportsFormats(
        compresses=[format1],
        decompresses=[format1]
    )
    ```

    is equivalent to:

    ```py
    supportsFormats(
        both=[format1]
    )
    ```

    If a codec does NOT support the named formats on any particular platforms, give them
    in the `notOnPlatforms` parameter. For possible values, see `os.name`.

    :param compresses: The formats that the codec can compress. defaults to None
    :type format: Optional[Iterable[CompressionFormat]]
    :param decompresses: The formats that the codec can decompress. defaults to None
    :type format: Optional[Iterable[CompressionFormat]]
    :param both: The formats that the codec can compress AND decompress. defaults to None
    :type format: Optional[Iterable[CompressionFormat]]
    :param notOnPlatforms: Platforms on which the formats are NOT supported. defaults to None
    :type notOnPlatforms: Optional[Iterable[str]]
    """
    notOnPlatforms = list(notOnPlatforms) if notOnPlatforms else None

    def inner(cls: Type[TCodec]) -> Type[TCodec]:
        registration = CodecRegistration(cls, notOnPlatforms)

        if compresses:
            for f in compresses:
                compressors.setdefault(f, []).append(registration)

        if decompresses:
            for f in decompresses:
                decompressors.setdefault(f, []).append(registration)

        if both:
            for f in both:
                compressors.setdefault(f, []).append(registration)
                decompressors.setdefault(f, []).append(registration)

        return cls
    return inner


def compressorFor(format: CompressionFormat) -> Type[ImageCodecAdaptor]:
    """Get the codec for the given compression format.

    :param format: The compression format for which the codec should support compression
    :type format: CompressionFormat
    :return: An ImageCodecAdaptor subclass that can compress `format`
    :rtype: Type[ImageCodecAdaptor]
    :raises AeiWriteException: If no compatible codec is loaded
    """
    if codecs := compressors.get(format, None):
        try:
            return next(
                reg.codec
                for reg in codecs
                if reg.notOnPlatforms is None or os.name not in reg.notOnPlatforms
            )
        except StopIteration:
            pass

    raise UnsupportedCompressionFormatException(format)


def decompressorFor(format: CompressionFormat) -> Type[ImageCodecAdaptor]:
    """Get the codec for the given decompression format.

    :param format: The compression format for which the codec should support decompression
    :type format: CompressionFormat
    :return: An ImageCodecAdaptor subclass that can decompress `format`
    :rtype: Type[ImageCodecAdaptor]
    :raises AeiReadException: If no compatible codec is loaded
    """
    if codecs := decompressors.get(format, None):
        try:
            return next(
                reg.codec
                for reg in codecs
                if reg.notOnPlatforms is None or os.name not in reg.notOnPlatforms
            )
        except StopIteration:
            pass

    raise UnsupportedCompressionFormatException(format)
