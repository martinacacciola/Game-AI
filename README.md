## Procedural Content Generation for Minecraft

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
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
build area. The generated structures are not only architecturally distinct but also adapt to the terrain and environment of the building area. The algorithm takes into account the randomness and infinite possibilities of the Minecraft world, ensuring
that each generated structure is unique and integrates seamlessly into the existing world.

The development of this project involved creating a procedural generation algorithm that constructs houses within a specified build area in Minecraft. 
The algorithm was designed to generate structures that are not only architecturally distinct but also adapt to the terrain and environment of the build area. 

The houses are generated with random dimensions within a given range, and the algorithm adapts these dimensions according to the available space in the selected environment. 
Among the suitable positions identified for the house, one is chosen at random. 
This ensures that the placement of the house is not deterministic and adds an element of variability to the procedural generation process.

Two different architectural styles, modern and medieval, were implemented, and the style is chosen randomly at the time of building. 
The materials used for each part of the house are chosen randomly from a provided list, adding an element of variability to the interior decoration.

The interior of the house is decorated with a few elements, keeping the houses simple and focusing more on adaptability to the terrain and functionality. 
The algorithm also includes a terrain adaptation function that clears the blocks above and below the house, ensuring that the house integrates smoothly into the existing terrain.


<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

This section should list any major frameworks/libraries used to bootstrap your project. Leave any add-ons/plugins for the acknowledgements section. Here are a few examples.

* [![Next][Next.js]][Next-url]
* [![React][React.js]][React-url]
* [![Vue][Vue.js]][Vue-url]
* [![Angular][Angular.io]][Angular-url]
* [![Svelte][Svelte.dev]][Svelte-url]
* [![Laravel][Laravel.com]][Laravel-url]
* [![Bootstrap][Bootstrap.com]][Bootstrap-url]
* [![JQuery][JQuery.com]][JQuery-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* npm
  ```sh
  npm install npm@latest -g
  ```

### Installation

_Below is an example of how you can instruct your audience on installing and setting up your app. This template doesn't rely on any external dependencies or services._

1. Get a free API Key at [https://example.com](https://example.com)
2. Clone the repo
   ```sh
   git clone https://github.com/your_username_/Project-Name.git
   ```
3. Install NPM packages
   ```sh
   npm install
   ```
4. Enter your API in `config.js`
   ```js
   const API_KEY = 'ENTER YOUR API';
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>


