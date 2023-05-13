from abc import ABC, abstractmethod
from typing import Dict, Optional, Type, TypeVar, Iterable
from PIL.Image import Image

from .constants import CompressionFormat, CompressionQuality

class ImageCodecAdaptor(ABC):
    @classmethod
    @abstractmethod
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
        raise NotImplementedError()


    @classmethod
    @abstractmethod
    def decompress(cls, fp: bytes, format: CompressionFormat, quality: Optional[CompressionQuality]) -> Image:
        """Decompress a `format`-compressed BGRA image into a BGRA Image.

        :param fp: The compressed image to decompress
        :type im: bytes
        :param format: The compression format
        :type format: CompressionFormat
        :return: `fp`, decompressed into a BGRA image
        :rtype: Image
        """
        raise NotImplementedError()


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
        for f in compresses or []:
            compressors[f] = cls

        for f in decompresses or []:
            decompressors[f] = cls

        for f in both or []:
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
    :raises KeyError: If no compatible codec is loaded
    """
    if format not in compressors:
        raise KeyError(f"No {ImageCodecAdaptor.__name__} found for format '{format.name}' compression. Make sure that the module containing the class has been imported.")
    return compressors[format]


def decompressorFor(format: CompressionFormat) -> Type[ImageCodecAdaptor]:
    """Get the codec for the given decompression format.

    :param format: The compression format for which the codec should support decompression
    :type format: CompressionFormat
    :return: An ImageCodecAdaptor subclass that can decompress `format`
    :rtype: Type[ImageCodecAdaptor]
    :raises KeyError: If no compatible codec is loaded
    """
    if format not in decompressors:
        raise KeyError(f"No {ImageCodecAdaptor.__name__} found for format '{format.name}' decompression. Make sure that the module containing the class has been imported.")
    return decompressors[format]
