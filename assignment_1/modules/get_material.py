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
        'windows': ['minecraft:glass_pane', 'minecraft:iron_bars'],
        'door':['minecraft:wooden_door', 'minecraft:iron_door'],
    }
    return medieval_materials

def get_modern_materials():
    """
    Get materials for a modern building
    """
    modern_materials = {
        'foundation': ['minecraft:white_concrete', 'minecraft:iron_block', 'minecraft:stone'],
        'walls': ['minecraft:glass_pane', 'minecraft:white_concrete', 'minecraft:iron_block'],
        'roof': ['minecraft:iron_block', 'minecraft:cyan_concrete', 'minecraft:glass_pane'],
        'windows': ['minecraft:glass_pane', 'minecraft:iron_bars'],
        'door':['birch_door', 'cherry_door'],
    }
    return modern_materials

def get_random_material(component_materials):
    """
    Get a random material from the list for the given component
    """
    return random.choice(component_materials)
