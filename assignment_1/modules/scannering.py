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

# Read start and end coordinates of the build area
BUILD_AREA = ED.getBuildArea()
buildRect = BUILD_AREA.toRect()
STARTX, STARTY, STARTZ = BUILD_AREA.begin
LASTX, LASTY, LASTZ = BUILD_AREA.last

# Global variables
WORLDSLICE = ED.loadWorldSlice(buildRect, cache=True)
heights = WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"]


def find_position(heights, dx=randint(6, 9), dz=randint(6, 9)):
    positions = []
    height_x, height_z = heights.shape
    
    # Loop over the heightmap coordinates
    for x in range(height_x):
        for z in range(height_z):
            # Initialize the arrays to control consecutive heights along z and x axes
            check_x, check_z = [], []

            # Check heights in the z direction
            for i in range(dz):
                if z + i < height_z:
                    y = heights[x, z + i]
                    excluded_blocks = ["minecraft:air", "minecraft:water", "minecraft:gold_block",
                                       "minecraft:end_stone", "minecraft:iron_block", "minecraft:glowstone"]
                    # Check if the block below the current position is not in the excluded blocks list
                    if ED.getBlock((x + STARTX, y - 1, z + i + STARTZ)).id not in excluded_blocks:
                        check_z.append(heights[x, z + i])

            # If consecutive heights are found along the z-axis, check heights in the x direction
            if len(check_z) == dz and all(check_z == check_z[0]):
                for j in range(dx):
                    if x + j < height_x:
                        y = heights[x + j, z]
                        if ED.getBlock((x + STARTX + j, y - 1, z + STARTZ)).id != "minecraft:air" and ED.getBlock(
                                (x + STARTX + j, y - 1, z + STARTZ)).id != "minecraft:water":
                            check_x.append(heights[x + j, z])

                # If consecutive heights are found along the x-axis, found a suitable position
                if len(check_x) == dx and all(check_x == check_x[0]):
                    positions.append((x, z, dx, dz))  # Include dx and dz in the tuple
                    
                     # Adjust coordinates to avoid overlapping with previously checked locations
                    if x < height_x - 2 * dx:
                        x += dx
                    if z < height_z - 2 * dz:
                        z += dz
    
    print("There are {} locations".format(len(positions)))

    if len(positions) == 0:
        # Reduce the dimensions and try again
        if dz > 6 and dx > 6:
            dz -= 2
            dx -= 2
            print(f"Recursive call with dz={dz}, dx={dx}")
            return find_position(heights, dz=dz, dx=dx)  # Return the result of the recursive call
        else:
            print("Returning None - dimensions not greater than 6")
            return None

    return positions[randint(0, len(positions) - 1)] # Return a random location from the list of possible ones








