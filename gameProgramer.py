import pygame
import random
import time
import sys
from enum import Enum
import tkinter as tk
import queue
import os
import threading

# Constants
COMMAND_HEIGHT = 30
COMMAND_WIDTH = 80
BUTTON_HEIGHT = 40
BUTTON_WIDTH = 100
BUTTON_MARGIN = 10
CELL_SIZE = 80
MARGIN = 5
ANIMATION_SPEED = 0.3  # seconds per move

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 205, 50)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (169, 169, 169)
YELLOW = (255, 255, 0)
PLAYER_COLOR = (0, 150, 255)

class Direction(Enum):
    UP = (0, -1)
    RIGHT = (1, 0)
    DOWN = (0, 1)
    LEFT = (-1, 0)

class CellType(Enum):
    NEUTRAL = 0
    GRASS = 1
    ROCK = 2
    STRAWBERRY = 3

class Command(Enum):
    TURN_LEFT = 0
    TURN_RIGHT = 1
    FORWARD = 2

# Re-ordered directions for standard left/right rotation:
DIRECTION_ORDER = [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT]

class StrawberryGridGame:
    level_data = [
        (3, 1, 0),
        (4, 2, 1),
        (5, 3, 2),
        (6, 4, 3),
        (7, 5, 4),
        (8, 6, 5)
    ]

    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.font = pygame.font.SysFont('Arial', 20)
        self.small_font = pygame.font.SysFont('Arial', 16)

        self.current_level = 1
        self.all_levels_completed = False

        # Define panel widths for the three columns:
        # Left: grid (rotated), Middle: command sequence, Right: command buttons.
        self.selected_commands_panel_width = 300
        self.command_buttons_panel_width = BUTTON_WIDTH + 5  # as requested

        # Initial screen size (will be recalculated in reset_game)
        self.screen_width = 1024
        self.screen_height = 768

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Програмер")

        # Load images
        self.strawberry_img = self.load_image("strawberry.png", CELL_SIZE - 10)
        self.rock_img = self.load_image("rock.png", CELL_SIZE - 10)
        self.player_img = self.load_image("player.png", CELL_SIZE - 15)
        self.grass_img = self.load_image("grass.png", CELL_SIZE)
        self.forward_img = self.load_image("forward.png", BUTTON_WIDTH - 20)
        self.turn_left_img = self.load_image("turn_left.png", BUTTON_WIDTH - 20)
        self.turn_right_img = self.load_image("turn_right.png", BUTTON_WIDTH - 20)

        self.reset_game()

    def load_image(self, filename, size):
        base_path = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(base_path, "assets", "programer", filename)
        try:
            image = pygame.image.load(image_path)
            return pygame.transform.scale(image, (size, size))
        except pygame.error as e:
            print(f"Warning: Failed to load {filename}. Using placeholder. Error: {e}")
            surface = pygame.Surface((size, size), pygame.SRCALPHA)
            return surface

    def turn_left(self):
        i = DIRECTION_ORDER.index(self.player_direction)
        i = (i - 1) % 4
        self.player_direction = DIRECTION_ORDER[i]

    def turn_right(self):
        i = DIRECTION_ORDER.index(self.player_direction)
        i = (i + 1) % 4
        self.player_direction = DIRECTION_ORDER[i]

    def draw_grid(self):
        # Draw the grid with a 90° counterclockwise rotation.
        # Transformation: drawing_row = n - 1 - col, drawing_col = row.
        for r in range(self.n):
            for c in range(self.n):
                draw_row = self.n - 1 - c
                draw_col = r
                x = draw_col * (CELL_SIZE + MARGIN) + MARGIN
                y = draw_row * (CELL_SIZE + MARGIN) + MARGIN

                # Mark start and finish with yellow.
                if self.grid[r][c] == CellType.NEUTRAL:
                    if (r, c) in [(0, 0), (self.n - 1, self.n - 1)]:
                        color = BROWN
                    else:
                        color = WHITE
                    pygame.draw.rect(self.screen, color, [x, y, CELL_SIZE, CELL_SIZE])
                elif self.grid[r][c] == CellType.GRASS:
                    self.screen.blit(self.grass_img, (x, y))
                elif self.grid[r][c] == CellType.ROCK:
                    pygame.draw.rect(self.screen, WHITE, [x, y, CELL_SIZE, CELL_SIZE])
                    self.screen.blit(self.rock_img, (x + 5, y + 5))
                elif self.grid[r][c] == CellType.STRAWBERRY:
                    self.screen.blit(self.grass_img, (x, y))
                    self.screen.blit(self.strawberry_img, (x + 5, y + 5))

        # Draw player: transform underlying position to rotated coordinates.
        player_r, player_c = self.player_pos  # underlying position
        rot_row = self.n - 1 - player_c
        rot_col = player_r
        player_x = rot_col * (CELL_SIZE + MARGIN) + MARGIN + CELL_SIZE // 2
        player_y = rot_row * (CELL_SIZE + MARGIN) + MARGIN + CELL_SIZE // 2

        # # Compute original angle based on underlying direction.
        # if self.player_direction == Direction.RIGHT:
        #     orig_angle = 0
        # elif self.player_direction == Direction.DOWN:
        #     orig_angle = 90
        # elif self.player_direction == Direction.LEFT:
        #     orig_angle = 180
        # else:  # UP
        #     orig_angle = 270

        # Adjust angle by subtracting 90° for the rotated view.
        rotated_angle = 0#(orig_angle - 90) % 360

        rotated_player = pygame.transform.rotate(self.player_img, rotated_angle)
        player_rect = rotated_player.get_rect(center=(player_x, player_y))
        self.screen.blit(rotated_player, player_rect)

    def bfs_path_exists(self, grid, n):
        start = (0, 0)
        end = (n - 1, n - 1)
        if grid[0][0] == CellType.ROCK or grid[n - 1][n - 1] == CellType.ROCK:
            return False

        visited = [[False] * n for _ in range(n)]
        q = queue.Queue()
        q.put(start)
        visited[0][0] = True

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        while not q.empty():
            r, c = q.get()
            if (r, c) == end:
                return True
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < n and 0 <= nc < n:
                    if not visited[nr][nc] and grid[nr][nc] != CellType.ROCK:
                        visited[nr][nc] = True
                        q.put((nr, nc))
        return False

    def generate_level_grid(self, n, rock_count, strawberry_count):
        while True:
            grid = [[CellType.GRASS for _ in range(n)] for _ in range(n)]
            # Underlying start (0,0) and finish (n-1,n-1) are neutral.
            grid[0][0] = CellType.NEUTRAL
            grid[n - 1][n - 1] = CellType.NEUTRAL

            positions = [(r, c) for r in range(n) for c in range(n)
                         if (r, c) not in [(0, 0), (n - 1, n - 1)]]
            if rock_count > 0:
                rock_positions = random.sample(positions, k=rock_count)
                for r, c in rock_positions:
                    grid[r][c] = CellType.ROCK

            if self.bfs_path_exists(grid, n):
                grass_positions = [(r, c) for r in range(n) for c in range(n) if grid[r][c] == CellType.GRASS]
                actual_strawberry_count = min(len(grass_positions), strawberry_count)
                if actual_strawberry_count > 0:
                    strawberry_spots = random.sample(grass_positions, k=actual_strawberry_count)
                    for r, c in strawberry_spots:
                        grid[r][c] = CellType.STRAWBERRY
                return grid, actual_strawberry_count

    def reset_game(self):
        if self.current_level > 6:
            self.all_levels_completed = True
            self.current_level = 1

        n, strawberry_count, rock_count = self.level_data[self.current_level - 1]
        self.n = n
        self.strawberry_count = strawberry_count
        self.rock_count = rock_count

        self.grid_width = self.n * (CELL_SIZE + MARGIN) + MARGIN
        self.grid_height = self.n * (CELL_SIZE + MARGIN) + MARGIN

        # Full screen width includes the grid plus the two side panels.
        self.screen_height = max(self.grid_height, 600)
        self.screen_width = self.grid_width + self.selected_commands_panel_width + self.command_buttons_panel_width

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

        self.grid, actual_strawberry_count = self.generate_level_grid(
            self.n, self.rock_count, self.strawberry_count)
        self.total_strawberries = actual_strawberry_count
        self.collected_strawberries = 0
        self.game_won = False
        self.game_lost = False
        self.is_executing = False
        self.game_message = ""  # Clear any previous message

        # Set player start at underlying (0, 0)
        self.player_pos = [0, 0]

        # Choose initial direction.
        if self.n > 1:
            if self.grid[0][1] != CellType.ROCK:
                self.player_direction = Direction.RIGHT
            elif self.grid[1][0] != CellType.ROCK:
                self.player_direction = Direction.DOWN
            else:
                self.player_direction = Direction.RIGHT
        else:
            self.player_direction = Direction.RIGHT

        self.command_sequence = []
        self.current_command_index = 0
        self.animation_timer = 0

    def add_command(self, command):
        if not self.is_executing:
            self.command_sequence.append(command)

    def clear_commands(self):
        self.command_sequence = []

    def move_forward(self):
        dx, dy = self.player_direction.value
        new_row = self.player_pos[0] + dy
        new_col = self.player_pos[1] + dx
        # Check for moving off the grid.
        if not (0 <= new_row < self.n and 0 <= new_col < self.n):
            self.game_lost = True
            self.game_message = "Ударили сте у ивицу!"
            self.is_executing = False
            return
        # Check for moving into a rock.
        if self.grid[new_row][new_col] == CellType.ROCK:
            self.game_lost = True
            self.game_message = "Ударили сте у камен!"
            self.is_executing = False
            return
        # Valid move.
        self.player_pos = [new_row, new_col]
        if self.grid[new_row][new_col] == CellType.STRAWBERRY:
            self.collected_strawberries += 1
            self.grid[new_row][new_col] = CellType.GRASS

    def execute_command(self, command):
        if command == Command.TURN_LEFT:
            self.turn_left()
        elif command == Command.TURN_RIGHT:
            self.turn_right()
        elif command == Command.FORWARD:
            self.move_forward()

    def run_sequence(self):
        if not self.is_executing:
            self.is_executing = True
            self.current_command_index = 0
            self.animation_timer = time.time()
            self.game_won = False
            self.game_lost = False
            self.game_message = ""
            # Reset player to underlying start (0,0)
            self.player_pos = [0, 0]
            if self.n > 1:
                if self.grid[0][1] != CellType.ROCK:
                    self.player_direction = Direction.RIGHT
                elif self.grid[1][0] != CellType.ROCK:
                    self.player_direction = Direction.DOWN
                else:
                    self.player_direction = Direction.RIGHT
            else:
                self.player_direction = Direction.RIGHT
            self.collected_strawberries = 0

    def update_animation(self):
        if self.is_executing and time.time() - self.animation_timer >= ANIMATION_SPEED:
            if self.current_command_index < len(self.command_sequence):
                self.execute_command(self.command_sequence[self.current_command_index])
                self.current_command_index += 1
                self.animation_timer = time.time()
            else:
                self.is_executing = False
                # If no failure occurred during moves, check final conditions.
                if not self.game_lost:
                    if self.player_pos != [self.n - 1, self.n - 1]:
                        self.game_lost = True
                        self.game_message = "Морате доћи до базе!"
                    elif self.collected_strawberries < self.total_strawberries:
                        self.game_lost = True
                        self.game_message = "Нисте покупили јагоде!"
                    else:
                        self.game_won = True

                if self.game_won:
                    if self.current_level < 6:
                        self.current_level += 1
                        self.reset_game()
                        self.clear_commands()
                    else:
                        self.all_levels_completed = True

    def draw_selected_commands_panel(self):
        # Draw the middle column panel for command sequence with wrapping.
        panel_x = self.grid_width
        panel_y = 0
        panel_width = self.selected_commands_panel_width
        panel_height = self.screen_height
        pygame.draw.rect(self.screen, WHITE, [panel_x, panel_y, panel_width, panel_height])
        title_text = self.font.render("Наредбе:", True, BLACK)
        self.screen.blit(title_text, (panel_x + 10, panel_y + 10))
        # Start positions for drawing commands.
        command_x = panel_x + 10
        command_y = panel_y + 40
        for i, cmd in enumerate(self.command_sequence):
            if cmd == Command.TURN_LEFT:
                text = "Лево"
                color = BLUE
            elif cmd == Command.TURN_RIGHT:
                text = "Десно"
                color = RED
            else:
                text = "Напред"
                color = GREEN

            # Wrap to next column if exceeding panel bottom.
            if command_y + COMMAND_HEIGHT > panel_y + panel_height:
                command_x += COMMAND_WIDTH + 10
                command_y = panel_y + 40

            if self.is_executing and i == self.current_command_index:
                pygame.draw.rect(self.screen, YELLOW, [command_x, command_y, COMMAND_WIDTH, COMMAND_HEIGHT])
            pygame.draw.rect(self.screen, color, [command_x, command_y, COMMAND_WIDTH, COMMAND_HEIGHT], 2)
            cmd_text = self.small_font.render(text, True, BLACK)
            self.screen.blit(cmd_text, (command_x + 5, command_y + 5))
            command_y += COMMAND_HEIGHT + 5

    def draw_command_buttons_panel(self):
        # Draw the right column panel for command buttons.
        panel_x = self.grid_width + self.selected_commands_panel_width
        panel_y = 0
        panel_width = self.command_buttons_panel_width
        panel_height = self.screen_height
        pygame.draw.rect(self.screen, GRAY, [panel_x, panel_y, panel_width, panel_height])

        total_buttons = 5
        total_buttons_height = total_buttons * BUTTON_HEIGHT + (total_buttons - 1) * BUTTON_MARGIN
        btn_start_y = panel_y + (panel_height - total_buttons_height) // 2
        button_x = panel_x + (panel_width - BUTTON_WIDTH) // 2

        # Turn Left Button
        turn_left_button = pygame.Rect(button_x, btn_start_y, BUTTON_WIDTH, BUTTON_HEIGHT)
        pygame.draw.rect(self.screen, BLUE, turn_left_button)
        turn_left_button_text = self.font.render("Лево", True, WHITE)
        self.screen.blit(turn_left_button_text, (
            turn_left_button.x + (BUTTON_WIDTH - turn_left_button_text.get_width()) // 2,
            turn_left_button.y + (BUTTON_HEIGHT - turn_left_button_text.get_height()) // 2
        ))

        # Turn Right Button
        turn_right_button = pygame.Rect(button_x, btn_start_y + (BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT)
        pygame.draw.rect(self.screen, RED, turn_right_button)
        turn_right_button_text = self.font.render("Десно", True, WHITE)
        self.screen.blit(turn_right_button_text, (
            turn_right_button.x + (BUTTON_WIDTH - turn_right_button_text.get_width()) // 2,
            turn_right_button.y + (BUTTON_HEIGHT - turn_right_button_text.get_height()) // 2
        ))

        # Forward Button
        forward_button = pygame.Rect(button_x, btn_start_y + 2 * (BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT)
        pygame.draw.rect(self.screen, GREEN, forward_button)
        forward_button_text = self.font.render("Напред", True, WHITE)
        self.screen.blit(forward_button_text, (
            forward_button.x + (BUTTON_WIDTH - forward_button_text.get_width()) // 2,
            forward_button.y + (BUTTON_HEIGHT - forward_button_text.get_height()) // 2
        ))

        # Run/Reset Button
        run_button = pygame.Rect(button_x, btn_start_y + 3 * (BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT)
        if self.is_executing:
            pygame.draw.rect(self.screen, GRAY, run_button)
            run_button_text = self.font.render("Поново", True, WHITE)
        else:
            pygame.draw.rect(self.screen, PLAYER_COLOR, run_button)
            run_button_text = self.font.render("ПОКРЕНИ", True, WHITE)
        self.screen.blit(run_button_text, (
            run_button.x + (BUTTON_WIDTH - run_button_text.get_width()) // 2,
            run_button.y + (BUTTON_HEIGHT - run_button_text.get_height()) // 2
        ))

        # New Game Button
        new_game_button = pygame.Rect(button_x, btn_start_y + 4 * (BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT)
        pygame.draw.rect(self.screen, YELLOW, new_game_button)
        ng_text = self.font.render("Нова игра", True, BLACK)
        self.screen.blit(ng_text, (
            new_game_button.x + (BUTTON_WIDTH - ng_text.get_width()) // 2,
            new_game_button.y + (BUTTON_HEIGHT - ng_text.get_height()) // 2
        ))

    def draw_game_message(self):
        # Display the game message at the top center if the game is over.
        if not self.is_executing and (self.game_lost or self.game_won) and self.game_message:
            msg_color = RED if self.game_lost else GREEN
            message_surface = self.font.render(self.game_message, True, msg_color)
            x = 10 #(self.screen_width - message_surface.get_width()) // 2
            y = self.screen_height -30
            self.screen.blit(message_surface, (x, y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                # Determine which column was clicked.
                if pos[0] < self.grid_width:
                    # Click in the grid area – (optional) handle grid clicks if needed.
                    pass
                elif pos[0] < self.grid_width + self.selected_commands_panel_width:
                    # Click in the middle column (command sequence panel)
                    panel_x = self.grid_width
                    panel_y = 0
                    panel_height = self.screen_height
                    command_x = panel_x + 10
                    command_y = panel_y + 40
                    for i, _ in enumerate(self.command_sequence):
                        if command_y + COMMAND_HEIGHT > panel_y + panel_height:
                            command_x += COMMAND_WIDTH + 10
                            command_y = panel_y + 40
                        command_rect = pygame.Rect(command_x, command_y, COMMAND_WIDTH, COMMAND_HEIGHT)
                        if command_rect.collidepoint(pos) and not self.is_executing:
                            self.command_sequence.pop(i)
                            break
                        command_y += COMMAND_HEIGHT + 5
                else:
                    # Click in the right column (command buttons panel)
                    panel_x = self.grid_width + self.selected_commands_panel_width
                    panel_y = 0
                    panel_width = self.command_buttons_panel_width
                    panel_height = self.screen_height
                    total_buttons = 5
                    total_buttons_height = total_buttons * BUTTON_HEIGHT + (total_buttons - 1) * BUTTON_MARGIN
                    btn_start_y = panel_y + (panel_height - total_buttons_height) // 2
                    button_x = panel_x + (panel_width - BUTTON_WIDTH) // 2

                    turn_left_button = pygame.Rect(button_x, btn_start_y, BUTTON_WIDTH, BUTTON_HEIGHT)
                    turn_right_button = pygame.Rect(button_x, btn_start_y + (BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT)
                    forward_button = pygame.Rect(button_x, btn_start_y + 2 * (BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT)
                    run_button = pygame.Rect(button_x, btn_start_y + 3 * (BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT)
                    new_game_button = pygame.Rect(button_x, btn_start_y + 4 * (BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT)

                    if turn_left_button.collidepoint(pos) and not self.is_executing:
                        self.add_command(Command.TURN_LEFT)
                    elif turn_right_button.collidepoint(pos) and not self.is_executing:
                        self.add_command(Command.TURN_RIGHT)
                    elif forward_button.collidepoint(pos) and not self.is_executing:
                        self.add_command(Command.FORWARD)
                    elif run_button.collidepoint(pos):
                        if self.is_executing:
                            self.is_executing = False
                            self.player_pos = [0, 0]
                            if self.n > 1:
                                if self.grid[0][1] != CellType.ROCK:
                                    self.player_direction = Direction.RIGHT
                                elif self.grid[1][0] != CellType.ROCK:
                                    self.player_direction = Direction.DOWN
                                else:
                                    self.player_direction = Direction.RIGHT
                            else:
                                self.player_direction = Direction.RIGHT
                        else:
                            self.run_sequence()
                    elif new_game_button.collidepoint(pos):
                        self.reset_game()
                        self.clear_commands()
            # Other events can be handled here.
        return True

    def run(self):
        running = True
        clock = pygame.time.Clock()

        while running:
            running = self.handle_events()
            self.update_animation()

            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_selected_commands_panel()
            self.draw_command_buttons_panel()
            self.draw_game_message()

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

def main(parent=None):

    if not pygame.get_init():
        pygame.init()

    if parent is None:
        # Standalone
        game = StrawberryGridGame()
        game.run()
    else:
        # Modal / blocking mode with a hidden dummy Toplevel
        dummy = tk.Toplevel(parent)
        dummy.withdraw()
        dummy.grab_set()

        def game_thread():
            # Run Pygame game
            game = StrawberryGridGame()
            game.run()
            # Once game ends, destroy dummy
            dummy.destroy()

        threading.Thread(target=game_thread, daemon=True).start()
        parent.wait_window(dummy)


if __name__ == "__main__":
    main()
