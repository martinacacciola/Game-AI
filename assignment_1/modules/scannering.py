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

""" # Find a suitable position for the building
def find_position(heights,dx= randint(10, 20), dz= randint(10, 20)):
    
   # Find a suitable position for the building
   
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
                    y = heights[x, z+i]
                    blocks_to_check = ["minecraft:air", "minecraft:water", "minecraft:gold_block",
                                       "minecraft:end_stone", "minecraft:iron_block", "minecraft:glowstone"] # capire
                    # Check if the block below the current position is not in the excluded blocks list
                    if ED.getBlock((x+STARTX, y-1, z+i+STARTZ)).id not in blocks_to_check:
                        check_z.append(heights[x, z+i])
            
            # If consecutive heights are found along the z-axis, check heights in the x direction
            if len(check_z) == dz and all(check_z==check_z[0]):
                for j in range(dx):
                    if x+j < height_x:
                        y = heights[x+j, z]
                        #if ED.getBlock((x+j+STARTX, y-1, z+STARTZ)).id not in ["minecraft:air", "minecraft:water"]:
                        if ED.getBlock((x + STARTX + j, y - 1, z + STARTZ)).id != "minecraft:air" and ED.getBlock((x + STARTX + j, y - 1, z + STARTZ)).id != "minecraft:water":
                            check_x.append(heights[x+j, z])
            
            # If consecutive heights are found along the x-axis, found a suitable position
            if len(check_x) == dz and all(check_x==check_x[0]):
                print("Suitable position found")
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
    print("n {} locations".format(len(positions)))

    if len(positions) == 0:
        print("No suitable position found")
    
        # Reduce the dimensions and try again
        if dx > 10 and dz > 10:
            dx -= 2
            dz -= 2
            return find_position(heights,dx, dz)

        else:
            return None
        
    # Handle the case when one suitable position is found
    '''
    In each case, return the coordinates and dimensions of the building
    '''
    if len(positions)==1:
        x,z = positions[0]
        return x, z, x+STARTX, z+STARTZ, dx, dz
    print("n {} locations2".format(len(positions)))
    
    # Handle the case when multiple suitable positions are found
    # Choose a random position among the suitable ones
    #random_position = randint(0, len(positions)-1)
    x, z = positions[randint(0, len(positions)-1)]
    print("Random position chosen", (x, z))
    return x, z, x+STARTX, z+STARTZ, dx, dz """

def find_position(heights, house_depth = randint(6, 9), house_width = randint(6, 9)):
    house_locations = []

    for x in range(heights.shape[0]):
        for z in range(heights.shape[1]):
            control_z = []
            control_x = []
            for i in range(house_depth):
                if z + i < heights.shape[1]:
                    print("i = {}".format(z+i))
                    print(heights.shape[1])
                    y = heights[x,z + i]
                    excluded_blocks = ["minecraft:air", "minecraft:water", "minecraft:gold_block",
                                       "minecraft:end_stone", "minecraft:iron_block", "minecraft:glowstone"]
                    if ED.getBlock((x + STARTX, y - 1, z + i + STARTZ)).id not in excluded_blocks:
                        control_z.append(heights[x, z + i])
            if len(control_z) == house_depth and all(control_z == control_z[0]):
                for j in range(house_width):
                    if x + j < heights.shape[0]:
                        y = heights[x + j, z]
                        if ED.getBlock((x + STARTX + j, y - 1, z + STARTZ)).id != "minecraft:air" and ED.getBlock((x + STARTX + j, y - 1, z + STARTZ)).id != "minecraft:water":
                            control_x.append(heights[x + j, z])
                if len(control_x ) == (house_width) and all(control_x == control_x[0]):
                    print("found location")
                    house_locations.append((x, z))
                    if x < heights.shape[0] - 2 * house_width:
                        x += house_width
                    if z < heights.shape[1] - 2 * house_depth:
                        z += house_depth
            else:
                if z < heights.shape[1] - 2 * house_depth:
                    z += house_depth



    print("n {} locations".format(len(house_locations)))

    if len(house_locations) == 0:
        print("Impossible to find a location with {} consecutive blocks at the same height and not on the water".format(
            house_depth))
        if house_depth > 6 and house_width > 6:
            house_depth = house_depth - 2
            house_width = house_width - 2
            find_position(heights, house_depth, house_width)
        else:
            return None

    if len(house_locations) == 1:
        chosen_location = house_locations[0]
        x, z = chosen_location
        return z, x, z + STARTZ, x + STARTX, house_width, house_depth

    # Return a random location from the list of possible house locations
    print("n {} locations2".format(len(house_locations)))
    if len(house_locations) == 0:
        return None

    chosen_location = house_locations[randint(0, len(house_locations) - 1)]
    x, z = chosen_location
    return z, x, z + STARTZ, x + STARTX, house_width, house_depth

   



     

            

