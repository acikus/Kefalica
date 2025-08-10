import pygame
import os
from enum import Enum
from constants import *

# Define the path to the assets directory
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets", "roadparts")

class TileType(Enum):
    BRIDGE_HORIZONTAL = 0
    BRIDGE_VERTICAL = 1
    CROSSROAD = 2
    HORIZONTAL = 3
    OBSTACLE_FOREST = 4
    OBSTACLE_RAILROAD_BOTTOM_LEFT = 5
    OBSTACLE_RAILROAD_HORIZONTAL = 6
    OBSTACLE_RAILROAD_LEFT_TOP = 7
    OBSTACLE_RAILROAD_RIGHT_BOTTOM = 8
    OBSTACLE_RAILROAD_RIVER_HORIZONTAL = 9
    OBSTACLE_RAILROAD_TOP_RIGHT = 10
    OBSTACLE_RAILROAD_VERTICAL = 11
    OBSTACLE_RIVER_HORIZONTAL = 12
    OBSTACLE_RIVER_TURN_BOTTOM_LEFT = 13
    OBSTACLE_RIVER_TURN_BOTTOM_RIGHT = 14
    OBSTACLE_RIVER_TURN_TOP_LEFT = 15
    OBSTACLE_RIVER_TURN_TOP_RIGHT = 16
    OBSTACLE_RIVER_VERTICAL = 17
    OBSTACLE_STATION = 18
    OBSTACLE_STONE = 19
    PARKING = 20
    RAILROAD_CROSSING_HORIZONTAL = 21
    RAILROAD_CROSSING_VERTICAL = 22
    TURN_BOTTOM_LEFT = 23
    TURN_LEFT_TOP = 24
    TURN_RIGHT_BOTTOM = 25
    TURN_TOP_RIGHT = 26
    VERTICAL = 27

class Tile:
    def __init__(self, tile_type, draggable=False):
        self.tile_type = tile_type
        self.draggable = draggable  # Can this tile be moved?
        self.image = self.load_image()

    def load_image(self):
        """
        Load tile images dynamically from the assets folder.
        If the image is missing, create a placeholder.
        """
        file_name = f"{self.tile_type.name}.png"  # Convert ENUM name to filename
        image_path = os.path.join(ASSETS_DIR, file_name)

        try:
            # Load the image and scale it to fit the tile size
            image = pygame.image.load(image_path)
            image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
            return image
        except pygame.error:
            print(f"Warning: Missing image {file_name}, using placeholder.")
            return self.create_placeholder()

    def create_placeholder(self):
        """
        Generate a placeholder tile with a unique color and text if the image is missing.
        """
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((200, 50, 50))  # Red placeholder for missing images
        font = pygame.font.SysFont(None, 20)
        text = font.render(self.tile_type.name, True, (255, 255, 255))
        surf.blit(text, (5, TILE_SIZE // 3))  # Position the text
        return surf

    def draw(self, surface, x, y, is_selected=False):
        """
        Draw the tile at the given position. If selected, add a yellow overlay.
        """
        surface.blit(self.image, (x, y))
        if is_selected:
            overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            overlay.fill((255, 255, 0, 100))  # Yellow transparency
            surface.blit(overlay, (x, y))

class Inventory:
    def __init__(self):
        self.tiles = []
        self.max_tiles = 3
        self.start_x = INVENTORY_START_X
        self.start_y = INVENTORY_START_Y

    def add_tile(self, tile):
        if len(self.tiles) < self.max_tiles:
            self.tiles.append(tile)

    def remove_tile(self, tile):
        if tile in self.tiles:
            self.tiles.remove(tile)

    def clear(self):
        self.tiles = []

    def draw(self, surface):
        """
        Draws the inventory panel and tiles inside it.
        """
        inv_bg = pygame.Rect(self.start_x, self.start_y,
                             TILE_SIZE + 20, (TILE_SIZE + 20) * self.max_tiles)
        pygame.draw.rect(surface, GRID_BACKGROUND_COLOR, inv_bg)
        pygame.draw.rect(surface, (150, 150, 150), inv_bg, 2)

        for i, tile in enumerate(self.tiles):
            tile.draw(surface, self.start_x + 10, self.start_y + 10 + i * (TILE_SIZE + 20))

    def handle_click(self, pos):
        """
        Checks if a tile in the inventory was clicked and returns the tile.
        """
        for i, tile in enumerate(self.tiles):
            rect = pygame.Rect(self.start_x + 10,
                               self.start_y + 10 + i * (TILE_SIZE + 20),
                               TILE_SIZE, TILE_SIZE)
            if rect.collidepoint(pos):
                return tile
        return None
