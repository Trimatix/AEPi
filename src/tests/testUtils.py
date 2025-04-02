from typing import Any, Callable
from contextlib import contextmanager
from PIL.Image import Image

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