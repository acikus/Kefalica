import pygame
import sys
import random
import json
import os
import math
import tkinter as tk
import threading
from enum import Enum, auto
from PIL import Image  # Pillow is used to load animated GIF frames

from tiles import TileType, Tile, Inventory  # Assumes you have these modules.
from constants import *  # Assumes constants like SCREEN_WIDTH, SCREEN_HEIGHT, etc.

# Asset directories
BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "roadparts")

# -------------------------------------------------------------------------
# Helper: Load Animated GIF Frames with White Background Made Transparent
# -------------------------------------------------------------------------
def load_gif_frames(filename, target_size, white_threshold=240):
    """
    Loads frames from an animated GIF, converting nearly-white pixels to transparent.
    """
    frames = []
    try:
        gif = Image.open(filename)
        while True:
            frame = gif.convert("RGBA")
            new_data = []
            for pixel in frame.getdata():
                # Turn near-white to transparent
                if (pixel[0] >= white_threshold and
                    pixel[1] >= white_threshold and
                    pixel[2] >= white_threshold):
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(pixel)
            frame.putdata(new_data)
            mode = frame.mode
            size = frame.size
            data = frame.tobytes()
            py_image = pygame.image.fromstring(data, size, mode).convert_alpha()
            py_image = pygame.transform.scale(py_image, target_size)
            frames.append(py_image)
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass
    except Exception as e:
        print(f"Error loading GIF frames: {e}")
    return frames if frames else None


# -------------------------------------------------------------------------
# Level Loader
# -------------------------------------------------------------------------
class LevelLoader:
    """
    Loads levels where each cell can have multiple tile entries.
    """
    def __init__(self, filename="levels_data.json"):
        # Build the path to the JSON file in the assets directory.
        json_path = os.path.join(os.path.dirname(__file__), ASSETS_DIR, filename)
        with open(json_path, "r") as f:
            data = json.load(f)
        self.levels_data = data["levels"]

    def load_level(self, level_number):
        index = level_number - 1
        if index < 0 or index >= len(self.levels_data):
            raise IndexError(f"No level data for level {level_number}.")
        level_info = self.levels_data[index]
        w = level_info["grid_width"]
        h = level_info["grid_height"]

        # Each cell is a list of Tile objects.
        grid = [[[] for _ in range(w)] for _ in range(h)]

        for tile_obj in level_info["tiles"]:
            x = tile_obj["x"]
            y = tile_obj["y"]
            tile_type_name = tile_obj["type"]
            missing = tile_obj.get("missing", False)
            if not missing:
                tile_type = TileType[tile_type_name]
                new_tile = Tile(tile_type, draggable=False)
                grid[y][x].append(new_tile)
            # For missing tiles, no tile is pre-placed.
        return grid, level_info


# -------------------------------------------------------------------------
# Game States
# -------------------------------------------------------------------------
class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    ANIMATING = auto()
    LEVEL_COMPLETE = auto()


# -------------------------------------------------------------------------
# Main Game Class with All Modifications
# -------------------------------------------------------------------------
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Аутопут")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)

        # Load last solved level if exists, otherwise start at level 1
        self.level_loader = LevelLoader("levels_data.json")
        self.current_level = self.load_progress()
        self.grid = None
        self.current_level_info = None
        self.inventory = Inventory()
        self.selected_tile = None
        self.missing_positions = {}  # (gx, gy) -> expected tile type

        # --- Button Layout: All in one vertical column ---
        BUTTON_WIDTH = 150
        BUTTON_HEIGHT = 40
        BUTTON_SPACING = 10
        BUTTON_START_X = SCREEN_WIDTH - 180
        BUTTON_START_Y = 30

        self.check_solution_button = pygame.Rect(
            BUTTON_START_X,
            BUTTON_START_Y,
            BUTTON_WIDTH,
            BUTTON_HEIGHT
        )
        self.prev_level_button = pygame.Rect(
            BUTTON_START_X,
            BUTTON_START_Y + (BUTTON_HEIGHT + BUTTON_SPACING) * 1,
            BUTTON_WIDTH,
            BUTTON_HEIGHT
        )
        self.undo_button = pygame.Rect(
            BUTTON_START_X,
            BUTTON_START_Y + (BUTTON_HEIGHT + BUTTON_SPACING) * 2,
            BUTTON_WIDTH,
            BUTTON_HEIGHT
        )
        self.new_tiles_button = pygame.Rect(
            BUTTON_START_X,
            BUTTON_START_Y + (BUTTON_HEIGHT + BUTTON_SPACING) * 3,
            BUTTON_WIDTH,
            BUTTON_HEIGHT
        )

        self.message = ""
        self.message_timer = 0

        # Car animation settings
        self.road_path_pixels = []
        self.path_index = 0
        self.car_speed = 5
        self.car_angle = 0
        self.show_path_points = True

        # Load Car GIF frames
        target_size = (TILE_SIZE, TILE_SIZE)
        gif_path = os.path.join(ASSETS_DIR, "car.gif")
        self.car_frames = load_gif_frames(gif_path, target_size)
        if not self.car_frames:
            fallback = pygame.Surface(target_size, pygame.SRCALPHA)
            fallback.fill((200, 0, 0))
            self.car_frames = [fallback]
        self.frame_index = 0
        self.frame_delay = 5
        self.frame_timer = 0

        # Load car sound
        try:
            sound_path = os.path.join(ASSETS_DIR, "car_sound.wav")
            self.car_sound = pygame.mixer.Sound(sound_path)
            self.car_sound.set_volume(0.3)
        except Exception as e:
            print("Could not load car sound:", e)
            self.car_sound = None

        # For undo functionality: record moves as (action, tile, gx, gy)
        self.move_history = []

        # Start level (or resume progress)
        self.start_level()

    # ---------------------------------------------------------------------
    # Button Drawing with Highlight Effect
    # ---------------------------------------------------------------------
    def draw_button(self, rect, text):
        # Get current mouse position and button state
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = rect.collidepoint(mouse_pos)
        is_clicked = is_hovered and pygame.mouse.get_pressed()[0]

        # Define colors
        default_color = (255, 255, 0)    # Yellow
        highlight_color = (255, 215, 0)  # Lighter yellow for hover
        clicked_color = (255, 165, 0)    # Orange for click

        if is_clicked:
            color = clicked_color
        elif is_hovered:
            color = highlight_color
        else:
            color = default_color

        pygame.draw.rect(self.screen, color, rect)
        text_surface = self.font.render(text, True, TEXT_COLOR)
        self.screen.blit(
            text_surface,
            (rect.centerx - text_surface.get_width() // 2,
             rect.centery - text_surface.get_height() // 2)
        )

    # ---------------------------------------------------------------------
    # Progress Save/Load
    # ---------------------------------------------------------------------
    def save_progress(self, level):
        progress_path = os.path.join(ASSETS_DIR, "progress.json")
        data = {"last_solved_level": level}
        with open(progress_path, "w") as f:
            json.dump(data, f)

    def load_progress(self):
        progress_path = os.path.join(ASSETS_DIR, "progress.json")
        if os.path.exists(progress_path):
            with open(progress_path, "r") as f:
                data = json.load(f)
            return data.get("last_solved_level", 1)
        else:
            return 1

    # ---------------------------------------------------------------------
    # Level Management
    # ---------------------------------------------------------------------
    def start_level(self):
        self.grid, self.current_level_info = self.level_loader.load_level(self.current_level)
        self.inventory.clear()
        self.refresh_inventory()
        self.selected_tile = None
        self.road_path_pixels.clear()
        self.path_index = 0
        self.state = GameState.PLAYING

        self.missing_positions = {}
        for tile_obj in self.current_level_info["tiles"]:
            if tile_obj.get("missing", False):
                self.missing_positions[(tile_obj["x"], tile_obj["y"])] = tile_obj["type"]

        self.move_history.clear()

    def refresh_inventory(self):
        while len(self.inventory.tiles) < self.inventory.max_tiles:
            allowed_road_types = [
                TileType.HORIZONTAL, TileType.VERTICAL,
                TileType.TURN_TOP_RIGHT, TileType.TURN_RIGHT_BOTTOM,
                TileType.TURN_BOTTOM_LEFT, TileType.TURN_LEFT_TOP,
                TileType.CROSSROAD, TileType.PARKING
            ]
            if self.current_level >= 5:
                allowed_road_types += [TileType.BRIDGE_HORIZONTAL, TileType.BRIDGE_VERTICAL]
            if self.current_level >= 11:
                allowed_road_types += [TileType.RAILROAD_CROSSING_HORIZONTAL, TileType.RAILROAD_CROSSING_VERTICAL]
            tile_type = random.choice(allowed_road_types)
            new_tile = Tile(tile_type, draggable=True)
            self.inventory.add_tile(new_tile)

    # ---------------------------------------------------------------------
    # Grid Helpers
    # ---------------------------------------------------------------------
    def get_top_tile(self, gx, gy):
        cell_stack = self.grid[gy][gx]
        if cell_stack:
            return cell_stack[-1]
        return None

    def place_tile_on_grid(self, gx, gy, tile):
        self.grid[gy][gx].append(tile)

    def pop_top_tile(self, gx, gy):
        if self.grid[gy][gx]:
            return self.grid[gy][gx].pop()
        return None

    def is_missing_position(self, gx, gy):
        return (gx, gy) in self.missing_positions

    # ---------------------------------------------------------------------
    # Undo Functionality
    # ---------------------------------------------------------------------
    def undo_last_move(self):
        if not self.move_history:
            return
        action_type, tile, gx, gy = self.move_history.pop()
        if action_type == "PLACE":
            popped = self.pop_top_tile(gx, gy)
            if popped:
                self.inventory.add_tile(popped)
        elif action_type == "REMOVE":
            if tile in self.inventory.tiles:
                self.inventory.tiles.remove(tile)
            self.place_tile_on_grid(gx, gy, tile)

    # ---------------------------------------------------------------------
    # Event Handling
    # ---------------------------------------------------------------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if self.state == GameState.MENU:
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    self.state = GameState.PLAYING

            elif self.state == GameState.PLAYING:
                self.handle_playing_events(event)

            elif self.state == GameState.ANIMATING:
                pass

            elif self.state == GameState.LEVEL_COMPLETE:
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    total_levels = len(self.level_loader.levels_data)
                    if self.current_level < total_levels:
                        self.current_level += 1
                        self.start_level()
                        self.state = GameState.PLAYING
                    else:
                        self.game_over()
        return True

    def handle_playing_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # Check inventory click
            tile_clicked = self.inventory.handle_click(mouse_pos)
            if tile_clicked is not None:
                if self.selected_tile:
                    self.inventory.add_tile(self.selected_tile)
                    self.selected_tile = None
                else:
                    self.inventory.remove_tile(tile_clicked)
                    self.selected_tile = tile_clicked
                return

            # Check buttons using the vertical layout
            if self.check_solution_button.collidepoint(mouse_pos):
                self.check_solution()
                return

            if self.new_tiles_button.collidepoint(mouse_pos):
                self.inventory.clear()
                self.refresh_inventory()
                self.selected_tile = None
                return

            if self.undo_button.collidepoint(mouse_pos):
                self.undo_last_move()
                return

            if self.prev_level_button.collidepoint(mouse_pos):
                if self.current_level > 1:
                    self.current_level -= 1
                    self.start_level()
                return

            # Check grid click
            gx = (mouse_pos[0] - GRID_START_X) // TILE_SIZE
            gy = (mouse_pos[1] - GRID_START_Y) // TILE_SIZE
            if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                if not self.selected_tile:
                    top_tile = self.get_top_tile(gx, gy)
                    if top_tile and top_tile.draggable:
                        removed_tile = self.pop_top_tile(gx, gy)
                        if removed_tile:
                            self.move_history.append(("REMOVE", removed_tile, gx, gy))
                            self.selected_tile = removed_tile
                    return
                else:
                    if self.can_place_tile(self.selected_tile, gx, gy):
                        top_tile = self.get_top_tile(gx, gy)
                        if top_tile and top_tile.draggable:
                            popped = self.pop_top_tile(gx, gy)
                            if popped:
                                self.move_history.append(("REMOVE", popped, gx, gy))
                        self.place_tile_on_grid(gx, gy, self.selected_tile)
                        self.move_history.append(("PLACE", self.selected_tile, gx, gy))
                        self.selected_tile = None
                    else:
                        self.message = "Invalid placement!"
                        self.message_timer = pygame.time.get_ticks()

    # ---------------------------------------------------------------------
    # Allow any tile on missing positions.
    # ---------------------------------------------------------------------
    def can_place_tile(self, tile, gx, gy):
        is_missing = self.is_missing_position(gx, gy)
        top_tile = self.get_top_tile(gx, gy)
        if is_missing:
            return True
        if top_tile is not None:
            cell_stack = self.grid[gy][gx]
            obstacle_river = any(t.tile_type.name.startswith("OBSTACLE_RIVER") for t in cell_stack)
            obstacle_rail = any(t.tile_type.name.startswith("OBSTACLE_RAILROAD") for t in cell_stack)
            if obstacle_river:
                return tile.tile_type in [TileType.BRIDGE_HORIZONTAL, TileType.BRIDGE_VERTICAL]
            elif obstacle_rail:
                return tile.tile_type in [TileType.RAILROAD_CROSSING_HORIZONTAL, TileType.RAILROAD_CROSSING_VERTICAL]
            else:
                return top_tile.draggable
        else:
            for tile_obj in self.current_level_info["tiles"]:
                if tile_obj["x"] == gx and tile_obj["y"] == gy:
                    if tile_obj.get("isObstacle", False):
                        obstacle_type = tile_obj["type"].upper()
                        if obstacle_type == "RIVER":
                            return tile.tile_type in [TileType.BRIDGE_HORIZONTAL, TileType.BRIDGE_VERTICAL]
                        elif obstacle_type == "RAILROAD":
                            return tile.tile_type in [TileType.RAILROAD_CROSSING_HORIZONTAL, TileType.RAILROAD_CROSSING_VERTICAL]
                        else:
                            return False
            return True

    # ---------------------------------------------------------------------
    # Drawing Helpers
    # ---------------------------------------------------------------------
    def draw_missing_highlight(self):
        margin = 4
        corner_radius = 8
        for (gx, gy), expected_type in self.missing_positions.items():
            rect_x = GRID_START_X + gx * TILE_SIZE + margin
            rect_y = GRID_START_Y + gy * TILE_SIZE + margin
            rect_w = TILE_SIZE - margin * 2
            rect_h = TILE_SIZE - margin * 2
            highlight_surf = pygame.Surface((rect_w, rect_h), pygame.SRCALPHA)
            pygame.draw.rect(highlight_surf, (255, 255, 0, 100),
                             highlight_surf.get_rect(), border_radius=corner_radius)
            self.screen.blit(highlight_surf, (rect_x, rect_y))

    def draw_path_points(self):
        if not self.road_path_pixels:
            return
        for idx, (x, y) in enumerate(self.road_path_pixels):
            pygame.draw.circle(self.screen, (0, 0, 0), (int(x), int(y)), 10)
            order_text = self.font.render(str(idx), True, (255, 255, 255))
            text_rect = order_text.get_rect(center=(int(x), int(y)))
            self.screen.blit(order_text, text_rect)

    def draw_car(self):
        current_frame = self.car_frames[self.frame_index]
        rotated_car = pygame.transform.rotate(current_frame, self.car_angle)
        rect = rotated_car.get_rect(center=(self.car_x, self.car_y))
        self.screen.blit(rotated_car, rect.topleft)

    def draw_game(self):
        grid_rect = pygame.Rect(GRID_START_X, GRID_START_Y,
                                GRID_WIDTH * TILE_SIZE, GRID_HEIGHT * TILE_SIZE)
        pygame.draw.rect(self.screen, GRID_BACKGROUND_COLOR, grid_rect)

        for gy in range(GRID_HEIGHT):
            for gx in range(GRID_WIDTH):
                stack = self.grid[gy][gx]
                if stack:
                    for tile_obj in stack:
                        tile_x = GRID_START_X + gx * TILE_SIZE
                        tile_y = GRID_START_Y + gy * TILE_SIZE
                        tile_obj.draw(self.screen, tile_x, tile_y)

        self.draw_missing_highlight()
        self.inventory.draw(self.screen)

        if self.selected_tile:
            mx, my = pygame.mouse.get_pos()
            self.selected_tile.draw(self.screen,
                                    mx - TILE_SIZE // 2,
                                    my - TILE_SIZE // 2,
                                    is_selected=True)

        # Draw buttons with highlight effect using the new helper method
        self.draw_button(self.check_solution_button, "Провери")
        self.draw_button(self.undo_button, "Врати")
        self.draw_button(self.prev_level_button, "Претходни ниво")
        self.draw_button(self.new_tiles_button, "Нови делови")

        lvl_text = self.font.render(f"Ниво: {self.current_level}", True, TEXT_COLOR)
        self.screen.blit(lvl_text, (10, 10))
        if self.message:
            msg_render = self.font.render(self.message, True, TEXT_COLOR)
            self.screen.blit(msg_render, (SCREEN_WIDTH // 2 - msg_render.get_width() // 2, SCREEN_HEIGHT - 50))

    def calculate_path_points(self):
        path_list = self.current_level_info.get("path", [])
        if not path_list:
            return []
        smooth_path = []
        tile_size = TILE_SIZE
        half_tile = tile_size / 2
        obstacle_types = {
            TileType.OBSTACLE_STONE,
            TileType.OBSTACLE_RIVER_VERTICAL,
            TileType.OBSTACLE_RAILROAD_VERTICAL,
            TileType.OBSTACLE_RIVER_HORIZONTAL,
            TileType.OBSTACLE_RAILROAD_HORIZONTAL,
            TileType.OBSTACLE_FOREST,
            TileType.OBSTACLE_STATION,
            TileType.OBSTACLE_RAILROAD_BOTTOM_LEFT,
            TileType.OBSTACLE_RAILROAD_LEFT_TOP,
            TileType.OBSTACLE_RAILROAD_RIGHT_BOTTOM,
            TileType.OBSTACLE_RAILROAD_RIVER_HORIZONTAL,
            TileType.OBSTACLE_RAILROAD_TOP_RIGHT,
            TileType.OBSTACLE_RIVER_TURN_BOTTOM_LEFT,
            TileType.OBSTACLE_RIVER_TURN_BOTTOM_RIGHT,
            TileType.OBSTACLE_RIVER_TURN_TOP_LEFT,
            TileType.OBSTACLE_RIVER_TURN_TOP_RIGHT
        }
        for i in range(len(path_list)):
            current = path_list[i]
            current_x, current_y = current["x"], current["y"]
            top_tile = self.get_top_tile(current_x, current_y)
            if not top_tile or top_tile.tile_type in obstacle_types:
                continue
            center_x = GRID_START_X + current_x * tile_size + half_tile
            center_y = GRID_START_Y + current_y * tile_size + half_tile - 10
            is_turn = top_tile.tile_type in [
                TileType.TURN_TOP_RIGHT,
                TileType.TURN_RIGHT_BOTTOM,
                TileType.TURN_BOTTOM_LEFT,
                TileType.TURN_LEFT_TOP
            ]
            if not is_turn or i == 0 or i == len(path_list) - 1:
                smooth_path.append((center_x, center_y))
            else:
                prev = path_list[i-1]
                next_tile = path_list[i+1]
                entry_dx = current_x - prev["x"]
                entry_dy = current_y - prev["y"]
                exit_dx = next_tile["x"] - current_x
                exit_dy = next_tile["y"] - current_y
                entry_x = center_x - entry_dx * half_tile
                entry_y = center_y - entry_dy * half_tile
                exit_x = center_x + exit_dx * half_tile
                exit_y = center_y + exit_dy * half_tile
                corner_x = center_x
                corner_y = center_y
                if top_tile.tile_type == TileType.TURN_TOP_RIGHT:
                    corner_x = center_x + half_tile
                    corner_y = center_y - half_tile
                elif top_tile.tile_type == TileType.TURN_BOTTOM_LEFT:
                    corner_x = center_x + half_tile
                    corner_y = center_y + half_tile
                elif top_tile.tile_type == TileType.TURN_RIGHT_BOTTOM:
                    corner_x = center_x - half_tile
                    corner_y = center_y + half_tile
                elif top_tile.tile_type == TileType.TURN_LEFT_TOP:
                    corner_x = center_x - half_tile
                    corner_y = center_y - half_tile
                smooth_path.append((entry_x, entry_y))
                radius = half_tile
                num_arc_points = 6
                start_angle = math.atan2(entry_y - corner_y, entry_x - corner_x)
                end_angle = math.atan2(exit_y - corner_y, exit_x - corner_x)
                while abs(end_angle - start_angle) > math.pi:
                    if end_angle > start_angle:
                        end_angle -= 2 * math.pi
                    else:
                        end_angle += 2 * math.pi
                for j in range(1, num_arc_points):
                    t = j / num_arc_points
                    angle = start_angle * (1 - t) + end_angle * t
                    arc_x = corner_x + radius * math.cos(angle)
                    arc_y = corner_y + radius * math.sin(angle)
                    smooth_path.append((arc_x, arc_y))
                smooth_path.append((exit_x, exit_y))
        return smooth_path

    def check_solution(self):
        correct = True
        for tile_obj in self.current_level_info["tiles"]:
            gx, gy = tile_obj["x"], tile_obj["y"]
            is_obstacle = tile_obj.get("isObstacle", False)
            is_missing = tile_obj.get("missing", False)
            required_type = tile_obj["type"]
            if is_missing:
                top_tile = self.get_top_tile(gx, gy)
                if not top_tile:
                    correct = False
                    break
            elif not is_obstacle:
                top_tile = self.get_top_tile(gx, gy)
                if not top_tile or top_tile.tile_type.name != required_type:
                    correct = False
                    break
        if correct:
            self.road_path_pixels = self.calculate_path_points()
            if not self.road_path_pixels:
                self.message = "Нема исправне путање!"
                self.message_timer = pygame.time.get_ticks()
                return
            self.car_x, self.car_y = self.road_path_pixels[0]
            self.path_index = 0
            self.state = GameState.ANIMATING
            self.message = "Супер! Погледај пролазак аутомобила."
            self.message_timer = pygame.time.get_ticks()
            if self.car_sound:
                self.car_sound.play(-1)
        else:
            self.message = "Нетачно решење. Пробај поново."
            self.message_timer = pygame.time.get_ticks()

    def update_car_animation(self):
        if self.path_index >= len(self.road_path_pixels) - 1:
            self.state = GameState.LEVEL_COMPLETE
            self.message = "Ниво је завршен! Кликни за наставак."
            self.message_timer = pygame.time.get_ticks()
            self.save_progress(self.current_level)
            if self.car_sound:
                self.car_sound.stop()
            return

        self.frame_timer += 1
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.car_frames)

        target_x, target_y = self.road_path_pixels[self.path_index + 1]
        dx = target_x - self.car_x
        dy = target_y - self.car_y

        target_angle = math.degrees(math.atan2(-dy, dx))
        def angle_diff(a, b):
            diff = (a - b + 180) % 360 - 180
            return diff
        angle_difference = angle_diff(target_angle, self.car_angle)
        max_turn = 5
        if abs(angle_difference) < max_turn:
            self.car_angle = target_angle
        else:
            self.car_angle += max_turn if angle_difference > 0 else -max_turn

        dist = math.hypot(dx, dy)
        if dist < 1:
            self.car_x, self.car_y = target_x, target_y
            self.path_index += 1
        else:
            step = min(self.car_speed, dist)
            self.car_x += (dx / dist) * step
            self.car_y += (dy / dist) * step

    def update(self):
        if self.message and (pygame.time.get_ticks() - self.message_timer > 2000):
            self.message = ""
        if self.state == GameState.ANIMATING:
            self.update_car_animation()

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        if self.state == GameState.MENU:
            self.draw_menu()
        else:
            self.draw_game()
            if self.state == GameState.ANIMATING:
                self.draw_car()
        pygame.display.flip()

    def draw_menu(self):
        title = self.font.render("АУТОПУТ", True, TEXT_COLOR)
        instr = self.font.render("Кликни за почетак игре", True, TEXT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//3))
        self.screen.blit(instr, (SCREEN_WIDTH//2 - instr.get_width()//2, SCREEN_HEIGHT//2))

    def run(self):
        running = True
        while running:
            if not self.handle_events():
                break
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

    def game_over(self):
        self.message = "Игра је завршена! Нема више нивоа."
        self.message_timer = pygame.time.get_ticks() 
        self.state = GameState.MENU

def main(parent=None):
    # Make sure Pygame is initialized
    if not pygame.get_init():
        pygame.init()

    # --- Standalone Mode (no parent) ---
    # If you run this file directly (python gameKefalica.py)
    if parent is None:
        game = Game()       # Your Pygame game class
        game.run()
        return

    # --- Modal Mode (with a parent Tk window) ---
    dummy = tk.Toplevel(parent)
    dummy.withdraw()       # Hide the dummy window
    dummy.transient(parent)  # Keep it "on top" of the parent
    dummy.grab_set()       # Block interaction with the parent

    # A function to properly close the dummy window and release the parent
    def close_dummy():
        # Release the grab before destroying the window
        dummy.grab_release()
        dummy.destroy()
        # Ensure the parent knows the game is closed
        parent.game_running = False
        # Give focus back to the parent window
        parent.focus_set()
        
    def game_thread():
        try:
            # Run the Pygame game loop in a thread
            game = Game()
            game.run()
        except Exception as e:
            print(f"Game error: {e}")
        finally:
            # Always ensure cleanup happens, even if there's an error
            # Schedule dummy closing on Tk's main thread
            if parent and parent.winfo_exists():
                parent.after(100, close_dummy)

    # Start the game in a separate thread
    game_thread = threading.Thread(target=game_thread, daemon=True)
    game_thread.start()

    # Block here until the dummy is destroyed
    parent.wait_window(dummy)



if __name__ == "__main__":
    main()
