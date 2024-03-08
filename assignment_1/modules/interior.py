import logging
from random import randint
import numpy as np
from termcolor import colored

from gdpc import Block, Editor
from gdpc import geometry as geo
from gdpc import minecraft_tools as mt
from gdpc import editor_tools as et
from gdpc import vector_tools as vec

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

import random

""" class Interior:
    def __init__(self, style):
        self.style = style

    def decorate(self, ED, start_x, start_y, start_z, dx, dy, dz):
        if self.style == 'medieval':
            self.add_medieval_interior(ED, start_x, start_y, start_z, dx, dy, dz)
        elif self.style == 'modern':
            self.add_modern_interior(ED, start_x, start_y, start_z, dx, dy, dz)
        else:
            raise ValueError(f"Invalid interior style: {self.style}")
        
    def add_medieval_interior(self, ED, start_x, start_y, start_z, dx, dy, dz):
    # Example medieval interior elements
        for i in range(1, dx - 1):
            for j in range(1, dz - 1):
                # Add medieval-style furniture or decorations
                if i % 4 == 0 and j % 4 == 0:
                    # Wooden table and chairs
                    ED.placeBlock((start_x + i, start_y + 1, start_z + j), Block("minecraft:oak_planks"))
                    ED.placeBlock((start_x + i, start_y + 1, start_z + j + 1), Block("minecraft:oak_stairs"))
                elif i % 5 == 0 and j % 5 == 0:
                    # Bookshelf placed on the pavement
                    ED.placeBlock((start_x + i, start_y, start_z + j), Block("minecraft:oak_planks"))
                    ED.placeBlock((start_x + i, start_y + 1, start_z + j), Block("minecraft:bookshelf"))
                elif i % 6 == 0 and j % 6 == 0:
                    # Randomly choose the size of the carpet
                    carpet_width = randint(2, min(dx - i, 5))
                    carpet_depth = randint(2, min(dz - j, 5))
                    # Place the carpet inside the house
                    for k in range(carpet_width):
                        for l in range(carpet_depth):
                            ED.placeBlock((start_x + i + k, start_y, start_z + j + l), Block("minecraft:red_carpet"))
                elif i % 7 == 0 and j % 7 == 0:
                    # Medieval-style lamp (attach to the roof)
                    ED.placeBlock((start_x + i, start_y + dy - 1, start_z + j), Block("minecraft:lantern"))

        print("Medieval interior added successfully!")

    def add_modern_interior(self, ED, start_x, start_y, start_z, dx, dy, dz):
        # Example modern interior elements
        for i in range(1, dx - 1):
            for j in range(1, dz - 1):
                # Add modern-style furniture or decorations
                if i % 3 == 0 and j % 3 == 0:
                    # White concrete block as a table base
                    ED.placeBlock((start_x + i, start_y + 1, start_z + j), Block("minecraft:white_concrete"))
                    # Pressure plate on top to represent the table surface
                    ED.placeBlock((start_x + i, start_y + 2, start_z + j), Block("minecraft:stone_pressure_plate"))
                elif i % 4 == 0 and j % 4 == 0:
                    # Sofa made of white concrete blocks
                    ED.placeBlock((start_x + i, start_y, start_z + j), Block("minecraft:white_concrete"))
                    ED.placeBlock((start_x + i, start_y + 1, start_z + j), Block("minecraft:white_concrete"))
                    # Add a sign on the sides of the sofa to represent armrests
                    ED.placeBlock((start_x + i + 1, start_y, start_z + j), Block("minecraft:oak_sign"))
                    ED.placeBlock((start_x + i - 1, start_y, start_z + j), Block("minecraft:oak_sign"))
                elif i % 5 == 0 and j % 5 == 0:
                    # Modern art on the wall
                    ED.placeBlock((start_x + i, start_y + dy - 1, start_z + j), Block("minecraft:painting"))
                elif i % 6 == 0 and j % 6 == 0:
                    # Randomly choose the size of the carpet
                    carpet_width = randint(2, min(dx - i, 5))
                    carpet_depth = randint(2, min(dz - j, 5))
                    # Place the carpet inside the house
                    for k in range(carpet_width):
                        for l in range(carpet_depth):
                            ED.placeBlock((start_x + i + k, start_y, start_z + j + l), Block("minecraft:red_carpet"))
                elif i % 7 == 0 and j % 7 == 0:
                    # Modern lamp (attach to the roof)
                    ED.placeBlock((start_x + i, start_y + dy - 1, start_z + j), Block("minecraft:sea_lantern"))

        print("Modern interior added successfully!") """


import logging
from random import randint


class Interior:
    def __init__(self, style):
        self.style = style

    def decorate(self, ED, start_x, start_y, start_z, dx, dy, dz):
        if self.style == 'medieval':
            self.add_medieval_interior(ED, start_x, start_y, start_z, dx, dy, dz)
        elif self.style == 'modern':
            self.add_modern_interior(ED, start_x, start_y, start_z, dx, dy, dz)
        else:
            raise ValueError(f"Invalid interior style: {self.style}")

    def add_medieval_interior(self, ED, start_x, start_y, start_z, dx, dy, dz):
        # Place a wooden table and chairs at the center
        center_x, center_z = start_x + dx // 2, start_z + dz // 2
        ED.placeBlock((center_x, start_y, center_z), Block("minecraft:oak_planks"))
        ED.placeBlock((center_x, start_y, center_z + 1), Block("minecraft:oak_stairs"))

        # Place bookshelves along one wall
        for i in range(start_x + 1, start_x + dx - 1):
            ED.placeBlock((i, start_y + 1, start_z + 1), Block("minecraft:bookshelf"))

        # Place a rug in front of the table
        for i in range(center_x - 1, center_x + 2):
            for j in range(center_z - 1, center_z + 2):
                ED.placeBlock((i, start_y, j), Block("minecraft:red_carpet"))

        # Place a lantern at the center of the ceiling
        ED.placeBlock((center_x, start_y + dy -2, center_z), Block("minecraft:lantern"))

        print("Medieval interior added successfully!")

def add_modern_interior(self, ED, start_x, start_y, start_z, dx, dy, dz):
    # Place a bed along one wall, taking up half the width
    for i in range(start_x + 1, start_x + dx // 2):
        ED.placeBlock((i, start_y, start_z + 1), Block("minecraft:white_bed"))

    # Place a desk at the center instead of a table
    center_x, center_z = start_x + dx // 2, start_z + dz // 2
    ED.placeBlock((center_x, start_y + 1, center_z), Block("minecraft:oak_planks"))
    ED.placeBlock((center_x, start_y + 2, center_z), Block("minecraft:book"))

    # Clear the block in front of the door with air
    ED.placeBlock((start_x + dx // 2, start_y, start_z), Block("minecraft:air"))

    # Place bookshelves along the opposite wall
    for i in range(start_x + 1, start_x + dx - 1):
        ED.placeBlock((i, start_y + 1, start_z + dz - 2), Block("minecraft:bookshelf"))

    # Place a modern lamp at the center of the ceiling
    ED.placeBlock((center_x, start_y + dy - 1, center_z), Block("minecraft:sea_lantern"))

    print("Modern interior added successfully!")









