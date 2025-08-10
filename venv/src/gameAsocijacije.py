import tkinter as tk
import os
import json

# ---------------------------
# Configuration and JSON Loading
# ---------------------------

try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    current_dir = os.getcwd()

PUZZLE_DATA_JSON = os.path.join(current_dir, "assets", "asoc", "puzzle_data_sr.json")

with open(PUZZLE_DATA_JSON, "r", encoding="utf8") as f:
    puzzle_data = json.load(f)

# ---------------------------
# Helpers
# ---------------------------

def normalize_serbian(s: str) -> str:
    s = s.lower()
    s = s.replace("dž", "dz").replace("đ", "dj").replace("č", "c").replace("ć", "c").replace("š", "s").replace("ž", "z")
    return s


def filename_to_text(name: str) -> str:
    base = os.path.splitext(str(name))[0]
    return base.replace("_", " ").upper()

# ---------------------------
# Main Game (TEXT ONLY, SR↔EN toggle on click)
# Rule: when a column is solved/opened OR final solved, words must be EN and stay EN
# ---------------------------

class AsocijacijaIgra:
    def __init__(self, root):
        self.root = root
        self.root.title("Associations - Text Only (SR↔EN, EN when solved)")

        self.canvas = tk.Canvas(self.root, width=1024, height=750, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.score = 0
        self.puzzle_index = 0
        self.final_solved = False

        self.main_frame = tk.Frame(self.canvas, bg="lightblue")
        self.frame_window = self.canvas.create_window(0, 0, window=self.main_frame, anchor="nw", width=1024)

        self.score_label = tk.Label(self.main_frame, text=f"Score: {self.score}", font=("Impact", 14), fg="blue", bg="lightblue")
        self.score_label.pack(pady=5)

        self.info_label = tk.Label(self.main_frame, text="", font=("Arial", 14), fg="black", bg="lightblue")
        self.info_label.pack(pady=5)

        self.puzzle_frame = tk.Frame(self.main_frame, bg="lightblue")
        self.puzzle_frame.pack()

        self.next_game_button = tk.Button(self.main_frame, text="Next Puzzle", command=self._next_game)
        self.next_game_button.pack(pady=5)
        self.next_game_button.config(state="disabled")

        # holders
        self.text_map = {}              # {col: {"srpski": [..], "icons": [..]}}
        self.current_language_map = {}  # {col: ["srpski"|"icons", ...]}
        self.widget_map = {}            # {col: [Button, Button, Button, Button]}

        self._load_puzzle(self.puzzle_index)
        self.root.bind("<Configure>", self.resize_frame)

    def resize_frame(self, event):
        self.canvas.itemconfig(self.frame_window, width=self.canvas.winfo_width())

    def _extract_texts(self, col_data):
        en_items = col_data.get("icons", [])
        sr_items = col_data.get("srpski", []) or en_items
        def to_words(items):
            out = []
            for x in items:
                out.append(filename_to_text(x))
            return out
        return to_words(sr_items), to_words(en_items)

    def _load_puzzle(self, index):
        self.current_puzzle = puzzle_data[index]
        self.columns = self.current_puzzle["columns"]
        self.final_solution = self.current_puzzle["final_solution"]
        self.final_solved = False

        self.revealed = {col: [False]*4 for col in self.columns}
        self.solved_columns = {col: False for col in self.columns}
        self.widget_map = {col: [] for col in self.columns}
        self.entry_map = {}
        self.button_map = {}
        self.text_map = {}
        self.current_language_map = {col: ["srpski"]*4 for col in self.columns}

        for w in self.puzzle_frame.winfo_children():
            w.destroy()
        self.info_label.config(text="")
        self.next_game_button.config(state="disabled")

        # Load words from JSON (strip extensions)
        for col, col_data in self.columns.items():
            sr_texts, en_texts = self._extract_texts(col_data)
            # Ensure length 4 with safe fallbacks
            def ensure4(lst):
                return (lst + [""]*4)[:4]
            self.text_map[col] = {"srpski": ensure4(sr_texts), "icons": ensure4(en_texts)}

        # Build UI per column
        for i, col in enumerate(self.columns.keys()):
            frame = tk.Frame(self.puzzle_frame, padx=10, pady=10, bg="lightblue")
            frame.grid(row=0, column=i, sticky="n")

            tk.Label(frame, text=f"{col}", font=("Impact", 14), fg="blue", bg="lightblue").pack()

            for j in range(4):
                btn = tk.Button(
                    frame,
                    text=self.text_map[col]["srpski"][j],
                    width=18,
                    height=3,
                    wraplength=180,
                    justify="center",
                    bg="lightyellow",
                    relief=tk.RAISED,
                    command=lambda c=col, idx=j: self._toggle_field(c, idx)
                )
                btn.pack(pady=3, fill="x")
                self.widget_map[col].append(btn)

            entry = tk.Entry(frame)
            entry.pack(pady=5)
            self.entry_map[col] = entry

            check_btn = tk.Button(frame, text="✅", command=lambda c=col, e=entry: self._check_column_solution(c, e))
            check_btn.pack(pady=5)
            self.button_map[col] = check_btn

        final_frame = tk.Frame(self.puzzle_frame, pady=20, bg="lightblue")
        final_frame.grid(row=1, columnspan=4)

        tk.Label(final_frame, text="Final answer:", font=("Arial", 12), bg="lightblue").pack()
        self.final_entry = tk.Entry(final_frame)
        self.final_entry.pack(pady=2)
        tk.Button(final_frame, text="Submit", command=self._check_final_solution).pack(pady=2)

    # === Click toggles SR ↔ EN for that field (until column/final is solved) ===
    def _toggle_field(self, col, idx):
        if self.solved_columns[col] or self.final_solved:
            return  # once solved, keep EN (set elsewhere)
        cur = self.current_language_map[col][idx]
        nxt = "icons" if cur == "srpski" else "srpski"
        self.current_language_map[col][idx] = nxt
        btn = self.widget_map[col][idx]
        btn.config(text=self.text_map[col][nxt][idx])
        # mark as opened (green) for scoring purposes
        if not self.revealed[col][idx]:
            btn.config(bg="lightgreen")
            self.revealed[col][idx] = True

    # === Force EN when revealing a solved column ===
    def _reveal_all_in_column(self, col):
        for i, btn in enumerate(self.widget_map[col]):
            self.current_language_map[col][i] = "icons"  # lock to EN
            btn.config(text=self.text_map[col]["icons"][i], bg="lightgreen")
            self.revealed[col][i] = True

    def _reveal_all_in_puzzle(self):
        for col in self.columns:
            self._reveal_all_in_column(col)  # this locks every column to EN

    def _count_unopened_fields(self, col):
        return sum(not opened for opened in self.revealed[col])

    # === Checking logic ===
    def _check_column_solution(self, col, entry):
        user_answer_raw = entry.get().strip()
        user_answer = normalize_serbian(user_answer_raw)
        valid_answers = self.columns[col]["solution"]
        valid_norm = [normalize_serbian(ans) for ans in valid_answers]

        if user_answer in valid_norm:
            if not self.solved_columns[col]:
                unopened = self._count_unopened_fields(col)
                points = 2 + unopened
                self.score += points
                self._update_score()
                self.solved_columns[col] = True
                self.info_label.config(text=f"Column {col} solved! +{points} points.", fg="green")
                self._reveal_all_in_column(col)  # switch & lock to EN for this column
            else:
                self.info_label.config(text="Column already solved.", fg="orange")
        else:
            self.info_label.config(text="Incorrect column answer.", fg="red")

    def _check_final_solution(self):
        if not self.final_solved:
            user_answer = normalize_serbian(self.final_entry.get().strip())
            valid_norm = [normalize_serbian(ans) for ans in self.final_solution]
            if user_answer in valid_norm:
                self.final_solved = True
                base_final = 5
                extra = 0
                for col in self.columns:
                    if not self.solved_columns[col]:
                        unopened = self._count_unopened_fields(col)
                        extra += 2 + unopened
                total = base_final + extra
                self.score += total
                self._update_score()
                self.info_label.config(text=f"Bravo! Final answer is: {self.final_solution[0]} (+{total} points)", fg="green")
                self._reveal_all_in_puzzle()  # switch & lock all to EN
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
        root.title("Associations (EN when solved)")
        root.resizable(True, True)
        AsocijacijaIgra(root)
        root.mainloop()
    else:
        top = tk.Toplevel(parent)
        top.title("Associations (EN when solved)")
        top.resizable(True, True)
        top.grab_set()
        top.focus_set()
        AsocijacijaIgra(top)
        top.wait_window()


if __name__ == "__main__":
    main()
