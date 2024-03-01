from typing import Type
from AEPi.codec import ImageCodecAdaptor, supportsFormats, compressorFor, decompressorFor
from AEPi.codec import compressors as RegisteredCompressors
from AEPi.codec import decompressors as RegisteredDecompressors
from AEPi.constants import CompressionFormat
from AEPi.exceptions import UnsupportedCompressionFormatException
from contextlib import contextmanager
import pytest
from PIL.Image import Image


@supportsFormats(compresses=[CompressionFormat.DXT5])
class Dxt5Compressor(ImageCodecAdaptor):
    @classmethod
    def compress(cls, im, format, quality): return b'' # type: ignore[reportMissingParameterType]
    
    @classmethod
    def decompress(cls, fp, format, width, height, quality): return Image() # type: ignore[reportMissingParameterType]


# @supportsFormats(decompresses=[CompressionFormat.ETC1])
class Etc1Decompressor(ImageCodecAdaptor):
    @classmethod
    def compress(cls, im, format, quality): return b'' # type: ignore[reportMissingParameterType]
    
    @classmethod
    def decompress(cls, fp, format, width, height, quality): return Image() # type: ignore[reportMissingParameterType]


# @supportsFormats(both=[CompressionFormat.PVRTC12A])
class PvrCodec(ImageCodecAdaptor):
    @classmethod
    def compress(cls, im, format, quality): return b'' # type: ignore[reportMissingParameterType]
    
    @classmethod
    def decompress(cls, fp, format, width, height, quality): return Image() # type: ignore[reportMissingParameterType]


@contextmanager
def mockCodecs():
    decompressors = {k: v for k, v in RegisteredDecompressors.items()}
    compressors = {k: v for k, v in RegisteredCompressors.items()}
    RegisteredDecompressors.clear()
    RegisteredCompressors.clear()
    supportsFormats(both=[CompressionFormat.PVRTC12A])(PvrCodec)
    supportsFormats(decompresses=[CompressionFormat.ETC1])(Etc1Decompressor)
    supportsFormats(compresses=[CompressionFormat.DXT5])(Dxt5Compressor)
    try:
        yield
    finally:
        RegisteredDecompressors.clear()
        RegisteredCompressors.clear()
        RegisteredDecompressors.update(decompressors)
        RegisteredCompressors.update(compressors)


@pytest.mark.parametrize(("format", "codec"),
                            [
                                (CompressionFormat.DXT5, Dxt5Compressor),
                                (CompressionFormat.PVRTC12A, PvrCodec)
                            ])
def test_compressorFor_GetsCorrectCodec(format: CompressionFormat, codec: Type[ImageCodecAdaptor]):
    with mockCodecs():
        compressor = compressorFor(format)
        assert compressor is codec


@pytest.mark.parametrize(("format", "codec"),
                            [
                                (CompressionFormat.ETC1, Etc1Decompressor),
                                (CompressionFormat.PVRTC12A, PvrCodec)
                            ])
def test_decompressorFor_GetsCorrectCodec(format: CompressionFormat, codec: Type[ImageCodecAdaptor]):
    with mockCodecs():
        decompressor = decompressorFor(format)
        assert decompressor is codec


def test_compressorFor_unknownFormat_throws():
    with mockCodecs():
        with pytest.raises(UnsupportedCompressionFormatException):
            compressorFor(CompressionFormat.PVRTC14A)
