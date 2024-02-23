from typing import Optional
from io import BytesIO
from PIL import Image
from ..codec import ImageCodecAdaptor, supportsFormats
from ..constants import CompressionFormat, CompressionQuality


@supportsFormats(decompresses=[
    CompressionFormat.DXT1,
    CompressionFormat.DXT3,
    CompressionFormat.DXT5
])
class PillowCodec(ImageCodecAdaptor):
    @classmethod
    def compress(cls, im: Image.Image, format: CompressionFormat, quality: Optional[CompressionQuality]) -> bytes:
        raise NotImplementedError(f"Codec {PillowCodec.__name__} is not capable of compression")
    

    @classmethod
    def decompress(cls, fp: BytesIO, format: CompressionFormat) -> Image.Image:
        if format not in [CompressionFormat.DXT1, CompressionFormat.DXT3, CompressionFormat.DXT5]:
            raise ValueError(f"Codec {PillowCodec.__name__} does not support format {format.name}")

        return Image.open(fp, formats=["dxt1", "dxt5"])
        
    