from typing import Optional
from io import BytesIO
from PIL import Image
from ..codec import ImageCodecAdaptor, supportsFormats
from ..constants import CompressionFormat, CompressionQuality
from PIL.DdsImagePlugin import DdsRgbDecoder

FORMAT_MODE_MAP = {
    CompressionFormat.DXT1: "RGB",
    CompressionFormat.DXT5: "RGBA"
}

@supportsFormats(decompresses=FORMAT_MODE_MAP.keys())
class PillowCodec(ImageCodecAdaptor):
    @classmethod
    def compress(cls, im: Image.Image, format: CompressionFormat, quality: Optional[CompressionQuality]) -> bytes:
        raise NotImplementedError(f"Codec {PillowCodec.__name__} is not capable of compression")
    

    @classmethod
    def decompress(cls, fp: BytesIO, format: CompressionFormat) -> Image.Image:
        if format not in [CompressionFormat.DXT1, CompressionFormat.DXT3, CompressionFormat.DXT5]:
            raise ValueError(f"Codec {PillowCodec.__name__} does not support format {format.name}")

        if format == CompressionFormat.DXT1:
            mode = "RGB"
        decoder = DdsRgbDecoder()
        return Image.open(fp, formats=["dds"])
        
    