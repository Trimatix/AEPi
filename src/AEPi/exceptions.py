from typing import Optional


class CodecLoadException(Exception):
    """Thrown when a codec failed to initialize, and so should be ignored.
    
    :var str codecName: The name of the codec which failed to load
    """
    def __init__(self, codecName: str, *args: object) -> None:
        super().__init__(*args)
        self.codecName = codecName


class DependencyFailedException(CodecLoadException):
    """Thrown when a codec failed to initialize due to a dependency error.

    :var str dependencyName: The name of the dependency which failed
    :var Optional[Exception] inner: The exception which caused the failure, if applicable
    """
    def __init__(self, codecName: str, dependencyName: str, inner: Optional[Exception] = None, *args: object) -> None:
        super().__init__(codecName, *args)
        self.dependencyName = dependencyName
        self.inner = inner


class DependancyMissingException(DependencyFailedException):
    """Thrown when a codec failed to initialize because a dependency is not installed.
    """
    def __init__(self, codecName: str, dependencyName: str, inner: ImportError, *args: object) -> None:
        super().__init__(codecName, dependencyName, None, *args)
        self.inner = inner
