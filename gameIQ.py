import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import random
import matplotlib
matplotlib.use("TkAgg")  # Use Tkinter backend
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os

class MathGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Мислиша")
        # Fix window dimensions to 1024x600 pixels.
        self.root.geometry("1024x600")
        
        # Determine current directory reliably.
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            current_dir = os.getcwd()
        
        # Set up the paths for the images (adjust these as necessary).
        IMAGE_PATH1 = os.path.join(current_dir, "assets", "IQ", "circle.png")
        IMAGE_PATH2 = os.path.join(current_dir, "assets", "IQ", "star.png")
        IMAGE_PATH3 = os.path.join(current_dir, "assets", "IQ", "triangle.png")
        
        # Load images for variables.
        self.img_x = ImageTk.PhotoImage(Image.open(IMAGE_PATH1).resize((40, 40)))
        self.img_y = ImageTk.PhotoImage(Image.open(IMAGE_PATH2).resize((40, 40)))
        self.img_z = ImageTk.PhotoImage(Image.open(IMAGE_PATH3).resize((40, 40)))
        # Keep a persistent list reference to avoid garbage collection.
        self.images = [self.img_x, self.img_y, self.img_z]
        
        # --- Layout Setup ---
        # Create two main frames: left for the game form and right for the graph.
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # In the left frame, create subframes for choices, controls, equations/answers, and result message.
        self.choice_frame = tk.Frame(self.left_frame)
        self.choice_frame.pack(pady=10)

        self.lbl_choice = tk.Label(self.choice_frame, text="Изаберите број непознатих:", font=("Arial", 14))
        self.lbl_choice.pack(side=tk.LEFT, padx=5)

        self.num_unknowns_var = tk.IntVar(value=2)  # Start default at 2

        self.rb_two = ttk.Radiobutton(
            self.choice_frame,
            text="две непознате",
            variable=self.num_unknowns_var,
            value=2,
            command=self.setup_system  # Re-generate system if user switches
        )
        self.rb_two.pack(side=tk.LEFT, padx=5)

        self.rb_three = ttk.Radiobutton(
            self.choice_frame,
            text="три непознате",
            variable=self.num_unknowns_var,
            value=3,
            command=self.setup_system  # Re-generate system if user switches
        )
        self.rb_three.pack(side=tk.LEFT, padx=5)

        self.game_frame = tk.Frame(self.left_frame)
        self.game_frame.pack(pady=10)

        # Label frames for equations and answers inside game_frame.
        self.equations_frame = tk.LabelFrame(self.game_frame, text="Систем једначина", padx=10, pady=10)
        self.equations_frame.pack(side=tk.TOP, padx=10, pady=10)

        self.answers_frame = tk.LabelFrame(self.game_frame, text="(Лопта, Звезда,(Троугао))", padx=10, pady=10)
        self.answers_frame.pack(side=tk.TOP, padx=10, pady=10)

        self.btn_check = tk.Button(self.game_frame, text="Провери", command=self.check_answer)
        self.btn_check.pack(side=tk.LEFT, padx=10)

        self.control_frame = tk.Frame(self.left_frame)
        self.control_frame.pack(pady=10)

        self.btn_restart = tk.Button(self.control_frame, text="Поново", command=self.restart_game)
        self.btn_restart.pack(side=tk.LEFT, padx=10)

        self.btn_exit = tk.Button(self.control_frame, text="Изађи", command=self.root.destroy)
        self.btn_exit.pack(side=tk.LEFT, padx=10)
        
        # Result message label in the left frame.
        self.result_label_frame = tk.Frame(self.left_frame)
        self.result_label_frame.pack(pady=10)
        self.lbl_result = tk.Label(self.result_label_frame, text="", font=("Arial", 18), fg="blue")
        self.lbl_result.pack()

        # In the right frame, create a frame for the graph.
        self.graph_frame = tk.Frame(self.right_frame)
        self.graph_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Variables to keep track of system data
        self.coeffs = None     # matrix of coefficients (A)
        self.consts = None     # vector of constants (b)
        self.solution = None   # correct solution (s)
        self.answers = []      # possible answers
        self.answer_var = tk.StringVar()  # for radio buttons

        # Immediately generate a 2x2 system on startup
        self.setup_system()

    def setup_system(self):
        """Set up a random system (2x2 or 3x3) with a unique integer solution
           and with all coefficients non-zero."""
        self.clear_equations_and_answers()
        
        n = self.num_unknowns_var.get()

        # 1) Pick a random integer solution vector s (range -5..5)
        # 2) Generate an invertible matrix A (with entries from [-5..-1] U [1..5])
        # 3) Compute b = A * s
        nonzero_choices = list(range(-5, 0)) + list(range(1, 6))
        solution = np.random.randint(-5, 6, size=n)

        while True:
            A = np.random.choice(nonzero_choices, size=(n, n))
            det_val = round(np.linalg.det(A))
            if det_val != 0:
                break

        b = A.dot(solution)

        self.coeffs = A
        self.consts = b
        self.solution = solution

        # Display the system with proper sign formatting.
        if n == 2:
            for i in range(2):
                a, b_ = self.coeffs[i]
                c_ = self.consts[i]
                frame_eq = tk.Frame(self.equations_frame)
                frame_eq.pack(anchor='w')
                
                # First term (for x)
                if a < 0:
                    term1 = f"- {abs(a)}·"
                else:
                    term1 = f"  {a}·"
                tk.Label(frame_eq, text=term1, font=("Arial", 18)).pack(side=tk.LEFT)
                tk.Label(frame_eq, image=self.img_x).pack(side=tk.LEFT)
                
                # Second term (for y)
                if b_ < 0:
                    term2 = f"  - {abs(b_)}·"
                else:
                    term2 = f" + {b_}·"
                tk.Label(frame_eq, text=term2, font=("Arial", 18)).pack(side=tk.LEFT)
                tk.Label(frame_eq, image=self.img_y).pack(side=tk.LEFT)
                
                # Constant term
                tk.Label(frame_eq, text=f" = {c_}", font=("Arial", 18)).pack(side=tk.LEFT)
        else:
            for i in range(3):
                a, b_, c_ = self.coeffs[i]
                d_ = self.consts[i]
                frame_eq = tk.Frame(self.equations_frame)
                frame_eq.pack(anchor='w')
                
                # First term (for x)
                if a < 0:
                    term1 = f"- {abs(a)}·"
                else:
                    term1 = f"  {a}·"
                tk.Label(frame_eq, text=term1, font=("Arial", 18)).pack(side=tk.LEFT)
                tk.Label(frame_eq, image=self.img_x).pack(side=tk.LEFT)
                
                # Second term (for y)
                if b_ < 0:
                    term2 = f"  - {abs(b_)}·"
                else:
                    term2 = f" + {b_}·"
                tk.Label(frame_eq, text=term2, font=("Arial", 18)).pack(side=tk.LEFT)
                tk.Label(frame_eq, image=self.img_y).pack(side=tk.LEFT)
                
                # Third term (for z)
                if c_ < 0:
                    term3 = f"  - {abs(c_)}·"
                else:
                    term3 = f" + {c_}·"
                tk.Label(frame_eq, text=term3, font=("Arial", 18)).pack(side=tk.LEFT)
                tk.Label(frame_eq, image=self.img_z).pack(side=tk.LEFT)
                
                # Constant term
                tk.Label(frame_eq, text=f" = {d_}", font=("Arial", 18)).pack(side=tk.LEFT)

        # Build multiple-choice answers (one correct plus four nearby integer answers).
        self.answers = []
        correct = tuple(self.solution)
        self.answers.append(correct)
        for _ in range(4):
            perturb = np.random.randint(-2, 3, size=n)
            alt_sol = self.solution + perturb
            alt_sol_tuple = tuple(alt_sol)
            while alt_sol_tuple == correct:
                perturb = np.random.randint(-2, 3, size=n)
                alt_sol = self.solution + perturb
                alt_sol_tuple = tuple(alt_sol)
            self.answers.append(alt_sol_tuple)
        random.shuffle(self.answers)

        self.answer_var.set("")
        for ans in self.answers:
            ans_str = "(" + ", ".join(str(a) for a in ans) + ")"
            r = tk.Radiobutton(
                self.answers_frame,
                text=ans_str,
                variable=self.answer_var,
                value=ans_str
            )
            r.pack(anchor='w')

        self.lbl_result.config(text="")

    def check_answer(self):
        """Check the chosen answer and display a message plus the graph."""
        chosen = self.answer_var.get().strip()
        if not chosen:
            self.lbl_result.config(text="Молимо одаберите решење!", fg="red")
            return

        chosen_values = tuple(int(x) for x in chosen.strip("()").split(","))
        correct_tuple = tuple(self.solution)

        if chosen_values == correct_tuple:
            self.lbl_result.config(text="Тачан одговор!", fg="green")
        else:
            self.lbl_result.config(text="Нетачан одговор!", fg="red")

        self.show_graph()

    def show_graph(self):
        """Display a 2D or 3D plot of the equations and highlight the intersection."""
        n = self.num_unknowns_var.get()
        # Clear any previous graph in the graph_frame.
        for widget in self.graph_frame.winfo_children():
            if isinstance(widget, tk.Canvas):
                widget.destroy()

        fig = Figure(figsize=(5, 4), dpi=100)
        if n == 2:
            ax = fig.add_subplot(111)
            ax.set_title("Графички приказ (2D)")
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            a1, b1 = self.coeffs[0]
            c1 = self.consts[0]
            a2, b2 = self.coeffs[1]
            c2 = self.consts[1]
            
            eq1 = f"{a1}x + {b1}y = {c1}"
            eq2 = f"{a2}x + {b2}y = {c2}"
            
            x_vals = np.linspace(-10, 10, 200)
            y1_vals = (c1 - a1*x_vals) / b1
            y2_vals = (c2 - a2*x_vals) / b2
            
            ax.plot(x_vals, y1_vals, label=eq1)
            ax.plot(x_vals, y2_vals, label=eq2)
            ax.legend()
            ax.grid(True)
            
            try:
                inter_point = np.linalg.solve(np.array([[a1, b1], [a2, b2]]), np.array([c1, c2]))
                ax.plot(inter_point[0], inter_point[1], 'ro', markersize=8, label="Пресек")
                ax.legend()
            except np.linalg.LinAlgError:
                pass
        else:
            ax = fig.add_subplot(111, projection='3d')
            ax.set_title("Графички приказ (3D)")
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.set_zlabel("z")
            x_vals = np.linspace(-10, 10, 20)
            y_vals = np.linspace(-10, 10, 20)
            X, Y = np.meshgrid(x_vals, y_vals)
            a1, b1, c1 = self.coeffs[0]
            d1 = self.consts[0]
            a2, b2, c2 = self.coeffs[1]
            d2 = self.consts[1]
            a3, b3, c3 = self.coeffs[2]
            d3 = self.consts[2]
            def plane_z(a, b, c, d, X, Y):
                return (d - a*X - b*Y) / c
            Z1 = plane_z(a1, b1, c1, d1, X, Y)
            Z2 = plane_z(a2, b2, c2, d2, X, Y)
            Z3 = plane_z(a3, b3, c3, d3, X, Y)
            ax.plot_surface(X, Y, Z1, alpha=0.5, color="red")
            ax.plot_surface(X, Y, Z2, alpha=0.5, color="green")
            ax.plot_surface(X, Y, Z3, alpha=0.5, color="blue")
            
            n1 = np.array([a1, b1, c1])
            n2 = np.array([a2, b2, c2])
            direction = np.cross(n1, n2)
            if np.linalg.norm(direction) > 1e-6:
                free_idx = np.argmax(np.abs(direction))
                t_vals = np.linspace(-10, 10, 100)
                xs, ys, zs = [], [], []
                for t in t_vals:
                    if free_idx == 0:
                        mat = np.array([[b1, c1],
                                        [b2, c2]])
                        rhs = np.array([d1 - a1*t, d2 - a2*t])
                        try:
                            sol = np.linalg.solve(mat, rhs)
                            y_val, z_val = sol
                            xs.append(t)
                            ys.append(y_val)
                            zs.append(z_val)
                        except np.linalg.LinAlgError:
                            continue
                    elif free_idx == 1:
                        mat = np.array([[a1, c1],
                                        [a2, c2]])
                        rhs = np.array([d1 - b1*t, d2 - b2*t])
                        try:
                            sol = np.linalg.solve(mat, rhs)
                            x_val, z_val = sol
                            xs.append(x_val)
                            ys.append(t)
                            zs.append(z_val)
                        except np.linalg.LinAlgError:
                            continue
                    else:
                        mat = np.array([[a1, b1],
                                        [a2, b2]])
                        rhs = np.array([d1 - c1*t, d2 - c2*t])
                        try:
                            sol = np.linalg.solve(mat, rhs)
                            x_val, y_val = sol
                            xs.append(x_val)
                            ys.append(y_val)
                            zs.append(t)
                        except np.linalg.LinAlgError:
                            continue
                ax.plot(xs, ys, zs, color="k", linewidth=2, label="Пресек црвене и зелене равни")
                ax.legend()
            sol_point = self.solution
            label_text = f"Пресечна тачка ({sol_point[0]}, {sol_point[1]}, {sol_point[2]})"
            ax.scatter(sol_point[0], sol_point[1], sol_point[2], color="r", s=50, label=label_text)
            ax.legend()
            
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def clear_equations_and_answers(self):
        """Clear the old equations and answers from the GUI."""
        for widget in self.equations_frame.winfo_children():
            widget.destroy()
        for widget in self.answers_frame.winfo_children():
            widget.destroy()
        self.answers = []

    def restart_game(self):
        """Restart the game by resetting the system and clearing previous results."""
        for widget in self.graph_frame.winfo_children():
            if isinstance(widget, tk.Canvas):
                widget.destroy()
        self.lbl_result.config(text="")
        self.setup_system()

def main(parent=None):
    """
    If a parent widget is provided (from your main switchboard), create a Toplevel;
    otherwise, create a new Tk root.
    NOTE: When a parent is provided, do not call mainloop() here.
    """
    if parent:
        window = tk.Toplevel(parent)
        window.transient(parent)
        app = MathGame(window)
        window.grab_set()           # Make the game modal.
        parent.wait_window(window)  # Wait until the game window is closed.
    else:
        window = tk.Tk()
        app = MathGame(window)
        window.mainloop()

if __name__ == "__main__":
    main()