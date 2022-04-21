from PIL import Image # type: ignore[import]
import etcpak # type: ignore[import]
from AEPi import config
from AEPi import util
from io import BytesIO


def compressDXT5(im: Image.Image) -> bytes:
    """Compress an image with DXT5 compression

    :param im: The image to convert
    :type im: Image.Image
    :return: `im` compressed with DXT5
    :rtype: bytes
    """
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    return etcpak.compress_to_dxt5(im.tobytes(), im.width, im.height)


def compressETC1(im: Image.Image) -> bytes:
    """Compress an image with ETC1 compression

    :param im: The image to convert
    :type im: Image.Image
    :return: `im` compressed with ETC1
    :rtype: bytes
    """
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    return etcpak.compress_to_etc1(im.tobytes(), im.width, im.height)


_compress = {config.Format.DXT5: compressDXT5, config.Format.ETC1: compressETC1}


def makeAEI(im: Image.Image, platform: config.Platform) -> BytesIO:
    """Convert a single image to AEI. This function is intended for converting ship textures,
    hence the limitation placed on compression format.

    :param im: The image to convert
    :type im: Image.Image
    :param platform: Which platform the image will be used on
    :type platform: config.Platform
    :return: The converted image as bytes
    :rtype: BytesIO
    """
    platformCfg: config.PlatformConfiguration = platform.value
    compressed = _compress[platformCfg.format](im)
    return util.makeSingleTextureAEI(platformCfg.format, compressed, im.width, im.height, platformCfg.endianness)
