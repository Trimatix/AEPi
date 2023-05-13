import pytest
from PIL import Image
from AEPi.lib import imageOps

def test_switchRGBA_BGRA_switchesChannels():
    with Image.new("RGBA", (1, 1), (50, 100, 150, 200)) as im:
        with imageOps.switchRGBA_BGRA(im) as swapped:
            assert swapped.getpixel((0, 0)) == (150, 100, 50, 200)


def test_switchRGBA_BGRA_incorrectMode_raises():
    with Image.new("L", (1, 1)) as im:
        with pytest.raises(ValueError):
            imageOps.switchRGBA_BGRA(im)
