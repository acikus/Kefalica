import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import importlib
import os

# --- Import game modules ---
import gameWords
import gameSludoku
import gameRecenice
import gamePuzzle
import gamePogodi
import gameProgramer
import gameMemory      # Memory game module with dual-mode (Tk/Toplevel) support
import gameMathador
import gameColoring
import gameBasicOps
import gameAsocijacije
import gameIQ
import gameKocke
import gameSort
import gamePositions
import gameSnake
import about
import gameKefalica

# --- Custom Transparent Button ---
class TransparentButton(tk.Canvas):
    def __init__(self, parent, text="", command=None, font=("Arial", 12),
                 width=200, height=60, bg=None, bg_image=None,
                 activefill="blue", fg="black", **kwargs):
        """
        A custom button widget using Canvas that simulates transparency and can have an image background.
        """
        if bg is None:
            bg = parent.cget("bg")
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=0, bd=0, **kwargs)
        
        self.command = command
        self.activefill = activefill
        self.default_fg = fg
        self.font = font
        self.text = text
        self.width = width
        self.height = height
        self.enabled = True  # Button is enabled by default.

        # Keep a reference to the background image if provided.
        self.bg_image = bg_image
        if self.bg_image:
            self.create_image(0, 0, image=self.bg_image, anchor="nw")
        
        # Create the text centered in the canvas.
        self.text_id = self.create_text(width // 2, height // 2, text=self.text, font=self.font, fill=self.default_fg)

        # Bind events for clicking and hover.
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_click(self, event):
        if not self.enabled:
            return  # Ignore clicks when disabled.
        if self.command:
            self.command()

    def on_enter(self, event):
        if self.enabled:
            self.itemconfig(self.text_id, fill=self.activefill)

    def on_leave(self, event):
        if self.enabled:
            self.itemconfig(self.text_id, fill=self.default_fg)

    def disable(self):
        """Disable this button."""
        self.enabled = False
        self.itemconfig(self.text_id, fill="gray")

    def enable(self):
        """Enable this button."""
        self.enabled = True
        self.itemconfig(self.text_id, fill=self.default_fg)

# Example function to load an image for the button
def load_button_image(image_path, width, height):
    try:
        pil_image = Image.open(image_path)
        pil_image = pil_image.resize((width, height), Image.LANCZOS)
        return ImageTk.PhotoImage(pil_image)
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None

# --- Game Launch Functions ---
def launch_basicops(parent):
    gameBasicOps.main(parent=parent)

def launch_asocijacije(parent):
    gameAsocijacije.main(parent=parent)

def launch_coloring(parent):
    gameColoring.main(parent=parent)

def launch_emoji_sudoku(parent):
    gameSludoku.main(parent=parent)

def launch_words(parent):
    gameWords.main(parent=parent)

def launch_recenice_game(parent):
    gameRecenice.main(parent=parent)

def launch_puzzle(parent):
    gamePuzzle.main(parent=parent)

def launch_pogodi(parent):
    gamePogodi.main(parent=parent)

def launch_program(parent):
    gameProgramer.main(parent=parent)

def launch_memory_game(parent):
    # This will call the memory game in modal mode. Ensure that
    # gameMemory.main() checks for a parent and creates a Toplevel accordingly.
    gameMemory.main(parent=parent)

def launch_shooter(parent):
    gameMathador.main(parent=parent)

def launch_kocke_game(parent):
    gameKocke.main(parent=parent)
    
def launch_iq_game(parent):
    gameIQ.main(parent=parent)

def launch_sort_game(parent):
    gameSort.main(parent=parent)

def launch_position_game(parent):
    gamePositions.main(parent=parent)

def launch_snake_game(parent):
    gameSnake.main(parent=parent)

def launch_main_game(self):
    gameKefalica.main(parent=self)


def launch_about(parent):
    about.main(parent=parent)

def launch_game(game_module_name, parent):
    """
    Generic launcher that imports the given game module and ensures that 
    the game window remains on top of the main form.
    """
    if parent.game_running:
        return  # Prevent launching multiple games simultaneously.

    try:
        game_module = importlib.import_module(game_module_name)
        modal_window = tk.Toplevel(parent)
        modal_window.transient(parent)  # Keep the game window above the main window
        modal_window.grab_set()  # Prevent interaction with main window until closed
        modal_window.focus_set()  # Ensure the game window receives focus
        parent.game_running = True  # Mark a game as running

        # Set a protocol to reset the flag when the window is closed
        def on_game_close():
            parent.game_running = False
            parent.enable_game_buttons()  # Re-enable the buttons
            modal_window.destroy()

        modal_window.protocol("WM_DELETE_WINDOW", on_game_close)

        parent.disable_game_buttons()  # Disable game buttons while a game is open
        game_module.main(parent=modal_window)  # Start the game
        modal_window.wait_window(modal_window)  # Wait until game closes

    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch {game_module_name}: {e}")
        parent.game_running = False  # Reset flag in case of an error
        parent.enable_game_buttons()


# --- Main Window Class ---
class MainGameLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kefalica")
        self.state('zoomed')
        self.resizable(False, False)
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.bg_image_container = [None]
        self.original_bg = None  # To store the original PIL image

        # This flag indicates if a game is currently running.
        self.game_running = False
        # Store references to game buttons (not including exit button)
        self.game_buttons = []

        self.load_background()
        self.create_widgets()

    def exit_app(self):
        self.quit()
        self.destroy()

    def load_background(self):
        image_path = os.path.join(self.current_dir, "assets", "MainBack.jpg")
        try:
            self.original_bg = Image.open(image_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load background image: {e}")

    def disable_game_buttons(self):
        for btn in self.game_buttons:
            try:
                if btn.winfo_exists():
                    btn.disable()
            except tk.TclError:
                pass

    def enable_game_buttons(self):
        for btn in self.game_buttons:
            try:
                if btn.winfo_exists():
                    btn.enable()
            except tk.TclError:
                pass

    def run_game(self, game_func):
        """
        Disables all game buttons, runs the game, and re-enables buttons afterward.
        Assumes the game runs in a modal fashion (blocking until closed).
        """
        if self.game_running:
            return
        self.game_running = True
        self.disable_game_buttons()
        try:
            game_func()
        finally:
            # Schedule re-enabling after a short delay (100 ms)
            self.after(100, self._reenable_game_buttons)

    def _reenable_game_buttons(self):
        if self.winfo_exists():
            self.enable_game_buttons()
            self.game_running = False

 

    def create_widgets(self):
        # --- Create and place the background label ---
        self.background_label = tk.Label(self)
        self.background_label.grid(row=0, column=0, rowspan=10, columnspan=4, sticky="nsew")
        self.bind("<Configure>", self.on_resize)

        for r in range(10):
            self.grid_rowconfigure(r, weight=1)
        for c in range(4):
            self.grid_columnconfigure(c, weight=1)

        # --- Parameters for Transparent Buttons ---
        BTN_WIDTH_PX = 260
        BTN_HEIGHT_PX = 60
        BTN_FONT = ("Arial", 18)

        button_bg_image = load_button_image(os.path.join(self.current_dir, "assets", "button_bg.jpg"),
                                            BTN_WIDTH_PX, BTN_HEIGHT_PX)
        # Each tuple: (Button Text, game launch function, Row, Column)
        buttons_info = [
            ("Guess Who I Am", lambda: self.run_game(lambda: launch_pogodi(self)), 1, 0),
            ("Memory", lambda: self.run_game(lambda: launch_memory_game(self)), 1, 1),
            ("Mathador", lambda: self.run_game(lambda: launch_shooter(self)), 1, 2),
            ("Associations", lambda: self.run_game(lambda: launch_asocijacije(self)), 1, 3),
            ("Coloring", lambda: self.run_game(lambda: launch_coloring(self)), 2, 0),
            ("Programmer", lambda: self.run_game(lambda: launch_program(self)), 2, 1),
            ("Sudoku", lambda: self.run_game(lambda: launch_emoji_sudoku(self)), 2, 2),
            ("Words", lambda: self.run_game(lambda: launch_words(self)), 2, 3),
            ("Puzzle", lambda: self.run_game(lambda: launch_puzzle(self)), 3, 0),
            ("Missing Letters", lambda: self.run_game(lambda: launch_recenice_game(self)), 3, 1),
            ("Add and Subtract", lambda: self.run_game(lambda: launch_basicops(self)), 3, 2),
            ("Kefalica", lambda: self.run_game(lambda: launch_main_game(self)), 3, 3),
            ("Dice", lambda: self.run_game(lambda: launch_kocke_game(self)), 4, 1),
            ("Sorting", lambda: self.run_game(lambda: launch_sort_game(self)), 4, 2),
            ("Connect", lambda: self.run_game(lambda: launch_position_game(self)), 4, 3),
            ("Snakes and Ladders", lambda: self.run_game(lambda: launch_snake_game(self)), 4, 0)

        ]

        # Create game buttons and store references.
        for text, command, row, col in buttons_info:
            btn = TransparentButton(
                self,
                text=text,
                command=command,
                font=BTN_FONT,
                width=BTN_WIDTH_PX,
                height=BTN_HEIGHT_PX,
                bg="lightyellow",
                bg_image=button_bg_image,
                activefill="yellow",
                fg="white"
            )
            btn.grid(row=row+2, column=col, padx=10, pady=10)
            self.game_buttons.append(btn)
        about_btn = TransparentButton(
            self,
            text="About Kefalica",
            command=lambda: launch_about(self),
            font=BTN_FONT,
            width=BTN_WIDTH_PX,
            height=BTN_HEIGHT_PX,
            bg="lightyellow",
            bg_image=button_bg_image,
            activefill="yellow",
            fg="white"
        )
        about_btn.grid(row=9, column=0, padx=10, pady=10, sticky="e")
        # --- Exit Button (remains enabled) ---
        exit_btn = TransparentButton(
            self,
            text="Exit",
            command=self.exit_app,
            font=BTN_FONT,
            width=BTN_WIDTH_PX,
            height=BTN_HEIGHT_PX,
            bg="lightyellow",
            bg_image=button_bg_image,
            activefill="yellow",
            fg="white"
        )
        exit_btn.grid(row=9, column=3, padx=10, pady=10, sticky="e")
# --- Transparent IQ Button (Top-Right Half) ---
# Bind click event to top-right area of the background image
        self.background_label.bind("<Button-1>", self.check_iq_click_zone)





    def check_iq_click_zone(self, event):
        # Get full width of the window
        win_width = self.winfo_width()
        
        # If click is in top-right half and within top 120 pixels
        if event.x >= win_width // 2 and event.y <= 120:
            self.run_game(lambda: launch_iq_game(self))

    def on_resize(self, event):
        if event.widget == self and self.original_bg:
            width, height = event.width, event.height
            resized_bg = self.original_bg.resize((width, height), Image.LANCZOS)
            new_bg = ImageTk.PhotoImage(resized_bg)
            self.background_label.config(image=new_bg)
            self.bg_image_container[0] = new_bg

# --- Main Execution ---
def main():
    app = MainGameLauncher()
    app.mainloop()

if __name__ == "__main__":
    main()
