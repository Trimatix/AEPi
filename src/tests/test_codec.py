from typing import Type
from AEPi.codec import ImageCodecAdaptor, supportsFormats, compressorFor, decompressorFor
from AEPi.constants import CompressionFormat
import pytest


@supportsFormats(compresses=[CompressionFormat.DXT5])
class Dxt5Compressor(ImageCodecAdaptor):
    @classmethod
    def compress(cls, im, format, quality): pass
    
    @classmethod
    def decompress(cls, fp, format): pass


@supportsFormats(decompresses=[CompressionFormat.ETC1])
class Etc1Decompressor(ImageCodecAdaptor):
    @classmethod
    def compress(cls, im, format, quality): pass
    
    @classmethod
    def decompress(cls, fp, format): pass


@supportsFormats(both=[CompressionFormat.PVRTCI2A])
class PvrCodec(ImageCodecAdaptor):
    @classmethod
    def compress(cls, im, format, quality): pass
    
    @classmethod
    def decompress(cls, fp, format): pass


@pytest.mark.parametrize(("format", "codec"),
                            [
                                (CompressionFormat.DXT5, Dxt5Compressor),
                                (CompressionFormat.PVRTCI2A, PvrCodec)
                            ])
def test_compressorFor_GetsCorrectCodec(format: CompressionFormat, codec: Type[ImageCodecAdaptor]):
    assert compressorFor(format) is codec


@pytest.mark.parametrize(("format", "codec"),
                            [
                                (CompressionFormat.ETC1, Etc1Decompressor),
                                (CompressionFormat.PVRTCI2A, PvrCodec)
                            ])
def test_decompressorFor_GetsCorrectCodec(format: CompressionFormat, codec: Type[ImageCodecAdaptor]):
    assert decompressorFor(format) is codec


def test_compressorFor_unknownFormat_throws():
    with pytest.raises(KeyError):
        compressorFor(CompressionFormat.PVRTCI4A)