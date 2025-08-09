import os
import json
import random
import tkinter as tk
from PIL import Image, ImageTk
import time

# --- Configuration and Constants ---
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    current_dir = os.getcwd()

# Fallback background image (ensure this file exists or update the path)
BACKGROUND_IMAGE = os.path.join(current_dir, "assets", "slova.png")

GRID_SIZE = 6
PAIRS = (GRID_SIZE * GRID_SIZE) // 2
CYRILLIC_LETTERS = 'АБВГДЂЕЖЗИЈКЛЉМНЊОПРСТЋУФХЦЧЏШ'

# Define a list of colors for the letter pairs.
colors = [
    "lightcoral", "palegreen", "lightskyblue", "lightyellow",
    "lightpink", "lightsalmon", "thistle", "powderblue",
    "lavender", "peachpuff", "honeydew", "mistyrose",
    "lightcyan", "plum", "moccasin", "wheat",
    "lemonchiffon", "aquamarine"
]
if len(colors) < PAIRS:
    raise ValueError("Not enough colors for all pairs.")

# Global variables to hold the game data.
selected_letters = []  # will be reinitialized for each game
letter_to_color = {}   # mapping letter -> color

# --- MemoryGame Class ---
class MemoryGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Memory")
        self.attempts = 0
        self.found_pairs = 0
        
        # Timer attributes
        self.start_time = None
        self.timer_running = False
        self.update_timer_id = None  # store the after() id

        # Main frame for the game board.
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack()

        # Set up the game board.
        self.setup_game()

        # Control frame at the bottom for status and buttons.
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(fill="x", pady=5)

        self.attempts_label = tk.Label(self.control_frame, text="Attempts: 0", font=("Helvetica", 14))
        self.attempts_label.pack(side="left", padx=10)

        self.timer_label = tk.Label(self.control_frame, text="Time: 0 s", font=("Helvetica", 14))
        self.timer_label.pack(side="left", padx=10)

        self.info_label = tk.Label(self.control_frame, text="", font=("Helvetica", 14), fg="blue")
        self.info_label.pack(side="left", padx=10)

        next_btn = tk.Button(self.control_frame, text="Next Game", font=("Helvetica", 12), command=self.reset_game)
        next_btn.pack(side="left", padx=10)

        close_btn = tk.Button(self.control_frame, text="Close", font=("Helvetica", 12), command=self.root.destroy)
        close_btn.pack(side="right", padx=10)

    def load_background(self):
        """
        Attempt to load a random background image from assets/backgrounds.
        If none found, fall back to BACKGROUND_IMAGE.
        """
        backgrounds_dir = os.path.join(current_dir, "assets", "backgrounds")
        bg_files = []
        if os.path.exists(backgrounds_dir):
            for f in os.listdir(backgrounds_dir):
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    bg_files.append(os.path.join(backgrounds_dir, f))
        if bg_files:
            chosen_bg = random.choice(bg_files)
        else:
            chosen_bg = BACKGROUND_IMAGE

        try:
            self.bg_photo = tk.PhotoImage(file=chosen_bg)
            self.bg_width = self.bg_photo.width()
            self.bg_height = self.bg_photo.height()
        except Exception as e:
            print("Error loading background:", e)
            self.bg_width, self.bg_height = 600, 600
            self.bg_photo = None

    def setup_game(self):
        """Set up the canvas, background, and game board with shuffled letters."""
        self.load_background()
        self.canvas = tk.Canvas(self.main_frame, width=self.bg_width, height=self.bg_height)
        self.canvas.pack()

        # Draw the background image if available.
        if self.bg_photo:
            self.canvas.create_image(0, 0, anchor='nw', image=self.bg_photo)

        self.buttons = {}
        self.clicked = []
        self.cell_size = min(self.bg_width // GRID_SIZE, self.bg_height // GRID_SIZE)
        self.offset_x = 2
        self.offset_y = 2

        # Initialize game board letters and assign colors.
        global selected_letters, letter_to_color
        selected_letters = random.sample(CYRILLIC_LETTERS, PAIRS) * 2
        random.shuffle(selected_letters)

        unique_letters = list(set(selected_letters))
        random.shuffle(colors)
        letter_to_color = {}
        for i, letter in enumerate(unique_letters):
            letter_to_color[letter] = colors[i]

        # Create the grid buttons.
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                idx = i * GRID_SIZE + j
                letter = selected_letters[idx]
                btn = tk.Button(
                    self.canvas, text="", width=3, height=1,
                    font=("Helvetica", 32, "bold"),
                    bg="beige", command=lambda index=idx: self.on_button_click(index)
                )
                x = self.offset_x + j * self.cell_size + self.cell_size // 2
                y = self.offset_y + i * self.cell_size + self.cell_size // 2
                self.canvas.create_window(x, y, window=btn)
                self.buttons[idx] = {"button": btn, "letter": letter}

    def start_timer(self):
        if not self.timer_running:
            self.start_time = time.time()
            self.timer_running = True
            self.update_timer()

    def update_timer(self):
        if self.timer_running:
            elapsed = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Time: {elapsed} s")
            self.update_timer_id = self.root.after(1000, self.update_timer)

    def stop_timer(self):
        if self.timer_running:
            self.timer_running = False
            if self.update_timer_id:
                self.root.after_cancel(self.update_timer_id)
                self.update_timer_id = None

    def on_button_click(self, idx):
        """Handle button clicks, reveal letter and check for match."""
        if self.start_time is None:
            self.start_timer()

        if len(self.clicked) == 2:
            return  # Prevent clicking more than two buttons at once.

        btn_data = self.buttons[idx]
        button = btn_data["button"]
        letter = btn_data["letter"]
        color = letter_to_color[letter]

        button.config(text=letter, bg=color, state="disabled")
        self.clicked.append(idx)

        if len(self.clicked) == 2:
            self.attempts += 1
            self.attempts_label.config(text=f"Attempts: {self.attempts}")
            x1, x2 = self.clicked
            l1 = self.buttons[x1]["letter"]
            l2 = self.buttons[x2]["letter"]
            if l1 == l2:
                self.root.after(500, lambda: self.remove_matched(x1, x2))
            else:
                self.root.after(500, lambda: self.hide_letters(x1, x2))

    def remove_matched(self, x1, x2):
        """Remove matched buttons from the board."""
        self.buttons[x1]["button"].destroy()
        self.buttons[x2]["button"].destroy()
        self.clicked = []
        self.found_pairs += 1

        if self.found_pairs == PAIRS:
            self.stop_timer()
            self.info_label.config(text="Great!")

    def hide_letters(self, x1, x2):
        """Hide letters for unmatched pair and re-enable buttons."""
        for i in (x1, x2):
            self.buttons[i]["button"].config(text="", bg="beige", state="normal")
        self.clicked = []

    def reset_game(self):
        self.stop_timer()
        self.start_time = None
        self.timer_running = False
        self.attempts = 0
        self.found_pairs = 0
        self.attempts_label.config(text="Attempts: 0")
        self.timer_label.config(text="Time: 0 s")
        self.info_label.config(text="")
        # Clear the old game board.
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.setup_game()

# --- Main Function for Memory Game ---
def main(parent=None):
    """
    Launch the Memory Game.
      - If 'parent' is None, run as a standalone application.
      - If 'parent' is provided, run modally in a Toplevel window.
    """
    if parent is None:
        # Standalone mode.
        root = tk.Tk()
        root.title("Memory")
        root.geometry("800x650")
        root.resizable(True, True)
        MemoryGame(root)
        root.mainloop()
    else:
        # Modal mode.
        top = tk.Toplevel(parent)
        top.title("Memory")
        top.geometry("600x650")
        top.resizable(True, True)
        MemoryGame(top)
        top.grab_set()
        top.focus_set()
        top.transient(parent)
        top.wait_window(top)

if __name__ == "__main__":
    main()
