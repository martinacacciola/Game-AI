## Procedural Content Generation for Minecraft

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#packages">Packages</a></li>
      </ul>
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
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About the project
This work presents an approach to Procedural Content Generation (PCG) in the context of Minecraft. Our focus is on the procedural generation of buildings, specifically houses, within a 100x100 block
build area. The generated structures are not only architecturally distinct but also adapt to the terrain and environment of the building area. The algorithm takes into account the randomness and infinite possibilities of the Minecraft world, ensuring that each generated structure is unique and integrates seamlessly into the existing world.

The houses are generated with random dimensions within a given range, and the algorithm adapts these dimensions according to the available space in the selected environment. 
Among the suitable positions identified for the house, one is chosen at random. 
This ensures that the placement of the house is not deterministic and adds an element of variability to the procedural generation process.

Two different architectural styles, modern and medieval, were implemented, and the style is chosen randomly at the time of building. 
The materials used for each part of the house are chosen randomly from a provided list, adding an element of variability to the interior decoration.
The interior of the house is decorated with a few elements, keeping the houses simple and focusing more on adaptability to the terrain and functionality. 
The algorithm also includes a terrain adaptation function that clears the blocks above and below the house, ensuring that the house integrates smoothly into the existing terrain.


<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Packages
The project was developed using GDPC (Generative Design Python Client), a Python framework for use in conjunction with the [GDMC-HTTP](https://github.com/Niels-NTG/gdmc_http_interface) mod for Minecraft Java edition. To understand how the module and its component work, all the necessary information is in this [repository](https://github.com/avdstaaij/gdpc).
To interact with the Minecraft world through the GDMC HTTP interface, we first initialize an Editor. Then, we retrieve the initial and final coordinates of the building area we have manually
set inside the game, to obtain the necessary local information. We import the world slice we are working on, corresponding to a given rectangle in x-z coordinates. It is used for faster block retrieval.
An example of the intial set-up we have used in all files is the following: 
```python
ED = Editor()

# Get the building area set on the game
BUILD_AREA = ED.getBuildArea()
buildRect = BUILD_AREA.toRect()

# Get the coordinates
STARTX, STARTY, STARTZ = BUILD_AREA.begin
LASTX, LASTY, LASTZ = BUILD_AREA.last

# Global variables
WORLDSLICE = ED.loadWorldSlice(buildRect, cache=True)
heights = WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
```


<!-- GETTING STARTED -->
## Getting Started

To get the project running locally, it is necessary to follow the given instructions.

### Prerequisites and Installation
First, you need to install the [GDMC HTTP interface mod (v1.0.0)](https://github.com/Niels-NTG/gdmc_http_interface/releases/tag/v1.0.0). 
To install GDPC:
* npm
  ```sh
  pip install git+https://github.com/avdstaaij/gdpc 
  ```
or alternatively clone the [repository](https://github.com/avdstaaij/gdpc) and run `pip install .`.
The requirement for GDPC is Python 3.7 or above.
You must also install Minecraft 1.19.2 (Java Edition), which requires [Forge](https://files.minecraftforge.net/net/minecraftforge/forge/index_1.19.2.html). The Minecraft environment must be played with the mod installed to use the framework.

### Modules

The folder is composed of four scripts:

1. `scannering.py`: for evaluating the dimensional features of the selected environment and finding the optimal x-z coordinates of the house;
2. `structure.py`: for investigating the y-coordinate and explicitly build the house starting from foundation and finishing with decorations;
3. `get_material.py`: for providing a list of random materials for the different sections of the building, to add variety to the content;
4. `interior.py`: for defining the interior design elements characterizing the two architectural styles implemented.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage
To test the code, open the Minecraft application, press `t` and set a building area, with the command:
`/setbuildarea ~~~ ~100 ~ ~100` 
This is an example, you can provide of course specific coordinates. The important thing is to set up an area of dimensions 100x100.
Then, run on a terminal the command `python3 structure.py`. The runnning script will print out the coordinates at which the house is being built, along with its dimensions and some checks on what is being constructed. It will appear something like this:
```
Foundation built at coordinates: 2149 71 2140
Foundation built successfully!
Walls built successfully!
Roof built successfully!
Windows added successfully!
Windows built successfully!
Door built successfully!
Medieval interior added successfully!
```
Once the run is finished, the house should appear in the Minecraft world at the location found. It can happen that the building area is not suitable for a building even after the necessary adjustments of the dimensions, in that case the terminal will return this message: 
```
No suitable position found. Change the build area.
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


