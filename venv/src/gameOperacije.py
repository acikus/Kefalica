import tkinter as tk

class IgraSabOduz:
    def __init__(self, root):
        self.root = root
        self.root.title("Counter")

        # Set initial operation to "+"
        self.operacija = "+"

        # Counters for red circles in each canvas
        self.broj_crvenih_1 = 0
        self.broj_crvenih_2 = 0

        # Create main frames
        frame1 = tk.Frame(self.root, bg="lightyellow")
        frame1.pack(pady=5, fill=tk.X)

        frame2 = tk.Frame(self.root, bg="lightyellow")
        frame2.pack(pady=5, fill=tk.X)

        frame3 = tk.Frame(self.root)
        frame3.pack(pady=5)

        frame4 = tk.Frame(self.root, bg="lightblue")
        frame4.pack(pady=5, fill=tk.X)

        frame5 = tk.Frame(self.root)
        frame5.pack(pady=5)

        self.labela_red0 = tk.Label(frame1, text="Click a circle to color it. You can click plus (+) or minus (-).", font=("Arial", 14), fg="red", bg="wheat")
        self.labela_red0.pack()

        # Canvas for the first row of circles
        self.canvas1 = tk.Canvas(frame1, width=800, height=180, bg="lightyellow")
        self.canvas1.pack()
        self.krugovi1 = []
        self._nacrtaj_krugove(self.canvas1, self.krugovi1, redni_broj=1)

        # Label to display the number of red circles in the first row
        self.labela_red1 = tk.Label(frame2, text="0", font=("Arial", 36), fg="red", bg="lightyellow")
        self.labela_red1.pack()

        # Label for the operation symbol ("+" or "-"); clicking toggles the operation
        self.labela_operacija = tk.Label(frame3, text=self.operacija, font=("Arial", 36), fg="blue", cursor="hand2")
        self.labela_operacija.bind("<Button-1>", self._promeni_operaciju)
        self.labela_operacija.pack(padx=10)

        # Label to display the number of red circles in the second row
        self.labela_red2 = tk.Label(frame4, text="0", font=("Arial", 36), fg="red", bg="lightblue")
        self.labela_red2.pack()

        # Canvas for the second row of circles
        self.canvas2 = tk.Canvas(frame5, width=800, height=180, bg="lightblue")
        self.canvas2.pack()
        self.krugovi2 = []
        self._nacrtaj_krugove(self.canvas2, self.krugovi2, redni_broj=2)

        # Label for the equals sign
        self.labela_jednako = tk.Label(frame5, text="=", font=("Arial", 36))
        self.labela_jednako.pack(padx=5)

        # Label for the result (number)
        self.labela_rezultat = tk.Label(frame5, text="0", font=("Arial", 36), fg="red")
        self.labela_rezultat.pack(padx=5)

        # Calculate initial result (all counts are 0)
        self._izracunaj_rezultat()

    def _nacrtaj_krugove(self, canvas, lista_krugova, redni_broj):
        """
        Draw 5 circles on the given canvas and store their IDs in lista_krugova.
        Initially, all circles are light green. Clicking a circle toggles its color
        between light green and red.
        """
        razmak = 150  # Horizontal spacing between circle centers
        r = 45        # Circle radius
        poc_x = 90    # Starting x-coordinate for drawing
        y = 90        # y-coordinate for all circles

        for i in range(5):
            x_cent = poc_x + i * razmak
            krug_id = canvas.create_oval(
                x_cent - r, y - r, x_cent + r, y + r,
                fill="lightgreen", outline="black", width=2
            )
            canvas.tag_bind(
                krug_id, "<Button-1>",
                lambda event, cid=krug_id, c=canvas, rb=redni_broj: self._promeni_boju_kruga(c, cid, rb)
            )
            lista_krugova.append(krug_id)

    def _promeni_boju_kruga(self, canvas, krug_id, redni_broj):
        """
        Toggle the color of a circle between light green and red.
        Update the count of red circles and recalculate the result.
        """
        trenutna_boja = canvas.itemcget(krug_id, "fill")
        if trenutna_boja == "lightgreen":
            canvas.itemconfig(krug_id, fill="red")
            if redni_broj == 1:
                self.broj_crvenih_1 += 1
                self.labela_red1.config(text=f"{self.broj_crvenih_1}")
            else:
                self.broj_crvenih_2 += 1
                self.labela_red2.config(text=f"{self.broj_crvenih_2}")
        else:
            canvas.itemconfig(krug_id, fill="lightgreen")
            if redni_broj == 1:
                self.broj_crvenih_1 -= 1
                self.labela_red1.config(text=f"{self.broj_crvenih_1}")
            else:
                self.broj_crvenih_2 -= 1
                self.labela_red2.config(text=f"{self.broj_crvenih_2}")

        self._izracunaj_rezultat()

    def _promeni_operaciju(self, event):
        """
        Toggle the operation symbol between "+" and "-". Then, recalculate the result.
        """
        self.operacija = "-" if self.operacija == "+" else "+"
        self.labela_operacija.config(text=self.operacija)
        self._izracunaj_rezultat()

    def _izracunaj_rezultat(self):
        """
        Calculate the result based on the current operation.
        Update the result label with the new value.
        """
        if self.operacija == "+":
            rezultat = self.broj_crvenih_1 + self.broj_crvenih_2
        else:
            rezultat = self.broj_crvenih_1 - self.broj_crvenih_2

        self.labela_rezultat.config(text=str(rezultat))


def main(parent=None):
    """
    Launch the Sabiranje i Oduzimanje game.
    - If parent is None, create a new Tk root and run in standalone mode.
    - If parent is provided (a Tk/Toplevel), run modally in a Toplevel window.
    The window is made resizable so that it can be minimized and maximized.
    """
    if parent is None:
        root = tk.Tk()
        root.title("Counter")
        # Allow resizing of the window.
        root.resizable(True, True)
        app = IgraSabOduz(root)
        root.mainloop()
    else:
        top = tk.Toplevel(parent)
        top.title("Counter")
        top.resizable(True, True)
        # Optionally, if you want modal behavior, use grab_set(), but do not use transient()
        top.grab_set()
        top.focus_set()
        IgraSabOduz(top)
        top.wait_window()

if __name__ == "__main__":
    main()
