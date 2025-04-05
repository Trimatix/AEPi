from typing import BinaryIO, Optional
import PIL
from PIL.Image import Image
from contextlib import nullcontext
import os

from ..lib.imageOps import switchRGBA_BGRA
from ..codec import ImageCodecAdaptor, supportsFormats
from ..constants import CompressionFormat, CompressionQuality
from ..exceptions import DependancyMissingException, UnsupportedCompressionFormatException

try:
    import etcpak
except ImportError as e:
    raise DependancyMissingException("EtcPakCodec", "etcpak", e)

SWAP_CHANNELS_POST = {CompressionFormat.ETC1,CompressionFormat.ETC2}


@supportsFormats(
    compresses=[CompressionFormat.ETC1, CompressionFormat.ETC2],
    decompresses=[CompressionFormat.ETC2, CompressionFormat.DXT1, CompressionFormat.DXT5],
)
@supportsFormats(decompresses=[CompressionFormat.ETC1], notOnPlatforms=["nt"])
class EtcPakCodec(ImageCodecAdaptor):
    @classmethod
    def compress(
        cls, im: Image, format: CompressionFormat, quality: Optional[CompressionQuality]
    ) -> bytes:
        imageIn, ctx = cls._ensureRgba(im)
        with ctx:
            if format is CompressionFormat.DXT5:
                return etcpak.compress_to_dxt5(imageIn.tobytes(), imageIn.width, imageIn.height) # type: ignore[reportUnknownVariableType]

            elif format is CompressionFormat.ETC1:
                return etcpak.compress_to_etc1(imageIn.tobytes(), imageIn.width, imageIn.height) # type: ignore[reportUnknownVariableType]

            elif format is CompressionFormat.ETC2:
                # etcpak does provide a function for etc2 compression, but it produces almost completely black images
                # ETC2 is backwards compatible with ETC1, so as a stopgap we'll just compress as etc1
                # https://www.khronos.org/assets/uplo...pengl-es-bof/Ericsson-ETC2-SIGGRAPH_Aug12.pdf
                return etcpak.compress_to_etc1(imageIn.tobytes(), imageIn.width, imageIn.height) # type: ignore[reportUnknownVariableType]

        raise ValueError(
            f"Codec {EtcPakCodec.__name__} does not support format {format.name}"
        )

    @classmethod
    def decompress(
        cls,
        fp: bytes,
        format: CompressionFormat,
        width: int,
        height: int,
        quality: Optional[CompressionQuality],
    ) -> Image:
        match format:
            case CompressionFormat.DXT1:
                decompressed = etcpak.decompress_bc1(fp, width, height)
            case CompressionFormat.DXT5:
                decompressed = etcpak.decompress_bc3(fp, width, height)
            case CompressionFormat.ETC1:
                if os.name == "nt":
                    raise UnsupportedCompressionFormatException(format, f"{CompressionFormat.ETC1.name} is not supported on operating system '{os.name}' by {EtcPakCodec.__name__}. Please use another codec.")
                decompressed = etcpak.decompress_etc1_rgb(fp, width, height)
            case CompressionFormat.ETC2:
                decompressed = etcpak.decompress_etc2_rgb(fp, width, height)

        im = PIL.Image.frombytes("RGBA", (width, height), decompressed, "raw") # type: ignore[reportUnknownMemberType]

        if format in SWAP_CHANNELS_POST:
            with im:
                im = switchRGBA_BGRA(im)

        return im
    
    @classmethod
    def getCompressedImageLength(cls,
        readLength: int,
        fp: BinaryIO,
        format: CompressionFormat,
        mipmapped: bool,
        width: int,
        height: int,
    ) -> int:
        if not mipmapped:
            return super().getCompressedImageLength(readLength, fp, format, mipmapped, width, height)
        
        imageLength = width * height // 2

        # Adjust for these formats specifically
        if format in (CompressionFormat.ETC2, CompressionFormat.DXT5):
            imageLength *= 2

        return imageLength

    @classmethod
    def _ensureRgba(cls, im: Image):
        converted = im.mode != "RGBA"
        if converted:
            rgbaImg = im.convert("RGBA")
        else:
            rgbaImg = im

        return rgbaImg, (rgbaImg if converted else nullcontext())
