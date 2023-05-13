from PIL import Image

def switchRGBA_BGRA(im: Image.Image):
    """Swap the red and blue channels of an image, and return as a new image.
    This method does not discern between RGB/BGR images.

    :param im: The image whose channels to swap
    :type im: Image
    :return: `im`, but with the red and blue channels swapped
    :rtype: Image
    """
    if im.mode == "RGB":
        r, g, b = im.split()
        return Image.merge("RGB", (b, g, r))
    
    elif im.mode == "RGBA":
        r, g, b, a = im.split()
        return Image.merge("RGBA", (b, g, r, a))
    
    raise ValueError("Only RGB/RGBA images are accepted")
