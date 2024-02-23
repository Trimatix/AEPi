import importlib
import os
from ..exceptions import CodecLoadException

# Discover codecs

for file in os.scandir('.'):
    if file.is_file() and file.name.endswith(".py") and file.name != "__init__.py":
        try:
            importlib.import_module("." + file.name[:-3], "AEPi.codecs")
        except CodecLoadException:
            pass
