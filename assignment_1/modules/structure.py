import logging
from random import randint
import numpy as np
from termcolor import colored

from gdpc import Block, Editor
from gdpc import geometry as geo
from gdpc import minecraft_tools as mt
from gdpc import editor_tools as et
from gdpc import vector_tools as vec

# Modules made ad hoc
from get_material import get_random_material, get_medieval_materials, get_modern_materials
from scannering import find_position
from interior import Interior

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

def initializeHouse():
    global STARTY
    position = find_position(heights)
    
    if position is not None:
        x, z, dx, dz = position
        print('Position:',position)
        start_x, start_z = x + STARTX, z + STARTZ
        print('Coordinates:',start_x, start_z)
        dy = randint(3,7)  # You can set dy to 0 or any other value you need

        # Check if a suitable position is found
        if start_x + dx <= LASTX and start_z + dz <= LASTZ:
            start_y_choice = heights[x, z]
            print('Start_y:',start_y_choice)
            #if start_y_choice < STARTY:
                #print("Reduce the height of the house")
                #return None
            
            # Check if STARTY is greater than the terrain level
            if STARTY > 63: # 63 or start_y_choice
                print("Adjusting STARTY to the terrain level.")
                STARTY = 63
            
            # If the dimensions exceed the build area, reduce them
            while start_x + dx > LASTX or start_z + dz > LASTZ:
                dx = max(2, dx - 1)
                dz = max(2, dz - 1)
                print(f"Reducing dimensions: dx={dx}, dz={dz}")

            start_y = start_y_choice
            print(start_x, start_y, start_z, dx, dy, dz)
            # Now you can use start_x, start_y, start_z, dx, dy, dz in this function
            return x, z, start_x, start_y, start_z, dx, dy, dz

        
        else:
            print("House dimensions exceed build area.")
            return None
    else:
        print("No suitable position found.")
        return None



def foundation(x, y, z, dx, dy, dz, materials):
    """
    Create the foundation of the house
    """
    material = get_random_material(materials['foundation'])
    for i in range(x, x + dx):
        for j in range(z, z + dz):
            # Place the foundation block at the start_y coordinate
            ED.placeBlock((i, y, j), Block(material))
 

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
    material = get_random_material(materials['door'])
    door_x = x + dx // 2
    door_z = z + dz - 1
    # Replace the blocks in front of the door with air
    ED.placeBlock((door_x, y, door_z + 1), Block("air"))
    ED.placeBlock((door_x, y + 1, door_z + 1), Block("air"))
    # Place the door block
    ED.placeBlock((door_x, y + 1, door_z), Block(material))


def windows(x, y, z, dx, dy, dz, materials, num_windows=2):
    '''
    Create windows on the walls of the house
    '''
    # Take the material from another module (randomly)
    material = get_random_material(materials['windows'])
    
    for i in range(num_windows):
        if dy > 2:
            window_y = y + randint(1, dy - 2)
        else:
            window_y = y + 1  # Set a default value if dy is less than 2
        
        if i % 2 == 0:
            # Place windows on the first wall
            window_x = x + i
            window_z = z
        else:
            # Place windows on the opposite wall
            window_x = x + dx - i - 1
            window_z = z + dz - 1
        
        # Create the window
        ED.placeBlock((window_x, window_y, window_z), Block(material))



def generateHouse():
    # Initialize the dimensions of the building sampling randomly from an interval
    #dx = randint(10, 20)  # Building width
    #dy = randint(10, 15)  # Building height
    #dz = randint(10, 20)  # Building depth

    # Retrieve the found dimensions and position of the building
    position = initializeHouse()
    print(position)
    # Check if a suitable position is found
    if position is not None:
        x, z, start_x, start_y, start_z, dx, dy, dz = position
        
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
        num_windows = randint(1, 5)

        foundation(start_x, start_y, start_z, dx, dy, dz, materials)
        print("Foundation built successfully!")

        walls(start_x, start_y, start_z, dx, dy, dz, materials)
        print("Walls built successfully!")

        roof(start_x, start_y, start_z, dx, dy, dz, materials)
        print("Roof built successfully!")

        windows(start_x, start_y, start_z, dx, dy, dz, materials, num_windows)
        print("Windows built successfully!")

        door(start_x, start_y, start_z, dx, dy, dz, materials)
        print("Door built successfully!")
        #door(start_x, start_y, start_z, dx, dy, dz, materials)
    else:
        print("No suitable position found.")

def main():
    try:
        result = generateHouse()
        if result is not None:
            print("House built successfully!")
    except KeyboardInterrupt:
        print("Interrupted.")

# Call the main function if this script is executed
if __name__ == "__main__":
    main()