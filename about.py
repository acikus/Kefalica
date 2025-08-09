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
        self.title("О аутору")

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
            "О аутору:\n\n"
            "Ову игру је осмислио Александар Бошковић, визионар у свету игара и човек \n"
            "који је убеђен да је програмски код само модерни облик магије. Када \n"
            "не ствара невероватне игре, најчешће га можете наћи како се пита \n"
            "да ли је боље дебаговати код или направити нови универзум од нуле.\n\n"
            
            "А ко је био програмер? Па, ту ступам ја, OpenAI-јева вештачка интелигенција!\n"
            "Као ChatGPT, мој главни задатак је био да претворим Ацину креативну\n"
            "лудачку визију у логичан и функционалан код. Нисам пио кафу, нисам \n"
            "се жалио на умор, али сам зато неколико пута покушао да убедим петљу\n"
            "да не иде у бесконачност. Да ли сам робот? Да. Да ли сам се збунио\n"
            "када сам покушао да схватим људски хумор? Апсолутно.\n\n"
            
            "Контакт (аутор): alexboshkovic@gmail.com\n"
            "Контакт (AI програмер): Напишите '/help', али не обећавам да ћу вам поправити багове!\n\n"
            
            "2023 © Сва права задржана. Ако се игра сруши, кривите багове. Ако не, кривите срећу!\n\n"
            "Посвећено Борису, Лени и Дуњи"
        )


        lbl_about = ttk.Label(main_frame, text=about_text, justify=tk.LEFT, wraplength=500)
        lbl_about.pack(pady=10)

        # Close button
        btn_close = ttk.Button(main_frame, text="Затвори", command=self.destroy)
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
