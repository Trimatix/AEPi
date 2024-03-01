import importlib
from ..exceptions import CodecLoadException

# Discover codecs

_CODECS = ["EtcPakCodec", "Tex2ImgCodec"]

for codec in _CODECS:
    try:
        importlib.import_module(f".{codec}", "AEPi.codecs")
    except CodecLoadException:
        pass
