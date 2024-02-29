import logging
from gdpc import interface as INTF
from gdpc import geometry as GEO
from gdpc import Block, Editor
import numpy as np
import itertools
from tqdm import tqdm
from typing import Tuple, List, Dict

import random
from random import randint
# Setup Python's logging system
logging.basicConfig(format="%(name)s - %(levelname)s - %(message)s")

# Create an Editor object with buffering enabled
editor = Editor(buffering=False)

BUILD_AREA = editor.getBuildArea()
STARTX, STARTY, STARTZ = BUILD_AREA.begin
LASTX, LASTY, LASTZ = BUILD_AREA.last

# Global variables
WORLDSLICE = editor.loadWorldSlice(BUILD_AREA.toRect(), cache=True)
heights = WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"]

# Define block types
glass = Block('glass')
stone = Block('stone')
wood_planks = Block('oak_planks')
door = Block('oak_door')
bed = Block('pink_bed')
bookshelf = Block('bookshelf')
crafting_table = Block('crafting_table')
furnace = Block('furnace')
stairs = Block('oak_stairs')
wool = Block('white_wool')
carpet = Block('white_carpet')
chest = Block('chest')
flower_pot = Block('flower_pot')
oak_slab = Block('oak_slab')
quartz_stairs = Block('quartz_stairs')
lantern = Block('lantern')
chain = Block('chain')
end_rod = Block('end_rod')
enchanting_table = Block('enchanting_table')
quartz_slab = Block('quartz_slab')
oak_trapdoor = Block('oak_trapdoor')
white_banner = Block('white_wall_banner')
smooth_quartz = Block('smooth_quartz')
water = Block('water')
froglight = Block('pearlescent_froglight')
pink_glass = Block('pink_stained_glass')
red_big_coral = Block('fire_coral')
pink_big_coral = Block('brain_coral')
red_small_coral = Block('fire_coral_fan')
blue_big_coral = Block('tube_coral')
stone_brick_slab = Block('stone_brick_slab')
chest = Block('chest')
portal = Block('nether_portal')
fire = Block('fire')
air = Block('air')
obsidian = Block('obsidian')
deepslate_slab = Block('deepslate_tile_slab')
deepslate_bricks = Block('deepslate_bricks')
deepslate_brick_slab = Block('deepslate_brick_slab')
deepslate_brick_stairs = ('deepslate_brick_stairs')
quartz_bricks = Block('quartz_bricks')
air = Block('air')

def terraform_distance(heights: np.ndarray, y: int, origin: Tuple[int,int], size: Tuple[int,int]) -> int:
    """Calculate how many blocks need to be placed and removed to make area falt on level y.

    Args:
        heights (np.ndarray): heightmap
        y (int): desired height of area (
        origin (Tuple[int,int,int,int]): the bottom left corner of the area to flatten in local coordinates x,z
        size (Tuple[int,int,int,int]): the size of the area to flatten in x,z
    """
    assert origin >= (0,0)
    assert origin[0]+size[0] <= heights.shape[0]
    assert origin[1]+size[1] <= heights.shape[1]

    heights_slice = heights[origin[0]:origin[0]+size[0], 
                            origin[1]:origin[1]+size[1]]

    edit_distance = np.sum(np.abs(heights_slice - y))

    assert edit_distance == int(edit_distance)
    return int(edit_distance)

def score_all_possible_buildregions(heights: np.ndarray, square_sidelength=11, min_adjacent_squares=1, max_adjacent_squares=5, buffer=0):
    print("Analyzing world slice for possible build regions")
    max_x, max_z = heights.shape

    sidelengths = range(square_sidelength*min_adjacent_squares + 2*buffer, square_sidelength*max_adjacent_squares+1 + 2*buffer, square_sidelength)
    sizes = itertools.product(sidelengths, repeat=2)
    origins = itertools.product(range(max_x), range(max_z))
    for size, origin in tqdm(list(itertools.product(sizes, origins))):
            
        if origin[0]+size[0] <= heights.shape[0] and origin[1]+size[1] <= heights.shape[1]:
            heights_slice = heights[origin[0]:origin[0]+size[0], 
                                    origin[1]:origin[1]+size[1]]
            
            y_mean = int(np.mean(heights_slice))
            for y in range(y_mean-1, y_mean+2):
                if y == 63:
                    continue  # water level
                distance = terraform_distance(heights, y, origin, size)
                yield origin, size, y, distance

# Define dimensions of the house
random_length = randint(18, 31)

width, depth, height = random_length, random_length, random.choice([5,6,7,8])  # Dimensions for the ground floor
print(width, depth, height)
cellar_height = 4  # Height of the cellar

# Building functions
def build_cellar(x, y, z, width, depth, height):
    """Builds a cellar."""
    GEO.placeCuboid(editor, (x, y - height, z), (x + width - 1, y, z + depth - 1), stone)
    

def build_floor(x, y, z, width, depth, material):
    """Builds a floor."""
    GEO.placeCuboid(editor, (x, y, z), (x + width - 1, y, z + depth - 1), material)


def build_second_floor(x, y, z, width, depth, material):
    """builds a second floor with a gap for the stairs"""
    GEO.placeCuboid(editor, (x, y, z), (x + width -  1, y, z + depth - 1), material)
    """
    for dx in range(width):
        for dz in range(depth):
            if not (7 < dz < 13 and 4 < dx < width - 13):
                editor.placeBlock((x + dx, y, z + dz), material)
    """

def build_walls(x, y, z, width, depth, height, material):
    """Builds walls with windows."""
    # Front and back walls
    for dx in [0, width - 1]:
        for dy in range(height):
            for dz in range(depth):
                if not (2 < dz < depth - 3 and 1 < dy < height - 1):  # Wall area
                    editor.placeBlock((x + dx, y + dy, z + dz), material)
                else:  # Window area
                    editor.placeBlock((x + dx, y + dy, z + dz), glass)
                

    # Side walls
    for dz in [0, depth - 1]:
        for dy in range(height):
            for dx in range(width):
                if not (2 < dx < width - 3 and 1 < dy < height - 1):  # Wall area
                    editor.placeBlock((x + dx, y + dy, z + dz), material)
                else:  # Window area
                    editor.placeBlock((x + dx, y + dy, z + dz), glass)

def build_roof(x, y, z, width, depth, material):
    """Builds a sloping roof."""
    for dy in range(height):
        for dx in range(dy, width - dy):
            for dz in range(dy, depth - dy):
                editor.placeBlock((x + dx, y + height + dy, z + dz), material)
    GEO.placeCuboid(editor, (x + 1, y + 14, z + 1), (x + width - 1, y + 14, z + depth - 1), air)

def build_staircase(x, y, z, height, material):
    """Builds a staircase inside the house."""
    
    for i in range(height + 1):
        editor.placeBlock((x + 5, y + i, z + 7 + i), Block(material, {"facing": "south"}))
        if i < 6: 
            editor.placeBlock((x + 5, y + height, z + 7 + i), air)
    for i in range(height + 1):
        editor.placeBlock((x + 6, y + i, z + 7 + i), Block(material, {"facing": "south"}))
        if i < 6:
            editor.placeBlock((x + 6, y + height, z + 7 + i), air)
    for i in range(height):
        editor.placeBlock((x + 6, y + i, z + 8 + i), Block(material, {"half": "top"}))
    
    for i in range(height):
        editor.placeBlock((x + 5, y + i, z + 8 + i), Block(material, {"half": "top"}))

    #GEO.placeCuboid(editor,(x + 5, y + height, z + 8),(x + 6, y + height, z + depth - 8), air)

def space_emptier(x, y ,z):
    """empty the space inside and outside the house"""
    #1st floor
    GEO.placeCuboid(editor,(x + 1, y, z + 1),(x + width - 2, y + height - 1, z + depth - 2), air)
    #stairs_gap
    
    
    GEO.placeCuboid(editor,(x + 1, y + height + 1, z + 1),(x + width - 2, y + (height*2) , z + depth - 2), air)


def add_interior_features_2_floor(x, y, z):
    
    # Lights 2 floor
    for dy in range(2):
        editor.placeBlock((x + width - 2, y + height*2 - dy ,z + depth - 2), Block(chain,{"axis": "y"}))
    editor.placeBlock((x + width - 2, y + height + 4,z + depth - 2),Block(lantern, {"hanging": "true"}))
    
    for dy in range(2):
        editor.placeBlock((x + 1, y + height*2 - dy ,z + 1), Block(chain,{"axis": "y"}))
    editor.placeBlock((x + 1, y + height + 4,z + 1),Block(lantern, {"hanging": "true"}))
    
    for dy in range(2):
        editor.placeBlock((x + 1, y + height*2 - dy ,z + depth - 2), Block(chain,{"axis": "y"}))
    editor.placeBlock((x + 1, y + height + 4,z + depth - 2),Block(lantern, {"hanging": "true"}))
    
    for dy in range(2):
        editor.placeBlock((x + width - 2, y + height*2 - dy ,z + 1), Block(chain,{"axis": "y"}))
    editor.placeBlock((x + width - 2, y + height + 4,z + 1),Block(lantern, {"hanging": "true"}))

    
    #hanging lamp 2nd floor
    editor.placeBlock((x + 9, y + height*2, z + 9), Block(chain,{"axis": "y"}))
    for dx in range(3):
        for dz in range(3):
            editor.placeBlock((x + 8 + dx, y + height*2 - 1, z + 8 + dz), quartz_slab)    
    editor.placeBlock((x + 9, y + height*2 - 1, z + 9), Block(quartz_slab, {"type": "double"}))
    editor.placeBlock((x + 9, y + height*2 - 2, z + 9), Block(end_rod, {"facing": "down"}))
    for dx in range(3):
        editor.placeBlock((x + 8 + dx, y + height*2 - 1, z + 7), Block(white_banner,{"facing": "north"}))
    for dz in range(3):
        editor.placeBlock((x + 11, y + height*2 - 1, z + 8 + dz), Block(white_banner,{"facing": "east"}))
    for dz in range(3):
        editor.placeBlock((x + 7, y + height*2 - 1, z + 8 + dz), Block(white_banner,{"facing": "west"}))
    for dx in range(3):
        editor.placeBlock((x + 8 + dx, y + height*2 - 1, z + 11), Block(white_banner,{"facing": "south"})) 

    
    random_height= randint(4,5)
    #print(random_height)
    random_length = randint(4, depth - 4)
    #print(random_length)
    random_x_position = randint(13, width - 4)    
    #print(random_x_position)

    # ladder
    GEO.placeCuboid(editor, (x + random_x_position - 3, y + height + 1, z + 3),(x + random_x_position + 1, y + height + 1, z + random_length + 1), deepslate_slab)
    GEO.placeCuboid(editor, (x + random_x_position - 2, y + height + 1, z + 4),(x + random_x_position - 1, y + height + 1, z + random_length), Block(deepslate_slab, {"type": "double"}))
    # portal frame
    GEO.placeCuboid(editor, (x + random_x_position, y + height + 1, z + 4),(x + random_x_position, y + height + random_height + 1, z + random_length), obsidian)
    GEO.placeCuboid(editor, (x + random_x_position, y + height + 2, z + 5),(x + random_x_position, y + height + random_height, z + random_length - 1), air)
    editor.placeBlock((x + random_x_position, y + height + 2, z + 5), fire)
    
    

def add_interior_features(x, y, z):
    """Adds interior features like beds, a kitchen, and bookshelves."""
    
    # Bookshelves
    for i in range(6):
        editor.placeBlock((x + 1, y + height + 1, z + depth - 2 - i), bookshelf)
    
    for i in range(5):
        editor.placeBlock((x + 1, y + height + 2, z + depth - 2 - i), bookshelf)
    
    for i in range(5):
        editor.placeBlock((x + 2 + i, y + height + 1, z + depth - 2), bookshelf)
        
    for i in range(4):
        editor.placeBlock((x + 2 + i, y + height + 2, z + depth - 2), bookshelf)    
    
    #enchanting_table
    editor.placeBlock((x + 3, y + height + 1, z + depth - 4), enchanting_table)    
       
    # Lights 1st floor
    for dy in range(2):
        editor.placeBlock((x + width - 2, y + height - 1 - dy ,z + depth - 2), Block(chain,{"axis": "y"}))
    editor.placeBlock((x + width - 2, y + height - 3,z + depth - 2),Block(lantern, {"hanging": "true"}))
    
    for dy in range(2):
        editor.placeBlock((x + width - 2, y + height - 1 - dy ,z + 6), Block(chain,{"axis": "y"}))
    editor.placeBlock((x + width - 2, y + height - 3,z + 6),Block(lantern, {"hanging": "true"}))
    
    for dy in range(2):
        editor.placeBlock((x + 1, y + height - 1 - dy ,z + 1), Block(chain,{"axis": "y"}))
    editor.placeBlock((x + 1, y + height - 3,z + 1),Block(lantern, {"hanging": "true"}))
    
    for dy in range(2):
        editor.placeBlock((x + 1, y + height - 1 - dy ,z + depth - 2), Block(chain,{"axis": "y"}))
    editor.placeBlock((x + 1, y + height - 3,z + depth - 2),Block(lantern, {"hanging": "true"}))
    
    
    for dy in range(2):
        editor.placeBlock((x + width - 2, y + height - 1 - dy ,z + 1), Block(chain,{"axis": "y"}))
    editor.placeBlock((x + width - 2, y + height - 3,z + 1),Block(lantern, {"hanging": "true"}))
    
    
    
    # Hanging lamp 1st floor
    editor.placeBlock((x + 9, y + height - 1, z + 10), Block(chain,{"axis": "y"}))
    for dx in range(3):
        for dz in range(3):
            editor.placeBlock((x + 8 + dx, y + height - 2, z + 9 + dz), quartz_slab)    
    editor.placeBlock((x + 9, y + height - 2, z + 10), Block(quartz_slab, {"type": "double"}))
    editor.placeBlock((x + 9, y + height - 3, z + 10), Block(end_rod, {"facing": "down"}))
    for dx in range(3):
        editor.placeBlock((x + 8 + dx, y + height - 2, z + 8), Block(white_banner,{"facing": "north"}))
    for dz in range(3):
        editor.placeBlock((x + 11, y + height - 2, z + 9 + dz), Block(white_banner,{"facing": "east"}))
    for dz in range(3):
        editor.placeBlock((x + 7, y + height - 2, z + 9 + dz), Block(white_banner,{"facing": "west"}))
    for dx in range(3):
        editor.placeBlock((x + 8 + dx, y + height - 2, z + 12), Block(white_banner,{"facing": "south"}))    
    
    # Hanging lamp 1st floor
    editor.placeBlock((x + width - 5, y + height - 1, z + 10), Block(chain,{"axis": "y"}))
    for dx in range(3):
        for dz in range(3):
            editor.placeBlock((x + width - 6 + dx, y + height - 2, z + 9 + dz), quartz_slab)    
    editor.placeBlock((x + width - 5, y + height - 2, z + 10), Block(quartz_slab, {"type": "double"}))
    editor.placeBlock((x + width - 5, y + height - 3, z + 10), Block(end_rod, {"facing": "down"}))
    for dx in range(3):
        editor.placeBlock((x + width - 6 + dx, y + height - 2, z + 8), Block(white_banner,{"facing": "north"}))
    for dz in range(3):
        editor.placeBlock((x + width - 3, y + height - 2, z + 9 + dz), Block(white_banner,{"facing": "east"}))
    for dz in range(3):
        editor.placeBlock((x + width - 7, y + height - 2, z + 9 + dz), Block(white_banner,{"facing": "west"}))
    for dx in range(3):
        editor.placeBlock((x + width - 6 + dx, y + height - 2, z + 12), Block(white_banner,{"facing": "south"}))

    
       
        
    # interior pool
    GEO.placeCuboid(editor, (x + 6, y - 4, z + depth - 8), (x + 12, y - 1, z + depth - 2), smooth_quartz)
    GEO.placeCuboid(editor, (x + 7, y - 3, z + depth - 7), (x + 11, y - 1, z + depth - 3), water)
    for dx in range(5):
        for dz in range(5):
            editor.placeBlock((x + 7 + dx, y - 4, z + depth - 7 + dz), pink_glass)
    dx1 = 0
    dx2 = 0
    for i in range(2):
        editor.placeBlock((x + 7 + dx1, y - 4, z + depth - 7), froglight)
        dx1 += 4
    for i in range(2):
        editor.placeBlock((x + 7 + dx2, y - 4, z + depth - 3), froglight)
        dx2 += 4
    editor.placeBlock((x + 7, y - 3, z + depth - 7), red_big_coral)
    editor.placeBlock((x + 10, y - 3, z + depth - 3), red_big_coral)
    editor.placeBlock((x + 8, y - 3, z + depth - 4), red_small_coral)
    for dz in range(2):
        editor.placeBlock((x + 9, y - 3, z + depth - 7 + dz), blue_big_coral)
    for dx in range(2):
        for dz in range(2):
            if not(dx == 0 and dz == 1):
                editor.placeBlock((x + 10 + dx, y - 3, z + depth - 6 + dz), pink_big_coral)    
   


    # Function to create a living room set
def build_living_room(x, y, z):
    # Sofa
    for dz in range(6):
        editor.placeBlock((x + width - 2, y, z + depth - 7 + dz), Block(quartz_stairs,{"facing": "east"}))
   
    for dx in range(4):
        editor.placeBlock((x + width - 3 - dx, y, z + depth - 2), Block(quartz_stairs,{"facing": "south"}))
        
    # Carpet
    for dx in range(4):
        for dz in range(5):
            editor.placeBlock((x + width - 6 + dx, y, z + depth - 7 + dz), carpet)
    
    # Coffee table
    for dx in range(2):
        for dz in range(3):
            editor.placeBlock((x + width - 5 + dx, y, z + depth - 6 + dz), deepslate_brick_slab)
    
def build_bedroom(x, y, z):
    #carpet
    for dx in range(8):
        for dz in range(6):
            editor.placeBlock((x + width - 2 -dx, y, z + 1 + dz), carpet)   
    
    # bed_frame
    for dx in range(3):
        for dz in range(4):
            editor.placeBlock((x + width - 5 + dx, y, z + 2 + dz), quartz_slab) 
    
    # back_bed
    for dz in range(4):
        editor.placeBlock((x + width - 2, y, z + 2 + dz), deepslate_brick_slab)
    
    # shelf
    for dz in range(4):
        editor.placeBlock((x + width - 2, y + 1, z + 2 + dz), Block(deepslate_brick_slab, {"type": "top"}))
    
    # beds
    for dz in range(2):
        editor.placeBlock((x + width - 4, y, z + 3 + dz), Block(bed, {"facing": "east"}))
    
    # chests
    for dz in range(2):
        editor.placeBlock((x + width - 9, y, z + 3 + dz), Block(chest, {"facing":"east"}))
    
    # bedroom veranda    
    for dx in range(3):
        for dy in range(3):
            editor.placeBlock((x + width - 1 - dx, y + 2 + dy, z), glass)
    for dz in range(2):
        for dy in range(3):
            editor.placeBlock((x + width - 1, y + 2 + dy, z + 1 + dz), glass)
    
    
def build_interior_wall(x, y, z, material):
    """Builds low walls for rooms."""
    # bedroom walls
    for dy in range(3):
        editor.placeBlock((x + width - 1, y + 2 + dy, z + 7), smooth_quartz)
        
    for dz in range(7):
        for dy in range (3):
            editor.placeBlock((x + width - 10, y + dy, z + 1 + dz), material)
    
    for dy in range(3):
        editor.placeBlock((x + width - 10, y + 2 + dy, z), smooth_quartz)
        
    for dx in range(8):
        for dy in range (3):
            if not 4 < dx < 7:
                editor.placeBlock((x + width - 2 - dx, y + dy, z + 7), material)

  
def build_entrance(x, y, z, height):
    """Builds a grand entrance with a door."""
    # Entrance Door
    editor.placeBlock((x + 1, y, z), Block(door, {"facing": "south"}))
    #editor.placeBlock((x + 2, y, z), Block(door, {"facing": "south"}, {"hinge": "left"}))



def main():
    # Get the build area
    build_area = INTF.getBuildArea()
    x, y, z = build_area.begin
    print(x, y, z)

    random_materials = [Block('oak_planks'), Block('birch_planks'), Block('white_concrete'), Block('smooth_quartz'), Block('obsidian'), Block('emerald_block'), Block('diamond_block'), Block('gold_block'), Block('red_sandstone'), Block('purpur_block'), Block('pink_concrete'), Block('green_concrete')]

    # Build the cellar
    build_cellar(x, y - 1, z, width, depth, cellar_height)
    
    # Build the ground floor
    build_floor(x, y - 1, z, width, depth, random.choice(random_materials))
    
    # Build the first floor walls
    build_walls(x, y, z, width, depth, height, random.choice(random_materials))
    
    # Build the second floor
    build_second_floor(x, y + height, z, width, depth, random.choice(random_materials))
    
    # Build the second floor walls
    build_walls(x, y + height + 1, z, width, depth, height, random.choice(random_materials))
    
    # Build the roof
    build_roof(x, y + height + 1, z, width, depth, random.choice(random_materials))

    space_emptier(x, y, z)
    
    # Build the staircase
    build_staircase(x, y, z, height, deepslate_brick_stairs)
    
    # Build the interor walls
    build_interior_wall(x, y, z, deepslate_brick_slab)
    
    # Build Bedroom
    build_bedroom(x, y, z)
    
    # Add interior features
    add_interior_features(x, y, z)

    # Build the entrance
    build_entrance(x, y, z, height)
    
    # Placing furniture in the house
    build_living_room(x, y, z)
    
    # Placing 2nd floor features
    add_interior_features_2_floor(x, y, z)


def print_build_region():
    for build_region in score_all_possible_buildregions(heights):
        origin, size, y, distance = build_region
        print(f"Build region: Origin={origin}, Size={size}, Target Height={y}, Distance={distance}")

if __name__ == '__main__':
    main()