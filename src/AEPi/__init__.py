from .image import AEI, Texture
from .constants import CompressionFormat, CompressionQuality
from .codec import *
from . import codecs
from . import lib
from .lib.imageOps import switchRGBA_BGRA

__version__ = "0.8.0.1"
__all__ = ["AEI", "Texture", "CompressionFormat", "CompressionQuality", "codecs", "lib", "switchRGBA_BGRA", "codec"]
