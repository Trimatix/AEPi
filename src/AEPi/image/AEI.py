import io
from os import PathLike
from types import TracebackType
from typing import TYPE_CHECKING, List, Optional, Set, Tuple, Type, TypeVar, Union, overload
from PIL import Image

from ..lib import binaryio, imageOps

from ..constants import CompressionFormat, FILE_TYPE_HEADER, ENDIANNESS, CompressionQuality
from .. import codec

if TYPE_CHECKING:
    from .texture import Texture

TException = TypeVar("TException", bound=Exception)

class AEI:
    """An Abyss Engine Image file.
    Contains a set of textures, each with an image and coordinates.
    Each texture must fall within the bounds of the AEI shape.
    The AEI shape is mutable.
    `format` and `quality` can be set in the constructor, or on call of `AEI.write`.

    Use the `addTexture` and `removeTexture` helper methods for texture management.

    To decode an existing AEI file, use `AEI.read`.
    To encode an AEI into a file, use `AEI.write`.

    If the AEI is scoped in a `with` statement, when exiting the `with`,
    the AEI will attempt to close all images, and swallow any errors encountered.
    """
    @overload
    def __init__(self, shape: Tuple[int, int], /, format: Optional[CompressionFormat] = None, quality: Optional[CompressionQuality] = None): ...
    
    @overload
    def __init__(self, image: Image.Image, /, format: Optional[CompressionFormat] = None, quality: Optional[CompressionQuality] = None): ...

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
                if widthShrunk and tex.x + tex.width < value[0] \
                        or heightShrunk and tex.y + tex.height < value[1]:
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


    @classmethod
    def read(cls, fp: Union[str, PathLike, io.BytesIO]) -> "AEI":
        """Read an AEI file from bytes, or a file.
        `fp` can be a path to a file, or an in-memory buffer containing the contents of an encoded AEI file, including metadata.

        :param fp: The AEI itself, or a path to an AEI file on disk
        :type fp: Union[str, PathLike, io.BytesIO]
        :return: A new AEI file object, containing the decoded contents of `fp`
        :rtype: AEI
        """
        # if tempFp := (not isinstance(fp, io.BytesIO)):
        #     fp = open(fp, "rb")
        raise NotImplementedError()
        # if tempFp:
        #     fp.close()
    

    def write(self, fp: Optional[io.BytesIO] = None, format: Optional[CompressionFormat] = None, quality: Optional[CompressionQuality] = None) -> io.BytesIO:
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

        self._writeHeaderMeta(fp, format)
        self._writeImageContent(fp, format, quality)
        self._writeSymbols(fp)
        self._writeFooterMeta(fp, quality)

        return fp
    

    def _validateBoundingBox(self, val1: Union[Texture, int], y: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None) -> Tuple[int, int, int, int]:
        if isinstance(val1, Texture):
            y = val1.y
            width = val1.width
            height = val1.height
            val1 = val1.x
            
        elif y is None or width is None or height is None:
            raise ValueError("All of x, y, width and height are required")
        
        if val1 < 0 or width < 1 or y < 0 or height < 1 or val1 + width > self.width - 1 or y + height > self.height - 1:
            raise ValueError("The bounding box falls out of bounds of the AEI")
        
        return (val1, y, width, height)


    def _findTextureByBox(self, val1: Union[Texture, int], y: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None):
        x, y, width, height = self._validateBoundingBox(val1, y, width, height)
        
        try:
            texture = next(t for t in self.textures if t.x == x and t.y == y and t.width == width and t.height == height)
        except StopIteration:
            return None
        
        return texture


    def addTexture(self, image: Optional[Image.Image], texture: Texture):
        """Add a texture to this AEI.
        If an image is provided, it will be added to the underlying image. Otherwise, no change is made.
        This only really useful for creating overlapping textures.
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
    def removeTexture(self, texture: Texture, /, *, clearImage: Optional[bool] = None): ...

    @overload
    def removeTexture(self, x: int, y: int, width: int, height: int, /, *, clearImage: Optional[bool] = None): ...

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


    def _writeHeaderMeta(self, fp: io.BytesIO, format: CompressionFormat):
        fp.write(FILE_TYPE_HEADER)
        fp.write(binaryio.intToBytes(format.value))

        def writeUInt16(*values: int):
            for v in values:
                fp.write(binaryio.uint16(v, ENDIANNESS))

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
    

    def _writeImageContent(self, fp: io.BytesIO, format: CompressionFormat, quality: Optional[CompressionQuality]):
        imageCodec = codec.compressorFor(format)

        imageOps.switchRGBA_BGRA(self._image)

        compressed = imageCodec.compress(self._image, format, quality)

        imageOps.switchRGBA_BGRA(self._image)

        # image length only appears in compressed AEIs
        if format.isCompressed:
            fp.write(binaryio.uint32(len(compressed), ENDIANNESS))

        fp.write(compressed)


    def _writeSymbols(self, fp: io.BytesIO):
        #TODO: Unimplemented
        ...


    def _writeFooterMeta(self, fp: io.BytesIO, quality: Optional[CompressionQuality]):
        if quality is not None:
            fp.write(binaryio.intToBytes(quality))


    def close(self):
        """Close the underlying image.
        """
        self._image.close()


    def __enter__(self):
        """This method is called when entering a `with` statement.
        """
        pass


    def __exit__(self, exceptionType: Type[TException], exception: TException, trace: TracebackType):
        """This method is called when exiting a `with` statement.
        """
        try:
            self.close()
        except:
            pass
