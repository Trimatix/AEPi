from PIL import Image
from typing import List, TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from ..image import texture

def switchRGBA_BGRA(im: Image.Image):
    """Swap the red and blue channels of an image, in place.
    This method does not discern between RGB/BGR images.

    :param im: The image whose channels to swap
    :type im: Image
    """
    if im.mode == "RGB":
        r, g, b = im.split()
        return Image.merge("RGB", (b, g, r))
    
    elif im.mode == "RGBA":
        r, g, b, a = im.split()
        return Image.merge("RGBA", (b, g, r, a))
    
    raise ValueError("Only RGB/RGBA images are accepted")


def imageDimensionsForTextures(textures: List[texture.Texture]) -> Tuple[int, int]:
    """Find the minimum image shape required to contain all of the textures in `textures`.

    :param textures: The textures
    :type textures: List[texture.Texture]
    :return: (width, height)
    :rtype: Tuple[int, int]
    """
    width = 0
    height = 0

    for tex in textures:
        if (texWidth := tex.x + tex.image.width) > width:
            width = texWidth

        if (texHeight := tex.x + tex.image.height) > height:
            height = texHeight

    return width, height
