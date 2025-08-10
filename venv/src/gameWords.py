import pygame
import random
import os
import threading
import tkinter as tk

# --------------------
# Configuration Values
# --------------------
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Colors
WHITE      = (255, 255, 255)
BLACK      = (0, 0, 0)
GREEN      = (0, 255, 0)
RED        = (255, 0, 0)
BLUE       = (0, 0, 255)
GRAY       = (50, 50, 50)

# Lanes configuration
NUM_LANES = 9
LANE_WIDTH = SCREEN_WIDTH / NUM_LANES

# Letter dimensions and falling speed
LETTER_WIDTH = 40
LETTER_HEIGHT = 40
LETTER_SPEED = 1     # Base falling speed (multiplied by dt)
LETTER_SPAWN_INTERVAL = 1500  # Milliseconds

# Player configuration
PLAYER_HEIGHT = LETTER_HEIGHT // 2  # e.g., 20 pixels
PLAYER_Y = SCREEN_HEIGHT - PLAYER_HEIGHT - 10  # Fixed vertical position
PLAYER_MOVE_STEP = 1  # One lane per key press

# English alphabet characters (uppercase)
ENGLISH_ALPHABET = [
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
    "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"
]

# Define vowels (for English)
VOWELS = {"A", "E", "I", "O", "U"}

# --------------------
# Unique Light Colors for Each Letter
# --------------------
LIGHT_COLORS = [
    "lightcoral", "lightseagreen", "lightskyblue", "lightpink", "lightgoldenrodyellow",
    "lightgreen", "lightblue", "lightgray", "lightcyan", "lightyellow",
    "lavender", "thistle", "powderblue", "palegreen", "mistyrose",
    "peachpuff", "wheat", "navajowhite", "lemonchiffon", "mintcream",
    "azure", "honeydew", "floralwhite", "oldlace", "ivory",
    "aliceblue", "lavenderblush", "seashell", "snow", "ghostwhite"
]
LETTER_BG_COLORS = dict(zip(ENGLISH_ALPHABET, LIGHT_COLORS))

# Get the directory of the current file
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    current_dir = os.getcwd()

DICT_PATH = os.path.join(current_dir, "assets/slova", "dictionary.txt")

# --------------------
# Dictionary Manager
# --------------------
class DictionaryManager:
    """Manages the list of valid words for the game."""
    def __init__(self, filepath=DICT_PATH):
        self.words = []
        self.load_words(filepath)

    def load_words(self, filepath):
        """Loads words from the given file or uses a fallback list."""
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    word = line.strip().lower()
                    if word:
                        self.words.append(word)
            print(f"Loaded {len(self.words)} words from {filepath}")
        else:
            self.words = ["space", "star", "rocket", "galaxy", "sun"]
            print("Word file not found; fallback word list used.")

    def is_valid_word(self, word):
        """Returns True if the given word is in the dictionary."""
        return word.lower() in self.words

# --------------------
# Score Manager
# --------------------
class ScoreManager:
    """Manages the player's score."""
    def __init__(self):
        self.score = 0

    def add_points(self, word):
        """Adds points based on the word length (with bonus for long words)."""
        base_points = len(word) * 10
        if len(word) >= 7:
            base_points *= 2
        self.score += base_points

    def reset(self):
        """Resets the score to zero."""
        self.score = 0

# --------------------
# Letter Class
# --------------------
class Letter:
    """Represents a falling letter."""
    def __init__(self, letter, lane, y=0, speed=LETTER_SPEED):
        self.letter = letter
        self.lane = lane  # lane index (0 to NUM_LANES - 1)
        self.y = y
        self.speed = speed
        self.x = lane * LANE_WIDTH + (LANE_WIDTH - LETTER_WIDTH) / 2

        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 30)
        self.surface = self.font.render(self.letter, True, BLACK)
        self.rect = pygame.Rect(self.x, self.y, LETTER_WIDTH, LETTER_HEIGHT)

    def update(self, dt):
        """Update the letter's position based on elapsed time."""
        self.y += self.speed * dt
        self.rect.y = int(self.y)

    def draw(self, screen):
        """Draw the letter with a background rectangle using its unique light color."""
        bg_color = LETTER_BG_COLORS.get(self.letter, "lightblue")
        bg_rect = pygame.Rect(self.x, self.y, LETTER_WIDTH, LETTER_HEIGHT)
        pygame.draw.rect(screen, bg_color, bg_rect)
        pygame.draw.rect(screen, BLUE, bg_rect, 2)
        screen.blit(
            self.surface,
            (
                self.x + (LETTER_WIDTH - self.surface.get_width()) / 2,
                self.y + (LETTER_HEIGHT - self.surface.get_height()) / 2
            )
        )

# --------------------
# Letter Spawner
# --------------------
class LetterSpawner:
    """
    Manages the spawning of letters.
    
    When the queue is empty, a new word is chosen from the dictionary,
    extra random letters are inserted, and the letter queue is refilled.
    """
    def __init__(self, dictionary_manager, spawn_interval=LETTER_SPAWN_INTERVAL):
        self.spawn_interval = spawn_interval
        self.last_spawn_time = pygame.time.get_ticks()
        self.dictionary_manager = dictionary_manager
        self.letter_queue = []
        self.current_word = ""

    def refill_letter_queue(self):
        """Refills the letter queue using a word from the dictionary."""
        if not self.dictionary_manager.words:
            return
        limited_words = list(self.dictionary_manager.words)[:405]
        if not limited_words:
            return
        self.current_word = random.choice(limited_words).upper()
        mixed_letters = list(self.current_word)
        num_extra_letters = random.randint(2, len(self.current_word))
        for _ in range(num_extra_letters):
            insert_pos = random.randint(0, len(mixed_letters))
            mixed_letters.insert(insert_pos, random.choice(ENGLISH_ALPHABET))
        self.letter_queue.extend(mixed_letters)

    def try_spawn(self):
        """
        Attempts to spawn a new letter if the spawn interval has passed.
        Returns a Letter object or None.
        """
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn_time >= self.spawn_interval:
            self.last_spawn_time = current_time
            if not self.letter_queue:
                self.refill_letter_queue()
            if self.letter_queue:
                letter_choice = self.letter_queue.pop(0)
                # Spawn letter in one of the inner lanes.
                lane = random.randint(1, NUM_LANES - 2)
                score_text_height = 50
                return Letter(letter_choice, lane, y=score_text_height)
        return None

# --------------------
# Player Class
# --------------------
class Player:
    """
    Represents the player who controls two lanes (left and right)
    and collects falling letters to build a word.
    """
    def __init__(self):
        self.left_lane = NUM_LANES // 2 - 1
        self.right_lane = self.left_lane + 1
        self.current_word = ""
        player_img_path = os.path.join(current_dir, "assets", "slova", "player.png")
        if os.path.exists(player_img_path):
            self.image = pygame.image.load(player_img_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (int(LANE_WIDTH), int(PLAYER_HEIGHT)))
        else:
            self.image = None
            print("Player image not found at:", player_img_path)

    @property
    def lanes(self):
        """Returns a list of lane indices where the player is located."""
        return [self.left_lane, self.right_lane]

    def move(self, direction):
        """Moves the player's lanes left (-1) or right (+1) if within bounds."""
        new_left = self.left_lane + direction
        new_right = self.right_lane + direction
        if new_left >= 0 and new_right < NUM_LANES:
            self.left_lane = new_left
            self.right_lane = new_right

    def catch_letter(self, letter):
        """
        If a falling letter collides with the player's lanes,
        add its letter to the player's current word.
        The left lane letter is prepended while the right lane letter is appended.
        """
        if letter.lane == self.left_lane:
            self.current_word = letter.letter + self.current_word
        elif letter.lane == self.right_lane:
            self.current_word = self.current_word + letter.letter

    def reset_shape(self):
        """Resets the player's collected word."""
        self.current_word = ""

    def draw(self, screen, font):
        """Draws the player's zones and displays the current word above them."""
        for lane in self.lanes:
            x = lane * LANE_WIDTH
            if self.image:
                screen.blit(self.image, (x, PLAYER_Y))
            else:
                rect = pygame.Rect(x, PLAYER_Y, LANE_WIDTH, PLAYER_HEIGHT)
                pygame.draw.rect(screen, GREEN, rect)
                pygame.draw.rect(screen, GREEN, rect, 2)
                text_surface = font.render("U", True, WHITE)
                screen.blit(
                    text_surface,
                    (
                        x + (LANE_WIDTH - text_surface.get_width()) / 2,
                        PLAYER_Y + (PLAYER_HEIGHT - text_surface.get_height()) / 2
                    )
                )
        word_font = pygame.font.SysFont("Arial", 24)
        word_surface = word_font.render(self.current_word, True, BLACK)
        center_x = (self.left_lane * LANE_WIDTH + self.right_lane * LANE_WIDTH + LANE_WIDTH) / 2
        screen.blit(word_surface, (center_x - word_surface.get_width() / 2, PLAYER_Y - 30))

# --------------------
# Game Class
# --------------------
class Game:
    """
    The main game class that initializes and runs the Pygame loop.
    It manages events, updates game objects, and handles rendering.
    """
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Word Builder")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.big_font = pygame.font.SysFont("Arial", 48)

        bg_image_path = os.path.join(current_dir, "assets", "slova", "slovaBGR.png")
        if os.path.exists(bg_image_path):
            self.bg_image = pygame.image.load(bg_image_path).convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.bg_image = None
            print("Background image not found at:", bg_image_path)

        self.dictionary_manager = DictionaryManager()
        self.score_manager = ScoreManager()
        self.player = Player()
        self.letters = []
        self.letter_spawner = LetterSpawner(self.dictionary_manager)

        self.lives = 3
        self.game_over = False
        self.message = ""

    def run(self):
        """Main game loop. Exits when the window is closed."""
        running = True
        while running:
            dt = self.clock.tick(FPS) / 16.0  # Normalize dt to roughly 60 FPS
            if self._handle_events():
                running = False

            if not self.game_over:
                self._update(dt)
            self._draw()
        pygame.quit()

    def _handle_events(self):
        """Process events from the event queue."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True

            if event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                if self.bg_image:
                    self.bg_image = pygame.transform.scale(self.bg_image, event.size)

            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_k:
                        return True
                    continue

                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._submit_word()
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.player.move(-1)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.player.move(1)
        return False

    def _update(self, dt):
        """Update the state of letters and check for collisions."""
        new_letter = self.letter_spawner.try_spawn()
        if new_letter:
            self.letters.append(new_letter)

        for letter in self.letters[:]:
            letter.update(dt)
            if letter.y > self.screen.get_height():
                self.letters.remove(letter)
            else:
                if (letter.lane in self.player.lanes and
                    letter.y + LETTER_HEIGHT >= PLAYER_Y and
                    letter.y <= PLAYER_Y + PLAYER_HEIGHT):
                    self.player.catch_letter(letter)
                    self.letters.remove(letter)

    def _submit_word(self):
        """Submit the player's current word and update score if valid.
           Lose one life if the word is invalid."""
        word = self.player.current_word.strip()
        if word:
            if self.dictionary_manager.is_valid_word(word):
                self.score_manager.add_points(word)
                self.message = f"'{word}' - valid word! +{len(word) * 10} points"
            else:
                self.lives -= 1
                self.message = f"'{word}' is not a valid word. You lost a life!"
                if self.lives <= 0:
                    self.game_over = True
                    self.message = ""
            self.player.reset_shape()

    def _draw(self):
        """Render all game elements on the screen."""
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill(BLACK)

        for i in range(1, NUM_LANES):
            x = i * LANE_WIDTH
            pygame.draw.line(self.screen, GREEN, (x, 0), (x, self.screen.get_height()), 2)

        for letter in self.letters:
            letter.draw(self.screen)

        self.player.draw(self.screen, self.font)

        score_surface = self.font.render(f"Score: {self.score_manager.score}", True, BLACK)
        self.screen.blit(score_surface, (10, 10))
        lives_surface = self.font.render(f"Lives: {self.lives}", True, BLACK)
        self.screen.blit(lives_surface, (10, 40))
        if self.message:
            msg_color = BLUE if "-" in self.message else RED
            message_surface = self.font.render(self.message, True, msg_color)
            self.screen.blit(message_surface, (10, 70))

        instructions = "Move: Left/Right arrows (or A/D). Confirm: Space/Enter."
        inst_surface = self.font.render(instructions, True, BLACK)
        self.screen.blit(inst_surface, (self.screen.get_width() // 2 - inst_surface.get_width() // 2, 0))

        if self.letter_spawner.current_word:
            word_surface = self.font.render(f"Current word: {self.letter_spawner.current_word}", True, BLACK)
            self.screen.blit(word_surface, (self.screen.get_width() // 2 - word_surface.get_width() // 2, inst_surface.get_height()))

        if self.game_over:
            go_surface = self.big_font.render("GAME OVER", True, RED)
            self.screen.blit(go_surface, ((self.screen.get_width() - go_surface.get_width()) / 2, self.screen.get_height() / 2))
            prompt_surface = self.font.render("Press K to exit", True, RED)
            self.screen.blit(prompt_surface, ((self.screen.get_width() - prompt_surface.get_width()) / 2, self.screen.get_height() / 2 + 50))

        pygame.display.flip()

# --------------------
# Main Entry Point
# --------------------
def main(parent=None):
    """
    Launch the Pygame game.
    If a parent is provided (from your main switchboard), run the game in a separate thread
    and use a dummy Toplevel to simulate modal behavior.
    """
    if parent:
        # Create a hidden Toplevel for modal waiting.
        window = tk.Toplevel(parent)
        window.withdraw()  # Hide the dummy window.
        def run_game():
            game = Game()
            game.run()
            window.destroy()  # Destroy dummy when game is over.
        threading.Thread(target=run_game).start()
        parent.wait_window(window)
    else:
        game = Game()
        game.run()

if __name__ == "__main__":
    main()
