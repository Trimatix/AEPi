from typing import Optional
from typing import Optional
from PIL import Image
from ..codec import ImageCodecAdaptor, supportsFormats
from ..constants import CompressionFormat, CompressionQuality

@supportsFormats(both=[
    CompressionFormat.Uncompressed_UI,
    CompressionFormat.Uncompressed_CubeMap_PC,
    CompressionFormat.Uncompressed_CubeMap
])
class RawCodec(ImageCodecAdaptor):
    @classmethod
    def compress(cls, im: Image.Image, format: CompressionFormat, quality: Optional[CompressionQuality]) -> bytes:
        return im.tobytes() # type: ignore[reportUnknownMemberType]
    
    
    @classmethod
    def decompress(cls, fp: bytes, format: CompressionFormat, width: int, height: int, quality: Optional[CompressionQuality]) -> Image.Image:
        return Image.frombytes("RGBA", (width, height), fp, "raw") # type: ignore[reportUnknownMemberType]
    