from typing import Optional
from typing import Optional
from PIL import Image
from ..codec import ImageCodecAdaptor, supportsFormats
from ..constants import CompressionFormat, CompressionQuality
from ..lib import imageOps

@supportsFormats(both=[
    CompressionFormat.Uncompressed_UI,
    CompressionFormat.Uncompressed_CubeMap_PC,
    CompressionFormat.Uncompressed_CubeMap
])
class RawCodec(ImageCodecAdaptor):
    @classmethod
    def compress(cls, im: Image.Image, format: CompressionFormat, quality: Optional[CompressionQuality]) -> bytes:
        if im.mode != format.pillowMode:
            im = im.convert(format.pillowMode)
            
        return im.tobytes()
    
    @classmethod
    def decompress(cls, fp: bytes, format: CompressionFormat, width: int, height: int, quality: Optional[CompressionQuality]) -> Image.Image:
        im = Image.frombytes("RGBA", (width, height), fp, "raw") # type: ignore[reportUnknownMemberType]
        
        if im.mode != format.pillowMode:
            result = im.convert(format.pillowMode)
            im.close()
        else:
            result = im
        
        if format.isBgra:
            with result:
                return imageOps.switchRGBA_BGRA(result)
        
        return result
