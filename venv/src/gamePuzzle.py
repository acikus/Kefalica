import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import random
import os
import tempfile

class PuzzleGameApp(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master.title("Puzzle")
        self.pack(expand=True, fill=tk.BOTH)
        
        # Variables for difficulty and custom image
        self.level_var = tk.StringVar(value='easy')
        self.custom_image_path = None

        # Puzzle state variables
        self.tiles = []
        self.buttons = {}
        self.images = []
        self.current_positions = []
        self.correct_positions = []
        self.first_click = None
        self.move_count = 0
        self.rows = 0
        self.columns = 0

        # Main frames: left for controls, right for puzzle
        self.left_frame = tk.Frame(self)
        self.left_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=10)
        self.right_frame = tk.Frame(self)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Make the right frame expand
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Build the left control panel
        self.build_control_panel()

    def build_control_panel(self):
        # Title
        tk.Label(self.left_frame, text="Choose difficulty", font=('Arial', 24)).pack(pady=5)

        # Difficulty radio buttons
        rb_easy = tk.Radiobutton(
            self.left_frame,
            text="EASY",
            font=('Arial', 20),
            variable=self.level_var,
            value='easy'
        )
        rb_easy.pack(pady=2)

        rb_hard = tk.Radiobutton(
            self.left_frame,
            text="HARD",
            font=('Arial', 20),
            variable=self.level_var,
            value='hard'
        )
        rb_hard.pack(pady=2)

        # Custom image label
        self.custom_image_label = tk.Label(
            self.left_frame, 
            text="No custom image selected",
            font=('Arial', 12)
        )
        self.custom_image_label.pack(pady=5)

        # Button to load a custom image
        btn_load_image = tk.Button(
            self.left_frame,
            text="Load custom image",
            font=('Arial', 14),
            command=self.load_custom_image
        )
        btn_load_image.pack(pady=5)

        # Button to start (or restart) the puzzle
        btn_start_puzzle = tk.Button(
            self.left_frame,
            text="Start puzzle",
            font=('Arial', 14),
            command=self.start_puzzle
        )
        btn_start_puzzle.pack(pady=5)

        # Status label
        self.status_label = tk.Label(
            self.left_frame, 
            text="", 
            font=('Arial', 12), 
            wraplength=200, 
            justify="left"
        )
        self.status_label.pack(anchor="w", pady=5)

        # Move counter
        self.move_counter_label = tk.Label(
            self.left_frame, 
            text="Moves: 0",
            font=('Arial', 12)
        )
        self.move_counter_label.pack(anchor="w", pady=5)

        # Button: Next Image
        self.next_button = tk.Button(
            self.left_frame,
            text="Next image",
            font=('Arial', 14),
            command=self.load_new_image,
            state=tk.DISABLED  # Disabled until a puzzle is started
        )
        self.next_button.pack(pady=5)

        # Close button
        btn_close = tk.Button(
            self.left_frame,
            text="Close",
            font=('Arial', 14),
            command=self.master.destroy
        )
        btn_close.pack(pady=5)

    def load_custom_image(self):
        file_path = filedialog.askopenfilename(
            title="Choose image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")]
        )
        if not file_path:
            return

        try:
            img = Image.open(file_path)
        except Exception as e:
            self.custom_image_label.config(text=f"Cannot open image:\n{e}")
            return

        width, height = img.size
        if width != height:
            self.custom_image_label.config(text="Please choose a square image.")
            return

        if width > 800:
            img = img.resize((800, 800), Image.Resampling.LANCZOS)

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        try:
            img.save(temp_file, format="PNG")
        except Exception as e:
            self.custom_image_label.config(text=f"Cannot save custom image:\n{e}")
            temp_file.close()
            return
        temp_file.close()

        self.custom_image_path = temp_file.name
        filename = os.path.basename(file_path)
        self.custom_image_label.config(text=f"Selected image: {filename}")

    def start_puzzle(self):
        # Clear any previous puzzle
        for btn in self.buttons.values():
            btn.destroy()
        self.buttons.clear()
        self.images.clear()
        self.tiles.clear()

        self.first_click = None
        self.move_count = 0
        self.update_move_counter()

        if self.load_images():
            self.create_puzzle()
            self.status_label.config(text="New puzzle loaded. Make your move.")
            self.next_button.config(state=tk.NORMAL)
        else:
            self.status_label.config(text="Error: Cannot load image.")
            self.next_button.config(state=tk.DISABLED)

    def load_images(self):
        if self.custom_image_path and os.path.exists(self.custom_image_path):
            try:
                self.original_image = Image.open(self.custom_image_path)
            except Exception as e:
                print(f"Error loading custom image: {e}")
                return False
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            image_folder = os.path.join(current_dir, "assets", "puzzle")
            image_files = [
                os.path.join(image_folder, f)
                for f in os.listdir(image_folder)
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
            ]
            if not image_files:
                return False
            self.original_image = Image.open(random.choice(image_files))

        level = self.level_var.get()
        if level == 'easy':
            self.rows = 3
            self.columns = 4
        elif level == 'hard':
            self.rows = 4
            self.columns = 6
        else:
            self.status_label.config(text="Unknown difficulty level.")
            return False

        tile_width = self.original_image.size[0] // self.columns
        tile_height = self.original_image.size[1] // self.rows
        self.original_image = self.original_image.resize(
            (tile_width * self.columns, tile_height * self.rows)
        )

        self.tiles = []
        self.correct_positions = []
        self.current_positions = []

        for row in range(self.rows):
            for col in range(self.columns):
                x0 = col * tile_width
                y0 = row * tile_height
                x1 = x0 + tile_width
                y1 = y0 + tile_height
                tile = self.original_image.crop((x0, y0, x1, y1))
                self.tiles.append(tile)

        self.correct_positions = list(range(len(self.tiles)))
        self.current_positions = list(self.correct_positions)
        random.shuffle(self.current_positions)

        return True

    def create_puzzle(self):
        self.images = []
        self.buttons = {}
        for idx, pos in enumerate(self.current_positions):
            row = idx // self.columns
            col = idx % self.columns
            img = ImageTk.PhotoImage(self.tiles[pos])
            self.images.append(img)
            button = tk.Button(
                self.right_frame,
                image=img,
                command=lambda i=idx: self.on_tile_click(i)
            )
            button.grid(row=row, column=col, padx=1, pady=1)
            self.buttons[idx] = button

    def on_tile_click(self, idx):
        if all(button["state"] == tk.DISABLED for button in self.buttons.values()):
            return

        if self.first_click is None:
            self.first_click = idx
            self.buttons[idx].config(borderwidth=4, relief=tk.SOLID)
        else:
            self.swap_tiles(self.first_click, idx)
            self.first_click = None
            self.move_count += 1
            self.update_move_counter()

            if self.check_solution():
                self.status_label.config(
                    text="Congratulations! The puzzle is solved.\nClick 'Next image' for a new puzzle."
                )
                for btn in self.buttons.values():
                    btn.config(state=tk.DISABLED)

    def swap_tiles(self, idx1, idx2):
        self.current_positions[idx1], self.current_positions[idx2] = (
            self.current_positions[idx2], 
            self.current_positions[idx1]
        )
        self.images[idx1], self.images[idx2] = self.images[idx2], self.images[idx1]
        self.buttons[idx1].config(image=self.images[idx1], relief=tk.RAISED)
        self.buttons[idx2].config(image=self.images[idx2], relief=tk.RAISED)

    def check_solution(self):
        return self.current_positions == self.correct_positions

    def update_move_counter(self):
        self.move_counter_label.config(text=f"Moves: {self.move_count}")

    def load_new_image(self):
        for btn in self.buttons.values():
            btn.destroy()
        self.buttons.clear()
        self.images.clear()
        self.tiles.clear()

        self.first_click = None
        self.move_count = 0
        self.update_move_counter()

        old_custom_path = self.custom_image_path
        self.custom_image_path = None

        if self.load_images():
            self.create_puzzle()
            self.status_label.config(text="Loading new puzzle. Make your move.")
        else:
            self.status_label.config(text="Error: Cannot load image.")

        # Restore custom image path so user can go back to the custom puzzle if needed.
        self.custom_image_path = old_custom_path

def main(parent=None):
    """
    If parent is None, creates a main Tk window.
    Otherwise, creates a Toplevel window on top of parent.
    In both cases, the window is made resizable so that if it is minimized,
    it can be maximized again.
    """
    if parent is None:
        root = tk.Tk()
        root.title("Puzzle")
        root.resizable(True, True)
        app = PuzzleGameApp(master=root)
        root.mainloop()
    else:
        top = tk.Toplevel(parent)
        top.title("Puzzle")
        top.resizable(True, True)
        app = PuzzleGameApp(master=top)
        top.wait_window(top)

if __name__ == "__main__":
    main()
