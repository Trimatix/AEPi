import io
from os import PathLike
from typing import TYPE_CHECKING, List, Optional, Union, overload
from PIL import Image

from ..lib import binaryio, imageOps

from ..constants import CompressionFormat, FILE_TYPE_HEADER, ENDIANNESS, CompressionQuality
from .. import codec

if TYPE_CHECKING:
    from .texture import Texture

class AEI:
    def __init__(self, image: Image.Image, isBgra: bool = False, format: Optional[CompressionFormat] = None, quality: Optional[CompressionQuality] = None) -> None:
        self.textures: List[Texture] = []
        self.image = image
        self.format = format
        self.quality: Optional[CompressionQuality] = quality
        self.isBgra = isBgra

    
    @overload
    def getTexture(self, texture: Texture, /) -> Image.Image:
        """Get a texture region from the AEI.

        :param value: The bounding box of the region to get
        :type value: Texture
        :return: A copy of the internal image, restricted to the bounding box
        :rtype: Image
        """
        ...

    @overload
    def getTexture(self, index: int, /) -> Image.Image:
        """Get a texture region from the AEI.

        :param value: The index of the region's bounding box, from `self.textures`
        :type value: int
        :return: A copy of the internal image, restricted to the bounding box
        :rtype: Image
        """
        ...

    def getTexture(self, value: Union[Texture, int], /) -> Image.Image:
        if isinstance(value, int):
            value = self.textures[value]
        
        return self.image.crop((value.x, value.y, value.x + value.width, value.y + value.height))
    

    @classmethod
    def read(cls, fp: Union[str, PathLike, io.BytesIO]) -> "AEI":
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
        # An AEI must contain at least one texture
        if tempTexture := (not self.textures):
            self.textures.append(
                Texture(0, 0, self.image.width, self.image.height)
            )

        format = format or self.format
        quality = self.quality if quality is None else quality

        if format is None:
            raise ValueError("This AEI has no compression format specified. Set self.format, or specify the format in the self.toFile.format kwarg")

        fp = io.BytesIO() if fp is None else fp

        self._writeHeaderMeta(fp, format)
        self._writeImageContent(fp, format, quality)
        self._writeSymbols(fp)
        self._writeFooterMeta(fp, quality)

        if tempTexture:
            self.textures.clear()

        return fp
    

    def _writeHeaderMeta(self, fp: io.BytesIO, format: CompressionFormat):
        fp.write(FILE_TYPE_HEADER)
        fp.write(binaryio.intToBytes(format.value))

        def writeUInt16(*values: int):
            for v in values:
                fp.write(binaryio.uint16(v, ENDIANNESS))

        # AEI dimensions and texture count
        writeUInt16(
            self.image.width,
            self.image.height,
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

        # AEIs must have 4 channels
        if (oldMode := self.image.mode) != "RGBA":
            self.image = self.image.convert("RGBA")

        # AEIs are BGRA, not RGBA, so swap the colour channels before compression, and then back again
        if switchChannels := (not self.isBgra):
            imageOps.switchRGBA_BGRA(self.image)

        compressed = imageCodec.compress(self.image, format, quality)

        if oldMode != "RGBA":
            self.image = self.image.convert(oldMode)
        
        if switchChannels:
            imageOps.switchRGBA_BGRA(self.image)

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
