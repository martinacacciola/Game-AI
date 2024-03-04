import logging
from random import randint
import numpy as np
from termcolor import colored

from gdpc import Block, Editor
from gdpc import geometry as geo
from gdpc import minecraft_tools as mt
from gdpc import editor_tools as et

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
avg_height = np.mean(heights)

#Initialize the dimensions of the building sampling randomly from a interval
dx = randint(10, 20) # Building width #questa parte può essere commentata
dy = 1 # Building height
dz = randint(10, 20) # Building depth

height_x = heights.shape[0]
height_z = heights.shape[1]

# Find a suitable position for the building
def find_position(dx, dz, heights):
    """
    Find a suitable position for the building
    """
    positions = []
    # Loop over the heightmap coordinates
    for x in range(height_x):
       for z in range(height_z):
            # Initialize the arrays to control consecutive heights along z and x axes
            check_x = []
            check_z = []
            # Check heights in the z direction
            for i in range(dz):
                if z + i < height_z:
                    y = heights[x, z+i]
                    blocks_to_check = ["minecraft:air", "minecraft:water", "minecraft:gold_block",
                                       "minecraft:end_stone", "minecraft:iron_block", "minecraft:glowstone"] # capire
                    # Check if the block below the current position is not in the excluded blocks list
                    if ED.getBlock((x+STARTX, y-1, z+i+STARTZ)).id != blocks_to_check:
                        check_z.append(heights[x, z+i])
            
            # If consecutive heights are found along the z-axis, check heights in the x direction
            if len(check_z) == dz and all(check_z==check_z[0]):
                for j in range(dx):
                    if x+j < height_x:
                        y = heights[x+j, z]
                        if ED.getBlock((x+j+STARTX, y-1, z+STARTZ)).id != ["minecraft:air", "minecraft:water"]:
                            check_z.append(heights[x+j, z])
            
            # If consecutive heights are found along the x-axis, found a suitable position
            if len(check_x) == dz and all(check_x==check_x[0]):
                positions.append((x, z))

                # Adjust coordinates to avoid overlapping with previously checked locations
                if x < height_x - 2 * dx:
                    x += dx
                if z < height_z - 2 * dz:
                    z += dz
            # If no suitable location is found along the z-axis, move to the next z-coordinate
            else:
                if z < height_z - 2 * dz:
                    z += dz

    if len(positions) == 0:
        print("No suitable position found")
    
        # Reduce the dimensions and try again
        if dx > 10 and dz > 10:
            dx -= 2
            dz -= 2
            find_position(dx, dz, heights)

        else:
            return None
        
    # Handle the case when one suitable position is found
    '''
    In each case, return the coordinates and dimensions of the building
    '''
    if len(positions)==1:
        x,z = positions[0]
        return x, z, x+STARTX, z+STARTZ, dx, dy, dz
    
    # Handle the case when multiple suitable positions are found
    if len(positions) > 1:
        # Choose a random position among the suitable ones
        random_position = randint(0, len(positions)-1)
        x, z = positions[random_position]
        return x, z, x+STARTX, z+STARTZ, dx, dy, dz
    


     

            

