import os
from typing import Optional

from PIL import Image

from ..codec import ImageCodecAdaptor, supportsFormats
from ..constants import CompressionFormat, CompressionQuality
from ..exceptions import DependancyMissingException, UnsupportedCompressionFormatException
from ..lib.imageOps import switchRGBA_BGRA

try:
    import tex2img
except ImportError as e:
    raise DependancyMissingException("Tex2ImgCodec", "tex2img", e)

TEX2IMG_FORMAT_MAP = {
    # CompressionFormat.PVRTC14A: 12, # Tex2ImgCodec segfaults decoding PVRTC with all tests (#29)
    CompressionFormat.ATC: 14,
    CompressionFormat.DXT1: 5,
    CompressionFormat.DXT5: 6,
    CompressionFormat.ETC1: 0,
    CompressionFormat.ETC2: 2
}

# tex2img seems to swap ETC2's R and B channels - but not ETC1?
SWAP_CHANNELS_POST = { CompressionFormat.ETC2 }

@supportsFormats(decompresses=TEX2IMG_FORMAT_MAP.keys(), notOnPlatforms=["posix"])
class Tex2ImgCodec(ImageCodecAdaptor):
    @classmethod
    def decompress(cls, fp: bytes, format: CompressionFormat, width: int, height: int, quality: Optional[CompressionQuality]) -> Image.Image:
        if format not in TEX2IMG_FORMAT_MAP:
            raise ValueError(f"Codec {Tex2ImgCodec.__name__} does not support format {format.name}")
        
        if os.name == "posix":
            raise UnsupportedCompressionFormatException(format, f"Operating system '{os.name}' by {Tex2ImgCodec.__name__}. Please use another codec.")

        decompressed = tex2img.basisu_decompress(fp, width, height, TEX2IMG_FORMAT_MAP[format]) # type: ignore[reportUnknownMemberType]
        im = Image.frombytes("RGBA", (width, height), decompressed, "raw") # type: ignore[reportUnknownMemberType]
        
        if format in SWAP_CHANNELS_POST:
            with im:
                im = switchRGBA_BGRA(im)
        
        return im
