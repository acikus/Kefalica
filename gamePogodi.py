import os
import json
import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
#import time

"""
This version of the sub-game does not load all 60MB of images into memory at once.
Instead, it only indexes each image's file path. When a random image is chosen,
it loads that single file from disk ("lazy loading")—improving startup speed and
memory usage.

We also wrap the game in a `main(parent=None)` function so it can be run either
stand-alone or modally from the main Tkinter launcher.
"""

try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    current_dir = os.getcwd()

# Define paths for assets
TRANSLATED_FILE_PATH = os.path.join(current_dir, "assets", "translated_labels.json")
DATASET_PATH = os.path.join(current_dir, "assets", "dataset", "dataset")
BACKGROUND_IMAGE_PATH = os.path.join(current_dir, "assets", "pogodiBGR.png")


def index_animals151_data_with_translation(dataset_path, translated_labels):
    """
    Indexes the dataset folders but does NOT load all images at once.
    Instead, we store only the file paths and label indices.

    Returns:
        image_paths (list of str): Paths to all discovered images.
        labels (list of int): Label index (class) for each image path.
        label_names (list of str): Class names, possibly translated.
    """
    image_paths = []
    labels = []
    label_names = []

    # Go through each class folder
    class_folders = [
        d for d in os.listdir(dataset_path)
        if os.path.isdir(os.path.join(dataset_path, d))
    ]
    # Sort to maintain a stable ordering if needed
    class_folders.sort()

    for label_idx, class_name in enumerate(class_folders):
        class_path = os.path.join(dataset_path, class_name)
        translated_name = translated_labels.get(class_name, class_name)
        label_names.append(translated_name)

        # Index every image path in the class folder
        for image_name in os.listdir(class_path):
            image_path = os.path.join(class_path, image_name)
            if os.path.isfile(image_path):
                image_paths.append(image_path)
                labels.append(label_idx)

    return image_paths, labels, label_names


class GuessingGame:
    """
    A guessing game with a large dataset of images.
    We use lazy loading of images to reduce startup time and memory usage.
    """

    # Serbian Cyrillic alphabet letters (30 letters)
    SERBIAN_CYRILLIC = [
        'А', 'Б', 'В', 'Г', 'Д', 'Ђ', 'Е', 'Ж', 'З', 'И',
        'Ј', 'К', 'Л', 'Љ', 'М', 'Н', 'Њ', 'О', 'П', 'Р',
        'С', 'Т', 'Ћ', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Џ', 'Ш'
    ]

    def __init__(self, root, parent=None):
        """
        :param root: The Tk or Toplevel window in which this game runs.
        :param parent: If called modally from a parent, we can store it here (unused otherwise).
        """
        self.root = root
        self.parent = parent
        self.root.title("Погоди ко сам")
        self.root.geometry("1024x768")
        # Allow the window to be resized so that it can be maximized after minimizing
        self.root.resizable(True, True)

        # Load background image.
        self.bg_image = Image.open(BACKGROUND_IMAGE_PATH)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        # Create a canvas for the background and use `place` to fill the window.
        self.canvas = tk.Canvas(self.root, width=1024, height=768)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
        self.canvas.lower("all")  # Lower the canvas behind all other widgets

        # Load translated labels from JSON
        try:
            with open(TRANSLATED_FILE_PATH, "r", encoding="utf-8") as file:
                translated_labels = json.load(file)
        except Exception as e:
            messagebox.showerror("Error", f"Error loading translated labels: {e}")
            self.root.destroy()
            return

        # Index image paths and label info (no heavy loading yet)
        self.image_paths, self.labels, self.label_names = index_animals151_data_with_translation(
            DATASET_PATH,
            translated_labels
        )

        # Build a parallel list of words (class names) for each image
        self.words = [self.label_names[label] for label in self.labels]

        # Prepare game state
        self.remaining_indices = list(range(len(self.image_paths)))
        self.current_word = ""
        self.missing_indices = []   # List of indices (positions) still hidden
        self.display_chars = []     # List of characters for display (letters or '_')
        self.score = 0
        self.current_level = 1
        self.lives = 10             # Starting life count

        # UI Setup
        self.setup_ui()

        # Load the first image
        self.load_next_image()

    def setup_ui(self):
        """Creates and arranges the user interface components."""
        # Label for displaying the image
        self.img_label = tk.Label(self.root, bg="lightyellow")
        self.img_label.pack(pady=5)

        # Label for displaying the word with missing letters
        self.word_label = tk.Label(self.root, font=("Arial", 24), bg="lightyellow")
        self.word_label.pack(pady=5)

        # Label for displaying score and lives
        self.status_label = tk.Label(self.root, font=("Arial", 16), bg="lightyellow")
        self.status_label.pack(pady=10)
        self.update_status_label()

        # Frame to hold the control buttons (only Next Image now)
        control_frame = tk.Frame(self.root, bg="lightyellow")
        control_frame.pack(pady=5)

        # Next image button (disabled until current puzzle is solved)
        self.next_button = tk.Button(
            control_frame,
            text="Следећа Слика",
            font=("Arial", 14),
            command=self.load_next_image,
            state=tk.DISABLED
        )
        self.next_button.grid(row=0, column=0, padx=5, pady=5) 
        self.end_button = tk.Button(
            control_frame,
            text="Крај",
            font=("Arial", 14),
            command=self.root.destroy
        )
        self.end_button.grid(row=0, column=1, padx=5, pady=5)
        # Frame to hold the Serbian Cyrillic letter buttons
        self.letters_frame = tk.Frame(self.root, bg="lightyellow")
        self.letters_frame.pack(pady=20)

        # Create buttons for each letter
        self.letter_buttons = {}
        # For layout, we can display 10 buttons per row (adjust as needed)
        buttons_per_row = 10
        for idx, letter in enumerate(self.SERBIAN_CYRILLIC):
            btn = tk.Button(
                self.letters_frame,
                text=letter,
                font=("Arial", 16),
                width=3,
                command=lambda l=letter: self.process_letter(l)
            )
            btn.grid(row=idx // buttons_per_row, column=idx % buttons_per_row, padx=3, pady=3)
            self.letter_buttons[letter] = btn

    def update_status_label(self):
        """Updates the status label with score and lives."""
        self.status_label.config(
            text=f"Резултат: {self.score} | Животи: {self.lives}"
        )

    def generate_display_word(self):
        """
        Constructs the word with missing letters based on current_level.
        Randomly chooses a number of positions (ignoring spaces) to hide.
        """
        # The number of missing letters is at most the length of the word (ignoring spaces)
        all_indices = [i for i, char in enumerate(self.current_word) if char != ' ']
        if not all_indices:
            self.display_chars = list(self.current_word)
            self.missing_indices = []
            return

        num_missing = min(self.current_level, len(all_indices))
        self.missing_indices = sorted(random.sample(all_indices, num_missing))

        # Build display_chars: copy the word and replace missing letters with underscores.
        self.display_chars = list(self.current_word)
        for i in self.missing_indices:
            if self.display_chars[i] != ' ':
                self.display_chars[i] = '_'

    def update_display_word(self):
        """Refreshes the word_label to show the current display_chars."""
        display_text = ' '.join(self.display_chars)
        self.word_label.config(text=display_text)

    def reset_letter_buttons(self):
        """Re-enable all letter buttons for the new puzzle."""
        for btn in self.letter_buttons.values():
            btn.config(state=tk.NORMAL)

    def disable_letter_buttons(self):
        """Disable all letter buttons (e.g. after puzzle is solved or game over)."""
        for btn in self.letter_buttons.values():
            btn.config(state=tk.DISABLED)

    def load_next_image(self):
        """Randomly chooses one image from the remaining set, loads it, and sets up the puzzle."""
        if not self.remaining_indices:
            messagebox.showinfo(
                "Крај игре",
                f"Нема више слика.\nРезултат: {self.score} тачних од много покушаја.\nЖивоти прекинути: {10 - self.lives}"
            )
            self.root.destroy()
            return

        idx = random.choice(self.remaining_indices)
        self.remaining_indices.remove(idx)

        # Lazy load the image from disk
        image_path = self.image_paths[idx]
        try:
            loaded_img = Image.open(image_path).convert('RGB')
        except Exception as e:
            messagebox.showwarning(
                "Упозорење",
                f"Не могу учитати слику: {image_path}\n{e}\nПрескакам..."
            )
            self.load_next_image()
            return

        # Set the current word (use upper-case for consistency)
        self.current_word = self.words[idx].upper()

        # Resize and display the image
        resized_image = loaded_img.resize((400, 400), Image.LANCZOS)
        self.rendered_image = ImageTk.PhotoImage(resized_image)
        self.img_label.config(image=self.rendered_image)
        self.img_label.image = self.rendered_image  # Keep a reference

        # Set up the puzzle: choose missing letters and display the masked word.
        self.generate_display_word()
        self.update_display_word()

        # Reset next button and re-enable letter buttons.
        self.next_button.config(state=tk.DISABLED)
        self.reset_letter_buttons()

    def process_letter(self, letter):
        """
        Called when a letter button is pressed.
        If the letter is among the missing letters, reveal it in all appropriate positions.
        Otherwise, decrement the life count.
        """
        found = False
        remaining_missing = []
        for i in self.missing_indices:
            if self.current_word[i] == letter:
                self.display_chars[i] = letter  # Reveal the letter
                found = True
            else:
                remaining_missing.append(i)
        self.missing_indices = remaining_missing

        if not found:
            self.lives -= 1
            self.update_status_label()
            if self.lives <= 0:
                self.disable_letter_buttons()
                self.next_button.config(state=tk.DISABLED)
                self.update_display_word()
                self.status_label.config(text=f"Изгубили сте све животе! Игра је завршена.Резултат: {self.score}")
                return

        self.update_display_word()

        if not self.missing_indices:
            self.score += 1
            self.update_status_label()
            self.disable_letter_buttons()
            self.word_label.config(text=self.current_word + "  ✔")
            self.next_button.config(state=tk.NORMAL)
            self.current_level += 1

def main(parent=None):
    """
    Launch this sub-game in stand-alone or modal mode.
    If parent is None, create a new Tk root.
    Otherwise, create a Toplevel and run it modally.
    The window is made resizable so that it can be minimized and maximized.
    """
    if parent is None:
        # Stand-alone
        root = tk.Tk()
        root.title("Погоди ко сам")
        root.geometry("1024x768")
        root.resizable(True, True)
        GuessingGame(root)
        root.mainloop()
    else:
        # Modal inside existing Tkinter app
        top = tk.Toplevel(parent)
        top.title("Погоди ко сам")
        top.geometry("1024x768")
        top.resizable(True, True)
        # Instead of calling top.mainloop(), use wait_window() so control returns to the parent.
        GuessingGame(top, parent=parent)
        top.grab_set()
        top.focus_set()
        top.transient(parent)
        top.wait_window(top)

if __name__ == "__main__":
    main()
