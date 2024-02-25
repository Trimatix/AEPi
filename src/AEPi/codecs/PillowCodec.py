from typing import Optional
from PIL import Image, ImageFile, __version__ as PillowVersion
from ..codec import ImageCodecAdaptor, supportsFormats
from ..constants import CompressionFormat, CompressionQuality
from ..exceptions import DependencyFailedException

try:
    pillowVersionSplit = PillowVersion.split(".")
    if (int(pillowVersionSplit[0]), int(pillowVersionSplit[1])) < (10, 2):
        raise DependencyFailedException("PillowCodec", "pillow", None, "installed Pillow version is lower than the required 10.2.x")
except Exception as ex:
    if not isinstance(ex, DependencyFailedException):
        raise ex
    raise DependencyFailedException("PillowCodec", "pillow", ex, "installed Pillow version could not be determined")

try:
    from PIL.DdsImagePlugin import DdsRgbDecoder
except ImportError as ex:
    raise DependencyFailedException("PillowCodec", "pillow", ex, "installed Pillow version does not include the DDS decoder")


# The channel configuration
FORMAT_MODE_MAP = {
    CompressionFormat.DXT1: "RGB",
    CompressionFormat.DXT5: "RGBA"
}

# The bits per pixel
FORMAT_BITCOUNT_MAP = {
    CompressionFormat.DXT1: 4,
    CompressionFormat.DXT5: 8
}

# I'm not sure what "masks" are in DXT; something to look into later.
FORMAT_MASKS_MAP = {
    CompressionFormat.DXT1: (),
    CompressionFormat.DXT5: ()
}

def makeImageFile(width: int, height: int, mode: str, pixelFormat: str):
    class AepiDdsImageFile(ImageFile.ImageFile):
        format = "DDS"
        format_description = "DirectDraw Surface"

        def _open(self):
            self._size = (width, height)
            self._mode  = mode
            self.pixel_format = pixelFormat
            extents = (0, 0) + self.size
            self.tile = [("raw", extents, 0, self.mode)]

    return AepiDdsImageFile


@supportsFormats(decompresses=FORMAT_MODE_MAP.keys())
class PillowCodec(ImageCodecAdaptor):
    @classmethod
    def compress(cls, im: Image.Image, format: CompressionFormat, quality: Optional[CompressionQuality]) -> bytes:
        raise NotImplementedError(f"Codec {PillowCodec.__name__} is not capable of compression")
    

    @classmethod
    def decompress(cls, fp: bytes, format: CompressionFormat, width: int, height: int, quality: Optional[CompressionQuality]) -> Image.Image:
        if format not in FORMAT_MODE_MAP:
            raise ValueError(f"Codec {PillowCodec.__name__} does not support format {format.name}")

        Image.
        mode = FORMAT_MODE_MAP[format]
        decoder = DdsRgbDecoder(mode)
        Image.frombytes(mode, (width, height), fp, decoder_name="dds_rgb")
        return Image.open(fp, formats=["dds"])
        
    