from typing import Optional
from typing import Optional
from PIL import Image
from ..codec import ImageCodecAdaptor, supportsFormats
from ..constants import CompressionFormat, CompressionQuality
from ..exceptions import DependancyMissingException

try:
    import tex2img
except ImportError as e:
    raise DependancyMissingException("Tex2ImgCodec", "tex2img", e)

TEX2IMG_FORMAT_MAP = {
    # CompressionFormat.PVRTC14A: 12, # Tex2ImgCodec segfaults decoding PVRTC with all tests (#29)
    CompressionFormat.ATC: 14,
    CompressionFormat.DXT1: 5,
    CompressionFormat.DXT5: 6,
    CompressionFormat.ETC1: 0
}


@supportsFormats(decompresses=TEX2IMG_FORMAT_MAP.keys())
class Tex2ImgCodec(ImageCodecAdaptor):
    @classmethod
    def decompress(cls, fp: bytes, format: CompressionFormat, width: int, height: int, quality: Optional[CompressionQuality]) -> Image.Image:
        if format not in TEX2IMG_FORMAT_MAP:
            raise ValueError(f"Codec {Tex2ImgCodec.__name__} does not support format {format.name}")
        
        decompressed = tex2img.basisu_decompress(fp, width, height, TEX2IMG_FORMAT_MAP[format]) # type: ignore[reportUnknownMemberType]
        im = Image.frombytes("RGBA", (width, height), decompressed, "raw") # type: ignore[reportUnknownMemberType]
        
        if im.mode != format.pillowMode:
            return im.convert(format.pillowMode)
        return im
