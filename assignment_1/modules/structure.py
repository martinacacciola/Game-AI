import logging
from random import randint
import numpy as np
from termcolor import colored

from gdpc import Block, Editor
from gdpc import geometry as geo
from gdpc import minecraft_tools as mt
from gdpc import editor_tools as et
from gdpc import vector_tools as vec

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

def initializeHouse():
    dy = randint(10, 15)  # Building height
    dx = randint(10, 20)  # Building width
    dz = randint(10, 20)  # Building depth
    position = find_position(dx, dy, dz, heights)
    
    # Check if a suitable position is found
    if position is not None:
        # Retrieve the found coordinates and dimensions
        x_coord, z_coord, start_x, start_z, dx, dy, dz = position
        
        start_y_choice = heights[x_coord, z_coord]
        if start_y_choice < STARTY:
            print("Reduce the height of the house")
            return None
        
        start_y = start_y_choice
        # Now you can use x_coord, z_coord, start_x, start_z, dx, dy, dz, start_y in this function
        return x_coord, z_coord, start_x, start_z, dx, dy, dz, start_y
    
    else:
        print("No suitable position found.")
        return None


def foundation(x, y, z, dx, dy, dz, materials):
    """
    Create the foundation of the house
    """
    # Take the material from another module (randomly)
    material = get_random_material(materials['foundation'])
    geo.placeCuboid(ED, (x, y, z), (x+dx-1, y, x+dz-1), Block(material))
    geo.placeCuboid(ED, (x, y+1, z), (x+dx-1, y+1, x+dz-1), Block(material))
   #base built false etc ?
    Base_Built = False
    i = 1
    while not Base_Built:
        control = 0
        tot_blocks = 0
        for block in vec.loop2D((x,z), (x + dx, z + dz)):
            tot_blocks += 1
            if ED.getBlock((block[0], y - i, block[1])).id == "minecraft:air" or ED.getBlock((block[0], y - i, block[1])).id == "minecraft:water":
                geo.placeCuboid(ED, (block[0], y - i, block[1]), (block[0], y - i, block[1]), Block(materials['foundation']))
            else:
                control += 1
        if control == tot_blocks:
            Base_Built = True
        i += 1
    

def walls(x, y, z, dx, dy, dz, materials):
    '''
    Create the walls of the house
    '''
    # Take the material from another module (randomly)
    material = get_random_material(materials['walls'])
    for i in range(0,dx):
        for j in range(0,dz):
            for k in range(0,dy):
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
    y_roof = y + dy
    # Create the roof
    geo.placeCuboid(ED, (x, y_roof, z), (x+dx-1, y_roof, z+dz-1), Block(material))
    # Create the air inside the roof
    geo.placeCuboid(ED, (x+1, y+1, z+1), (x+dx-2, y_roof-1, z+dz-2), Block("air"))


def door(x, y, z, dx, dy, dz, materials):
    '''
    Create the door of the house
    '''
    # Take the material from another module (randomly)
    material = get_random_material(materials['door'])
    # Place the door in the center of the front wall
    door_x = x + dx // 2
    door_z = z + dz - 1
    #ED.placeBlock((door_x, y, door_z), Block(material))
    geo.placeCuboid(ED, (door_x, y + 1, door_z), (door_x, y + 2, door_z), Block("air"))  # Remove the door block
    geo.placeCuboid(ED, (door_x, y, door_z + 1), (door_x, y + 2, door_z + 1), Block("air")) # Remove the block in front of the door
    geo.placeCuboid(ED, (door_x, y + 1, door_z), (door_x, y + 1, door_z), Block(material)) # Place the door
    #geo.placeCuboid(ED, (door_x, y, door_z + 1), (door_x, y, door_z + 1), Block("quartz_stairs")) # Stairs in front of the door


def windows(x, y, z, dx, dy, dz, materials, num_windows=2):
    '''
    Create windows on the walls of the house
    '''
    # Take the material from another module (randomly)
    material = get_random_material(materials['window'])
    # Place windows on two opposite walls
    for i in range(num_windows):
        if i % 2 == 0:
            # Place windows on the first wall
            window_x = x + i
            window_z = z
        else:
            # Place windows on the opposite wall
            window_x = x + dx - i - 1
            window_z = z + dz - 1
        
        # Choose a random height for the window
        window_y = y + randint(1, dy - 2)
        
        # Create the window
        ED.placeBlock((window_x, window_y, window_z), Block(material))


def main():
    # Initialize the dimensions of the building sampling randomly from an interval
    dx = randint(10, 20)  # Building width
    dy = randint(10, 15)  # Building height
    dz = randint(10, 20)  # Building depth

    # Retrieve the found dimensions and position of the building
    position = initializeHouse()
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
        windows(start_x, STARTY, start_z, dx, dy, dz, materials, num_windows)
        
    else:
        print("No suitable position found.")

# Call the main function if this script is executed
if __name__ == "__main__":
    main()

