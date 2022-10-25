from PIL import Image # type: ignore[import]
import etcpak # type: ignore[import]
from . import config
from . import util
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


def bgrToRgb(im: Image.Image) -> Image.Image:
    """Convert swap the red and blue channels in an RGB or RGBA image, and create a new image from the result.
    The final image will still be RGB/RGBA mode, rather than BGR/BRGA, since this is not supported by Pillow.

    :param im: The image to copy
    :type im: Image.Image
    :raises ValueError: If `im.mode` is neither `"RGBA"` nor `"RGB"`
    :return: A copy of `im`, in the same mode, but with the blue and red channels swapped
    :rtype: Image.Image
    """
    if im.mode == "RGB":
        r, g, b = im.split()
        return Image.merge("RGB", (b, g, r))
    
    elif im.mode == "RGBA":
        r, g, b, a = im.split()
        return Image.merge("RGBA", (b, g, r, a))
    
    raise ValueError("Only RGB/RGBA images are accepted")


_compress = {config.Format.DXT5: compressDXT5, config.Format.ETC1: compressETC1}


def makeAEI(im: Image.Image, platform: config.Platform, convertToBGR: bool = True) -> BytesIO:
    """Convert a single image to AEI. This function is intended for converting ship textures,
    hence the limitation placed on compression format.
    
    In AEI images, the blue and red channels are swapped - the image is BGR as opposed to RGB.
    Unless `convertToBGR` is given as `False`, `im` is assumed to be in RGB format. If platform.format is ETC, a copy will be made in BGR format prior to compression.    

    :param im: The image to convert
    :type im: Image.Image
    :param platform: Which platform the image will be used on
    :type platform: config.Platform
    :return: The converted image as bytes
    :rtype: BytesIO
    """
    platformCfg: config.PlatformConfiguration = platform.value
    if platformCfg.format == config.Format.ETC1 and convertToBGR:
        im = bgrToRgb(im)
    
    compressed = _compress[platformCfg.format](im)
    aei = util.makeSingleTextureAEI(platformCfg.format, compressed, im.width, im.height, platformCfg.endianness)
    
    if convertToBGR:
        im.close()
        
    return aei
