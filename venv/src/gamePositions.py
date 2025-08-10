import json
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import random
import os

try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    current_dir = os.getcwd()

IMAGE_AND_JSON_PATH = os.path.join(current_dir, "assets", "pairs")

def load_game_data(filename):
    """Load game data from a JSON file located in the assets folder."""
    full_path = os.path.join(IMAGE_AND_JSON_PATH, filename)
    if not os.path.exists(full_path):
        messagebox.showerror("File Error", f"JSON file '{full_path}' not found!")
        return None
    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)

BUTTON_HEIGHT = 70

class ImagePairingGame(tk.Toplevel):
    def __init__(self, master=None, data_file="data.json"):
        super().__init__(master)
        self.title("Connector")
        self.geometry("1024x768")

        # This variable determines whether the right column shows English words (True) or Serbian words (False).
        self.include_english = tk.BooleanVar(value=True)
        self.include_english.trace_add("write", self.reload_current_category)

        # Custom styles for ttk buttons
        self.style = ttk.Style()
        self.style.configure("Normal.TButton")
        self.style.configure("Selected.TButton", background="lightblue")

        # Load the game data
        self.game_data = load_game_data(data_file)
        if self.game_data is None:
            self.destroy()  # If data load failed, close the game window.
            return

        # Extract category list
        self.categories = sorted(set(item['category'] for item in self.game_data))
        self.current_category_index = 0
        self.current_category = self.categories[self.current_category_index]

        # Data for the current category
        self.category_data = []  # Full list of items for the chosen category
        self.images_data = []    # List of PhotoImages (or None if image missing)
        self.answer_buttons = [] # Middle column (answers)
        self.words_data = []     # Shuffled list of text labels (SR or EN)
        self.words_buttons = []  # Right column (word buttons)
        self.selected_image_row = None  # Currently selected image row

        self.setup_ui()
        self.load_category()

    def setup_ui(self):
        # Create three columns: Images, Answers, and Words.
        columns_frame = ttk.Frame(self)
        columns_frame.pack(pady=20, expand=True, fill="both")

        # --- Left Column: Images ---
        image_column = ttk.Frame(columns_frame)
        image_column.pack(side=tk.LEFT, padx=20, fill="y")
        ttk.Label(image_column, text="Image", font=("Arial", 18, "bold")).pack(pady=10)
        self.image_column_frame = ttk.Frame(image_column)
        self.image_column_frame.pack(expand=True, fill="both")

        # --- Middle Column: Answers ---
        answer_column = ttk.Frame(columns_frame)
        answer_column.pack(side=tk.LEFT, padx=20, fill="y")
        ttk.Label(answer_column, text="---------- Answer ----------", font=("Arial", 18, "bold")).pack(pady=10)
        self.answer_column_frame = ttk.Frame(answer_column)
        self.answer_column_frame.pack(expand=True, fill="both")

        # --- Right Column: Words ---
        words_column = ttk.Frame(columns_frame)
        words_column.pack(side=tk.LEFT, padx=20, fill="y")
        self.words_label = ttk.Label(words_column, text="---------- Words (Serbian) ----------", font=("Arial", 18, "bold"))
        self.words_label.pack(pady=10)
        self.words_column_frame = ttk.Frame(words_column)
        self.words_column_frame.pack(expand=True, fill="both")

        # Control frame with buttons and checkbox
        control_frame = ttk.Frame(self)
        control_frame.pack(pady=10)
        ttk.Button(control_frame, text="Check", command=self.check_solution).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Next", command=self.next_category).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Exit", command=self.destroy).pack(side=tk.LEFT, padx=5)

        en_checkbox = ttk.Checkbutton(
            control_frame, 
            text="Show English words",
            variable=self.include_english
        )
        en_checkbox.pack(side=tk.LEFT, padx=5)

        self.message_label = ttk.Label(self, text="", font=("Arial", 12))
        self.message_label.pack(pady=5)

    def load_category(self):
        """Load data for the current category and create UI elements."""
        self.current_category = self.categories[self.current_category_index]
        self.category_data = [item for item in self.game_data if item['category'] == self.current_category]

        # Create images for the left column.
        self.images_data = []
        for item in self.category_data:
            image_path = os.path.join(IMAGE_AND_JSON_PATH, item['image_name'])
            if os.path.exists(image_path):
                try:
                    img = Image.open(image_path)
                    img = img.resize((55, 55), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                except Exception:
                    photo = None
            else:
                photo = None
            self.images_data.append(photo)

        # Clear previous UI elements.
        for w in self.image_column_frame.winfo_children():
            w.destroy()
        for w in self.answer_column_frame.winfo_children():
            w.destroy()
        for w in self.words_column_frame.winfo_children():
            w.destroy()

        self.answer_buttons = []
        self.words_buttons = []
        self.selected_image_row = None

        # Build left (images) and middle (blank answers) columns.
        for i, photo in enumerate(self.images_data):
            img_frame = tk.Frame(self.image_column_frame, height=BUTTON_HEIGHT, bg="white")
            img_frame.pack(pady=1, fill="x")
            img_frame.pack_propagate(False)

            img_btn = ttk.Button(
                img_frame,
                image=photo,
                text="No Image" if photo is None else "",
                command=lambda row=i: self.on_image_click(row)
            )
            img_btn.pack(expand=True, fill="both", padx=2, pady=2)

            ans_frame = tk.Frame(self.answer_column_frame, height=BUTTON_HEIGHT)
            ans_frame.pack(pady=1, fill="x")
            ans_frame.pack_propagate(False)
            # Define a style
            style = ttk.Style()
            style.configure("Normal.TButton", font=("Arial", 18))  # Set font, size
            ans_btn = ttk.Button(
                ans_frame,
                text="",
                state=tk.DISABLED,
                style="Normal.TButton"
            )
            ans_btn.pack(expand=True, fill="both", padx=2, pady=1)
            self.answer_buttons.append(ans_btn)

        # Build the right (words) column.
        self.build_words_column()
        self.message_label.config(text="")

    def build_words_column(self):
        """Construct the right column with words based on the current language setting."""
        for w in self.words_column_frame.winfo_children():
            w.destroy()

        if self.include_english.get():
            self.words_label.config(text="---------- Words (English) ----------")
            words_list = [item['english_label'].upper() for item in self.category_data]
        else:
            self.words_label.config(text="---------- Words (Serbian) ----------")
            words_list = [item['serbian_label'].upper() for item in self.category_data]

        random.shuffle(words_list)
        self.words_data = words_list
        self.words_buttons = []
        for i, word in enumerate(self.words_data):
            w_frame = tk.Frame(self.words_column_frame, height=BUTTON_HEIGHT)
            w_frame.pack(pady=1, fill="x")
            w_frame.pack_propagate(False)

            w_btn = ttk.Button(
                w_frame,
                text=word,
                style="Normal.TButton",
                command=lambda idx=i: self.on_word_click(idx)
            )
            w_btn.pack(expand=True, fill="both")
            self.words_buttons.append(w_btn)

    def on_image_click(self, row):
        """Remember which image row was clicked."""
        self.selected_image_row = row
        self.message_label.config(text=f"Image {row+1} selected. Now click a word.")

    def on_word_click(self, word_index):
        """
        If an image row is selected, check the word.
        If the word is correct, place it in the answer column and disable the word button.
        """
        if self.selected_image_row is None:
            self.message_label.config(text="Select an image first, then a word.")
            return

        chosen_word = self.words_data[word_index]
        correct_label_sr = self.category_data[self.selected_image_row]['serbian_label'].upper()
        correct_label_en = self.category_data[self.selected_image_row]['english_label'].upper()

        correct_label = correct_label_en if self.include_english.get() else correct_label_sr

        if chosen_word == correct_label:
            self.answer_buttons[self.selected_image_row].config(text=chosen_word)
            self.words_buttons[word_index].config(state=tk.DISABLED)
            self.message_label.config(text=f"Correct! Word '{chosen_word}' placed in row {self.selected_image_row+1}.")
        else:
            self.message_label.config(text=f"Try again. Word '{chosen_word}' does not match this image.")

        self.selected_image_row = None

    def check_solution(self):
        """Check how many correct answers are placed and update the message."""
        correct_count = 0
        total = len(self.category_data)
        for i in range(total):
            ans_text = self.answer_buttons[i].cget("text").strip().upper()
            correct_label_sr = self.category_data[i]['serbian_label'].upper()
            correct_label_en = self.category_data[i]['english_label'].upper()
            correct_label = correct_label_en if self.include_english.get() else correct_label_sr
            if ans_text == correct_label:
                correct_count += 1

        if correct_count == total:
            self.message_label.config(text="Congratulations, all matches are correct!")
        else:
            self.message_label.config(text=f"Correct {correct_count} out of {total}. Some images are not matched correctly.")

    def next_category(self):
        """Advance to the next category."""
        self.current_category_index = (self.current_category_index + 1) % len(self.categories)
        self.load_category()

    def reload_current_category(self, *args):
        """Rebuild the words column when the language selection changes."""
        self.build_words_column()
        self.message_label.config(text="Word display changed.")

def main(parent=None):
    """
    Launch the ImagePairingGame.
    - If parent is None, the game runs standalone (with its own Tk main loop).
    - If a parent is provided (e.g. from your main switchboard), the game is a modal Toplevel window.
    """
    if parent is None:
        root = tk.Tk()
        root.title("Connector")
        game = ImagePairingGame(master=root)
        root.mainloop()
    else:
        game = ImagePairingGame(master=parent)
        game.grab_set()          # Optional: make the game modal.
        parent.wait_window(game) # Wait here until the game window is closed.

if __name__ == "__main__":
    main()
