<h3 align="center">AEPi</h3>
  <p align="center">
    Abyss Engine Image (AEI) conversion for python
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
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

The engine uses a proprietary file format for grids of images, called Abyss Engine Image (AEI). The internal image representiation is platform dependant, for example Android texture files are compressed with [Ericsson Texture Compression (ETC)](https://github.com/Ericsson/ETCPACK).
The AEI format was analysed by the Russian modding group 'CatLabs', who later created a GUI and command-line tool for conversion between PNG and AEI, named AEIEditor.

This tool was closed-source, and relied on a windows DLL for compression. AEPi is a minimal recreation of the image conversion logic provided by AEIEditor, leaning on [K0lb3](https://github.com/K0lb3)'s [etcpak](https://github.com/K0lb3/etcpak) for DirectX and Ericsson image compression internally.

AEPi was created for the conversion of ship textures for Galaxy on Fire 2, and so currently, only single-texutre conversions are supported, either for Android (ETC) or PC (DXT5) use.


<!-- GETTING STARTED -->
## Getting Started

AEPi is not currently available as a pypi package. It should instead be used as a submodule in your project, for which no additional setup is needed.


### Prerequisites

* python 3.6+

### Installation

1. Copy AEPi into your code, either by:
    a. If your project is a git repository, I would recommend installing AEPi as a git submodule with: `git submodule add https://github.com/Trimatix/AEPi.git`
    b. If your project is not a git repository, then click the green 'code' dropdown at the top of this page, and select Download Zip. Unzip the file into your project directory.
2. Install dependencies
   ```sh
   cd AEPi && pip install -r requirements.txt
   ```


<!-- USAGE EXAMPLES -->
## Usage

For maximum flexibility, AEPi returns AEIs as BytesIO objects.

```py
import AEPi
from PIL import Image

png_path = "ship-texture.png"
aei_path = "converted.aei"

png = Image.open(png_path)
aei_bytes = AEPi.makeAEI(my_png, AEPi.Platform.Android)
with open(aei_path, "wb") as f:
    f.write(aei_bytes.getbuffer())
```



<!-- ROADMAP -->
## Roadmap

- [ ] Support multiple images for a single AEI
- [ ] Support conversion from AEI to PNG
    - [ ] Support conversion of multi-image AEIs
- [ ] Support direct selection of compression formats
    - [ ] ETC1 and DXT5
    - [ ] None
    - [ ] None, interface
    - [ ] None, CubeMap(PC)
    - [ ] None, CubeMap
    - [ ] DXT1
    - [ ] DXT3
    - [ ] PVRTC1 2bpp
    - [ ] PVRTC1 4bpp
    - [ ] ATC 4bpp
- [ ] Support more platforms
    - [ ] iOS
    - [ ] macOS (does macOS use DXT5?)

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
