import tkinter as tk
import os
import json
from PIL import Image, ImageTk

# ---------------------------
# Configuration and JSON Loading
# ---------------------------

try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    current_dir = os.getcwd()

BACKGROUND_IMAGE_PATH = os.path.join(current_dir, "assets", "asoc", "asoc.png")
PUZZLE_DATA_JSON = os.path.join(current_dir, "assets", "asoc",  "puzzle_data_sr.json")

# === Behavior switches ===
# Show Serbian text on each "button" (label) from the start
SHOW_LANGUAGE_INITIAL = "srpski"   # "srpski" or "icons" (English)
# If True, clicking reveals an image; if False, clicking toggles text (EN↔SR)
USE_IMAGES_ON_REVEAL = False
# Which image set to use when revealing images (if USE_IMAGES_ON_REVEAL=True)
REVEAL_IMAGE_LANGUAGE = "srpski"    # "srpski" or "icons"

with open(PUZZLE_DATA_JSON, "r", encoding="utf8") as f:
    puzzle_data = json.load(f)

# ---------------------------
# Utility Function for Normalization / Display
# ---------------------------

def normalize_serbian(s: str) -> str:
    s = s.lower()
    s = s.replace("dž", "dz")
    s = s.replace("đ", "dj")
    s = s.replace("č", "c")
    s = s.replace("ć", "c")
    s = s.replace("š", "s")
    s = s.replace("ž", "z")
    return s


def filename_to_text(name: str) -> str:
    base = os.path.splitext(name)[0]
    return base.replace('_', ' ').upper()

# ---------------------------
# Main Game Class
# ---------------------------

class AsocijacijaIgra:
    def __init__(self, root):
        self.root = root
        self.root.title("Associations - Learn Serbian")

        # Load background image.
        self.bg_image = Image.open(BACKGROUND_IMAGE_PATH)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        # Create a canvas with fixed width and height.
        self.canvas = tk.Canvas(self.root, width=1024, height=750)
        self.canvas.pack()
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        self.score = 0
        self.puzzle_index = 0
        self.final_solved = False

        # Create main_frame that is embedded in the canvas.
        self.main_frame = tk.Frame(self.canvas, bg="lightblue")
        self.frame_window = self.canvas.create_window(0, 50, window=self.main_frame, anchor="nw", width=1024)

        # Widgets in the main_frame.
        self.score_label = tk.Label(
            self.main_frame,
            text=f"Score: {self.score}",
            font=("Impact", 14),
            fg="blue",
            bg="lightblue",
        )
        self.score_label.pack(pady=5)

        self.info_label = tk.Label(self.main_frame, text="", font=("Arial", 14), fg="black", bg="lightblue")
        self.info_label.pack(pady=5)

        self.puzzle_frame = tk.Frame(self.main_frame, bg="lightblue")
        self.puzzle_frame.pack()

        self.next_game_button = tk.Button(self.main_frame, text="Next Puzzle", command=self._next_game)
        self.next_game_button.pack(pady=5)
        self.next_game_button.config(state="disabled")

        # holders
        self.icon_images_en = {}
        self.icon_images_sr = {}
        self.text_map = {}         # {col: {"icons": [..], "srpski": [..]}}
        self.current_language_map = {}  # {col: ["srpski"|"icons", ...]}

        self._load_puzzle(self.puzzle_index)

        # Bind the resize event to ensure the canvas window stays 1024 pixels wide.
        self.root.bind("<Configure>", self.resize_frame)

    def resize_frame(self, event):
        self.canvas.itemconfig(self.frame_window, width=self.canvas.winfo_width())

    def _load_puzzle(self, index):
        self.current_puzzle = puzzle_data[index]
        self.columns = self.current_puzzle["columns"]
        self.final_solution = self.current_puzzle["final_solution"]
        self.final_solved = False

        self.revealed = {col: [False] * 4 for col in self.columns}
        self.solved_columns = {col: False for col in self.columns}
        self.label_map = {col: [] for col in self.columns}
        self.entry_map = {}
        self.button_map = {}
        self.icon_images_en = {}
        self.icon_images_sr = {}
        self.text_map = {}
        self.current_language_map = {col: [SHOW_LANGUAGE_INITIAL]*4 for col in self.columns}

        for w in self.puzzle_frame.winfo_children():
            w.destroy()
        self.info_label.config(text="")
        self.next_game_button.config(state="disabled")

        # Pillow resample compatibility
        if hasattr(Image, 'Resampling'):
            resample_mode = Image.Resampling.LANCZOS
        else:
            resample_mode = Image.LANCZOS

        # Preload images and texts for both languages
        for col, col_data in self.columns.items():
            # ---- English set ("icons") ----
            self.icon_images_en[col] = []
            en_files = col_data.get("icons", [])
            for fname in en_files:
                icon_path = os.path.join(current_dir, "assets", "asoc", "icons", fname)
                try:
                    pil_image = Image.open(icon_path)
                    pil_image = pil_image.resize((200, 80), resample_mode)
                    photo_image = ImageTk.PhotoImage(pil_image)
                except Exception as e:
                    print(f"Error loading image {icon_path}: {e}")
                    photo_image = None
                self.icon_images_en[col].append(photo_image)

            # ---- Serbian set ("srpski") ----
            self.icon_images_sr[col] = []
            sr_files = col_data.get("srpski", [])
            # if not provided, mirror EN list
            if not sr_files:
                sr_files = en_files
            for fname in sr_files:
                icon_path = os.path.join(current_dir, "assets", "asoc", "icons", fname)
                try:
                    pil_image = Image.open(icon_path)
                    pil_image = pil_image.resize((200, 80), resample_mode)
                    photo_image = ImageTk.PhotoImage(pil_image)
                except Exception as e:
                    print(f"Error loading image {icon_path}: {e}")
                    photo_image = None
                self.icon_images_sr[col].append(photo_image)

            # ---- Texts ----
            en_texts = [filename_to_text(x) for x in en_files]
            sr_texts = [filename_to_text(x) for x in sr_files]
            self.text_map[col] = {"icons": en_texts, "srpski": sr_texts}

        # Build UI
        for i, col in enumerate(self.columns.keys()):
            frame = tk.Frame(self.puzzle_frame, padx=10, pady=10, bg="lightblue")
            frame.grid(row=0, column=i, sticky="n")

            tk.Label(frame, text=f"{col}", font=("Impact", 14), fg="blue", bg="lightblue").pack()

            # Create a label for each field using configured initial language text.
            init_lang = SHOW_LANGUAGE_INITIAL
            for j in range(4):
                container = tk.Frame(frame, width=200, height=80, bg="lightyellow")
                container.pack(pady=2)
                container.pack_propagate(False)

                display_name = self.text_map[col][init_lang][j]
                lbl = tk.Label(container, text=display_name, bg="lightyellow", wraplength=190, justify="center")
                lbl.pack(expand=True, fill="both")
                lbl.bind("<Button-1>", lambda e, c=col, idx=j: self._reveal_one_field(c, idx))
                self.label_map[col].append(lbl)

            entry = tk.Entry(frame)
            entry.pack(pady=5)
            self.entry_map[col] = entry

            check_btn = tk.Button(
                frame,
                text="✅",
                command=lambda c=col, e=entry: self._check_column_solution(c, e)
            )
            check_btn.pack(pady=5)
            self.button_map[col] = check_btn

        final_frame = tk.Frame(self.puzzle_frame, pady=20, bg="lightblue")
        final_frame.grid(row=1, columnspan=4)

        tk.Label(final_frame, text="Final answer:", font=("Arial", 12), bg="lightblue").pack()
        self.final_entry = tk.Entry(final_frame)
        self.final_entry.pack(pady=2)
        final_btn = tk.Button(final_frame, text="Submit", command=self._check_final_solution)
        final_btn.pack(pady=2)

    def _normalize_input(self, text: str) -> str:
        return normalize_serbian(text)

    # === Reveal / Toggle logic ===
    def _reveal_one_field(self, col, idx):
        if self.solved_columns[col] or self.final_solved:
            return
        if not self.revealed[col][idx]:
            lbl = self.label_map[col][idx]

            if USE_IMAGES_ON_REVEAL:
                # choose which image set
                img_list = self.icon_images_sr[col] if REVEAL_IMAGE_LANGUAGE == "srpski" else self.icon_images_en[col]
                photo_image = img_list[idx] if idx < len(img_list) else None
                if photo_image:
                    lbl.config(image=photo_image, text="")
                    lbl.image = photo_image  # keep reference
                else:
                    # fallback to text if image missing
                    text_to_show = self.text_map[col][REVEAL_IMAGE_LANGUAGE][idx]
                    lbl.config(text=text_to_show)
            else:
                # Toggle text between EN <-> SR on click
                current_lang = self.current_language_map[col][idx]
                new_lang = "srpski" if current_lang == "icons" else "icons"
                self.current_language_map[col][idx] = new_lang
                lbl.config(text=self.text_map[col][new_lang][idx], image="")
                lbl.image = None

            lbl.config(bg="lightgreen")
            self.revealed[col][idx] = True

    def _reveal_all_in_column(self, col):
        for i, lbl in enumerate(self.label_map[col]):
            if USE_IMAGES_ON_REVEAL:
                img_list = self.icon_images_sr[col] if REVEAL_IMAGE_LANGUAGE == "srpski" else self.icon_images_en[col]
                photo_image = img_list[i] if i < len(img_list) else None
                if photo_image:
                    lbl.config(image=photo_image, text="")
                    lbl.image = photo_image
                else:
                    lbl.config(text=self.text_map[col]["srpski"][i])
            else:
                # Show Serbian text when revealing all
                self.current_language_map[col][i] = "srpski"
                lbl.config(text=self.text_map[col]["srpski"][i], image="")
                lbl.image = None

            lbl.config(bg="lightgreen")
            self.revealed[col][i] = True

    def _reveal_all_in_puzzle(self):
        for col in self.columns:
            self._reveal_all_in_column(col)

    def _count_unopened_fields(self, col):
        return sum(not opened for opened in self.revealed[col])

    # === Checking logic ===
    def _check_column_solution(self, col, entry):
        user_answer_raw = entry.get().strip()
        user_answer = self._normalize_input(user_answer_raw)
        valid_answers = self.columns[col]["solution"]
        valid_answers_normalized = [self._normalize_input(ans) for ans in valid_answers]

        if user_answer in valid_answers_normalized:
            if not self.solved_columns[col]:
                unopened = self._count_unopened_fields(col)
                points_for_column = 2 + unopened
                self.score += points_for_column
                self._update_score()

                self.solved_columns[col] = True
                self.info_label.config(
                    text=f"Column {col} solved! +{points_for_column} points.",
                    fg="green"
                )
                self._reveal_all_in_column(col)
            else:
                self.info_label.config(text="Column already solved.", fg="orange")
        else:
            self.info_label.config(text="Incorrect column answer.", fg="red")

    def _check_final_solution(self):
        if not self.final_solved:
            user_answer_raw = self.final_entry.get().strip()
            user_answer = self._normalize_input(user_answer_raw)
            valid_final_answers = self.final_solution
            valid_final_answers_normalized = [self._normalize_input(ans) for ans in valid_final_answers]

            if user_answer in valid_final_answers_normalized:
                self.final_solved = True
                base_final_points = 5
                extra_col_points = 0
                for col in self.columns:
                    if not self.solved_columns[col]:
                        unopened = self._count_unopened_fields(col)
                        col_points = 2 + unopened
                        extra_col_points += col_points

                total_final_points = base_final_points + extra_col_points
                self.score += total_final_points
                self._update_score()

                self.info_label.config(
                    text=f"Bravo! Final answer is: {valid_final_answers[0]} (+{total_final_points} points)",
                    fg="green"
                )

                self._reveal_all_in_puzzle()

                for col in self.columns:
                    self.entry_map[col].delete(0, tk.END)
                    self.entry_map[col].insert(0, self.columns[col]["solution"][0])
                    self.entry_map[col].config(state="disabled")
                    self.button_map[col].config(state="disabled")

                self.next_game_button.config(state="normal")
            else:
                self.info_label.config(text="Incorrect final answer.", fg="red")
        else:
            self.info_label.config(text="Final answer already guessed.", fg="orange")

    def _update_score(self):
        self.score_label.config(text=f"Score: {self.score}")

    def _next_game(self):
        self.puzzle_index += 1
        if self.puzzle_index < len(puzzle_data):
            self._load_puzzle(self.puzzle_index)
        else:
            self.info_label.config(text="No more puzzles!", fg="blue")
            self.next_game_button.config(state="disabled")

def main(parent=None):
    if parent is None:
        root = tk.Tk()
        root.title("Associations")
        root.resizable(True, True)
        app = AsocijacijaIgra(root)
        root.mainloop()
    else:
        top = tk.Toplevel(parent)
        top.title("Associations")
        top.resizable(True, True)
        top.grab_set()
        top.focus_set()
        AsocijacijaIgra(top)
        top.wait_window()

if __name__ == "__main__":
    main()
