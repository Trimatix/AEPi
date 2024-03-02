import io
from typing import Any, BinaryIO
from os import PathLike
from types import TracebackType
from typing import Any, List, Optional, Set, Tuple, Type, TypeVar, Union, cast, overload
from PIL import Image

from ..lib import imageOps
from ..lib.binaryio import uint8, uint16, uint32, readUInt8, readUInt16, readUInt32

from ..constants import CompressionFormat, FILE_TYPE_HEADER, ENDIANNESS, CompressionQuality
from .. import codec
from .texture import Texture
from ..exceptions import UnsupportedAeiFeatureException, AeiReadException, AeiWriteException

TException = TypeVar("TException", bound=Exception)

class AEI:
    """An Abyss Engine Image file.
    Contains a set of textures, each with an image and coordinates.
    Each texture must fall within the bounds of the AEI shape.
    The AEI shape is mutable, through the `shape` property.
    The coordinate origin (0, 0) is the top-left of the AEI.

    An AEI can be constructed either with its dimensions, or with an image.
    If an image is used, the AEI is created with a copy of the image.
    `format` and `quality` can be set in the constructor, or on call of `AEI.write`.

    Use the `addTexture` and `removeTexture` helper methods for texture management.

    To decode an existing AEI file, use `AEI.read`.
    To encode an AEI into a file, use `AEI.write`.

    If the AEI is scoped in a `with` statement, when exiting the `with`,
    the AEI will attempt to close all images, and swallow any errors encountered.
    """
    @overload
    def __init__(self, shape: Tuple[int, int], /, format: Optional[CompressionFormat] = None, quality: Optional[CompressionQuality] = None) -> None: ...
    
    @overload
    def __init__(self, image: Image.Image, /, format: Optional[CompressionFormat] = None, quality: Optional[CompressionQuality] = None) -> None: ...

    def __init__(self, val1: Union[Image.Image, Tuple[int, int]], /, format: Optional[CompressionFormat] = None, quality: Optional[CompressionQuality] = None):
        self._textures: List[Texture] = []
        self._texturesWithoutImages: Set[Texture] = set()
        self.format = format
        self.quality: Optional[CompressionQuality] = quality

        if isinstance(val1, Image.Image):
            self._shape = val1.size
            self._image = val1.copy()
        else:
            self._shape = val1
            self._image = Image.new("RGBA", self._shape)


    @property
    def shape(self):
        """The dimensions of the AEI, in pixels.

        :return: (width, height)
        :rtype: Tuple[int, int]
        """
        return self._shape
    

    @shape.setter
    def shape(self, value: Tuple[int, int]):
        widthShrunk = value[0] < self.shape[0]
        heightShrunk = value[1] < self.shape[1]

        if widthShrunk or heightShrunk:
            for tex in self.textures:
                if widthShrunk and tex.x + tex.width > value[0] \
                        or heightShrunk and tex.y + tex.height > value[1]:
                    raise ValueError(f"Changing shape from ({self.shape[0]}, {self.shape[1]}) to ({value[0]}, {value[1]}) would cause texture ({tex.x}, {tex.y}) to fall out of bounds")
        
        self._shape = value


    @property
    def width(self):
        return self.shape[0]
    

    @width.setter
    def width(self, value: int):
        self.shape = (value, self.height)
    

    @property
    def height(self):
        return self.shape[1]
    

    @height.setter
    def height(self, value: int):
        self.shape = (self.width, value)


    @property
    def textures(self):
        """Do not use this property to manage textures. Instead use `addTexture` and `removeTexture`.
        This is the mutable, internal representation. Altering directly could cause issues.

        :return: The textures within the AEI
        :rtype: List[Texture]
        """
        return self._textures
    

    def _validateBoundingBox(self, val1: Union[Texture, int], y: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None) -> Tuple[int, int, int, int]:
        if isinstance(val1, Texture):
            y = val1.y
            width = val1.width
            height = val1.height
            val1 = val1.x
            
        elif y is None or width is None or height is None:
            raise ValueError("All of x, y, width and height are required")
        
        if val1 < 0 or width < 1 or y < 0 or height < 1 or val1 + width > self.width or y + height > self.height:
            raise ValueError("The bounding box falls out of bounds of the AEI")
        
        return (val1, y, width, height)


    def _findTextureByBox(self, val1: Union[Texture, int], y: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None):
        x, y, width, height = self._validateBoundingBox(val1, y, width, height)
        
        try:
            texture = next(t for t in self.textures if t.x == x and t.y == y and t.width == width and t.height == height)
        except StopIteration:
            return None
        
        return texture


    @overload
    def addTexture(self, texture: Texture, /) -> None:
        """Add only a texture bounding box to this AEI. Use the overload with `Image` as the first parameter to add image content.
        This overload is only really useful for creating overlapping textures.

        :param texture: The new texture
        :type texture: Texture
        :raises ValueError: If the `texture` falls out of bounds of the AEI
        """
    
    @overload
    def addTexture(self, x: int, y: int, width: int, height: int, /) -> None:
        """Add only a texture bounding box to this AEI. Use the overload with `Image` as the first parameter to add image content.
        This overload is only really useful for creating overlapping textures.

        :param int x: The x-coordinate of the texture
        :param int y: The y-coordinate of the texture
        :param int width: The width of the texture
        :param int height: The height of the texture
        :raises ValueError: If the the bounding box falls out of bounds of the AEI
        """

    @overload
    def addTexture(self, image: Image.Image, x: int, y: int, /) -> None:
        """Add a texture with image content to this AEI.
        `image` is not retained, and can be closed after passing to this method without side effects.

        :param image: The new image
        :type image: Image.Image
        :param int x: The x-coordinate of the texture
        :param int y: The y-coordinate of the texture
        :raises ValueError: If `image.mode` is not `RGBA`
        :raises ValueError: If the bounding box falls out of bounds of the AEI
        """

    def addTexture(self, val1: Union[Image.Image, Texture, int], val2: Optional[int] = None, val3: Optional[int] = None, val4: Optional[int] = None, /):
        if isinstance(val1, Texture):
            image = None
            texture = val1
        elif isinstance(val1, int):
            if val2 is None or val3 is None or val4 is None:
                raise ValueError("All of x, y, width and height are required")
            image = None
            texture = Texture(val1, val2, val3, val4)
        elif val2 is None or val3 is None:
            raise ValueError("Both x and y are required")
        else:
            image = val1
            texture = Texture(val2, val3, image.width, image.height) 

        existingTexture = self._findTextureByBox(texture)
        if existingTexture is not None:
            raise ValueError("A texture already exists with the given bounding box")
        
        if image is None:
            self._texturesWithoutImages.add(texture)
        else:
            if texture.width != image.width or texture.height != image.height:
                raise ValueError("image dimensions do not match the texture dimensions")

            if image.mode != "RGBA":
                raise ValueError(f"image must be mode RGBA, but {image.mode} was given")
            
            self._image.paste(image, (texture.x, texture.y), image)
        
        self.textures.append(texture)


    def replaceTexture(self, image: Image.Image, texture: Texture):
        """Replace a texture in this AEI.
        `image` is not retained, and can be closed after passing to this method without side effects.

        :param image: The new image
        :type image: Image.Image
        :param texture: The new texture
        :type texture: Texture
        :raises ValueError: If `image.mode` is not `RGBA`
        :raises ValueError: If the `texture` falls out of bounds of the AEI
        :raises ValueError: If the dimensions in `texture` do not match the dimensions of `image`
        """
        existingTexture = self._findTextureByBox(texture)
        if existingTexture is None:
            raise KeyError(f"no texture was found with coordinates ({texture.x}, {texture.y}) and dimensions ({texture.width}, {texture.height})")
        
        if texture.width != image.width or texture.height != image.height:
            raise ValueError("image dimensions do not match the texture dimensions")

        if image.mode != "RGBA":
            raise ValueError(f"image must be mode RGBA, but {image.mode} was given")
        
        self._image.paste(image, (texture.x, texture.y), image)


    @overload
    def removeTexture(self, texture: Texture, /, *, clearImage: Optional[bool] = None) -> None: ...

    @overload
    def removeTexture(self, x: int, y: int, width: int, height: int, /, *, clearImage: Optional[bool] = None) -> None: ...

    def removeTexture(self, val1: Union[Texture, int], y: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None, /, *, clearImage: Optional[bool] = None):
        """Remove a texture from this AEI, by its bounding box.

        :param Optional[bool] clearImage: clear the area of the image. Default: Clear if an image was provided when the texture was added
        :raises KeyError: If no corresponding texture could be found for the bounding box
        """
        texture = self._findTextureByBox(val1, y, width, height)
        if texture is None:
            raise KeyError(f"no texture was found with coordinates ({val1}, {y}) and dimensions ({width}, {height})")
        
        if clearImage is not None and clearImage or clearImage is None and texture not in self._texturesWithoutImages:
            # Clear the area that the texture occupied
            self._image.paste(
                (0, 0, 0, 0),
                (texture.x, texture.y, texture.x + texture.width, texture.y + texture.height)
            )

        self._textures.remove(texture)
    

    @overload
    def getTexture(self, texture: Texture, /) -> Image.Image: ...

    @overload
    def getTexture(self, x: int, y: int, width: int, height: int, /) -> Image.Image: ...

    def getTexture(self, val1: Union[Texture, int], y: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None, /) -> Image.Image:
        """Get a copy of the image defined by the provided bounding box.

        :returns: a copy of the image defined by the provided bounding box
        :rtype: Image.Image
        :raises KeyError: The provided bounding box falls out of bounds of the AEI
        """
        x, y, width, height = self._validateBoundingBox(val1, y, width, height)
        
        return self._image.crop((x, y, x + width, y + height))


    @classmethod
    def read(cls, fp: Union[str, PathLike[Any], io.BytesIO]) -> "AEI":
        """Read an AEI file from bytes, or a file.
        `fp` can be a path to a file, or an in-memory buffer containing the contents of an encoded AEI file, including metadata.

        :param fp: The AEI itself, or a path to an AEI file on disk
        :type fp: Union[str, PathLike, io.BytesIO]
        :return: A new AEI file object, containing the decoded contents of `fp`
        :rtype: AEI
        """
        if isinstance(fp, io.StringIO):
            raise ValueError("fp must be of binary type, not StringIO")
        
        file: Union[io.BufferedReader, io.BytesIO]

        if tempFp := (not isinstance(fp, io.BytesIO)):
            file = open(fp, "rb")
        elif isinstance(fp, (str, PathLike)):
            file = open(fp, mode="rb")
        else:
            file = fp

        try:
            bFileType = file.read(len(FILE_TYPE_HEADER))
            if bFileType != FILE_TYPE_HEADER:
                raise ValueError(f"Given file is of unknown type '{str(bFileType, encoding='utf-8')}' expected '{str(FILE_TYPE_HEADER, encoding='utf-8')}'")

            formatId = readUInt8(file, ENDIANNESS)
            format, mipmapped = CompressionFormat.fromBinary(formatId)
            if mipmapped:
                raise UnsupportedAeiFeatureException("Mipmapped textures")
            
            imageCodec = codec.decompressorFor(format)

            width = readUInt16(file, ENDIANNESS)
            height = readUInt16(file, ENDIANNESS)
            numTextures = readUInt16(file, ENDIANNESS)

            textures: List[Texture] = []
            for _ in range(numTextures):
                texX = readUInt16(file, ENDIANNESS)
                texY = readUInt16(file, ENDIANNESS)
                texWidth = readUInt16(file, ENDIANNESS)
                texHeight = readUInt16(file, ENDIANNESS)
                textures.append(Texture(texX, texY, texWidth, texHeight))

            if format.isCompressed:
                imageLength = readUInt32(file, ENDIANNESS)
            else:
                imageLength = 4 * width * height

            compressed = file.read(imageLength)

            symbolGroups = readUInt16(file, ENDIANNESS)

            if symbolGroups > 0:
                raise UnsupportedAeiFeatureException("Symbol maps")
            
            bQuality = readUInt8(file, ENDIANNESS, None)
            quality = cast(Optional[CompressionQuality], bQuality) 

            decompressed = imageCodec.decompress(compressed, format, width, height, quality)

        except Exception as ex:
            raise AeiReadException(None, ex) from ex

        finally:
            if tempFp:
                file.close()

        aei = AEI(decompressed, format=format, quality=quality)
        for tex in textures:
            aei.addTexture(tex)

        return aei
    

    def write(self, fp: Optional[BinaryIO] = None, format: Optional[CompressionFormat] = None, quality: Optional[CompressionQuality] = None) -> BinaryIO:
        """Write this AEI to a BytesIO file.

        :param fp: Optional file to write to. If not given, a new one is created. defaults to None
        :type fp: Optional[io.BytesIO], optional
        :param format: Override for the compression format. defaults to the setting on the AEI
        :type format: Optional[CompressionFormat], optional
        :param quality: Override for the compression quality. defaults to the setting on the AEI
        :type quality: Optional[CompressionQuality], optional
        :raises ValueError: If format is omitted and no format is set on the AEI
        :raises ValueError: If the AEI has no textures
        :return: A file containing the AEI, including the compressed image and full metadata
        :rtype: io.BytesIO
        """
        format = format or self.format
        quality = self.quality if quality is None else quality

        if format is None:
            raise ValueError("This AEI has no compression format specified. Set self.format, or specify the format in the self.toFile.format kwarg")

        fp = io.BytesIO() if fp is None else fp

        # AEIs must contain at least one texture
        if tempTexture := (len(self.textures) == 0):
            self.addTexture(Texture(0, 0, self.width, self.height))

        try:
            self._writeHeaderMeta(fp, format)
            self._writeImageContent(fp, format, quality)
            self._writeSymbols(fp)
            self._writeFooterMeta(fp, quality)

        except Exception as ex:
            raise AeiWriteException(None, ex) from ex
        
        finally:
            if tempTexture:
                self.removeTexture(0, 0, self.width, self.height)

        return fp
    
#region write-util
    
    def _writeHeaderMeta(self, fp: BinaryIO, format: CompressionFormat):
        fp.write(FILE_TYPE_HEADER)
        fp.write(uint8(format.value, ENDIANNESS))

        def writeUInt16(*values: int):
            for v in values:
                fp.write(uint16(v, ENDIANNESS))

        # AEI dimensions and texture count
        writeUInt16(
            self.width,
            self.height,
            len(self.textures)
        )

        # texture bounding boxes
        for texture in self.textures:
            writeUInt16(
                texture.x,
                texture.y,
                texture.width,
                texture.height
            )
    

    def _writeImageContent(self, fp: BinaryIO, format: CompressionFormat, quality: Optional[CompressionQuality]):
        imageCodec = codec.compressorFor(format)

        with imageOps.switchRGBA_BGRA(self._image) as swapped:
            compressed = imageCodec.compress(swapped, format, quality)

        # image length only appears in compressed AEIs
        if format.isCompressed:
            fp.write(uint32(len(compressed), ENDIANNESS))

        fp.write(compressed)


    def _writeSymbols(self, fp: BinaryIO):
        #TODO: Unimplemented
        fp.write(uint16(0, ENDIANNESS)) # number of symbol groups
        ...


    def _writeFooterMeta(self, fp: BinaryIO, quality: Optional[CompressionQuality]):
        if quality is not None:
            fp.write(uint8(quality, ENDIANNESS))

#endregion write-util

    def close(self):
        """Close the underlying image.
        """
        self._image.close()


    def __enter__(self):
        """This method is called when entering a `with` statement.
        """
        return self


    def __exit__(self, exceptionType: Type[TException], exception: TException, trace: TracebackType):
        """This method is called when exiting a `with` statement.
        """
        try:
            self.close()
        except:
            pass
