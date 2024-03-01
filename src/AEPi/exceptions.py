from typing import Optional
from . import constants

def _append(base: str, extra: Optional[str]):
    return base + (f" {extra}" if extra else "")


class AEPiException(Exception):
    """Base class for all AEPi exceptions.
    """
    def __init__(self, message: Optional[str] = None, inner: Optional[Exception] = None, *args: object) -> None:
        super().__init__(*args)
        self.message = message
        self.inner = inner


    def __str__(self) -> str:
        items = [str(i) for i in (self.message, self.inner) if i]
        return "\n".join(items) + super().__str__()


class CodecLoadException(AEPiException):
    """Thrown when a codec failed to initialize, and so should be ignored.
    
    :var str codecName: The name of the codec which failed to load
    """
    def __init__(self, codecName: str, message: Optional[str] = None, inner: Optional[Exception] = None, *args: object) -> None:
        super().__init__(_append(f"Codec {codecName} failed to initialize.", message), inner, *args)
        self.codecName = codecName


class DependencyFailedException(CodecLoadException):
    """Thrown when a codec failed to initialize due to a dependency error.

    :var str dependencyName: The name of the dependency which failed
    :var Optional[Exception] inner: The exception which caused the failure, if applicable
    """
    def __init__(self, codecName: str, dependencyName: str, message: Optional[str] = None, inner: Optional[Exception] = None, *args: object) -> None:
        super().__init__(codecName, _append(f"Dependency '{dependencyName}' failed to load.", message), inner, *args)
        self.dependencyName = dependencyName


class DependancyMissingException(DependencyFailedException):
    """Thrown when a codec failed to initialize because a dependency is not installed.
    """
    def __init__(self, codecName: str, dependencyName: str, inner: ImportError, message: Optional[str] = None, *args: object) -> None:
        super().__init__(codecName, dependencyName, _append("The dependency is not installed.", message), inner, *args)


class AeiReadException(AEPiException):
    """Base class for exceptions thrown whilst reading an existing AEI file.
    """
    def __init__(self, message: Optional[str] = None, inner: Optional[Exception] = None, *args: object) -> None:
        super().__init__(_append("The AEI could not be read.", message), inner, *args)


class AeiWriteException(AEPiException):
    """Base class for exceptions thrown whilst writing a new AEI file.
    """
    def __init__(self, message: Optional[str] = None, inner: Optional[Exception] = None, *args: object) -> None:
        super().__init__(_append("The AEI could not be written.", message), inner, *args)


class InvalidCompressionFormatException(AeiReadException):
    """Thrown when an AEI file specified an unsupported compression format.
    """
    def __init__(self, formatId: int, message: Optional[str] = None, inner: Optional[Exception] = None, *args: object) -> None:
        super().__init__(_append(f"The AEI specified an unknown compression format: {formatId}.", message), inner, *args)
        self.compressionFormatId = formatId


class UnsupportedAeiFeatureException(AEPiException):
    """Thrown when an AEI contains a feature that AEPi does not yet support
    """
    def __init__(self, featureName: str, message: Optional[str] = None, inner: Optional[Exception] = None, *args: object) -> None:
        super().__init__(_append(f"This operation requires a feature that AEPi does not yet support: {featureName}", message), inner, *args)


class UnsupportedCompressionFormatException(UnsupportedAeiFeatureException):
    """Thrown when an AEI is compressed in a valid format that AEPi does not yet support
    """
    def __init__(self, format: "constants.CompressionFormat", message: Optional[str] = None, inner: Optional[Exception] = None, *args: object) -> None:
        super().__init__(f"Compression format '{format.name}'", message, inner, *args)
        self.compressionFormat = format
