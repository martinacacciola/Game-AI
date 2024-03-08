import logging
from random import randint
import numpy as np
from termcolor import colored

from gdpc import Block, Editor
from gdpc import geometry as geo
from gdpc import minecraft_tools as mt
from gdpc import editor_tools as et

# Create an Editor object with buffering enabled
ED = Editor(buffering=False)

BUILD_AREA = ED.getBuildArea()
buildRect = BUILD_AREA.toRect()
STARTX, STARTY, STARTZ = BUILD_AREA.begin
LASTX, LASTY, LASTZ = BUILD_AREA.last

# Global variables
WORLDSLICE = ED.loadWorldSlice(buildRect, cache=True)
heights = WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"]

import random

def get_medieval_materials():
    """
    Get materials for a medieval building
    """
    medieval_materials = {
        'foundation': ['minecraft:stone_bricks', 'minecraft:cobblestone', 'minecraft:nether_bricks'],
        'walls': ['minecraft:stone_bricks', 'minecraft:oak_planks', 'minecraft:nether_bricks'],
        'roof': ['minecraft:oak_planks', 'minecraft:stone_bricks', 'minecraft:cobblestone'],
        'windows': ['minecraft:glass_pane', 'minecraft:gray_stained_glass_pane', 'minecraft:brown_stained_glass_pane'],
        'door':['minecraft:jungle_door', 'minecraft:iron_door'],
    }
    return medieval_materials

def get_modern_materials():
    """
    Get materials for a modern building
    """
    modern_materials = {
        'foundation': ['minecraft:white_concrete', 'minecraft:light_gray_concrete', 'minecraft:gray_concrete'],
        'walls': ['minecraft:light_gray_concrete', 'minecraft:white_concrete', 'minecraft:gray_concrete'],
        'roof': ['minecraft:iron_block', 'minecraft:cyan_concrete', 'minecraft:dark_oak_wood'],
        'windows': ['minecraft:glass_pane', 'minecraft:lime_stained_glass_pane','minecraft:blue_stained_glass_pane'],
        'door':['minecraft:birch_door', 'minecraft:warped_door'],
    }
    return modern_materials

def get_random_material(component_materials):
    """
    Get a random material from the list for the given component
    """
    return random.choice(component_materials)
