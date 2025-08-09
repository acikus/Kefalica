import tkinter as tk
from tkinter import messagebox, Canvas, PhotoImage
from PIL import Image, ImageTk
import random
import os

class ArithmeticGame:
    def __init__(self, master, images_path):
        """
        Initialize the Arithmetic Game.
        - master: Tkinter root or Toplevel.
        - images_path: Folder path for image assets.
        """
        self.master = master
        self.master.title("Игра рачунања")
        self.master.geometry("1024x768")
        self.master.resizable(False, False)
        self.IMAGES_FILE_PATH = images_path

        # Initialize game variables.
        self.num1 = 0
        self.num2 = 0
        self.correct_answer = 0
        self.score = 0
        self.attempts = 0
        self.operation = '+'  # Default operation is addition.

        # Create frame for the arithmetic problem.
        self.problem_frame = tk.Frame(self.master, bg="white")
        self.problem_frame.pack(pady=2)

        # Create frame for answer buttons.
        self.button_frame = tk.Frame(self.master, bg="white")
        self.button_frame.pack(pady=2)

        # Feedback label.
        self.feedback_label = tk.Label(self.master, text="", font=("Arial", 16), bg="white")
        self.feedback_label.pack(pady=2)

        # Score and attempts frame.
        self.score_frame = tk.Frame(self.master, bg="white")
        self.score_frame.pack(pady=2)
        self.score_label = tk.Label(self.score_frame, text=f"Резултат: {self.score}", font=("Arial", 16), bg="white")
        self.score_label.pack(side=tk.LEFT)
        self.attempts_label = tk.Label(self.score_frame, text=f"Покушаји: {self.attempts}", font=("Arial", 16), bg="white")
        self.attempts_label.pack(side=tk.LEFT, padx=20)

        # Create labels for displaying numbers and operation.
        self.num1_label = tk.Label(self.problem_frame, text="", font=("Arial", 36), bg="white")
        self.num1_label.grid(row=0, column=0, padx=0)

        self.operator_label = tk.Label(self.problem_frame, text=self.operation, font=("Arial", 36), bg="white")
        self.operator_label.grid(row=0, column=1, padx=0)

        self.num2_label = tk.Label(self.problem_frame, text="", font=("Arial", 36), bg="white")
        self.num2_label.grid(row=0, column=2, padx=0)

        self.equals_label = tk.Label(self.problem_frame, text="=", font=("Arial", 36), bg="white")
        self.equals_label.grid(row=0, column=3, padx=0)

        self.answer_label = tk.Label(self.problem_frame, text="", font=("Arial", 36), bg="white")
        self.answer_label.grid(row=0, column=4, padx=0)

        # Create frame for images.
        self.image_frame = tk.Frame(self.master, bg="white")
        self.image_frame.pack(pady=2)

        self.images1_frame = tk.Frame(self.image_frame, bg="white")
        self.images1_frame.grid(row=0, column=0, padx=0)

        self.plus_image_label = tk.Label(self.image_frame, text=self.operation, font=("Arial", 24), bg="white")
        self.plus_image_label.grid(row=0, column=1, padx=0)

        self.images2_frame = tk.Frame(self.image_frame, bg="white")
        self.images2_frame.grid(row=0, column=2, padx=0)

        self.equals_image_label = tk.Label(self.image_frame, text="=", font=("Arial", 24), bg="white")
        self.equals_image_label.grid(row=0, column=3, padx=0)

        self.images3_frame = tk.Frame(self.image_frame, bg="white")
        self.images3_frame.grid(row=0, column=4, padx=0)

        # Instead of an entry and check button, create 9 answer buttons.
        self.answer_buttons_frame = tk.Frame(self.master, bg="white")
        self.answer_buttons_frame.pack(pady=5)
        self.answer_buttons = []
        for i in range(1, 10):
            btn = tk.Button(
                self.answer_buttons_frame,
                text=str(i),
                font=("Arial", 14),
                width=5,
                height=2,
                command=lambda num=i: self._check_answer(num)
            )
            btn.grid(row=(i - 1) // 3, column=(i - 1) % 3, padx=5, pady=5)
            self.answer_buttons.append(btn)

        # Button for next problem.
        self.next_button = tk.Button(
            self.master,
            text="Следећи задатак",
            command=lambda: self._generate_problem(self.IMAGES_FILE_PATH),
            font=("Arial", 14)
        )
        self.next_button.pack(pady=10)
        self.next_button.config(state=tk.DISABLED)

        # Button to toggle the operation (+ or -).
        self.operation_button = tk.Button(
            self.master,
            text=f"Изабери операцију: {self.operation}",
            command=self._toggle_operation,
            font=("Arial", 14)
        )
        self.operation_button.pack(pady=10)

        # Button to restart the game.
        self.restart_button = tk.Button(
            self.master,
            text="Рестартуј игру",
            command=self._restart_game,
            font=("Arial", 14)
        )
        self.restart_button.pack(pady=10)

        # Button to end the game.
        self.end_button = tk.Button(
            self.master,
            text="Крај игре",
            command=self._end_game,
            font=("Arial", 14)
        )
        self.end_button.pack(pady=10)

        # List of available image filenames.
        self.image_files = ["apple.png", "banana.png", "pear.png", "peach.png"]
        self.input_photo = None

        # Generate the first problem.
        self._generate_problem(self.IMAGES_FILE_PATH)

    def _generate_problem(self, images_path):
        """
        Generate a new arithmetic problem and update the interface.
        """
        self.feedback_label.config(text="")
        self.next_button.config(state=tk.DISABLED)
        for button in self.answer_buttons:
            button.config(state=tk.NORMAL)

        self.operator_label.config(text=self.operation)
        self.plus_image_label.config(text=self.operation)

        if self.operation == '+':
            self.num1 = random.randint(1, 5)
            self.num2 = random.randint(1, 5)
            # Avoid sum equal to 10.
            while self.num1 + self.num2 == 10:
                self.num1 = random.randint(1, 5)
                self.num2 = random.randint(1, 5)
            self.correct_answer = self.num1 + self.num2
        elif self.operation == '-':
            self.num1 = random.randint(2, 9)
            self.num2 = random.randint(1, self.num1 - 1)
            self.correct_answer = self.num1 - self.num2

        self.num1_label.config(text=str(self.num1))
        self.num2_label.config(text=str(self.num2))
        self.answer_label.config(text="")

        # Clear previously displayed images.
        for widget in self.images1_frame.winfo_children():
            widget.destroy()
        for widget in self.images2_frame.winfo_children():
            widget.destroy()
        for widget in self.images3_frame.winfo_children():
            widget.destroy()

        # Randomly choose an image.
        random_image = os.path.join(images_path, random.choice(self.image_files))
        try:
            self.input_image = Image.open(random_image)
            self.input_image = self.input_image.resize((50, 50), Image.Resampling.LANCZOS)
            self.input_photo = ImageTk.PhotoImage(self.input_image)
        except Exception as e:
            messagebox.showerror("Грешка при учитавању слике", f"Не могу да учитам '{random_image}': {e}")
            return

        # Display image copies for the first and second operands.
        for _ in range(self.num1):
            lbl = tk.Label(self.images1_frame, image=self.input_photo, bg="white")
            lbl.pack(side=tk.LEFT, padx=0)
        for _ in range(self.num2):
            lbl = tk.Label(self.images2_frame, image=self.input_photo, bg="white")
            lbl.pack(side=tk.LEFT, padx=0)

    def _check_answer(self, selected_number):
        """
        Check if the selected answer is correct and update the game state.
        """
        self.attempts += 1
        self.attempts_label.config(text=f"Покушаји: {self.attempts}")

        if selected_number == self.correct_answer:
            self.feedback_label.config(text="Тачно!", fg="green")
            self._display_answer_images()
            self.next_button.config(state=tk.NORMAL)
            for button in self.answer_buttons:
                button.config(state=tk.DISABLED)
            self.score += 1
            self.score_label.config(text=f"Резултат: {self.score}")
        else:
            self.feedback_label.config(text="Покушај поново!", fg="red")

    def _display_answer_images(self):
        """
        Display the answer images for the correct answer.
        """
        for widget in self.images3_frame.winfo_children():
            widget.destroy()
        for _ in range(self.correct_answer):
            lbl = tk.Label(self.images3_frame, image=self.input_photo, bg="white")
            lbl.pack(side=tk.LEFT, padx=0)
        self.answer_label.config(text=str(self.correct_answer))

    def _restart_game(self):
        """
        Reset the game score and attempts, then generate a new problem.
        """
        self.score = 0
        self.attempts = 0
        self.score_label.config(text=f"Резултат: {self.score}")
        self.attempts_label.config(text=f"Покушаји: {self.attempts}")
        self._generate_problem(self.IMAGES_FILE_PATH)

    def _end_game(self):
        """
        End the game and close the application.
        """
        # Optionally, ask for confirmation:
        # if messagebox.askyesno("Крај игре", "Да ли сте сигурни да желите да завршите игру?"):
        self.master.destroy()

    def _toggle_operation(self):
        """
        Toggle the arithmetic operation between addition and subtraction.
        Then, update the corresponding labels and generate a new problem.
        """
        self.operation = '-' if self.operation == '+' else '+'
        self.operation_button.config(text=f"Изабери операцију: {self.operation}")
        self.operator_label.config(text=self.operation)
        self.plus_image_label.config(text=self.operation)
        self._generate_problem(self.IMAGES_FILE_PATH)

def main(parent=None):
    """
    Launch the Arithmetic Game.
    - If parent is None, create a new Tk root and run standalone.
    - Otherwise, run modally in a Toplevel window.
    """
    if parent is None:
        root = tk.Tk()
        root.geometry("1024x768")

        # Create a canvas to serve as the background.
        canvas = Canvas(root, width=1024, height=768)
        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            current_dir = os.getcwd()
        IMAGES_FILE_PATH = os.path.join(current_dir, "assets")
        bg_path = os.path.join(current_dir, "assets", "racunanjeBgr.png")
        bg_image = PhotoImage(file=bg_path)
        bg = canvas.create_image(0, 0, anchor="nw", image=bg_image)

        game = ArithmeticGame(root, IMAGES_FILE_PATH)
        # Lower the canvas to serve as background.
        canvas.lower(bg)
        root.mainloop()
    else:
        top = tk.Toplevel(parent)
        top.geometry("1024x768")
        canvas = Canvas(top, width=1024, height=768)
        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            current_dir = os.getcwd()
        IMAGES_FILE_PATH = os.path.join(current_dir, "assets")
        bg_path = os.path.join(current_dir, "assets", "racunanjeBgr.png")
        bg_image = PhotoImage(file=bg_path)
        bg = canvas.create_image(0, 0, anchor="nw", image=bg_image)
        game = ArithmeticGame(top, IMAGES_FILE_PATH)
        canvas.lower(bg)
        top.wait_window()

if __name__ == "__main__":
    main()