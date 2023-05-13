import importlib

# Discover codecs

codecDependencies = {
    "EtcPakCodec": [
        "etcpak"
    ]
}

for codec, dependencies in codecDependencies.items():
    success = True
    
    for dependency in dependencies:
        try:
            importlib.import_module(dependency)
        except ImportError:
            success = False
            break

    if success:
        importlib.import_module("." + codec, "AEPi.codecs")
