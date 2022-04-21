from PIL import Image # type: ignore[import]
import etcpak # type: ignore[import]
import config
import util
from io import BytesIO


def compressDXT5(im: Image.Image) -> bytes:
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    return etcpak.compress_to_dxt5(im.tobytes(), im.width, im.height)


def compressETC1(im: Image.Image) -> bytes:
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    return etcpak.compress_to_etc1(im.tobytes(), im.width, im.height)


_compress = {config.Format.DXT5: compressDXT5, config.Format.ETC1: compressETC1}


def makeAEI(im: Image.Image, platform: config.Platform) -> BytesIO:
    platformCfg: config.PlatformConfiguration = platform.value
    compressed = _compress[platformCfg.format](im)
    return util.makeSingleTextureAEI(platformCfg.format, compressed, im.width, im.height, platformCfg.endianness)
