from typing import Type
from AEPi.codec import ImageCodecAdaptor, supportsFormats, compressorFor, decompressorFor
from AEPi.codec import compressors as RegisteredCompressors
from AEPi.codec import decompressors as RegisteredDecompressors
from AEPi.constants import CompressionFormat
from AEPi.exceptions import UnsupportedCompressionFormatException
from contextlib import contextmanager
import pytest
from PIL.Image import Image
import os

class MockCodec(ImageCodecAdaptor):
    @classmethod
    def compress(cls, im, format, quality): return b'' # type: ignore[reportMissingParameterType]
    
    @classmethod
    def decompress(cls, fp, format, width, height, quality): return Image() # type: ignore[reportMissingParameterType]


@supportsFormats(compresses=[CompressionFormat.DXT5])
class Dxt5Compressor(MockCodec): ...


class Etc1Decompressor(MockCodec): ...


class PvrCodec(MockCodec): ...


class AtcCodec(MockCodec): ...


class UncompressedCodec(MockCodec): ...


@contextmanager
def mockCodecs():
    decompressors = [i for i in RegisteredDecompressors]
    compressors = [i for i in RegisteredCompressors]
    RegisteredDecompressors.clear()
    RegisteredCompressors.clear()
    supportsFormats(both=[CompressionFormat.PVRTC12A])(PvrCodec)
    supportsFormats(decompresses=[CompressionFormat.ETC1])(Etc1Decompressor)
    supportsFormats(compresses=[CompressionFormat.DXT5])(Dxt5Compressor)
    supportsFormats(decompresses=[CompressionFormat.ATC], notOnPlatforms=["nt"])(AtcCodec)
    supportsFormats(decompresses=[CompressionFormat.Uncompressed], notOnPlatforms=["posix"])(UncompressedCodec)
    try:
        yield
    finally:
        RegisteredDecompressors.clear()
        RegisteredCompressors.clear()
        RegisteredDecompressors.extend(decompressors)
        RegisteredCompressors.extend(compressors)


@pytest.mark.parametrize(("format", "codec"),
                            [
                                (CompressionFormat.DXT5, Dxt5Compressor),
                                (CompressionFormat.PVRTC12A, PvrCodec)
                            ])
def test_compressorFor_getsCorrectCodec(format: CompressionFormat, codec: Type[ImageCodecAdaptor]):
    with mockCodecs():
        compressor = compressorFor(format)
        assert compressor is codec


@pytest.mark.parametrize(("format", "codec"),
                            [
                                (CompressionFormat.ETC1, Etc1Decompressor),
                                (CompressionFormat.PVRTC12A, PvrCodec)
                            ])
def test_decompressorFor_getsCorrectCodec(format: CompressionFormat, codec: Type[ImageCodecAdaptor]):
    with mockCodecs():
        decompressor = decompressorFor(format)
        assert decompressor is codec


def test_compressorFor_unknownFormat_throws():
    with mockCodecs():
        with pytest.raises(UnsupportedCompressionFormatException):
            compressorFor(CompressionFormat.PVRTC14A)


@pytest.mark.skipif(os.name != "nt", reason="Test logic relies on the host being windows")
def test_decompressorFor_windows_respectsPlatformRestriction():
    with mockCodecs():
        with pytest.raises(UnsupportedCompressionFormatException):
            decompressorFor(CompressionFormat.ATC)
        decompressor = decompressorFor(CompressionFormat.Uncompressed)
        assert decompressor is UncompressedCodec


@pytest.mark.skipif(os.name != "posix", reason="Test logic relies on the host being linux")
def test_decompressorFor_linux_respectsPlatformRestriction():
    with mockCodecs():
        with pytest.raises(UnsupportedCompressionFormatException):
            decompressorFor(CompressionFormat.Uncompressed)
        decompressor = decompressorFor(CompressionFormat.ATC)
        assert decompressor is AtcCodec