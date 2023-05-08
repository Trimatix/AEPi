from io import BytesIO
from PIL.Image import Image
from ..codec import ImageCodecAdaptor, supportsFormats
from ..constants import CompressionFormat, CompressionQuality

try:
    import etcpak
except ImportError:
    raise ValueError("Cannot use codec EtcPakCodec, because required library etcpak is not installed")


@supportsFormats(compresses=[
    CompressionFormat.DXT5,
    CompressionFormat.ETC1
])
class EtcPakCodec(ImageCodecAdaptor):
    @classmethod
    def compress(cls, im: Image, format: CompressionFormat, quality: CompressionQuality) -> bytes:
        if format is CompressionFormat.DXT5:
            if im.mode != "RGBA":
                im = im.convert("RGBA")
            return etcpak.compress_to_dxt5(im.tobytes(), im.width, im.height)

        if format is CompressionFormat.ETC1:
            if im.mode != "RGBA":
                im = im.convert("RGBA")
            return etcpak.compress_to_etc1(im.tobytes(), im.width, im.height)
        
        raise ValueError(f"Codec {EtcPakCodec.__name__} does not support format {format.name}")
    

    @classmethod
    def decompress(cls, fp: BytesIO, format: CompressionFormat, quality: CompressionQuality) -> Image:
        raise NotImplemented(f"Codec {EtcPakCodec.__name__} is not capable of decompression")
    