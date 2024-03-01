from abc import ABC
from typing import Dict, Optional, Type, TypeVar, Iterable
from PIL.Image import Image

from .constants import CompressionFormat, CompressionQuality
from .exceptions import UnsupportedCompressionFormatException

class ImageCodecAdaptor(ABC):
    @classmethod
    def compress(cls, im: Image, format: CompressionFormat, quality: Optional[CompressionQuality]) -> bytes:
        """Compress a BGRA image into format `format`, with quality `quality`

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
        """Decompress a `format`-compressed BGRA image into a BGRA Image.

        :param fp: The compressed image to decompress
        :type im: bytes
        :param format: The compression format
        :type format: CompressionFormat
        :param width: The width of the image
        :type width: int
        :param height: The height of the image
        :type height: int
        :return: `fp`, decompressed into a BGRA image
        :rtype: Image
        """
        raise NotImplementedError(f"Codec {cls.__name__} is not capable of decompression")


compressors: Dict[CompressionFormat, Type[ImageCodecAdaptor]] = {}
decompressors: Dict[CompressionFormat, Type[ImageCodecAdaptor]] = {}

TCodec = TypeVar("TCodec", bound=ImageCodecAdaptor)

def supportsFormats(
        compresses: Optional[Iterable[CompressionFormat]] = None,
        decompresses: Optional[Iterable[CompressionFormat]] = None,
        both: Optional[Iterable[CompressionFormat]] = None
    ):
    """Class decorator marking an image codec as able to compress/decompress images into the given compression formats.
    The codec class must assume that BGRA is passed, and return BGRA.

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

    :param compresses: The formats that the codec can compress. defaults to None
    :type format: Optional[Iterable[CompressionFormat]]
    :param decompresses: The formats that the codec can decompress. defaults to None
    :type format: Optional[Iterable[CompressionFormat]]
    :param both: The formats that the codec can compress AND decompress. defaults to None
    :type format: Optional[Iterable[CompressionFormat]]
    """
    def inner(cls: Type[TCodec]) -> Type[TCodec]:
        if compresses:
            for f in compresses:
                compressors[f] = cls

        if decompresses:
            for f in decompresses:
                decompressors[f] = cls

        if both:
            for f in both:
                compressors[f] = cls
                decompressors[f] = cls
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
    if format not in compressors:
        raise UnsupportedCompressionFormatException(format)
    return compressors[format]


def decompressorFor(format: CompressionFormat) -> Type[ImageCodecAdaptor]:
    """Get the codec for the given decompression format.

    :param format: The compression format for which the codec should support decompression
    :type format: CompressionFormat
    :return: An ImageCodecAdaptor subclass that can decompress `format`
    :rtype: Type[ImageCodecAdaptor]
    :raises AeiReadException: If no compatible codec is loaded
    """
    if format not in decompressors:
        raise UnsupportedCompressionFormatException(format)
    return decompressors[format]
