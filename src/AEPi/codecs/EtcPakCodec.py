from typing import Optional
from typing import Optional
from PIL.Image import Image
from ..codec import ImageCodecAdaptor, supportsFormats
from ..constants import CompressionFormat, CompressionQuality
from ..exceptions import DependancyMissingException

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
        if format is CompressionFormat.DXT5:
            if im.mode != "RGBA":
                im = im.convert("RGBA")
            return etcpak.compress_to_dxt5(im.tobytes(), im.width, im.height) # type: ignore[reportUnknownVariableType]

        if format is CompressionFormat.ETC1:
            if im.mode != "RGBA":
                im = im.convert("RGBA")
            return etcpak.compress_to_etc1(im.tobytes(), im.width, im.height) # type: ignore[reportUnknownVariableType]
        
        raise ValueError(f"Codec {EtcPakCodec.__name__} does not support format {format.name}")
