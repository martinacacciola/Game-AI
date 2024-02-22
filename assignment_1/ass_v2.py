import logging
import random as rnd
import numpy as np
from scipy import spatial as spt
from termcolor import colored
from gdpc import Block, Editor
from gdpc import geometry as geo
from gdpc import minecraft_tools as mt
from gdpc import editor_tools as et

logging.basicConfig(format=colored("%(name)s - %(levelname)s - %(message)s", color="yellow"))

# Global variables
ED = Editor(buffering=False)

def determineBuildArea():
    # Specify the range for determining the build area
    build_area_range = geo.Rect((0, 0), (100, 100))

    # Get the heightmap data for the specified range
    world_slice = ED.loadWorldSlice(build_area_range, cache=True)
    heights = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]

    # Extract the coordinates of terrain points within the specified range
    terrain_points = [(x, heights[x, z], z) for x in range(max(0, build_area_range.begin[0]), min(heights.shape[0] - 1, build_area_range.end[0] + 1))
                      for z in range(max(0, build_area_range.begin[1]), min(heights.shape[1] - 1, build_area_range.end[1] + 1))
                      if np.isin((x, z), heights).all()]

    # Calculate the convex hull of terrain points
    if terrain_points:
        terrain_points_2d = [(x, z) for x, _, z in terrain_points]
        convex_hull_indices = spt.ConvexHull(terrain_points_2d).vertices
        convex_hull_points = [terrain_points[i] for i in convex_hull_indices]
    else:
        # If no terrain points are found, use a default build area
        convex_hull_points = [(build_area_range.begin[0], 0, build_area_range.begin[1]),
                              (build_area_range.end[0], 0, build_area_range.begin[1]),
                              (build_area_range.end[0], 0, build_area_range.end[1]),
                              (build_area_range.begin[0], 0, build_area_range.end[1])]

    # Create a build area that covers the convex hull of terrain points
    min_x = min(x for x, _, _ in convex_hull_points)
    max_x = max(x for x, _, _ in convex_hull_points)
    min_z = min(z for _, _, z in convex_hull_points)
    max_z = max(z for _, _, z in convex_hull_points)

    build_area = geo.Rect((min_x, min_z), (max_x - min_x + 1, max_z - min_z + 1))

    return build_area

def adaptToTerrain(build_area):
    # Get the heightmap data for the build area
    world_slice = ED.loadWorldSlice(build_area, cache=True)
    heights = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]

    # Calculate the average ground level within the build area
    total_height = 0
    total_points = 0

    for x in range(build_area.begin[0], build_area.end[0]):
        for z in range(build_area.begin[1], build_area.end[1]):
            if np.isin((x, z), heights).all():
                total_height += heights[(x, z)]
                total_points += 1

    if total_points > 0:
        average_ground_level = total_height / total_points
    else:
        # No valid height data found, use a default value
        average_ground_level = 0

    # Adjust the building based on the calculated average_ground_level

    # Example: Lower the building by 5 blocks if the average ground level is higher than 10
    if average_ground_level > 10:
        ED.placeCuboid((0, -5, 0), build_area.size)

    # Example: Add a foundation if the average ground level is lower than 5
    elif average_ground_level < 5:
        foundation_height = 5  # Adjust as needed
        geo.placeCuboid(ED, (build_area.begin[0], build_area.begin[1], 0),
                        (build_area.end[0], build_area.begin[1] + foundation_height, build_area.end[1]),
                        Block("stone"))

    # Example: Flatten the terrain if it has significant variations
    flatten_threshold = 8  # Adjust as needed
    if np.max(heights) - np.min(heights) > flatten_threshold:
        # Flatten the terrain to make it more even
        target_height = int(average_ground_level)
        for x in range(build_area.begin[0], build_area.end[0]):
            for z in range(build_area.begin[1], build_area.end[1]):
                if np.isin((x, z), heights).all():
                    current_height = heights[(x, z)]
                    height_difference = target_height - current_height
                    ED.move((x, build_area.begin[2], z), (0, height_difference, 0))

    # You can add more sophisticated logic based on your specific requirements

    adaptation_result = {
        'average_ground_level': average_ground_level,
        'actions_taken': []  # You can add details about the actions taken
    }

    # Example: Lower the building by 5 blocks if the average ground level is higher than 10
    if average_ground_level > 10:
        ED.placeCuboid((0, -5, 0), build_area.size)
        adaptation_result['actions_taken'].append('Lowered the building by 5 blocks.')

    # Example: Add a foundation if the average ground level is lower than 5
    elif average_ground_level < 5:
        foundation_height = 5  # Adjust as needed
        geo.placeCuboid(ED, (build_area.begin[0], build_area.begin[1], 0),
                        (build_area.end[0], build_area.begin[1] + foundation_height, build_area.end[1]),
                        Block("stone"))
        adaptation_result['actions_taken'].append('Added a foundation.')

    # Example: Flatten the terrain if it has significant variations
    flatten_threshold = 8  # Adjust as needed
    if np.max(heights) - np.min(heights) > flatten_threshold:
        # Flatten the terrain to make it more even
        target_height = int(average_ground_level)
        for x in range(build_area.begin[0], build_area.end[0]):
            for z in range(build_area.begin[1], build_area.end[1]):
                if np.isin((x, z), heights).all():
                    current_height = heights[(x, z)]
                    height_difference = target_height - current_height
                    ED.move((x, build_area.begin[2], z), (0, height_difference, 0))
        adaptation_result['actions_taken'].append('Flattened the terrain.')

    # You can add more sophisticated logic based on your specific requirements

    return adaptation_result


def generateBuilding(build_area):
    # Determine ground level and adapt to terrain
    adaptation_result = adaptToTerrain(build_area)
    average_ground_level = adaptation_result['average_ground_level']
    actions_taken = adaptation_result['actions_taken']

    # Use the information from adaptation_result as needed
    print(f"Average Ground Level: {average_ground_level}")
    print("Actions Taken:")
    for action in actions_taken:
        print(f"- {action}")

    # Randomly choose an architectural style
    architectural_style = rnd.choice(["modern", "medieval"])

    # Generate building components based on the chosen style
    if architectural_style == "modern":
        generateModernBuilding(build_area)
    elif architectural_style == "medieval":
        generateMedievalBuilding(build_area)

    # Add interior decoration
    addInteriorDecoration(build_area, architectural_style)


def generateModernBuilding(build_area):
    # Example: Generate a more detailed modern-style building
    # Here you can use the provided functions like signBlock, lecternBlock, etc.

    # Place a modern sign welcoming visitors
    sign_block = mt.signBlock(wood="oak", facing="north", line1="Modern Building", line2="Welcome!")
    ED.placeBlock((50, 5, 50), sign_block)

    # Create a modern-style guidebook on a lectern
    lectern_block = mt.lecternBlock(facing="south", bookData=mt.bookData("Modern Building Guide"))
    ED.placeBlock((50, 6, 50), lectern_block)

    # Create a glass-pane facade for the building
    glass_pane_block = Block("minecraft:glass_pane", data='{"east": "true", "west": "true", "north": "true", "south": "true"}')
    geo.placeCuboid(ED, (build_area.begin[0] + 1, build_area.begin[1], 0),  # Assuming the height is set to 0
                    (build_area.end[0] - 1, build_area.begin[1] + 5, build_area.end[1] - 1),
                    glass_pane_block)

    # Place a modern door
    door_block = Block("minecraft:wooden_door", data='{"facing": "north", "half": "lower", "hinge": "left"}')
    ED.placeBlock((50, 1, 0), door_block)  # Assuming the height is set to 0

    # Place modern-style windows
    window_block = Block("minecraft:glass_pane", data='{"east": "true", "west": "true", "north": "false", "south": "false"}')
    for x in range(build_area.begin[0] + 1, build_area.end[0], 10):
        for z in range(build_area.begin[1] + 1, build_area.end[1], 10):
            geo.placeCuboid(ED, (x, build_area.begin[1] + 1, build_area.begin[0] + 1),
                            (x + 2, build_area.begin[1] + 4, build_area.begin[0] + 3),
                            window_block)


def generateMedievalBuilding(build_area):
    # Example: Generate a medieval-style building

    # Place a castle wall around the build area
    castle_wall = mt.signBlock(wood="stone_brick", wall=True, line1="Castle Wall")
    castle_wall_block = Block("stone_brick")
    geo.placeCuboid(ED, (build_area.begin[0], build_area.begin[1], 0),  # Assuming the height is set to 0
                    (build_area.end[0], build_area.begin[1] + 5, build_area.end[1]),
                    castle_wall_block)

    # Place towers at each corner of the build area
    tower_material = "cobblestone"
    tower_height = 10
    # Assuming tower_material is a valid block type
    for corner in [(build_area.begin[0], 0, build_area.begin[1]), (build_area.end[0], 0, build_area.begin[1]),
                   (build_area.end[0], 0, build_area.end[1]), (build_area.begin[0], 0, build_area.end[1])]:
        tower = mt.signBlock(wood=tower_material, wall=True, line1="Castle Tower")
        geo.placeCuboid(ED, (corner[0], build_area.begin[1], corner[2]),
                        (corner[0], build_area.begin[1] + tower_height, corner[2]), tower)

    # Place wooden structures inside the castle walls
    wooden_structure_material = "oak"
    structure_height = 8
    wooden_block = Block(wooden_structure_material)
    geo.placeCuboid((build_area.begin[0] + 3, build_area.begin[1], build_area.begin[1] + 3),
                    (build_area.end[0] - 3, build_area.begin[1] + structure_height, build_area.end[1] - 3),
                    wooden_block)

    # Add a lectern with a book describing the medieval building
    lectern_block = mt.lecternBlock(facing="south", bookData=mt.bookData("Medieval Castle Guide"))
    ED.placeBlock((build_area.centerx, build_area.begin[1] + 1, build_area.centerz), lectern_block)


def addInteriorDecoration(build_area, architectural_style):
    # Example: Add interior decoration with randomness

    # Define a list of possible interior decoration elements
    decoration_elements = []

    if architectural_style == "medieval":
        decoration_elements.extend([
            ("table", "wooden", (1, 1, 1)),
            ("chair", "oak", (0.5, 0.5, 1)),
            ("candle", "white", (0.2, 1, 0.2)),
        ])

    elif architectural_style == "modern":
        decoration_elements.extend([
            ("desk", "modern", (2, 1, 1)),
            ("computer", "silver", (1, 1, 1)),
            ("lamp", "modern", (0.5, 0.5, 2)),
        ])

    # Randomly choose the number of decoration elements to place
    num_elements = rnd.randint(3, 8)  # Adjust the range as needed

    for _ in range(num_elements):
        # Randomly choose a decoration element from the list
        element_type, material, size = rnd.choice(decoration_elements)

        # Randomly choose a position within the build area
        position = (rnd.randint(build_area.begin[0] + 2, build_area.end[0] - 2), build_area.begin[1] + 1,
                    rnd.randint(build_area.begin[1] + 2, build_area.end[1] - 2)
                    )

        # Place the chosen decoration element
        if element_type == "table":
            table_block = mt.lecternBlock(facing="south", bookData=mt.bookData("Table"))
            ED.placeBlock(position, table_block)
        elif element_type == "chair":
            chair_block = mt.signBlock(wood=material, facing="north", line1="Chair")
            ED.placeBlock(position, chair_block)
        elif element_type == "candle":
            candle_block = mt.signBlock(wood="nether_brick", facing="up", line1="Candle")
            ED.placeBlock(position, candle_block)
        elif element_type == "desk":
            desk_block = mt.signBlock(wood=material, facing="north", line1="Desk")
            ED.placeBlock(position, desk_block)
        elif element_type == "computer":
            computer_block = mt.lecternBlock(facing="south", bookData=mt.bookData("Desktop Computer"))
            ED.placeBlock(position, computer_block)
        elif element_type == "lamp":
            lamp_block = mt.lecternBlock(facing="south", bookData=mt.bookData("Modern Floor Lamp"))
            ED.placeBlock(position, lamp_block)

        # Add more conditions for other decoration elements as needed


def main():
    try:
        # Dynamically determine the build area based on terrain
        build_area = determineBuildArea()

        # Adapt the building to the terrain
        adaptation_result = adaptToTerrain(build_area)
        print("Adaptation Result:")
        print(f"- Average Ground Level: {adaptation_result['average_ground_level']}")
        if adaptation_result['actions_taken']:
            print("Actions Taken:")
            for action in adaptation_result['actions_taken']:
                print(f"- {action}")

        # Generate the building in the dynamic build area
        generateBuilding(build_area)

        print("Done!")

    except KeyboardInterrupt:
        print("Pressed Ctrl-C to kill the program.")


if __name__ == '__main__':
    main()