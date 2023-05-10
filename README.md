<h3 align="center">AEPi</h3>
  <p align="center">
    Abyss Engine Image (AEI) conversion for python<br>
    Join <a href='https://discord.gg/Qv8zTur'>The Kaamo Club discord server</a> for Galaxy on Fire fans and modding
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details open>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

**Abyss Engine** is an internal-only game engine developed by Deep Silver FishLabs, for the development of the Galaxy on Fire game series.

The engine uses a proprietary file format for grids of images, called Abyss Engine Image (AEI). The image compression is platform dependant, for example Android texture files are compressed with [Ericsson Texture Compression (ETC)](https://github.com/Ericsson/ETCPACK).

The AEI format was analysed by the Russian modding group 'CatLabs', who later created a GUI and command-line tool for conversion between PNG and AEI, named AEIEditor.

This tool was closed-source, and relied on a windows DLL for compression. AEPi is a minimal recreation of the image conversion logic provided by AEIEditor, leaning on [K0lb3](https://github.com/K0lb3)'s [etcpak](https://github.com/K0lb3/etcpak) for DirectX and Ericsson image compression internally.

AEPi was created for the conversion of ship textures for Galaxy on Fire 2, and so currently, only compression is supported, either for Android (ETC) or PC (DXT5) use.


<!-- GETTING STARTED -->
## Getting Started
### Prerequisites

* python 3.6+

### Installation

install AEPi from PyPi:
```
python -m pip install aepi
```

<!-- USAGE EXAMPLES -->
### Usage

This library reflects the real representation of an AEI file on disk; though textures are added to and read from an AEI object as individual images, the underlying representation is a single image. This improves encoding/decoding performance, and enables overlapping textures.

For maximum flexibility, AEPi returns AEIs as BytesIO objects.

The recommended best practise is to wrap your AEPi call in a `with` statement, to ensure that all of the AEI's images are cleaned out of memory when it goes out of scope.

#### Open an .aei file on disk

```py
from AEPi import AEI

with AEI.read("path/to/file.aei") as aei:
  print(
    f"The AEI is compressed in {aei.format.name} format, "
    f"with {len(aei.textures)} textures. "
    f"Width: {aei.shape[0]} Height: {aei.shape[0]}"
)
```

#### Create a new AEI

```py
from AEPi import AEI, Texture, CompressionFormat,
from PIL import Image

image_path = "ship-texture.jpg"

# create a new .aei file
with Image.open(image_path) as image:
  # Images are always assumed to be RGBA, not BGRA
  with AEI(textures=[Texture(image, 0, 0)]) as new_aei:
    ...
```

#### Write a new AEI file to disk

```py
    with open("path/to/newFile.aei", "wb") as new_file:
      # compression format can be specified at write time, or in the constructor
      aei.write(new_file, format=CompressionFormat.DXT5)
```

<!-- ROADMAP -->
## Roadmap

The project roadmap is now maintained as milestones: https://github.com/Trimatix/AEPi/milestones

To report a bug or request a feature, please submit an issue to the [open issues](https://github.com/Trimatix/AEPi/issues) page of this repository.


<!-- CONTRIBUTING -->
## Contributing

This project has a huge amount of potential to help the community and extend the lifetime of our beloved game series. Your contributions will make that possible, and so I thank you deeply for your help with this project.

Please star the repository to let me know that my work is appreciated!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
