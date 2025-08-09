import tkinter as tk
import random
import copy
import os

# For generating circular backgrounds behind images
from PIL import Image, ImageTk, ImageDraw

# =====================
# Configuration
# =====================

PASTEL_COLORS = [
    "lightblue", "lightgreen", "lightyellow", "lightpink", "lavender",
    "#FFDAB9", "#E0FFFF", "#F0E68C"
]

# =====================
# Puzzle Generation
# =====================

def generate_complete_board(dimension):
    """
    Generates a complete board (a Latin square) of the given dimension.
    The board is represented as a 2D list of integers in 1..dimension.
    """
    board = [[0] * dimension for _ in range(dimension)]
    symbols = list(range(1, dimension + 1))

    def is_valid(board, r, c, num):
        # Check row.
        if num in board[r]:
            return False
        # Check column.
        for i in range(dimension):
            if board[i][c] == num:
                return False
        return True

    def backtrack(cell=0):
        if cell == dimension * dimension:
            return True  # Board filled
        r = cell // dimension
        c = cell % dimension
        if board[r][c] != 0:
            return backtrack(cell + 1)
        nums = symbols[:]
        random.shuffle(nums)
        for num in nums:
            if is_valid(board, r, c, num):
                board[r][c] = num
                if backtrack(cell + 1):
                    return True
                board[r][c] = 0
        return False

    backtrack()
    return board

def generate_puzzle(dimension):
    """
    Generates a complete solution board and then removes some cells to form the puzzle.
    Returns (puzzle, solution).
    """
    solution = generate_complete_board(dimension)
    puzzle = copy.deepcopy(solution)

    num_cells = dimension * dimension
    # Remove roughly half of the cells
    num_remove = num_cells // 2
    cells = [(r, c) for r in range(dimension) for c in range(dimension)]
    random.shuffle(cells)
    for i in range(num_remove):
        r, c = cells[i]
        puzzle[r][c] = 0  # 0 represents a blank cell
    return puzzle, solution

# =====================
# Emoji (now PNG) Sudoku Game
# =====================

class EmojiSudoku:
    def __init__(self, root):
        self.root = root
        self.root.title("Судоку")
        # Make sure the window is resizable
        self.root.resizable(True, True)
        self.puzzle_count = 0  # Counts how many puzzles have been generated

        # Frame to choose board size.
        self.dimension_frame = tk.Frame(self.root)
        self.dimension_frame.pack(pady=5)
        tk.Label(self.dimension_frame, text="Изабери величину: ").pack(side=tk.LEFT)

        self.size_var = tk.IntVar(value=3)
        tk.Radiobutton(
            self.dimension_frame,
            text="3x3",
            variable=self.size_var,
            value=3,
            command=self.setup_game
        ).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(
            self.dimension_frame,
            text="4x4",
            variable=self.size_var,
            value=4,
            command=self.setup_game
        ).pack(side=tk.LEFT)

        # Frame for the board.
        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack(pady=10)

        # Control buttons.
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(pady=5)
        self.check_button = tk.Button(
            self.control_frame,
            text="Провери",
            command=self.check_solution
        )
        self.check_button.pack(side=tk.LEFT, padx=5)
        self.next_button = tk.Button(
            self.control_frame,
            text="Следећа игра",
            command=self.next_puzzle
        )
        self.next_button.pack(side=tk.LEFT, padx=5)
        self.next_button.config(state=tk.DISABLED)

        self.status_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.status_label.pack(pady=5)

        # Setup the first game.
        self.setup_game()

    def setup_game(self):
        # Clear any existing board.
        for widget in self.board_frame.winfo_children():
            widget.destroy()

        self.dimension = self.size_var.get()
        self.symbols = list(range(1, self.dimension + 1))

        # Generate a new puzzle.
        self.puzzle, self.solution = generate_puzzle(self.dimension)
        # Copy puzzle to board_values (the mutable state that the user changes).
        self.board_values = [row[:] for row in self.puzzle]

        # 1) Load the base symbol images from local folder (e.g. assets/images/3 or assets/images/4).
        #    Store them in a dict: {1: PIL.Image, 2: PIL.Image, ...}
        self.base_symbol_images = {}
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            current_dir = os.getcwd()

        for num in self.symbols:
            image_dir = os.path.join(current_dir, "assets", "images", f"{self.dimension}")
            path = os.path.join(image_dir, f"{num}.png")
            img = Image.open(path).convert("RGBA")
            self.base_symbol_images[num] = img

        # 2) Create a color mapping for each symbol using pastel colors.
        shuffled_colors = random.sample(PASTEL_COLORS, len(self.symbols))
        self.color_map = {}
        for i, num in enumerate(self.symbols):
            self.color_map[num] = shuffled_colors[i]
        # For blank cells:
        self.color_map[0] = "white"

        # 3) Create button widgets and store references to their PhotoImages.
        self.buttons = []
        self.cell_photos = [[None for _ in range(self.dimension)] for _ in range(self.dimension)]

        for r in range(self.dimension):
            row_buttons = []
            for c in range(self.dimension):
                value = self.board_values[r][c]
                cell_image = self.create_cell_image(value)
                self.cell_photos[r][c] = cell_image

                btn = tk.Button(
                    self.board_frame,
                    image=cell_image,
                    bd=0,                 # no border
                    highlightthickness=0, # no highlight
                    command=lambda rr=r, cc=c: self.cycle_symbol(rr, cc)
                )
                btn.grid(row=r, column=c, padx=2, pady=2)

                if value != 0:  # Pre-filled cell => disable
                    btn.config(state="disabled", disabledforeground="black")

                row_buttons.append(btn)
            self.buttons.append(row_buttons)

        self.status_label.config(text="Кликните на дугме да промените слику.")
        self.next_button.config(state=tk.DISABLED)

    def create_cell_image(self, value):
        """
        Generate a circular background in the color for `value`,
        and (if value != 0) paste the corresponding symbol image in the center.
        Returns a Tk-compatible PhotoImage.
        """
        size = 160  # total button size
        radius = 80  # half of size, for a circle

        # 1) Create a blank RGBA image.
        circle_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))

        # 2) Draw a circle with the pastel color.
        draw = ImageDraw.Draw(circle_img)
        color = self.color_map[value]
        draw.ellipse((0, 0, size, size), fill=color)

        # 3) If not blank, paste the symbol image in the center.
        if value != 0:
            symbol_img = self.base_symbol_images[value]
            sx, sy = symbol_img.size
            off_x = (size - sx) // 2
            off_y = (size - sy) // 2
            circle_img.alpha_composite(symbol_img, (off_x, off_y))

        # Convert to a PhotoImage for Tkinter.
        return ImageTk.PhotoImage(circle_img)

    def cycle_symbol(self, r, c):
        """
        When a blank cell is clicked, cycle through blank (0) plus any unused number in the row/col.
        """
        current = self.board_values[r][c]

        # Collect used symbols from row and col.
        used = set()
        for j in range(self.dimension):
            if j != c:
                used.add(self.board_values[r][j])
        for i in range(self.dimension):
            if i != r:
                used.add(self.board_values[i][c])

        # Valid choices: blank (0) plus any number not already used.
        valid_choices = [0] + [num for num in self.symbols]# if num not in used]

        # Cycle to the next valid choice.
        if current in valid_choices:
            idx = valid_choices.index(current)
            next_val = valid_choices[(idx + 1) % len(valid_choices)]
        else:
            next_val = valid_choices[0]

        self.board_values[r][c] = next_val

        # Update the button image.
        new_image = self.create_cell_image(next_val)
        self.cell_photos[r][c] = new_image  # keep a reference
        self.buttons[r][c].config(image=new_image)

    def check_solution(self):
        # Check rows.
        for row in self.board_values:
            if sorted(row) != self.symbols:
                self.status_label.config(text="Није исправно решено.")
                return
        
        # Check columns.
        for c in range(self.dimension):
            col = [self.board_values[r][c] for r in range(self.dimension)]
            if sorted(col) != self.symbols:
                self.status_label.config(text="Није исправно решено.")
                return
        
        self.status_label.config(text="Честитамо! Решили сте.")
        self.next_button.config(state=tk.NORMAL)

    def next_puzzle(self):
        """Generate a new puzzle."""
        self.puzzle_count += 1
        self.setup_game()

def main(parent=None):
    """
    Launches the Emoji (PNG) Sudoku game. 
    - If 'parent' is None, run standalone with its own Tk root.
    - If 'parent' is a Tk widget (e.g. from the main launcher), open a modal Toplevel.
    """
    if parent is None:
        # Standalone mode.
        root = tk.Tk()
        EmojiSudoku(root)
        root.mainloop()
    else:
        # Modal mode.
        top = tk.Toplevel(parent)
        top.resizable(True, True)  # Ensure the window is resizable/maximizable.
        top.grab_set()
        top.focus_set()
        # Do not use transient() if you want the maximize button to appear.
        # If you still need a modal look, you can keep grab_set().
        EmojiSudoku(top)
        top.wait_window()

if __name__ == "__main__":
    main()
