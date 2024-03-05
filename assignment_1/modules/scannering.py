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


#Initialize the dimensions of the building sampling randomly from a interval
#dx = randint(10, 20) # Building width #questa parte può essere commentata
#dy = randint(10,15) # Building height
#dz = randint(10, 20) # Building depth

""" def find_position(heights, dx = randint(6, 9), dz = randint(6, 9)):
    positions = []
    height_x = heights.shape[0]
    height_z = heights.shape[1] 

    # Loop over the heightmap coordinates
    for x in range(height_x):
        for z in range(height_z):
            # Initialize the arrays to control consecutive heights along z and x axes
            check_x = []
            check_z = []
            # Check heights in the z direction
            for i in range(dz):
                if z + i < height_z:
                    print("i = {}".format(z+i))
                    print(heights.shape[1])
                    y = heights[x,z + i]
                    excluded_blocks = ["minecraft:air", "minecraft:water", "minecraft:gold_block",
                                       "minecraft:end_stone", "minecraft:iron_block", "minecraft:glowstone"]
                    # Check if the block below the current position is not in the excluded blocks list
                    if ED.getBlock((x + STARTX, y - 1, z + i + STARTZ)).id not in excluded_blocks:
                        check_z.append(heights[x, z + i])
            # If consecutive heights are found along the z-axis, check heights in the x direction
            if len(check_z) == dz and all(check_z == check_z[0]):
                for j in range(dx):
                    if x + j < heights.shape[0]:
                        y = heights[x + j, z]
                        if ED.getBlock((x + STARTX + j, y - 1, z + STARTZ)).id != "minecraft:air" and ED.getBlock((x + STARTX + j, y - 1, z + STARTZ)).id != "minecraft:water":
                            check_x.append(heights[x + j, z])
            # If consecutive heights are found along the x-axis, found a suitable position
                if len(check_x) == (dx) and all(check_x == check_x[0]):
                    print("found location")
                    positions.append((x, z))
                    # Adjust coordinates to avoid overlapping with previously checked locations
                    if x < heights.shape[0] - 2 * dx:
                        x += dx
                    if z < heights.shape[1] - 2 * dz:
                        z += dz
            # If no suitable location is found along the z-axis, move to the next z-coordinate
            else:
                if z < heights.shape[1] - 2 * dz:
                    z += dz



    print("n {} locations".format(len(positions)))

    if len(positions) == 0:
        # Reduce the dimensions and try again
        if dz > 6 and dx > 6:
            dz = dz - 2
            dx =  dx -2
            find_position(heights, dz, dx)
        else:
            return None

    if len(positions) == 1:
        position_found = positions[0]
        x, z = position_found
        return z, x, z + STARTZ, x + STARTX, dx, dz

    # Return a random location from the list of possible house locations
    print("n {} locations2".format(len(positions)))
    if len(positions) == 0:
        return None

    position_found = positions[randint(0, len(positions) - 1)]
    x, z = position_found
    return z, x, z + STARTZ, x + STARTX, dx, dz """

""" def find_position(heights, dx=randint(6,9), dz=randint(6,9)):
    attempts = 0
    max_attempts = 10

    while attempts < max_attempts:
        positions = []
        height_x = heights.shape[0]
        height_z = heights.shape[1]

        # Loop over the heightmap coordinates
        for x in range(height_x):
            for z in range(height_z):
                # Initialize the arrays to control consecutive heights along z and x axes
                check_x = []
                check_z = []
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
                        if x + j < heights.shape[0]:
                            y = heights[x + j, z]
                            if ED.getBlock((x + STARTX + j, y - 1, z + STARTZ)).id != "minecraft:air" and ED.getBlock(
                                    (x + STARTX + j, y - 1, z + STARTZ)).id != "minecraft:water":
                                check_x.append(heights[x + j, z])
                    # If consecutive heights are found along the x-axis, found a suitable position
                    if len(check_x) == dx and all(check_x == check_x[0]):
                        positions.append((z, x, z + STARTZ, x + STARTX, dx, dz))
                        # Adjust coordinates to avoid overlapping with previously checked locations
                        if x < heights.shape[0] - 2 * dx:
                            x += dx
                        if z < heights.shape[1] - 2 * dz:
                            z += dz
                # If no suitable location is found along the z-axis, move to the next z-coordinate
                else:
                    if z < heights.shape[1] - 2 * dz:
                        z += dz

        print(f"Attempt {attempts + 1}: {len(positions)} locations")

        if len(positions) == 0:
            # Reduce the dimensions
            if dx > 6 and dz > 6:
                dx -= 2
                dz -= 2
            else:
                break  # Break the loop if dimensions cannot be reduced further
        elif len(positions) == 1:
            return positions[0]

        attempts += 1

    return None """

def find_position(heights, dx=randint(6, 9), dz=randint(6, 9)):
    positions = []
    height_x, height_z = heights.shape

    for x in range(height_x):
        for z in range(height_z):
            check_x, check_z = [], []

            for i in range(dz):
                if z + i < height_z:
                    y = heights[x, z + i]
                    excluded_blocks = ["minecraft:air", "minecraft:water", "minecraft:gold_block",
                                       "minecraft:end_stone", "minecraft:iron_block", "minecraft:glowstone"]

                    if ED.getBlock((x + STARTX, y - 1, z + i + STARTZ)).id not in excluded_blocks:
                        check_z.append(heights[x, z + i])

            if len(check_z) == dz and all(check_z == check_z[0]):
                for j in range(dx):
                    if x + j < height_x:
                        y = heights[x + j, z]
                        if ED.getBlock((x + STARTX + j, y - 1, z + STARTZ)).id != "minecraft:air" and ED.getBlock(
                                (x + STARTX + j, y - 1, z + STARTZ)).id != "minecraft:water":
                            check_x.append(heights[x + j, z])

                if len(check_x) == dx and all(check_x == check_x[0]):
                    positions.append((x, z, dx, dz))  # Include dx and dz in the tuple

                    if x < height_x - 2 * dx:
                        x += dx
                    if z < height_z - 2 * dz:
                        z += dz

    print("n {} locations".format(len(positions)))

    if len(positions) == 0:
        if dz > 6 and dx > 6:
            dz -= 2
            dx -= 2
            print(f"Recursive call with dz={dz}, dx={dx}")
            return find_position(heights, dz=dz, dx=dx)  # Return the result of the recursive call
        else:
            print("Returning None - dimensions not greater than 6")
            return None

    return positions[randint(0, len(positions) - 1)] # Return a random location from the list








