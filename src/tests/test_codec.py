from typing import Type, Any, Callable
import pytest
import os
from contextlib import contextmanager
from PIL.Image import Image

from AEPi.codec import ImageCodecAdaptor, supportsFormats, compressorFor, decompressorFor
from AEPi.constants import CompressionFormat
from AEPi.exceptions import UnsupportedCompressionFormatException
from AEPi.codec import ImageCodecAdaptor
from AEPi.codec import compressors as RegisteredCompressors
from AEPi.codec import decompressors as RegisteredDecompressors

class MockCodec(ImageCodecAdaptor):
    @classmethod
    def compress(cls, im, format, quality): return b'' # type: ignore[reportMissingParameterType]
    
    @classmethod
    def decompress(cls, fp, format, width, height, quality): return Image() # type: ignore[reportMissingParameterType]


@contextmanager
def mockCodecsContext(setupCodecs: Callable[[], Any]):
    decompressors = {k: v for k, v in RegisteredDecompressors.items()}
    compressors = {k: v for k, v in RegisteredCompressors.items()}
    RegisteredDecompressors.clear()
    RegisteredCompressors.clear()

    setupCodecs()
    
    try:
        yield
    finally:
        RegisteredDecompressors.clear()
        RegisteredCompressors.clear()
        RegisteredDecompressors.update(decompressors)
        RegisteredCompressors.update(compressors)


class Dxt5Compressor(MockCodec): ...


class Etc1Decompressor(MockCodec): ...


class PvrCodec(MockCodec): ...


class AtcCodec(MockCodec): ...


class UncompressedCodec(MockCodec): ...


def setupCodecs():
    supportsFormats(both=[CompressionFormat.PVRTC12A])(PvrCodec)
    supportsFormats(decompresses=[CompressionFormat.ETC1])(Etc1Decompressor)
    supportsFormats(compresses=[CompressionFormat.DXT5])(Dxt5Compressor)
    supportsFormats(decompresses=[CompressionFormat.ATC], notOnPlatforms=["nt"])(AtcCodec)
    supportsFormats(decompresses=[CompressionFormat.Uncompressed], notOnPlatforms=["posix"])(UncompressedCodec)


@pytest.mark.parametrize(("format", "codec"),
                            [
                                (CompressionFormat.DXT5, Dxt5Compressor),
                                (CompressionFormat.PVRTC12A, PvrCodec)
                            ])
def test_compressorFor_getsCorrectCodec(format: CompressionFormat, codec: Type[ImageCodecAdaptor]):
    with mockCodecsContext(setupCodecs):
        compressor = compressorFor(format)
        assert compressor is codec


@pytest.mark.parametrize(("format", "codec"),
                            [
                                (CompressionFormat.ETC1, Etc1Decompressor),
                                (CompressionFormat.PVRTC12A, PvrCodec)
                            ])
def test_decompressorFor_getsCorrectCodec(format: CompressionFormat, codec: Type[ImageCodecAdaptor]):
    with mockCodecsContext(setupCodecs):
        decompressor = decompressorFor(format)
        assert decompressor is codec


def test_compressorFor_unknownFormat_throws():
    with mockCodecsContext(setupCodecs):
        with pytest.raises(UnsupportedCompressionFormatException):
            compressorFor(CompressionFormat.PVRTC14A)


@pytest.mark.skipif(os.name != "nt", reason="Test logic relies on the host being windows")
def test_decompressorFor_windows_respectsPlatformRestriction():
    with mockCodecsContext(setupCodecs):
        with pytest.raises(UnsupportedCompressionFormatException):
            decompressorFor(CompressionFormat.ATC)
        decompressor = decompressorFor(CompressionFormat.Uncompressed)
        assert decompressor is UncompressedCodec


@pytest.mark.skipif(os.name != "posix", reason="Test logic relies on the host being linux")
def test_decompressorFor_linux_respectsPlatformRestriction():
    with mockCodecsContext(setupCodecs):
        with pytest.raises(UnsupportedCompressionFormatException):
            decompressorFor(CompressionFormat.Uncompressed)
        decompressor = decompressorFor(CompressionFormat.ATC)
        assert decompressor is AtcCodec