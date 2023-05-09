import io
from os import PathLike
from types import TracebackType
from typing import TYPE_CHECKING, List, Optional, Tuple, Type, TypeVar, Union, overload
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
    def __init__(self, shape: Optional[Tuple[int, int]] = None, textures: Optional[List[Texture]] = None, format: Optional[CompressionFormat] = None, quality: Optional[CompressionQuality] = None) -> None:
        if shape is None and not textures:
            raise ValueError("shape or at least one texture must be given")

        self._textures = textures or []
        self._shape = imageOps.imageDimensionsForTextures(self.textures) if shape is None else shape
        self.format = format
        self.quality: Optional[CompressionQuality] = quality


    @property
    def shape(self):
        """The dimensions of the AEI, in pixels.

        :return: (width, height)
        :rtype: Tuple[int, int]
        """
        return self._shape
    

    @shape.setter
    def setShape(self, value: Tuple[int, int]):
        widthShrunk = value[0] < self.shape[0]
        heightShrunk = value[1] < self.shape[1]

        if widthShrunk or heightShrunk:
            for tex in self.textures:
                if widthShrunk and tex.x + tex.image.width < value[0] \
                        or heightShrunk and tex.y + tex.image.height < value[1]:
                    raise ValueError(f"Changing shape from ({self.shape[0]}, {self.shape[1]}) to ({value[0]}, {value[1]}) would cause texture ({tex.x}, {tex.y}) to fall out of bounds")
        
        self._shape = value


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
    

    @overload
    def addTexture(self, texture: Texture, /):
        """Add a texture to this AEI, directly by the `Texture` object.

        :param texture: The new texture
        :type texture: Texture
        :raises ValueError: If `image.mode` is not `RGBA`
        :raises ValueError: If `x` is out of bounds of the AEI
        :raises ValueError: If `y` is out of bounds of the AEI
        """

    @overload
    def addTexture(self, image: Image.Image, x: int, y: int, /):
        """Add a texture to this AEI, by its image and coordinates.

        :param image: The new image
        :type image: Image.Image
        :param x: The x-coordinate of the new texture
        :type x: int
        :param y: The y-coordinate of the new texture
        :type y: int
        :raises ValueError: If `image.mode` is not `RGBA`
        :raises ValueError: If `x` is out of bounds of the AEI
        :raises ValueError: If `y` is out of bounds of the AEI
        """

    def addTexture(self, imageOrTexture: Union[Image.Image, Texture], x: Optional[int] = None, y: Optional[int] = None, /):
        if not isinstance(imageOrTexture, Texture):
            if x is None or y is None:
                raise ValueError("both x and y are required to add a texture by its coordinates")
            
            imageOrTexture = Texture(
                imageOrTexture,
                x,
                y
            )

        if imageOrTexture.image.mode != "RGBA":
            raise ValueError(f"image must be mode RGBA, but {imageOrTexture.image.mode} was given")
        
        if imageOrTexture.x < 0 or imageOrTexture.x > self.shape[0] - 1:
            raise ValueError(f"x coordinate {imageOrTexture.x} is out of range of the image (0 - {self.shape[0] - 1})")
        
        if imageOrTexture.y < 0 or imageOrTexture.y > self.shape[1] - 1:
            raise ValueError(f"y coordinate {imageOrTexture.y} is out of range of the image (0 - {self.shape[1] - 1})")
        
        self.textures.append(imageOrTexture)


    @overload
    def removeTexture(self, image: Image.Image, /):
        """Remove a texture from this AEI, by its image.
        The texture is looked up by image object identity; `image` must be the same object in memory to be removed.

        :raises KeyError: If no corresponding texture could be found for the image
        """

    @overload
    def removeTexture(self, texture: Texture, /):
        """Remove a texture from this AEI, directly by the `Texture` object.
        The texture is looked up by image object identity; `texture` must be the same object in memory to be removed.

        :raises KeyError: If `texture` does not belong to the AEI
        """

    @overload
    def removeTexture(self, x: int, y: int, /):
        """Remove a texture from this AEI, by its coordinates.

        :raises KeyError: If no corresponding texture could be found for the coordinates
        """

    def removeTexture(self, val1: Union[Image.Image, Texture, int], y: Optional[int] = None, /):
        if isinstance(val1, Image.Image):
            try:
                tex = next(i for i, t in enumerate(self.textures) if t.image is val1)
            except StopIteration:
                raise KeyError("image does not belong to this AEI")
            
        elif isinstance(val1, Texture):
            try:
                tex = self.textures.index(val1)
            except StopIteration:
                raise KeyError("texture does not belong to this AEI")
            
        elif y is None:
            raise ValueError("both x and y are required to remove a texture by its coordinates")
        
        else:
            try:
                tex = next(i for i, t in enumerate(self.textures) if t.x == val1 and t.y == y)
            except StopIteration:
                raise KeyError(f"no image was found with coordinates ({val1}, {y})")
        
        self.textures.pop(tex)
    

    def _writeHeaderMeta(self, fp: io.BytesIO, format: CompressionFormat):
        fp.write(FILE_TYPE_HEADER)
        fp.write(binaryio.intToBytes(format.value))

        def writeUInt16(*values: int):
            for v in values:
                fp.write(binaryio.uint16(v, ENDIANNESS))

        # AEI dimensions and texture count
        writeUInt16(
            self.shape[0],
            self.shape[1],
            len(self.textures)
        )

        # texture bounding boxes
        for texture in self.textures:
            writeUInt16(
                texture.x,
                texture.y,
                texture.image.width,
                texture.image.height
            )
    

    def _writeImageContent(self, fp: io.BytesIO, format: CompressionFormat, quality: Optional[CompressionQuality]):
        imageCodec = codec.compressorFor(format)

        image = self.build(True)
        compressed = imageCodec.compress(image, format, quality)

        # image length only appears in compressed AEIs
        if format.isCompressed:
            fp.write(binaryio.uint32(len(compressed), ENDIANNESS))

        fp.write(compressed)


    def build(self, bgra: bool) -> Image.Image:
        """Combile all textures into a single image.

        :param bgra: Switch the colour channels from RGBA to BGRA. Defaults to True
        :type bgra: bool
        :return: A new image containing all textures in this AEI
        :rtype: Image.Image
        """
        image = Image.new("RGBA", self.shape)

        for tex in self.textures:
            image.paste(tex.image, (tex.x, tex.y), tex.image)

        if bgra:
            imageOps.switchRGBA_BGRA(image)

        return image


    def _writeSymbols(self, fp: io.BytesIO):
        #TODO: Unimplemented
        ...


    def _writeFooterMeta(self, fp: io.BytesIO, quality: Optional[CompressionQuality]):
        if quality is not None:
            fp.write(binaryio.intToBytes(quality))


    def __enter__(self):
        pass


    def _silentCloseAllTextures(self):
        """Attempt to close all images held in the AEI, swallowing errors.
        """
        for tex in self.textures:
            try:
                tex.image.close()
            except Exception:
                pass


    def __exit__(self, exceptionType: Type[TException], exception: TException, trace: TracebackType):
        self._silentCloseAllTextures()
