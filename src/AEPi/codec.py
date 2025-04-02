from abc import ABC
from typing import List, Optional, Tuple, Type, TypeVar, Iterable
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


compressors: List[Tuple[CompressionFormat, Optional[List[str]], Type[ImageCodecAdaptor]]] = []
decompressors: List[Tuple[CompressionFormat, Optional[List[str]], Type[ImageCodecAdaptor]]] = []

TCodec = TypeVar("TCodec", bound=ImageCodecAdaptor)

def supportsFormats(
        compresses: Optional[Iterable[CompressionFormat]] = None,
        decompresses: Optional[Iterable[CompressionFormat]] = None,
        both: Optional[Iterable[CompressionFormat]] = None,
        notOnPlatforms: Optional[Iterable[str]] = None
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
        if compresses:
            for f in compresses:
                compressors.append((f, notOnPlatforms, cls))

        if decompresses:
            for f in decompresses:
                decompressors.append((f, notOnPlatforms, cls))

        if both:
            for f in both:
                compressors.append((f, notOnPlatforms, cls))
                decompressors.append((f, notOnPlatforms, cls))

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
    try:
        return next(
            codec
            for (f, notOnPlatforms, codec) in compressors
            if f == format and (notOnPlatforms is None or os.name not in notOnPlatforms)
        )
    except StopIteration:
        raise UnsupportedCompressionFormatException(format)


def decompressorFor(format: CompressionFormat) -> Type[ImageCodecAdaptor]:
    """Get the codec for the given decompression format.

    :param format: The compression format for which the codec should support decompression
    :type format: CompressionFormat
    :return: An ImageCodecAdaptor subclass that can decompress `format`
    :rtype: Type[ImageCodecAdaptor]
    :raises AeiReadException: If no compatible codec is loaded
    """
    try:
        return next(
            codec
            for (f, notOnPlatforms, codec) in decompressors
            if f == format and (notOnPlatforms is None or os.name not in notOnPlatforms)
        )
    except StopIteration:
        raise UnsupportedCompressionFormatException(format)
