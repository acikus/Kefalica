import pygame
import random
import sys
import time
import os
import math
import tkinter as tk
import threading

# Game constants based on the provided specifications
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 787
BOARD_START_X = 95
BOARD_START_Y = 80
CELL_SIZE = 72
CELL_GAP = 6
GRID_SIZE = 8  # Note: This creates 64 squares, not 36.

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets", "snake")

# Remove any Pygame initialization or display creation from the module level.
# All such calls now happen inside main().

def create_board_positions():
    """
    Creates a dictionary of board positions (1 to 64) mapped to their
    (x, y) pixel coordinates such that:
      - Square #1 is at the bottom-left of the board.
      - Square #64 is at the top-right.
      - Rows alternate directions (zigzag).
    """
    positions = {}
    for row in range(GRID_SIZE):
        logical_row = row  # row=0 is bottom row
        for col in range(GRID_SIZE):
            if logical_row % 2 == 0:
                position_num = logical_row * GRID_SIZE + (col + 1)
            else:
                position_num = logical_row * GRID_SIZE + (GRID_SIZE - col)
            x = BOARD_START_X + col * (CELL_SIZE + CELL_GAP) + CELL_SIZE // 2
            inverted_row = (GRID_SIZE - 1 - row)
            y = BOARD_START_Y + inverted_row * (CELL_SIZE + CELL_GAP) + CELL_SIZE // 2
            positions[position_num] = (x, y)
    return positions

# Global definitions for snakes and ladders remain
snakes = {
    42: 25,   # Land on 42 -> go down to 25
    23: 6,
    61: 37,
    35: 18
}
ladders = {
    8: 24,    # Land on 8 -> climb up to 24
    20: 36,
    16: 33,
    34: 50,
    43: 59
}

# Player class
class Player:
    def __init__(self, name, color, image):
        self.name = name
        self.color = color
        self.image = image
        self.position = 0  # Start off-board
        self.won = False
        
        # Animation properties
        self.current_x = 0
        self.current_y = 0
        self.target_x = 0
        self.target_y = 0
        self.is_animating = False
        self.animation_speed = 5
        self.animation_path = []
        self.animation_index = 0

    def move(self, dice_value, board_positions):
        if self.position + dice_value <= 64:
            if self.position > 0:
                self.current_x, self.current_y = board_positions[self.position]
            else:
                self.current_x, self.current_y = board_positions[1]
                self.current_y += 50
            
            old_position = self.position
            self.position += dice_value
            
            self.animation_path = []
            if old_position == 0:
                self.animation_path.append(board_positions[self.position])
            else:
                for pos in range(old_position + 1, self.position + 1):
                    if pos <= 64:
                        self.animation_path.append(board_positions[pos])
            
            message = f"{self.name} moved to {self.position}"
            
            if self.position in snakes:
                old_snake_position = self.position
                self.position = snakes[self.position]
                self.animation_path.append(board_positions[self.position])
                message = f"{self.name} was bitten! Moved from {old_snake_position} to {self.position}"
            elif self.position in ladders:
                old_ladder_position = self.position
                self.position = ladders[self.position]
                self.animation_path.append(board_positions[self.position])
                message = f"{self.name} climbed a ladder! Moved from {old_ladder_position} to {self.position}"
            
            if self.animation_path:
                self.target_x, self.target_y = self.animation_path[0]
                self.animation_index = 0
                self.is_animating = True
            
            if self.position == 64:
                self.won = True
                message = f"{self.name} has won!"

            return message
        else:
            return f"{self.name} needs exactly {64 - self.position} to win"
    
    def update_animation(self):
        if not self.is_animating or not self.animation_path:
            return
        
        dx = self.target_x - self.current_x
        dy = self.target_y - self.current_y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < self.animation_speed:
            self.current_x, self.current_y = self.target_x, self.target_y
            self.animation_index += 1
            
            if self.animation_index < len(self.animation_path):
                self.target_x, self.target_y = self.animation_path[self.animation_index]
            else:
                self.is_animating = False
        else:
            self.current_x += (dx / distance) * self.animation_speed
            self.current_y += (dy / distance) * self.animation_speed
    
    def draw(self, surface):
        if self.position > 0:
            x = int(self.current_x - self.image.get_width() // 2)
            y = int(self.current_y - self.image.get_height() // 2)
            surface.blit(self.image, (x, y))

# Button class
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)

        font = pygame.font.SysFont(None, 30)
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def check_click(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click

# Game class with a run() method encapsulating the main loop
class SnakesAndLadders:
    def __init__(self):
        self.players = []
        self.current_player_index = 0
        self.board_positions = create_board_positions()
        self.dice_value = 1
        self.game_started = False
        self.game_mode = None  # "1p" or "2p"
        self.game_message = "Beware of snakes!"
        self.roll_animation = False
        self.roll_end_time = 0
        self.waiting_for_animation = False

    def add_player(self, name, color, image):
        self.players.append(Player(name, color, image))

    def roll_dice(self):
        return random.randint(1, 6)

    def start_roll_animation(self):
        self.roll_animation = True
        self.roll_end_time = time.time() + 1  # 1 second animation

    def update_roll_animation(self):
        if self.roll_animation:
            if time.time() < self.roll_end_time:
                self.dice_value = random.randint(1, 6)
            else:
                self.roll_animation = False
                self.complete_turn()

    def computer_turn(self):
        self.start_roll_animation()
        # The move occurs in complete_turn() after the animation

    def player_turn(self):
        self.start_roll_animation()

    def complete_turn(self):
        if not self.roll_animation and not self.waiting_for_animation:
            self.dice_value = self.roll_dice()
            message = self.players[self.current_player_index].move(self.dice_value, self.board_positions)
            self.game_message = message
            self.waiting_for_animation = True

    def update_animations(self):
        if self.waiting_for_animation:
            current_player = self.players[self.current_player_index]
            current_player.update_animation()
            
            if not current_player.is_animating:
                self.waiting_for_animation = False
                self.next_player()

                if self.game_mode == "1p" and self.current_player_index == 1 and not any(player.won for player in self.players):
                    pygame.time.set_timer(pygame.USEREVENT, 1000)
        else:
            for player in self.players:
                player.update_animation()

    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        while self.players[self.current_player_index].won and not all(player.won for player in self.players):
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def reset_game(self):
        self.players = []
        self.current_player_index = 0
        self.dice_value = 1
        self.game_started = False
        self.game_mode = None
        self.game_message = "Snakes and Ladders!"
        self.roll_animation = False
        self.waiting_for_animation = False

    def draw_board_numbers(self, surface):
        font = pygame.font.SysFont(None, 24)
        for pos_num, (x, y) in self.board_positions.items():
            is_occupied = any(player.position == pos_num for player in self.players)
            if not is_occupied:
                text = font.render(str(pos_num), True, BLACK)
                text_rect = text.get_rect(center=(x, y))
                surface.blit(text, text_rect)

    def run(self):
        # Create buttons for in-game controls and menu options
        roll_btn = Button(SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT - 60, 100, 50, "Roll", (255, 255, 200), (255, 255, 150))
        new_game_btn = Button(SCREEN_WIDTH - 140, 20, 120, 40, "New Game", (255, 200, 200), (255, 150, 150))
        one_player_btn = Button(SCREEN_WIDTH//2 - 150, 300, 300, 50, "1 Player vs Computer", (200, 200, 255), (150, 150, 255))
        two_player_btn = Button(SCREEN_WIDTH//2 - 150, 370, 300, 50, "2 Players", (200, 255, 200), (150, 255, 150))
        
        clock = pygame.time.Clock()
        running = True

        while running:
            mouse_pos = pygame.mouse.get_pos()
            mouse_clicked = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_clicked = True
                elif event.type == pygame.USEREVENT:
                    pygame.time.set_timer(pygame.USEREVENT, 0)
                    if self.game_started and self.game_mode == "1p" and self.current_player_index == 1:
                        self.computer_turn()

            self.update_roll_animation()
            self.update_animations()

            # Draw the board background and game elements using the global images.
            screen.blit(board_img, (0, 0))

            if self.game_started:
                self.draw_board_numbers(screen)
                for player in self.players:
                    player.draw(screen)

                dice_x = SCREEN_WIDTH // 2 + 80
                dice_y = SCREEN_HEIGHT - 60
                screen.blit(dice_images[self.dice_value - 1], (dice_x, dice_y))

                font = pygame.font.SysFont(None, 30)
                if not any(player.won for player in self.players):
                    current_player = self.players[self.current_player_index]
                    text = font.render(f"Currently playing: {current_player.name}", True, current_player.color)
                    text_bg = pygame.Rect(20, 20, text.get_width() + 10, text.get_height() + 10)
                    pygame.draw.rect(screen, WHITE, text_bg)
                    pygame.draw.rect(screen, BLACK, text_bg, 1)
                    screen.blit(text, (25, 25))

                message_font = pygame.font.SysFont(None, 24)
                message_surface = message_font.render(self.game_message, True, BLACK)
                message_bg = pygame.Rect(20, 60, message_surface.get_width() + 10, message_surface.get_height() + 10)
                pygame.draw.rect(screen, WHITE, message_bg)
                pygame.draw.rect(screen, BLACK, message_bg, 1)
                screen.blit(message_surface, (25, 65))

                if not any(player.won for player in self.players) and not self.roll_animation and not self.waiting_for_animation:
                    # Always show the roll button in two-player mode
                    if self.game_mode == "2p" or self.game_mode == "1p" and self.current_player_index == 0:
                        roll_btn.check_hover(mouse_pos)
                        roll_btn.draw(screen)
                        if roll_btn.check_click(mouse_pos, mouse_clicked):
                            self.player_turn()


                new_game_btn.check_hover(mouse_pos)
                new_game_btn.draw(screen)
                if new_game_btn.check_click(mouse_pos, mouse_clicked):
                    self.reset_game()
            else:
                # Draw the game menu overlay
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((255, 255, 255, 200))
                screen.blit(overlay, (0, 0))
                
                title_font = pygame.font.SysFont(None, 60)
                title_text = title_font.render("Snakes and Ladders", True, BLACK)
                screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 150))
                
                one_player_btn.check_hover(mouse_pos)
                two_player_btn.check_hover(mouse_pos)
                one_player_btn.draw(screen)
                two_player_btn.draw(screen)
                
                if one_player_btn.check_click(mouse_pos, mouse_clicked):
                    self.game_mode = "1p"
                    self.add_player("Your Highness", RED, player_img)
                    self.add_player("Computer", BLUE, computer_img)
                    self.game_started = True
                elif two_player_btn.check_click(mouse_pos, mouse_clicked):
                    self.game_mode = "2p"  # Note: Adjust text as needed.
                    self.add_player("Player 1", RED, player_img)
                    self.add_player("Player 2", BLUE, computer_img)
                    self.game_started = True

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()

# Main method: All Pygame initialization, display creation, and image loading occur here.
def main(parent=None):
    # Initialize Pygame
    pygame.init()
    global screen, board_img, dice_images, player_img, computer_img

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snakes and Ladders")
    
    # Load images now (they won't be loaded on import)
    try:
        board_img = pygame.image.load(os.path.join(ASSETS_DIR, "board_background.png"))
        board_img = pygame.transform.scale(board_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        dice_images = [
            pygame.image.load(os.path.join(ASSETS_DIR, f"dice{i}.png")) for i in range(1, 7)
        ]
        dice_images = [pygame.transform.scale(img, (50, 50)) for img in dice_images]
        
        # Load player images
        player_img = pygame.image.load(os.path.join(ASSETS_DIR, "player.png"))
        player_img = pygame.transform.scale(player_img, (60, 60))
        
        computer_img = pygame.image.load(os.path.join(ASSETS_DIR, "computer.png"))
        computer_img = pygame.transform.scale(computer_img, (60, 60))
    
    except pygame.error as e:
        print(f"Error loading images: {e}")
        board_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        board_img.fill((100, 200, 100))
        dice_images = [pygame.Surface((50, 50)) for _ in range(6)]
        for i, img in enumerate(dice_images):
            img.fill((200, 200, 200))
            font = pygame.font.SysFont(None, 30)
            text = font.render(str(i + 1), True, BLACK)
            img.blit(text, (20, 15))
        player_img = pygame.Surface((60, 60))
        player_img.fill(RED)
        computer_img = pygame.Surface((60, 60))
        computer_img.fill(BLUE)
    
    if parent is None:
        game = SnakesAndLadders()
        game.run()
    else:
        # Modal mode: run in a separate thread with a hidden dummy Toplevel
        dummy = tk.Toplevel(parent)
        dummy.withdraw()
        dummy.grab_set()

        def game_thread():
            game = SnakesAndLadders()
            try:
                game.run()
            except SystemExit:
                pass  # Catch sys.exit() to prevent closing the main Tkinter app.
            dummy.destroy()

        threading.Thread(target=game_thread, daemon=True).start()
        parent.wait_window(dummy)

if __name__ == "__main__":
    main()
