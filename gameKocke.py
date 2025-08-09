import random
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import math

class Kocka:
    def __init__(self, x, y, z, boja):
        self.x = x
        self.y = y
        self.z = z
        self.boja = boja

def nacrtaj_kocku(ax, kocka):
    r = [0, 1]
    X, Y = np.meshgrid(r, r)
    ones = np.ones_like(X)
    zeros = np.zeros_like(X)
    ax.plot_surface(kocka.x + X, kocka.y + Y, kocka.z + zeros, 
                    color=kocka.boja, edgecolor='k')
    ax.plot_surface(kocka.x + X, kocka.y + Y, kocka.z + ones,
                    color=kocka.boja, edgecolor='k')
    ax.plot_surface(kocka.x + X, kocka.y + zeros, kocka.z + Y,
                    color=kocka.boja, edgecolor='k')
    ax.plot_surface(kocka.x + X, kocka.y + ones, kocka.z + Y,
                    color=kocka.boja, edgecolor='k')
    ax.plot_surface(kocka.x + zeros, kocka.y + X, kocka.z + Y,
                    color=kocka.boja, edgecolor='k')
    ax.plot_surface(kocka.x + ones, kocka.y + X, kocka.z + Y,
                    color=kocka.boja, edgecolor='k')

def run_pyramid_game(game_window):
    """Builds the pyramid/cube game UI in the given Toplevel (or root) window."""
    
    # Main frame
    main_frame = tk.Frame(game_window)
    main_frame.pack(fill='both', expand=True)

    # 3D plot
    fig = plt.Figure(figsize=(4, 4))
    ax = fig.add_subplot(111, projection='3d')
    canvas = FigureCanvasTkAgg(fig, master=main_frame)
    canvas.get_tk_widget().pack(side='left', fill='both', expand=True)

    controls_frame = tk.Frame(main_frame)
    controls_frame.pack(side='right', fill='y', padx=10)

    timer_label = tk.Label(controls_frame, text="Време: 0s", font=('Arial', 12))
    timer_label.pack(pady=5)

    score_label = tk.Label(controls_frame, text="Резултат: 0", font=('Arial', 12))
    score_label.pack(pady=5)

    question_label = tk.Label(controls_frame, text="Колико има коцкица?", font=('Arial', 12))
    question_label.pack(pady=5)

    result_label = tk.Label(controls_frame, text="Одговор: ", font=('Arial', 12))
    result_label.pack(pady=5)

    answer_buttons = [tk.Button(controls_frame, text="", font=('Arial', 10), width=10)
                      for _ in range(4)]
    for btn in answer_buttons:
        btn.pack(pady=2)

    # Timer logic
    timer_id = None
    start_time = time.time()

    def exit_game():
        nonlocal timer_id
        if timer_id is not None:
            try:
                game_window.after_cancel(timer_id)
            except Exception:
                pass
        # Destroy ONLY the sub-game window, not the main switchboard
        game_window.destroy()

    exit_button = tk.Button(controls_frame, text="Излаз", font=('Arial', 10), width=10, 
                            command=exit_game)
    exit_button.pack(pady=10)

    score = 0
    previous_count = None

    def update_timer():
        nonlocal timer_id
        if not game_window.winfo_exists():
            return
        elapsed = int(time.time() - start_time)
        timer_label.config(text=f"Време: {elapsed}s")
        timer_id = game_window.after(1000, update_timer)

    update_timer()

    def generate_cubes(total):
        cubes = []
        grid_dim = math.ceil(total ** (1/3))
        positions = []
        for x in range(grid_dim):
            for y in range(grid_dim):
                for z in range(grid_dim):
                    positions.append((x, y, z))
        random.shuffle(positions)
        for pos in positions[:total]:
            boja = "#%06x" % random.randint(0, 0xFFFFFF)
            cubes.append(Kocka(*pos, boja))
        return cubes, grid_dim

    def next_level():
        nonlocal previous_count, correct_answer
        while True:
            total = random.randint(4, 24)
            if total != previous_count:
                break
        previous_count = total
        cubes, grid_dim = generate_cubes(total)
        ax.clear()
        for cube in cubes:
            nacrtaj_kocku(ax, cube)
        ax.set_xlim(0, grid_dim)
        ax.set_ylim(0, grid_dim)
        ax.set_zlim(0, grid_dim)
        ax.view_init(elev=20, azim=30)
        canvas.draw()

        correct = total
        options = [correct]
        while len(options) < 4:
            opt = correct + random.choice([-3, -2, -1, 1, 2, 3])
            if opt > 0 and opt not in options:
                options.append(opt)
        random.shuffle(options)
        for btn, opt in zip(answer_buttons, options):
            btn.config(text=str(opt), command=lambda o=opt: check_answer(o))
        correct_answer = correct

    def check_answer(selected):
        nonlocal score
        if selected == correct_answer:
            score += 10
            result_label.config(text="Одговор: Тачно")
        else:
            score -= 5
            result_label.config(text="Одговор: Нетачно")
        score_label.config(text=f"Резултат: {score}")
        next_level()

    correct_answer = 0
    next_level()

def main(parent=None):
    if parent is None:
        # Standalone
        root_window = tk.Tk()
        root_window.title("Коцкице")
        root_window.geometry("1024x768")
        run_pyramid_game(root_window)
        root_window.mainloop()
    else:
        # Modal mode
        local_toplevel = tk.Toplevel(parent)
        local_toplevel.title("Коцкице")
        local_toplevel.geometry("1024x768")
        local_toplevel.grab_set()
        local_toplevel.focus_set()
        local_toplevel.transient(parent)

        # Pass the Toplevel to the game
        run_pyramid_game(local_toplevel)

        # wait_window ensures this sub-game blocks until closed
        local_toplevel.wait_window(local_toplevel)
