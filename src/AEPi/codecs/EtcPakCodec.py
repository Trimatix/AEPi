from typing import Optional
from typing import Optional
from PIL.Image import Image
from contextlib import nullcontext
from ..codec import ImageCodecAdaptor, supportsFormats
from ..constants import CompressionFormat, CompressionQuality
from ..exceptions import DependancyMissingException
from ..lib import imageOps

try:
    import etcpak
except ImportError as e:
    raise DependancyMissingException("EtcPakCodec", "etcpak", e)


@supportsFormats(compresses=[
    CompressionFormat.DXT5,
    CompressionFormat.ETC1
])
class EtcPakCodec(ImageCodecAdaptor):
    @classmethod
    def compress(cls, im: Image, format: CompressionFormat, quality: Optional[CompressionQuality]) -> bytes:
        imageIn, ctx = cls._ensureRgba(im)
        with ctx:
            imageIn, ctx = cls._maybeSwapChannels(imageIn, format)
            with ctx:
                if format is CompressionFormat.DXT5:
                    return etcpak.compress_to_dxt5(imageIn.tobytes(), imageIn.width, imageIn.height) # type: ignore[reportUnknownVariableType]

                elif format is CompressionFormat.ETC1:
                    return etcpak.compress_to_etc1(imageIn.tobytes(), imageIn.width, imageIn.height) # type: ignore[reportUnknownVariableType]
        
        raise ValueError(f"Codec {EtcPakCodec.__name__} does not support format {format.name}")
    
    
    @classmethod
    def _ensureRgba(cls, im: Image):
        converted = im.mode != "RGBA"
        if converted:
            rgbaImg = im.convert("RGBA")
        else:
            rgbaImg = im
        
        return rgbaImg, (rgbaImg if converted else nullcontext())
    
    
    @classmethod
    def _maybeSwapChannels(cls, im: Image, format: CompressionFormat):
        swapped = format.isBgra
        if swapped:
            bgraImg = imageOps.switchRGBA_BGRA(im)
        else:
            bgraImg = im
        
        return bgraImg, (bgraImg if swapped else nullcontext())
