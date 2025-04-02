from io import BytesIO
import pytest
from PIL.Image import Image
from PIL import Image

from AEPi import AEI, Texture, CompressionFormat
from AEPi.codec import ImageCodecAdaptor, supportsFormats
from AEPi.constants import CompressionFormat

from src.tests.testUtils import mockCodecsContext

SMILEY_AEI_2TEXTURES_PATH = "src/tests/assets/smiley_ATC_twotextures_nomipmap_nosymbols_high.aei"
SMILEY_PNG_PATH = "src/tests/assets/smiley.png"

PIXEL_AEI_PATH = "src/tests/assets/pixel_ATC_nomipmap_nosymbols_high.aei"

DECOMPRESSED = Image.new("RGBA", (1, 1), (100, 200, 200, 255))
# This is the RGBA pixel from DECOMPRESSED, compressed to ATC 4bpp using AEIEditor.
COMPRESSED = b"\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\x58\x66\xFF\xFF\xFF\xFF"
# This is the smiley image compressed to ATC 4bpp, using AEIEditor.
COMPRESSED_SMILEY_ATC = b"\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xF7\x20\xFF\xFF\x00\x55\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xF7\x20\xFF\xFF\x00\x55\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xF7\x20\xFF\xFF\x00\x55\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xF7\x20\xFF\xFF\x00\xD5\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\xFF\xFF\xFF\xFF\xFC\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\xFF\xFF\xFF\xFF\xCF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\xFF\xFF\xFF\xFF\x3F\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xE7\xD0\xFF\xFF\xFF\xFF\xFF\xA8\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\xFF\xFF\xFF\xFF\xFF\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\xFF\xFF\xFF\xFF\xF3\xFC\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xE7\x54\xFF\xFF\x03\xC3\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x87\x25\xFF\xFF\xFF\xFF\x3F\x00"


def smileyImage():
    png = Image.open(SMILEY_PNG_PATH)

    if png.mode != "RGBA":
        return png.convert("RGBA")
    
    return png

g_useSmiley = False

class MockCodec(ImageCodecAdaptor):
    @classmethod
    def compress(cls, im, format, quality): # type: ignore[reportMissingParameterType]
        global g_useSmiley
        if g_useSmiley:
            return COMPRESSED_SMILEY_ATC
        return COMPRESSED
    
    @classmethod
    def decompress(cls, fp, format, width, height, quality): # type: ignore[reportMissingParameterType]
        global g_useSmiley
        if g_useSmiley:
            return smileyImage()
        return DECOMPRESSED


def setupCodecs():
    supportsFormats(both=[CompressionFormat.ATC])(MockCodec)

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
#region read


def test_read_readsImage():
    with mockCodecsContext(setupCodecs), AEI.read(PIXEL_AEI_PATH) as aei:
        assert aei.width == DECOMPRESSED.width
        assert aei.height == DECOMPRESSED.height

        for x in range(DECOMPRESSED.width):
            for y in range(DECOMPRESSED.height):
                assert aei._image.getpixel((x, y)) == DECOMPRESSED.getpixel((x, y)) # type: ignore[reportUnknownMemberType]


def test_read_readsTextures():
    with mockCodecsContext(setupCodecs), AEI.read(PIXEL_AEI_PATH) as aei:
        assert aei.textures[0].x == 0
        assert aei.textures[0].y == 0
        assert aei.textures[0].width == DECOMPRESSED.width
        assert aei.textures[0].height == DECOMPRESSED.height


def test_read_twoTextures_isCorrect():
    global g_useSmiley
    g_useSmiley = True
    with mockCodecsContext(setupCodecs), AEI.read(SMILEY_AEI_2TEXTURES_PATH) as aei:
        assert len(aei.textures) == 2
        assert aei.textures[0].shape == (8, 8)
        assert aei.textures[0].position == (0, 0)
        assert aei.textures[1].shape == (8, 8)
        assert aei.textures[1].position == (8, 8)
    g_useSmiley = False


#endregion read
#region write

def test_write_isCorrect():
    with (
        mockCodecsContext(setupCodecs),
        AEI(DECOMPRESSED) as aei,
        BytesIO() as outBytes,
        open(PIXEL_AEI_PATH, "rb") as expected
    ):
        aei.write(outBytes, format=CompressionFormat.ATC, quality=3)
        expectedText = expected.read()
        outBytes.seek(0)
        actualText = outBytes.read()
        assert expectedText == actualText


def test_write_twoTextures_isCorrect():
    global g_useSmiley
    g_useSmiley = True
    with (
        mockCodecsContext(setupCodecs),
        smileyImage() as png,
        open(SMILEY_AEI_2TEXTURES_PATH, "rb") as expected,
        AEI(png) as aei,
        BytesIO() as outBytes
    ):
        aei.addTexture(0, 0, 8, 8)
        aei.addTexture(8, 8, 8, 8)
        aei.write(outBytes, format=CompressionFormat.ATC, quality=3)
        expectedText = expected.read()
        outBytes.seek(0)
        actualText = outBytes.read()
        assert expectedText == actualText
    g_useSmiley = False

#endregion write
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
                assert aei._image.getpixel((x, y)) == png.getpixel((x, y)) # type: ignore[reportUnknownMemberType]


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
        assert aei._image.getpixel((0, 0)) == (0, 0, 0, 0) # type: ignore[reportUnknownMemberType]


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
        assert aei._image.getpixel((0, 0)) == (255, 255, 255, 255) # type: ignore[reportUnknownMemberType]
        

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
        assert actual.getpixel((0, 0)) == (255, 255, 255, 255) # type: ignore[reportUnknownMemberType]


def test_getTexture_outOfBounds_raises():
    with AEI((10, 10)) as aei:
        with pytest.raises(ValueError):
            aei.getTexture(Texture(11, 0, 10, 10))

#endregion textures