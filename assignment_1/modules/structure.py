import logging
from random import randint
import numpy as np
from termcolor import colored

from gdpc import Block, Editor
from gdpc import geometry as geo
from gdpc import minecraft_tools as mt
from gdpc import editor_tools as et

from get_material import get_random_material, get_medieval_materials, get_modern_materials
from scannering import find_position

# Setup Python's logging system
logging.basicConfig(format="%(name)s - %(levelname)s - %(message)s")

# Create an Editor object with buffering enabled
ED = Editor(buffering=False)

BUILD_AREA = ED.getBuildArea()
buildRect = BUILD_AREA.toRect()
STARTX, STARTY, STARTZ = BUILD_AREA.begin
LASTX, LASTY, LASTZ = BUILD_AREA.last

# Global variables
WORLDSLICE = ED.loadWorldSlice(buildRect, cache=True)
heights = WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
#avg_height = np.mean(heights) non serve in questo codice


def foundation(x, y, z, dx, dy, dz, materials):
    """
    Create the foundation of the house
    """
    # Take the material from another module (randomly)
    material = get_random_material(materials['foundation'])
    for i in range(0,dx):
        for j in range(0,dz):
            for k in range(1): # 0,dy???
            # Create the foundation
                ED.placeBlock((x+i, y+k, z+j), Block(material))


def walls(x, y, z, dx, dy, dz, materials):
    '''
    Create the walls of the house
    '''
    # Take the material from another module (randomly)
    material = get_random_material(materials['walls'])
    for i in range(0,dx):
        for j in range(0,dz):
            for k in range(1):
                # Create the walls inside the perimeter
                if i == 0 or i == dx-1 or j == 0 or j == dz-1:
                    ED.placeBlock((x+i, y+k, z+j), Block(material))
                # Create air outside the perimeter
                else:
                    ED.placeBlock((x+i, y+k, z+j), Block("air"))

def roof(x, y, z, dx, dy, dz, materials):
    '''
    Create the roof of the house
    '''
    # Take the material from another module (randomly)
    material = get_random_material(materials['roof'])
    for i in range(0,dx):
        for j in range(0,dz):
            for k in range(1):
                # Create the roof
                if i == 0 or i == dx-1 or j == 0 or j == dz-1:
                    ED.placeBlock((x+i, y+k, z+j), Block(material))
                # Create air on the bottom layer of the roof
                elif k == 0:
                    ED.placeBlock((x+i, y+k, z+j), Block("air")) # da rivedere

def windows(x, y, z, dx, dy, dz, num_windows, materials):
    '''
    Create windows in the walls of the house
    '''
    for i in range(0, dx):
        for j in range(0, dz):
            for k in range(0, dy):
                # Check if the current position is on a wall and not on the corners
                if (i == 0 or i == dx - 1 or j == 0 or j == dz - 1) and not (i == 0 and j == 0) and not (
                        i == dx - 1 and j == dz - 1):
                    # Randomly decide whether to place a window
                    if randint(1, 100) <= num_windows * 10:  # Adjust the probability as needed
                        material = get_random_material(materials['windows'])
                        ED.placeBlock((x + i, y + k, z + j), Block(material))


def main():
    # Initialize the dimensions of the building sampling randomly from an interval
    dx = randint(10, 20)  # Building width
    #dy = randint(10, 20)  # Building height
    dy =1
    dz = randint(10, 20)  # Building depth

    # Retrieve the found dimensions of the building
    position = find_position(dx, dz, heights)
    # Check if a suitable position is found
    if position is not None:
        x, z, start_x, start_z, dx, dy, dz = position

        # Choose randomly the building style (medieval or modern)
        building_style = 'medieval' if randint(0, 1) == 0 else 'modern' 

        # Get materials based on the chosen building style
        if building_style == 'medieval':
            materials = get_medieval_materials()
        elif building_style == 'modern':
            materials = get_modern_materials()
        else:
            raise ValueError(f"Invalid building style: {building_style}")
        
        # Choose a random number of windows
        num_windows = randint(0, 5)

        foundation(start_x, STARTY, start_z, dx, dy, dz, materials)
        walls(start_x, STARTY, start_z, dx, dy, dz, materials)
        roof(start_x, STARTY, start_z, dx, dy, dz, materials)
        windows(start_x, STARTY, start_z, dx, dy, dz, num_windows, materials)
        
    else:
        print("No suitable position found.")

# Call the main function if this script is executed
if __name__ == "__main__":
    main()
