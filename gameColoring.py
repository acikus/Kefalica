import tkinter as tk 
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import os
import math

def complementary_color(color):
    # Calculate the complementary color.
    r, g, b, _ = color
    return (255 - r, 255 - g, 255 - b)

class ColoringGame:
    def __init__(self, master, folder):
        """
        Initialize the Coloring Game.
        - master: the Tkinter parent window or Toplevel.
        - folder: path to the folder containing coloring images.
        """
        self.master = master
        self.folder = folder

        # Default settings.
        self.tolerance = 30         # Fill tolerance.
        self.brush_weight = 5       # Brush radius in pixels.
        self.mode = "fill"          # Modes: "fill" or "brush".
        self.selected_color = (255, 0, 0, 255)  # Default fill/brush color: red.

        # List image files in the folder.
        self.image_files = [f for f in os.listdir(folder)
                            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        if not self.image_files:
            raise Exception(f"No image files found in folder: {folder}")
        self.current_index = 0

        # Load the first image.
        self._load_image_from_folder()

        # Create main UI layout: left frame for controls, right frame for canvas.
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create control elements in the left frame.
        self._create_color_palettes(self.left_frame)
        self._create_mode_toggle(self.left_frame)
        self._create_sliders(self.left_frame)
        self._create_file_buttons(self.left_frame)
        self._create_control_buttons(self.left_frame)

        # Create the canvas in the right frame.
        self.canvas = tk.Canvas(self.right_frame,
                                width=self.image.width,
                                height=self.image.height,
                                cursor="cross")
        self.image_on_canvas = self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind mouse events.
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<Motion>", self._on_mouse_move)

        # Variable for brush cursor on canvas.
        self.brush_cursor = None

    def _load_image_from_folder(self):
        """Load the current image from the pre-defined folder."""
        image_path = os.path.join(self.folder, self.image_files[self.current_index])
        self.original_image = Image.open(image_path).convert("RGBA")
        self.image = self.original_image.copy()
        self.photo = ImageTk.PhotoImage(self.image)

    def _load_custom_image(self):
        """Load an image from a file chosen by the user."""
        filetypes = [("Image files", "*.png;*.jpg;*.jpeg;*.gif"), ("All files", "*.*")]
        filepath = filedialog.askopenfilename(title="Choose image", filetypes=filetypes)
        if filepath:
            try:
                self.original_image = Image.open(filepath).convert("RGBA")
                self.image = self.original_image.copy()
                self.photo = ImageTk.PhotoImage(self.image)
                # Resize canvas to new image size.
                self.canvas.config(width=self.image.width, height=self.image.height)
                self.canvas.itemconfig(self.image_on_canvas, image=self.photo)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open image:\n{e}")

    def _save_image(self):
        """Save the current image to a file chosen by the user."""
        filetypes = [("PNG", "*.png"), ("JPEG", "*.jpg;*.jpeg"), ("All files", "*.*")]
        filepath = filedialog.asksaveasfilename(title="Save image as", defaultextension=".png",
                                                filetypes=filetypes)
        if filepath:
            try:
                self.image.save(filepath)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot save image:\n{e}")

    def _create_color_palettes(self, parent):
        """Create two palettes: one for standard colors and one for light colors."""
        # Standard colors.
        palette_frame = tk.LabelFrame(parent, text="Colors", padx=5, pady=5)
        palette_frame.pack(pady=5)

        colors = [
            ("Red", (255, 0, 0, 255)),
            ("Orange", (255, 165, 0, 255)),
            ("Yellow", (255, 255, 0, 255)),
            ("Green", (0, 128, 0, 255)),
            ("Blue", (0, 0, 255, 255)),
            ("Indigo", (75, 0, 130, 255)),
            ("Purple", (238, 130, 238, 255)),
            ("Black", (0, 0, 0, 255)),
            ("White", (255, 255, 255, 255)),
            ("Brown", (139, 69, 19, 255)),
            ("Pink", (255, 192, 203, 255)),
            ("Cyan", (0, 255, 255, 255))
        ]

        for index, (name, color) in enumerate(colors):
            row = index // 2
            column = index % 2
            bg_color = "#%02x%02x%02x" % color[:3]
            fg_color = "#%02x%02x%02x" % complementary_color(color)
            btn = tk.Button(
                palette_frame,
                text=name,
                bg=bg_color,
                fg=fg_color,
                width=10,
                command=lambda c=color: self._set_color(c)
            )
            btn.grid(row=row, column=column, padx=5, pady=2, sticky="ew")

        light_palette_frame = tk.LabelFrame(parent, text="Light colors", padx=5, pady=5)
        light_palette_frame.pack(pady=5)

        light_colors = [
            ("Pink", (255, 182, 193, 255)),
            ("Blue", (173, 216, 230, 255)),
            ("Green", (144, 238, 144, 255)),
            ("Lavender", (230, 230, 250, 255)),
            ("Beige", (245, 245, 220, 255)),
            ("Yellow", (255, 255, 224, 255))
        ]

        for index, (name, color) in enumerate(light_colors):
            row = index // 2
            column = index % 2
            btn = tk.Button(
                light_palette_frame,
                text=name,
                bg="#%02x%02x%02x" % color[:3],
                width=10,
                command=lambda c=color: self._set_color(c)
            )
            btn.grid(row=row, column=column, padx=5, pady=2, sticky="ew")

    def _create_mode_toggle(self, parent):
        """Create a button to toggle between Fill and Brush modes."""
        self.mode_btn = tk.Button(parent,
                                  text="Bucket",
                                  width=12,
                                  command=self._toggle_mode)
        self.mode_btn.pack(pady=5)

    def _create_sliders(self, parent):
        """Create sliders for fill tolerance and brush weight."""
        tol_frame = tk.LabelFrame(parent, text="Fill tolerance", padx=5, pady=5)
        tol_frame.pack(pady=5)
        self.tol_slider = tk.Scale(tol_frame, from_=0, to=100,
                                   orient=tk.HORIZONTAL,
                                   command=lambda val: self._update_tolerance(val))
        self.tol_slider.set(self.tolerance)
        self.tol_slider.pack()

        brush_frame = tk.LabelFrame(parent, text="Brush thickness", padx=5, pady=5)
        brush_frame.pack(pady=5)
        self.brush_slider = tk.Scale(brush_frame, from_=1, to=50,
                                     orient=tk.HORIZONTAL,
                                     command=lambda val: self._update_brush_weight(val))
        self.brush_slider.set(self.brush_weight)
        self.brush_slider.pack()

    def _create_file_buttons(self, parent):
        """Create Load and Save buttons for image file operations."""
        file_frame = tk.Frame(parent)
        file_frame.pack(pady=10)
        load_btn = tk.Button(file_frame, text="Load Image", width=15,
                             command=self._load_custom_image)
        load_btn.pack(pady=2)
        save_btn = tk.Button(file_frame, text="Save Image", width=15,
                             command=self._save_image)
        save_btn.pack(pady=2)

    def _create_control_buttons(self, parent):
        """Create navigation and exit buttons."""
        ctrl_frame = tk.Frame(parent)
        ctrl_frame.pack(pady=10)
        next_btn = tk.Button(ctrl_frame, text="Next Image", width=15,
                             command=self._next_image)
        next_btn.pack(pady=2)
        reset_btn = tk.Button(ctrl_frame, text="Reset Image", width=15,
                              command=self._reset_image)
        reset_btn.pack(pady=2)
        exit_btn = tk.Button(ctrl_frame, text="Close", width=15,
                             command=self.master.destroy)
        exit_btn.pack(pady=2)

    def _set_color(self, color):
        """Set the selected fill/brush color."""
        self.selected_color = color

    def _toggle_mode(self):
        """Toggle between fill mode and brush mode."""
        if self.mode == "fill":
            self.mode = "brush"
            self.mode_btn.config(text="Brush")
        else:
            self.mode = "fill"
            self.mode_btn.config(text="Bucket")
            if self.brush_cursor:
                self.canvas.delete(self.brush_cursor)
                self.brush_cursor = None

    def _update_tolerance(self, val):
        """Update the fill tolerance from the slider."""
        self.tolerance = int(val)

    def _update_brush_weight(self, val):
        """Update the brush weight from the slider."""
        self.brush_weight = int(val)

    def _on_canvas_click(self, event):
        """
        Handle a click on the canvas.
        In fill mode, perform flood fill.
        In brush mode, paint a circle.
        """
        if self.mode == "fill":
            self._fill_at(event.x, event.y)
        elif self.mode == "brush":
            self._brush_at(event.x, event.y)
        self._update_canvas()

    def _on_canvas_drag(self, event):
        """Handle dragging with the mouse in brush mode."""
        if self.mode == "brush":
            self._brush_at(event.x, event.y)
            self._update_canvas()

    def _on_mouse_move(self, event):
        """Update the brush cursor when in brush mode."""
        if self.mode == "brush":
            self._update_brush_cursor(event.x, event.y)
        else:
            if self.brush_cursor:
                self.canvas.delete(self.brush_cursor)
                self.brush_cursor = None

    def _update_brush_cursor(self, x, y):
        """Draw or move the brush cursor circle on the canvas."""
        r = self.brush_weight
        if self.brush_cursor is None:
            self.brush_cursor = self.canvas.create_oval(x - r, y - r, x + r, y + r,
                                                         outline="black", width=1)
        else:
            self.canvas.coords(self.brush_cursor, x - r, y - r, x + r, y + r)

    def _fill_at(self, x, y):
        """Perform flood fill at the given canvas coordinates."""
        if x < 0 or y < 0 or x >= self.image.width or y >= self.image.height:
            return
        target_color = self.image.getpixel((x, y))
        if self._colors_similar(target_color, self.selected_color, tolerance=0):
            return
        self._flood_fill(self.image, (x, y), target_color, self.selected_color)

    def _brush_at(self, x, y):
        """Draw a circle (brush stroke) at the given coordinates."""
        draw = ImageDraw.Draw(self.image)
        r = self.brush_weight
        bbox = [x - r, y - r, x + r, y + r]
        draw.ellipse(bbox, fill=self.selected_color)

    def _colors_similar(self, color1, color2, tolerance=None):
        """
        Compare two RGBA colors using Euclidean distance.
        If tolerance is None, use self.tolerance.
        """
        if tolerance is None:
            tolerance = self.tolerance
        diff = math.sqrt(sum((a - b) ** 2 for a, b in zip(color1, color2)))
        return diff <= tolerance

    def _flood_fill(self, img, start_pos, target_color, replacement_color):
        if self._colors_similar(target_color, replacement_color, tolerance=0):
            return
        pixel_data = img.load()
        width, height = img.size
        stack = [start_pos]
        visited = set()
        while stack:
            x, y = stack.pop()
            if (x, y) in visited:
                continue
            visited.add((x, y))
            if x < 0 or y < 0 or x >= width or y >= height:
                continue
            current_color = pixel_data[x, y]
            if not self._colors_similar(current_color, target_color):
                continue
            pixel_data[x, y] = replacement_color
            stack.append((x - 1, y))
            stack.append((x + 1, y))
            stack.append((x, y - 1))
            stack.append((x, y + 1))

    def _update_canvas(self):
        """Update the canvas with the modified image."""
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas.itemconfig(self.image_on_canvas, image=self.photo)
        if self.brush_cursor:
            self.canvas.tag_raise(self.brush_cursor)

    def _next_image(self):
        """Load the next image in the folder."""
        self.current_index = (self.current_index + 1) % len(self.image_files)
        self._load_image_from_folder()
        self.canvas.config(width=self.image.width, height=self.image.height)
        self.canvas.itemconfig(self.image_on_canvas, image=self.photo)

    def _reset_image(self):
        """Reset the image to its original state."""
        self.image = self.original_image.copy()
        self._update_canvas()

def main(parent=None):
    """
    Launch the Coloring Game.
    - If parent is None, run standalone in a new Tk root.
    - Otherwise, build the interface on the given parent.
    The window is made resizable so that it can be minimized and maximized.
    """
    if parent is None:
        # Standalone mode: create a new root window.
        root = tk.Tk()
        root.title("Coloring Game")
        root.resizable(True, True)
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
        except Exception:
            current_dir = os.getcwd()
        folder = os.path.join(current_dir, "assets", "coloring")
        ColoringGame(root, folder)
        root.mainloop()
    else:
        # Modal mode: create a new Toplevel.
        top = tk.Toplevel(parent)
        top.title("Coloring Book")
        top.resizable(True, True)
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
        except Exception:
            current_dir = os.getcwd()
        folder = os.path.join(current_dir, "assets", "coloring")
        ColoringGame(top, folder)
        top.grab_set()
        top.focus_set()
        top.transient(parent)
        top.wait_window(top)

if __name__ == '__main__':
    main()
