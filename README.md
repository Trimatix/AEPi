<h3 align="center">AEPi</h3>
  <p align="center">
    Abyss Engine Image (AEI) conversion for python<br>
    Join <a href='https://discord.gg/Qv8zTur'>The Kaamo Club discord server</a> for Galaxy on Fire fans and modding
  </p>
</div>
<p align="center">
  <a href="https://github.com/Trimatix/AEPi/actions"
    ><img
      src="https://img.shields.io/github/actions/workflow/status/Trimatix/AEPi/testing.yml?branch=main"
      alt="GitHub Actions workflow status"
  /></a>
  <a href="https://github.com/Trimatix/AEPi/projects/1?card_filter_query=label%3Abug"
    ><img
      src="https://img.shields.io/github/issues-search?color=eb4034&label=bug%20reports&query=repo%3ATrimatix%2FAEPi%20is%3Aopen%20label%3Abug"
      alt="GitHub open bug reports"
  /></a>
  <a href="https://github.com/Trimatix/AEPi/actions"
    ><img
      src="https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/Trimatix/8a5430ecc0f87b003367174b1521f3bb/raw/AEPi__heads_main.json"
      alt="Test coverage"
  /></a>
</p>
<p align="center">
  <a href="https://pypi.org/project/AEPi"
    ><img
      src='https://badgen.net/pypi/v/AEPi/'
      alt="Pypi package version"
  /></a>
  <a href="https://pypi.org/project/AEPi"
    ><img
      src="https://img.shields.io/pypi/pyversions/AEPi.svg"
      alt="Minimum supported Python version"
  /></a>
  <a href="https://github.com/Trimatix/AEPi/blob/master/LICENSE"
    ><img
      src="https://img.shields.io/github/license/Trimatix/AEPi.svg"
      alt="License"
</p>
<p align="center">
  <a href="https://sonarcloud.io/dashboard?id=Trimatix_AEPi"
    ><img
      src="https://sonarcloud.io/api/project_badges/measure?project=Trimatix_AEPi&metric=bugs"
      alt="SonarCloud bugs analysis"
  /></a>
  <a href="https://sonarcloud.io/dashboard?id=Trimatix_AEPi"
    ><img
      src="https://sonarcloud.io/api/project_badges/measure?project=Trimatix_AEPi&metric=code_smells"
      alt="SonarCloud code smells analysis"
  /></a>
  <a href="https://sonarcloud.io/dashboard?id=Trimatix_AEPi"
    ><img
      src="https://sonarcloud.io/api/project_badges/measure?project=Trimatix_AEPi&metric=alert_status"
      alt="SonarCloud quality gate status"
  /></a>
</p>



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
    <li>
      <a href="#usage">Usage</a></li>
      <ul>
        <li><a href="#open-an-aei-file-on-disk">Open an .aei file on disk</a></li>
        <li><a href="#create-a-new-aei">Create a new AEI</a></li>
      </ul>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

**Abyss Engine** is an internal-only game engine developed by Deep Silver FishLabs, for the development of the Galaxy on Fire game series.

The engine uses a proprietary file format for grids of images, called Abyss Engine Image (AEI). The image compression is platform dependant, for example Android texture files are compressed with [Ericsson Texture Compression (ETC)](https://github.com/Ericsson/ETCPACK).

The AEI format was analysed by the Russian modding group 'CatLabs', who later created a GUI and command-line tool for conversion between PNG and AEI, named AEIEditor.

This tool was closed-source, and relied on a windows DLL for compression. AEPi is a minimal recreation of the image conversion logic provided by AEIEditor, leaning on open source image codecs:
- [K0lb3/etcpak](https://github.com/K0lb3/etcpak)
- [K0lb3/tex2img](https://github.com/K0lb3/tex2img)

See <a href="#roadmap">the project roadmap</a> for currently supported and upcoming features.


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

##### Reading textures as image segments

`AEI.textures` provides read access to all of the AEI's bounding boxes. The `AEI.getTexture` method returns the relevant segment of the AEI, as a Pillow `Image`.

Using this, you could for example, batch export all of the individual images within an AEI:

```py
for i, tex in enumerate(aei.textures):
  with aei.getTexture(tex) as im:
    im.save(f"batch/export/{i}.png")
```

#### Create a new AEI

```py
from AEPi import AEI, CompressionFormat,
from PIL import Image

image_path = "ship-texture.png"
image2_path = "another-texture.png"

# create a new .aei file
with Image.open(image_path) as image, Image.open(image2_path) as image2:
  # Images are always assumed to be RGBA, not BGRA
  with AEI(image) as new_aei:
    # 'textures' - image bounding boxes
    new_aei.addTexture(image2, 0, 0)
    # The below operation is legal, but would leave unused image content in the AEI!
    new_aei.removeTexture(0, 0, image2.width, image2.height, clearImage=False)
```

#### Write a new AEI file to disk

```py
    with open("path/to/newFile.aei", "wb") as new_file:
      # compression format can be specified at write time, or in the constructor
      aei.write(new_file, format=CompressionFormat.DXT5)
```

<!-- ROADMAP -->
## Roadmap

The AEPi 1.0 release will mark feature parity with AEIEditor, which theoretically reflects all of the capabilities required to manipulate Galaxy on Fire 2 AEIs on all platforms.

For details of the work that needs to be done, see the issues listed under the 1.0 milestone: https://github.com/Trimatix/AEPi/milestones

Other work is needed (e.g documentation, QOL improvements...), but below is an overview of the *features* implementation progress towards AEIEditor parity:

|Feature                    |Read support|Write support |
|---------------------------|:----------:|:------------:|
|Raw image content          |     ✅     |      ✅      |
|Basic metadata             |     ✅     |      ✅      |
|Texture regions            |     ✅     |      ✅      |
|Mipmapping                 |     ❌     |      ❌      |
|Compression quality (l/m/h)|     ❌     |      ❌      |

And compression format support progress:

|Format                 |Read support|Write support |
|-----------------------|:----------:|:------------:|
|Unknown                |     ❌     |      ❌      |
|Uncompressed_UI        |     ❌     |      ❌      |
|Uncompressed_CubeMap_PC|     ❌     |      ❌      |
|Uncompressed_CubeMap   |     ❌     |      ❌      |
|PVRTC12A               |     ❌     |      ❌      |
|PVRTC14A               |     ❌     |      ❌      |
|ATC                    |     ✅     |      ❌      |
|DXT1                   |     ✅     |      ❌      |
|DXT3                   |     ❌     |      ❌      |
|DXT5                   |     ✅     |      ✅      |
|ETC1                   |     ✅     |      ✅      |

Extra feature requests for after the 1.0 release are very welcome.

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
