import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    current_dir = os.getcwd()

# Path to a placeholder author image (adjust to your own)
AUTHOR_IMG_PATH = os.path.join(current_dir, "assets", "author_photo.png")

class AboutGameForm(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("About the Author")

        # Make this form modal (optional)
        if master is not None:
            self.grab_set()
            self.focus_set()
            self.transient(master)

        # Set a fixed size (optional)
        self.geometry("600x400")

        # Main frame
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Attempt to load author image
        self.author_photo = None
        if os.path.exists(AUTHOR_IMG_PATH):
            try:
                pil_img = Image.open(AUTHOR_IMG_PATH)
                # Resize if you want a smaller display
                pil_img = pil_img.resize((100, 100), Image.LANCZOS)
                self.author_photo = ImageTk.PhotoImage(pil_img)
            except Exception as e:
                print(f"Error loading author image: {e}")

        # Image label (if found)
        if self.author_photo is not None:
            img_label = ttk.Label(main_frame, image=self.author_photo)
            img_label.pack(pady=5)

        # A label with some “demo text” about the author
        about_text = (
            "About the author:\n\n"
            "This game was created by Aleksandar Bošković, a visionary in the world of games and a man \n"
            "convinced that programming code is simply a modern form of magic. When he isn't creating \n"
            "incredible games, you can usually find him wondering whether it's better to debug code or \n"
            "build a brand new universe from scratch.\n\n"

            "And who was the programmer? That's where I come in, OpenAI's artificial intelligence!\n"
            "As ChatGPT, my main task was to turn Aca's creative, crazy vision into logical and functional code. \n"
            "I didn't drink coffee, never complained about being tired, but I did try several times to convince a loop \n"
            "not to run forever. Am I a robot? Yes. Did I get confused trying to understand human humor? Absolutely.\n\n"

            "Contact (author): alexboshkovic@gmail.com\n"
            "Contact (AI programmer): Type '/help', but I can't promise I'll fix your bugs!\n\n"

            "2023 © All rights reserved. If the game crashes, blame the bugs. If not, blame luck!\n\n"
            "Dedicated to Boris, Lena, and Dunja"
        )


        lbl_about = ttk.Label(main_frame, text=about_text, justify=tk.LEFT, wraplength=500)
        lbl_about.pack(pady=10)

        # Close button
        btn_close = ttk.Button(main_frame, text="Close", command=self.destroy)
        btn_close.pack(pady=5)

def main(parent=None):
    """
    Launch the About form.
    - If parent is None, run standalone (creates a Tk root and mainloop).
    - If parent is given, create a modal Toplevel above the parent and wait.
    """
    if parent is None:
        root = tk.Tk()
        root.title("About Game (Standalone)")
        app = AboutGameForm(master=root)
        root.mainloop()
    else:
        app = AboutGameForm(master=parent)
        parent.wait_window(app)

if __name__ == "__main__":
    main()
