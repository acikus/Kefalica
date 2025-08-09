import json
import pygame
import os
import sys
from tiles import TileType, Tile
from constants import *

# Adjust palette tile size for the level creator (if needed)
TILE_SIZE = TILE_SIZE - 50
BASE_DIR = os.path.dirname(__file__)
JSON_FILE = os.path.join(BASE_DIR, "assets", "roadparts", "levels_data.json")

def level_creator():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Autoput Level Creator")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    # Load images for all TileTypes and scale them to fit the palette container (TILE_SIZE x TILE_SIZE)
    tile_images = {
        tile_type: pygame.transform.scale(Tile(tile_type).image, (TILE_SIZE, TILE_SIZE))
        for tile_type in TileType
    }

    # grid[y][x] is now a *list* of tile-dictionaries
    grid = [[[] for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    # Updated palette: only base road tiles and allowed crucial obstacles are provided.
    tile_type_list = [
        TileType.HORIZONTAL,
        TileType.VERTICAL,
        TileType.TURN_TOP_RIGHT,
        TileType.TURN_RIGHT_BOTTOM,
        TileType.TURN_BOTTOM_LEFT,
        TileType.TURN_LEFT_TOP,
        TileType.CROSSROAD,
        TileType.PARKING,
        # Crucial obstacles:
        TileType.BRIDGE_HORIZONTAL,
        TileType.BRIDGE_VERTICAL,
        TileType.RAILROAD_CROSSING_HORIZONTAL,
        TileType.RAILROAD_CROSSING_VERTICAL,
        # Other obstacles that can be placed on land
        TileType.OBSTACLE_STONE,
        TileType.OBSTACLE_FOREST,
        TileType.OBSTACLE_STATION,
        # (Other OBSTACLE_RIVER_* and OBSTACLE_RAILROAD_* types are intentionally excluded)
        TileType.OBSTACLE_RAILROAD_BOTTOM_LEFT,
        TileType.OBSTACLE_RAILROAD_HORIZONTAL,
        TileType.OBSTACLE_RAILROAD_LEFT_TOP,
        TileType.OBSTACLE_RAILROAD_RIGHT_BOTTOM,
        TileType.OBSTACLE_RAILROAD_TOP_RIGHT,
        TileType.OBSTACLE_RAILROAD_VERTICAL,
        TileType.OBSTACLE_RIVER_HORIZONTAL,
        TileType.OBSTACLE_RIVER_TURN_BOTTOM_LEFT,
        TileType.OBSTACLE_RIVER_TURN_BOTTOM_RIGHT,
        TileType.OBSTACLE_RIVER_TURN_TOP_LEFT,
        TileType.OBSTACLE_RIVER_TURN_TOP_RIGHT,
        TileType.OBSTACLE_RIVER_VERTICAL,
    ]
    current_tile_type = tile_type_list[0]
    missing_mode = False

    current_level = 0
    levels_data = {"levels": []}

    # We'll keep track of the path in which non-obstacle tiles (road parts) are placed
    placement_path = []

    # For UNDO: store a stack of actions
    # Each action is (x, y, tile_data, 'add')
    undo_stack = []

    def push_undo_add(x, y, tile_data):
        """Record that we added a tile_data to grid[y][x]."""
        undo_stack.append(("add", x, y, tile_data))

    def pop_undo():
        """Pop the last action and undo it."""
        if not undo_stack:
            return
        action_type, x, y, tile_data = undo_stack.pop()
        if action_type == "add":
            if grid[y][x] and grid[y][x][-1] == tile_data:
                grid[y][x].pop()
            if placement_path and placement_path[-1] == (x, y):
                placement_path.pop()

    # Buttons
    buttons = {
        "save": pygame.Rect(GRID_START_X, SCREEN_HEIGHT-100, 100, 30),
        "load": pygame.Rect(GRID_START_X + 110, SCREEN_HEIGHT-100, 100, 30),
        "clear": pygame.Rect(GRID_START_X + 220, SCREEN_HEIGHT-100, 100, 30),
        "prev_level": pygame.Rect(GRID_START_X + 330, SCREEN_HEIGHT-100, 30, 30),
        "next_level": pygame.Rect(GRID_START_X + 370, SCREEN_HEIGHT-100, 30, 30),
        "missing": pygame.Rect(INVENTORY_START_X - 300, 10, 100, 30),
        "undo": pygame.Rect(INVENTORY_START_X - 400, 10, 100, 30),
    }

    # Palette layout
    PALETTE_X_LEFT = INVENTORY_START_X - 400
    PALETTE_Y_START = 70
    PALETTE_ROW_HEIGHT = TILE_SIZE + 10
    PALETTE_COLS = 6  # number of columns in the palette
    PALETTE_COL_WIDTH = TILE_SIZE + 10

    def get_palette_position(index):
        col = index % PALETTE_COLS
        row = index // PALETTE_COLS
        x = PALETTE_X_LEFT + col * PALETTE_COL_WIDTH
        y = PALETTE_Y_START + row * PALETTE_ROW_HEIGHT
        return x, y

    def get_tile_from_palette(mouse_pos):
        for index, tile_type in enumerate(tile_type_list):
            x, y = get_palette_position(index)
            tile_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            if tile_rect.collidepoint(mouse_pos):
                return tile_type
        return None

    def load_grid_from_level(level_data):
        new_grid = [[[] for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        for tile_info in level_data.get("tiles", []):
            x = tile_info.get("x", 0)
            y = tile_info.get("y", 0)
            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                tile_type_name = tile_info.get("type", "HORIZONTAL")
                missing = tile_info.get("missing", False)
                is_obstacle = tile_info.get("isObstacle", False)
                try:
                    ttype = TileType[tile_type_name]
                    tile_dict = {
                        "type": ttype,
                        "missing": missing,
                        "isObstacle": is_obstacle
                    }
                    new_grid[y][x].append(tile_dict)
                except (KeyError, ValueError):
                    print(f"Unknown tile type: {tile_type_name}")
        return new_grid

    def convert_grid_to_level_data(grid):
        tile_list = []
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if grid[y][x]:
                    for tile_data in grid[y][x]:
                        entry = {
                            "x": x,
                            "y": y,
                            "type": tile_data["type"].name,
                            "missing": tile_data.get("missing", False),
                        }
                        if tile_data["type"].name.startswith("OBSTACLE_"):
                            entry["isObstacle"] = True
                        tile_list.append(entry)
        return {
            "grid_width": GRID_WIDTH,
            "grid_height": GRID_HEIGHT,
            "tiles": tile_list
        }

    def clear_grid():
        return [[[] for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    levels_file = JSON_FILE
    if os.path.exists(levels_file):
        with open(levels_file, "r") as f:
            levels_data = json.load(f)
        if levels_data["levels"]:
            grid = load_grid_from_level(levels_data["levels"][0])
            placement_path.clear()
            if "path" in levels_data["levels"][0]:
                for p in levels_data["levels"][0]["path"]:
                    placement_path.append((p["x"], p["y"]))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # Toggle missing mode with 'M'
                if event.key == pygame.K_m:
                    missing_mode = not missing_mode

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # Check UI Buttons
                if buttons["save"].collidepoint(mouse_pos):
                    current_level_data = convert_grid_to_level_data(grid)
                    path_list = [{"x": px, "y": py} for (px, py) in placement_path]
                    current_level_data["path"] = path_list

                    if current_level < len(levels_data["levels"]):
                        levels_data["levels"][current_level] = current_level_data
                    else:
                        levels_data["levels"].append(current_level_data)

                    with open(levels_file, "w") as f:
                        json.dump(levels_data, f, indent=2)
                    continue

                if buttons["load"].collidepoint(mouse_pos):
                    if os.path.exists(levels_file):
                        with open(levels_file, "r") as f:
                            levels_data = json.load(f)
                        if 0 <= current_level < len(levels_data["levels"]):
                            grid = load_grid_from_level(levels_data["levels"][current_level])
                            placement_path.clear()
                            if "path" in levels_data["levels"][current_level]:
                                for p in levels_data["levels"][current_level]["path"]:
                                    placement_path.append((p["x"], p["y"]))
                    continue

                if buttons["clear"].collidepoint(mouse_pos):
                    grid = clear_grid()
                    placement_path.clear()
                    undo_stack.clear()
                    continue

                if buttons["prev_level"].collidepoint(mouse_pos):
                    if current_level > 0:
                        current_level -= 1
                        grid = load_grid_from_level(levels_data["levels"][current_level])
                        placement_path.clear()
                        undo_stack.clear()
                        if "path" in levels_data["levels"][current_level]:
                            for p in levels_data["levels"][current_level]["path"]:
                                placement_path.append((p["x"], p["y"]))
                    continue

                if buttons["next_level"].collidepoint(mouse_pos):
                    current_level += 1
                    if current_level < len(levels_data["levels"]):
                        grid = load_grid_from_level(levels_data["levels"][current_level])
                        placement_path.clear()
                        undo_stack.clear()
                        if "path" in levels_data["levels"][current_level]:
                            for p in levels_data["levels"][current_level]["path"]:
                                placement_path.append((p["x"], p["y"]))
                    else:
                        grid = clear_grid()
                        placement_path.clear()
                        undo_stack.clear()
                    continue

                if buttons["missing"].collidepoint(mouse_pos):
                    missing_mode = not missing_mode
                    continue

                if buttons["undo"].collidepoint(mouse_pos):
                    pop_undo()
                    continue

                # Check if user clicked on the tile palette
                palette_tile = get_tile_from_palette(mouse_pos)
                if palette_tile is not None:
                    current_tile_type = palette_tile
                    continue

                # Otherwise, the user is placing a tile on the grid
                grid_x = (mouse_pos[0] - GRID_START_X) // TILE_SIZE
                grid_y = (mouse_pos[1] - GRID_START_Y) // TILE_SIZE
                if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:

                    # --- Crucial obstacle checks ---
                    # If placing a bridge, ensure the underlying base tile is a river (and not already a bridge)
                    if current_tile_type in [TileType.BRIDGE_HORIZONTAL, TileType.BRIDGE_VERTICAL]:
                        if grid[grid_y][grid_x]:
                            base_tile = grid[grid_y][grid_x][0]
                            base_name = base_tile["type"].name
                            # Check that the cell is a river cell (and not already a bridge)
                            if "RIVER" not in base_name or "BRIDGE" in base_name:
                                continue
                            # Check orientation: horizontal bridge only on horizontal river, vertical bridge only on vertical river
                            if current_tile_type == TileType.BRIDGE_HORIZONTAL and "HORIZONTAL" not in base_name:
                                continue
                            if current_tile_type == TileType.BRIDGE_VERTICAL and "VERTICAL" not in base_name:
                                continue
                        else:
                            continue  # No base tile -> cannot place a bridge

                    # If placing a railroad crossing, ensure the underlying base tile is a railroad cell (and not already a crossing)
                    elif current_tile_type in [TileType.RAILROAD_CROSSING_HORIZONTAL, TileType.RAILROAD_CROSSING_VERTICAL]:
                        if grid[grid_y][grid_x]:
                            base_tile = grid[grid_y][grid_x][0]
                            base_name = base_tile["type"].name
                            if "RAILROAD" not in base_name or "RAILROAD_CROSSING" in base_name:
                                continue
                            if current_tile_type == TileType.RAILROAD_CROSSING_HORIZONTAL and "HORIZONTAL" not in base_name:
                                continue
                            if current_tile_type == TileType.RAILROAD_CROSSING_VERTICAL and "VERTICAL" not in base_name:
                                continue
                        else:
                            continue

                    # Build the tile data dictionary
                    tile_data = {
                        "type": current_tile_type,
                        "missing": missing_mode,
                        "isObstacle": False
                    }
                    if current_tile_type.name.startswith("OBSTACLE_"):
                        tile_data["isObstacle"] = True

                    # Add to that cell and record for undo
                    grid[grid_y][grid_x].append(tile_data)
                    push_undo_add(grid_x, grid_y, tile_data)

                    # Optionally add to the placement path if not an obstacle
                    if not tile_data["isObstacle"]:
                        placement_path.append((grid_x, grid_y))

        # --- Drawing ---
        screen.fill(BACKGROUND_COLOR)
        pygame.draw.rect(screen, GRID_BACKGROUND_COLOR,
                         (GRID_START_X, GRID_START_Y, GRID_WIDTH * TILE_SIZE, GRID_HEIGHT * TILE_SIZE))

        # Grid lines
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(screen, GRID_LINE_COLOR,
                             (GRID_START_X + x * TILE_SIZE, GRID_START_Y),
                             (GRID_START_X + x * TILE_SIZE, GRID_START_Y + GRID_HEIGHT * TILE_SIZE))
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(screen, GRID_LINE_COLOR,
                             (GRID_START_X, GRID_START_Y + y * TILE_SIZE),
                             (GRID_START_X + GRID_WIDTH * TILE_SIZE, GRID_START_Y + y * TILE_SIZE))

        # Draw tiles in each cell (from bottom to top)
        for gy in range(GRID_HEIGHT):
            for gx in range(GRID_WIDTH):
                if grid[gy][gx]:
                    for tile_data in grid[gy][gx]:
                        ttype = tile_data["type"]
                        tile_x = GRID_START_X + gx * TILE_SIZE
                        tile_y = GRID_START_Y + gy * TILE_SIZE
                        img = tile_images[ttype]
                        screen.blit(img, (tile_x, tile_y))
                        if tile_data["missing"]:
                            overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                            overlay.fill((255, 255, 0, 100))
                            screen.blit(overlay, (tile_x, tile_y))

        # --- New: Draw order numbers on road parts (non-obstacle tiles) ---
        # Create a map of each cell's first occurrence in the placement path.
        order_map = {}
        for i, (gx, gy) in enumerate(placement_path):
            if (gx, gy) not in order_map:
                order_map[(gx, gy)] = i + 1  # Order numbers start at 1
        for (gx, gy), order in order_map.items():
            text = font.render(str(order), True, (0, 0, 0))
            tile_center_x = GRID_START_X + gx * TILE_SIZE + TILE_SIZE // 2
            tile_center_y = GRID_START_Y + gy * TILE_SIZE + TILE_SIZE // 2
            text_rect = text.get_rect(center=(tile_center_x, tile_center_y))
            screen.blit(text, text_rect)

        # Draw UI buttons
        for name, rect in buttons.items():
            btn_color = (100, 150, 200)
            if name == "missing" and missing_mode:
                btn_color = (255, 200, 100)
            pygame.draw.rect(screen, btn_color, rect)
            pygame.draw.rect(screen, (50, 50, 50), rect, 2)
            if name == "prev_level":
                text = font.render("<", True, (0, 0, 0))
            elif name == "next_level":
                text = font.render(">", True, (0, 0, 0))
            else:
                text = font.render(name.capitalize(), True, (0, 0, 0))
            text_pos = (rect.x + (rect.width - text.get_width()) // 2,
                        rect.y + (rect.height - text.get_height()) // 2)
            screen.blit(text, text_pos)

        # Draw the tile palette region
        palette_width = PALETTE_COL_WIDTH * PALETTE_COLS
        palette_height = PALETTE_ROW_HEIGHT * ((len(tile_type_list) + PALETTE_COLS - 1) // PALETTE_COLS)
        pygame.draw.rect(screen, GRID_BACKGROUND_COLOR,
                         (PALETTE_X_LEFT - 10, PALETTE_Y_START - 10, palette_width + 20, palette_height + 20))
        pygame.draw.rect(screen, GRID_LINE_COLOR,
                         (PALETTE_X_LEFT - 10, PALETTE_Y_START - 10, palette_width + 20, palette_height + 20), 2)

        for index, tile_type in enumerate(tile_type_list):
            x, y = get_palette_position(index)
            screen.blit(tile_images[tile_type], (x, y))
            if tile_type == current_tile_type:
                pygame.draw.rect(screen, (255, 255, 0), (x, y, TILE_SIZE, TILE_SIZE), 3)

        # Preview of the current tile
        preview_text = font.render("Preview:", True, (0, 0, 0))
        preview_x = PALETTE_X_LEFT
        preview_y = PALETTE_Y_START + palette_height + 40
        screen.blit(preview_text, (preview_x, preview_y))
        preview_image = tile_images[current_tile_type]
        screen.blit(preview_image, (preview_x, preview_y + 30))
        if missing_mode:
            overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            overlay.fill((255, 255, 0, 100))
            screen.blit(overlay, (preview_x, preview_y + 30))

        # Show current level info
        level_text = font.render(
            f"Level: {current_level+1}/{max(len(levels_data['levels']), current_level+1)}",
            True, (0, 0, 0)
        )
        screen.blit(level_text, (10, 10))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    level_creator()
