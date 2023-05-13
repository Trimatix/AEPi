from io import BytesIO

from PIL.Image import Image
from AEPi import AEI, Texture, CompressionFormat
from AEPi.codecs import EtcPakCodec
from AEPi.codec import ImageCodecAdaptor, supportsFormats
import pytest
from PIL import Image

from AEPi.constants import CompressionFormat

SMILEY_AEI_PATH = "src/tests/assets/smiley_DXT5_nomipmap_nosymbols_high.aei"
SMILEY_PNG_PATH = "src/tests/assets/smiley.png"

PIXEL_AEI_PATH = "src/tests/assets/pixel_ATC_nomipmap_nosymbols_high.aei"

DECOMPRESSED = Image.new("RGBA", (1, 1), (100, 200, 200, 255))
# This is the RGBA pixel from DECOMPRESSED, compressed to ATC 4bpp using AEIEditor.
COMPRESSED = b"\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\x58\x66\xFF\xFF\xFF\xFF"


def smileyImage():
    png = Image.open(SMILEY_PNG_PATH)

    if png.mode != "RGBA":
        return png.convert("RGBA")
    
    return png


@supportsFormats(
    both=[CompressionFormat.ATC]
)
class MockCodec(ImageCodecAdaptor):
    @classmethod
    def compress(cls, im, format, quality):
        return COMPRESSED
    
    @classmethod
    def decompress(cls, fp, format, quality):
        return DECOMPRESSED

#region dimensions

def test_resize_shrink_succeeds():
    with AEI((10, 10)) as aei:
        aei.addTexture(Texture(0, 0, 9, 10))
        aei.shape = (9, 10)
        assert aei.shape == (9, 10)


def test_resize_grow_succeeds():
    with AEI((10, 10)) as aei:
        aei.addTexture(Texture(0, 0, 10, 10))
        aei.shape = (11, 10)
        assert aei.shape == (11, 10)


def test_setWidth_shrink_succeeds():
    with AEI((10, 10)) as aei:
        aei.addTexture(Texture(0, 0, 9, 10))
        aei.width = 9
        assert aei.width == 9


def test_setWidth_grow_succeeds():
    with AEI((10, 10)) as aei:
        aei.addTexture(Texture(0, 0, 10, 10))
        aei.width = 11
        assert aei.width == 11


def test_setHeight_grow_succeeds():
    with AEI((10, 10)) as aei:
        aei.addTexture(Texture(0, 0, 10, 10))
        aei.height = 10
        assert aei.height == 10


def test_setHeight_shrink_succeeds():
    with AEI((10, 10)) as aei:
        aei.addTexture(Texture(0, 0, 10, 9))
        aei.height = 9
        assert aei.height == 9


def test_resize_shrink_failsFor_outOfBounds():
    with AEI((10, 10)) as aei:
        aei.addTexture(Texture(0, 0, 10, 10))
        
        with pytest.raises(ValueError):
            aei.shape = (9, 10)


def test_setWidth_shrink_failsFor_outOfBounds():
    with AEI((10, 10)) as aei:
        aei.addTexture(Texture(0, 0, 10, 10))
        
        with pytest.raises(ValueError):
            aei.width = 9


def test_setHeight_shrink_failsFor_outOfBounds():
    with AEI((10, 10)) as aei:
        aei.addTexture(Texture(0, 0, 10, 10))
        
        with pytest.raises(ValueError):
            aei.height = 9


def test_getWidth_getsWidth():
    with AEI((10, 5)) as aei:
        assert aei.width == 10


def test_getHeight_getsHeight():
    with AEI((10, 5)) as aei:
        assert aei.height == 5

#endregion dimensions
#region aei files

def test_write_isCorrect():
    with AEI(DECOMPRESSED) as aei, BytesIO() as outBytes, open(PIXEL_AEI_PATH, "rb") as expected:
        aei.write(outBytes, format=CompressionFormat.ATC, quality=3)
        expectedText = expected.read()
        outBytes.seek(0)
        actualText = outBytes.read()
        assert expectedText == actualText


def test_read_readsImage():
    with AEI.read(SMILEY_AEI_PATH) as aei, Image.open(SMILEY_PNG_PATH) as png:
        assert aei.width == png.width
        assert aei.height == png.height

        for x in range(png.width):
            for y in range(png.height):
                assert aei._image.getpixel((x, y)) == png.getpixel((x, y))


def test_read_readsTextures():
    with AEI.read(SMILEY_AEI_PATH) as aei, Image.open(SMILEY_PNG_PATH) as png:
        assert aei.textures[0].x == 0
        assert aei.textures[0].y == 0
        assert aei.textures[0].width == png.width
        assert aei.textures[0].height == png.height


#endregion aei files
#region textures

def test_addTexture_addsTexture():
    with AEI((10, 10)) as aei:
        aei.addTexture(Texture(0, 0, 10, 10))
        assert aei.textures[0].x == 0
        assert aei.textures[0].y == 0
        assert aei.textures[0].width == 10
        assert aei.textures[0].height == 10


def test_addTexture_withImage_addsImage():
    with smileyImage() as png, AEI((16, 16)) as aei:
        aei.addTexture(png, 0, 0)
        for x in range(png.width):
            for y in range(png.height):
                assert aei._image.getpixel((x, y)) == png.getpixel((x, y))


def test_addTexture_conflict_raises():
    with AEI((10, 10)) as aei:
        aei.addTexture(Texture(0, 0, 10, 10))

        with pytest.raises(ValueError):
            aei.addTexture(Texture(0, 0, 10, 10))


def test_addTexture_outOfBounds_raises():
    with AEI((10, 10)) as aei:
        with pytest.raises(ValueError):
            aei.addTexture(Texture(11, 0, 10, 10))


def test_addTexture_withImage_incorrectMode_raises():
    with smileyImage() as png, AEI((16, 16)) as aei:
        with png.convert("L") as converted:
            with pytest.raises(ValueError):
                aei.addTexture(converted, 0, 0)


def test_removeTexture_removesTexture():
    with AEI((10, 10)) as aei:
        aei.addTexture(Texture(0, 0, 10, 10))
        aei.removeTexture(0, 0, 10, 10)
        assert len(aei.textures) == 0


def test_removeTexture_clearImage_clearsImage():
    with Image.new("RGBA", (1, 1), (255, 255, 255, 255)) as png, AEI((1, 1)) as aei:
        aei.addTexture(png, 0, 0)
        aei.removeTexture(0, 0, 1, 1, clearImage=True)
        assert aei._image.getpixel((0, 0)) == (0, 0, 0, 0)


def test_removeTexture_unknown_raises():
    with AEI((10, 10)) as aei:
        with pytest.raises(KeyError):
            aei.removeTexture(0, 0, 10, 10)


def test_removeTexture_outOfBounds_raises():
    with AEI((10, 10)) as aei:
        with pytest.raises(ValueError):
            aei.removeTexture(11, 0, 10, 10)


def test_replaceTexture_replacesTexture():
    with Image.new("RGBA", (1, 1), (100, 100, 100, 100)) as png, Image.new("RGBA", (1, 1), (255, 255, 255, 255)) as newPng, AEI((1, 1)) as aei:
        aei.addTexture(png, 0, 0)
        aei.replaceTexture(newPng, Texture(0, 0, 1, 1))
        assert aei._image.getpixel((0, 0)) == (255, 255, 255, 255)
        

def test_replaceTexture_unknown_raises():
    with Image.new("RGBA", (1, 1)) as png, AEI((10, 10)) as aei:
        with pytest.raises(KeyError):
            aei.replaceTexture(png, Texture(0, 0, 1, 1))


def test_replaceTexture_outOfBounds_raises():
    with Image.new("RGBA", (1, 1)) as png, AEI((10, 10)) as aei:
        with pytest.raises(ValueError):
            aei.replaceTexture(png, Texture(11, 0, 1, 1))


def test_replaceTexture_withImage_incorrectTexture_raises():
    with Image.new("RGBA", (1, 1)) as png, AEI((10, 10)) as aei:
        with pytest.raises(ValueError):
            aei.replaceTexture(png, Texture(10, 0, 2, 2))


def test_replaceTexture_withImage_incorrectMode_raises():
    with Image.new("L", (1, 1)) as png, AEI((10, 10)) as aei:
        aei.addTexture(0, 0, 1, 1)
        with pytest.raises(ValueError):
            aei.replaceTexture(png, Texture(0, 0, 1, 1))


def test_getTexture_getsTexture():
    with Image.new("RGBA", (1, 1), (255, 255, 255, 255)) as png, AEI((16, 16)) as aei:
        aei.addTexture(png, 0, 0)
        actual = aei.getTexture(0, 0, 1, 1)
        assert actual.getpixel((0, 0)) == (255, 255, 255, 255)


def test_getTexture_outOfBounds_raises():
    with AEI((10, 10)) as aei:
        with pytest.raises(ValueError):
            aei.getTexture(Texture(11, 0, 10, 10))

#endregion textures