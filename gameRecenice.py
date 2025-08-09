import tkinter as tk
from tkinter import Canvas, PhotoImage, messagebox
import random
import os

class RecenicaIgra:
    def __init__(self, root, fajl_putanja, SLIKE_PUTANJA, putanja_bgr):
        """
        Inicijalizuje GUI i učitava podatke za igru.
        :param root: Glavni (ili Toplevel) prozor aplikacije.
        :param fajl_putanja: Putanja do .txt fajla sa rečenicama i nazivima slika.
        :param SLIKE_PUTANJA: Putanja do foldera koji sadrži slike.
        :param putanja_bgr: Putanja do slike za pozadinu.
        """
        self.root = root
        self.root.title("Missing Letters")
        self.root.geometry("1024x768")  # Fiksne dimenzije
        # Allow the window to be resized
        self.root.resizable(True, True)

        # Kreiramo canvas za pozadinu i postavljamo sliku
        self.canvas = Canvas(root, width=1024, height=768)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_image_obj = PhotoImage(file=putanja_bgr)
        bg = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image_obj)
        self.canvas.lower(bg)

        # Učitavamo podatke iz fajla
        self.SLIKE_PUTANJA = SLIKE_PUTANJA
        self.linije = self.ucitaj_linije(fajl_putanja)
        self.trenutni_indeks = 0
        self.ukupno_recenica = len(self.linije)

        # --------------------------
        # Kreiramo okvire po redovima:
        # 1. Red: Slika
        self.frame_image = tk.Frame(self.root, bg="white")
        self.frame_image.pack(pady=10, fill=tk.NONE)
        self.label_slika = tk.Label(self.frame_image, bg="white")
        self.label_slika.pack()

        # 2. Red: Dostupne reči (horizontalno raspoređene)
        self.frame_available = tk.Frame(self.root, bg="white")
        self.frame_available.pack(pady=10)

        # 3. Red: Izabrane reči (horizontalno raspoređene, ispod dostupnih)
        self.frame_selected = tk.Frame(self.root, bg="white")
        self.frame_selected.pack(pady=10)

        # 4. Red: Navigacija (prethodni/sledeći, napredak i ostalo)
        self.frame_navigacija = tk.Frame(self.root, bg="white")
        self.frame_navigacija.pack(pady=10)
        self.btn_prethodni = tk.Button(
            self.frame_navigacija, text="Previous",
            command=self.prethodni, font=("Arial", 12), bg="lightblue"
        )
        self.btn_prethodni.grid(row=0, column=0, padx=5)
        self.btn_sledeci = tk.Button(
            self.frame_navigacija, text="Next",
            command=self.sledeci, font=("Arial", 12), bg="lightgreen",
            state=tk.DISABLED  # Onemogućeno dok rečenica nije tačna
        )
        self.btn_sledeci.grid(row=0, column=1, padx=5)
        self.lbl_progress = tk.Label(
            self.frame_navigacija, text="", font=("Arial", 12), bg="white", fg="black"
        )
        self.lbl_progress.grid(row=0, column=2, padx=10)
        self.btn_zavrsi = tk.Button(
            self.frame_navigacija, text="Finish Game", font=("Arial", 12), bg="tomato",
            command=self.zavrsi_igru
        )
        self.btn_zavrsi.grid(row=0, column=3, padx=5)

        # Liste za čuvanje dugmića koje predstavljaju reči
        self.available_buttons = []
        self.selected_buttons = []

        # Čuvamo originalnu rečenicu (kao listu reči)
        self.trenutna_recenica = []

        # Prikaz prve linije (slika i reči)
        self.prikazi_liniju(self.trenutni_indeks, self.SLIKE_PUTANJA)
        self.azuriraj_napredak()

    def ucitaj_linije(self, putanja):
        """
        Učitava sve linije iz fajla i parsira podatke.
        Svaka linija treba da sadrži naziv slike i rečenicu, odvojene zarezom.
        :param putanja: Putanja do .txt fajla.
        :return: Lista tuple-ova (putanja_slike, recenica)
        """
        rezultati = []
        if not os.path.exists(putanja):
            messagebox.showerror("Error", f"File {putanja} not found.")
            return rezultati

        with open(putanja, "r", encoding="utf-8") as f:
            for linija in f:
                linija = linija.strip()
                if not linija:
                    continue
                prva_zagrada = linija.find(",")
                if prva_zagrada == -1:
                    continue
                putanja_slike = linija[:prva_zagrada].strip()
                recenica = linija[prva_zagrada+1:].strip()
                if recenica.startswith('"'):
                    recenica = recenica[1:]
                if recenica.endswith('"'):
                    recenica = recenica[:-1]
                rezultati.append((putanja_slike, recenica))
        return rezultati

    def prikazi_liniju(self, indeks, SLIKE_PUTANJA):
        """
        Prikazuje sliku i pomešane reči za dati indeks.
        :param indeks: Indeks rečenice u listi.
        :param SLIKE_PUTANJA: Putanja do foldera sa slikama.
        """
        if indeks < 0 or indeks >= len(self.linije):
            return
        putanja_slike, recenica = self.linije[indeks]
        self.prikazi_sliku(os.path.join(SLIKE_PUTANJA, putanja_slike))
        self.prikazi_pomesane_reci(recenica)
        self.azuriraj_napredak()

    def prikazi_sliku(self, putanja_slike):
        """
        Prikazuje sliku u labeli, ili ispisuje grešku ako slika ne postoji.
        :param putanja_slike: Puna putanja do slike.
        """
        if not os.path.exists(putanja_slike):
            self.label_slika.config(image="", text="Slika nije pronađena")
            return
        else:
            self.label_slika.config(text="")
        self.slika_obj = PhotoImage(file=putanja_slike)
        self.label_slika.config(image=self.slika_obj)

    def prikazi_pomesane_reci(self, recenica):
        """
        Prikazuje pomešane reči kao dugmiće.
        Dugmići se inicijalno kreiraju i nakon toga se "pakiraju" u odgovarajuće okvire:
        dostupne (drugi red) i izabrane (treći red).
        Pre kreiranja novih dugmića, prethodni se uništavaju.
        :param recenica: Originalna rečenica koja će se rastaviti i pomešati.
        """
        # Uništavamo stare dugmiće (ako postoje)
        for btn in self.available_buttons:
            btn.destroy()
        for btn in self.selected_buttons:
            btn.destroy()

        # Takođe osvežavamo okvire, ako su u njima ostali neki widgeti
        for widget in self.frame_available.winfo_children():
            widget.destroy()
        for widget in self.frame_selected.winfo_children():
            widget.destroy()

        # Pripremamo novu rečenicu i mešamo reči
        self.trenutna_recenica = recenica.upper().split()
        pomesane_reci = self.trenutna_recenica[:]
        random.shuffle(pomesane_reci)

        # Reset lista dugmića
        self.available_buttons = []
        self.selected_buttons = []

        moguce_boje = ["lightblue", "lightgreen", "lightyellow", "lightpink", "orange", "lavender", "tomato"]

        # Kreiramo nove dugmiće – roditelj je self.root, pa se kasnije "prepakovavaju"
        for rec in pomesane_reci:
            boja = random.choice(moguce_boje)
            btn = tk.Button(
                self.root,  # roditelj je self.root
                text=rec,
                font=("Arial", 14),
                bg=boja,
                relief=tk.RAISED,
                command=lambda btn=None: None  # privremeno, kasnije se prepisuje komanda
            )
            # Izbegavamo kasno vezivanje pomoću default argumenta
            btn.config(command=lambda btn=btn: self.toggle_word(btn))
            self.available_buttons.append(btn)

        # Postavljamo dugmiće u odgovarajuće okvire
        self.update_word_layout()
        self.proveri_recenicu()

    def toggle_word(self, btn):
        """
        Ako je dugme trenutno među dostupnim rečima, premešta ga u red izabranih.
        Ako je već u izabranim, vraća ga nazad među dostupne.
        :param btn: Dugme koje je kliknuto.
        """
        if btn in self.available_buttons:
            self.available_buttons.remove(btn)
            self.selected_buttons.append(btn)
        elif btn in self.selected_buttons:
            self.selected_buttons.remove(btn)
            self.available_buttons.append(btn)
        self.update_word_layout()
        self.proveri_recenicu()

    def update_word_layout(self):
        """
        Osvježava prikaz dugmića tako da se dugmići za dostupne reči
        pakiraju u okvir self.frame_available (drugi red),
        dok se dugmići za izabrane reči pakiraju u okvir self.frame_selected (treći red).
        """
        # Prvo uklanjamo prethodni raspored
        for widget in self.frame_available.winfo_children():
            widget.pack_forget()
        for widget in self.frame_selected.winfo_children():
            widget.pack_forget()

        # Pakujemo dugmiće za dostupne reči u okvir 'frame_available'
        for btn in self.available_buttons:
            btn.pack(in_=self.frame_available, side=tk.LEFT, padx=2, pady=2)

        # Pakujemo dugmiće za izabrane reči u okvir 'frame_selected'
        for btn in self.selected_buttons:
            btn.pack(in_=self.frame_selected, side=tk.LEFT, padx=2, pady=2)

    def proveri_recenicu(self):
        """
        Checks whether the current arrangement of selected words is correct.
        If all words are selected and in the proper order,
        the 'Next' button is enabled.
        """
        if len(self.selected_buttons) != len(self.trenutna_recenica):
            self.btn_sledeci.config(state=tk.DISABLED)
            return

        izabrane_reci = " ".join([btn.cget("text") for btn in self.selected_buttons])
        if izabrane_reci == " ".join(self.trenutna_recenica):
            self.btn_sledeci.config(state=tk.NORMAL)
        else:
            self.btn_sledeci.config(state=tk.DISABLED)

    def prethodni(self):
        """Prikazuje prethodnu rečenicu ako postoji."""
        if self.trenutni_indeks > 0:
            self.trenutni_indeks -= 1
            self.prikazi_liniju(self.trenutni_indeks, self.SLIKE_PUTANJA)

    def sledeci(self):
        """Prikazuje sledeću rečenicu ako postoji i resetuje stanje dugmeta."""
        if self.trenutni_indeks < len(self.linije) - 1:
            self.trenutni_indeks += 1
            self.prikazi_liniju(self.trenutni_indeks, self.SLIKE_PUTANJA)
            self.btn_sledeci.config(state=tk.DISABLED)

    def azuriraj_napredak(self):
        """Ažurira prikaz napretka (Rečenica X od Y)."""
        indeks_prikaz = self.trenutni_indeks + 1
        self.lbl_progress.config(
            text=f"Sentence {indeks_prikaz}/{self.ukupno_recenica}" if self.ukupno_recenica > 0 else "No sentences"
        )

    def zavrsi_igru(self):
        """Zatvara prozor i završava igru."""
        self.root.destroy()


def main(parent=None):
    """
    Pokreće RecenicaIgra.
    Ako je 'parent' None, kreira se novi Tk root i igra radi u stand-alone modu.
    Ako je 'parent' Toplevel ili Tk, otvara se modalni prozor.
    """
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        current_dir = os.getcwd()

    IMAGES_FILE_PATH = os.path.join(current_dir, "assets", "recenice")
    putanja_bgr  = os.path.join(current_dir, "assets", "receniceBGR.png")
    putanja_fajla  = os.path.join(current_dir, "assets", "recenice.txt")

    if parent is None:
        root = tk.Tk()
        root.title("Sentence Game")
        # Allow resizing of the main window
        root.resizable(True, True)
        if os.path.exists(putanja_fajla):
            app = RecenicaIgra(root, putanja_fajla, IMAGES_FILE_PATH, putanja_bgr)
            root.mainloop()
        else:
            print("No file selected, exiting program.")
    else:
        top = tk.Toplevel(parent)
        top.title("Sentence Game")
        # Allow maximizing/minimizing.
        top.resizable(True, True)
        top.grab_set()
        top.focus_set()
        # Remove or comment out transient() so that maximize button appears.
        # top.transient(parent)
        if os.path.exists(putanja_fajla):
            RecenicaIgra(top, putanja_fajla, IMAGES_FILE_PATH, putanja_bgr)
            top.wait_window()
        else:
            messagebox.showerror("Error", "Sentence file not found.")

if __name__ == "__main__":
    main()
