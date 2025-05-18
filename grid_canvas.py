import tkinter as tk
import numpy as np
import random
from PIL import Image, ImageTk


class GridCanvas:
    def __init__(self, master, rows, cols, cell_size, forklift_path, crate_paths, on_start_selected):
        self.master = master
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.canvas = tk.Canvas(master, width=cols * cell_size, height=rows * cell_size)
        self.canvas.pack()

        self.grid = np.zeros((rows, cols), dtype=int)
        self.on_start_selected = on_start_selected
        self.start = None

        # Load images
        self.forklift_img = self.load_image(forklift_path)
        self.crate_imgs = [self.load_image(p) for p in crate_paths]

        self.icon_refs = {}      # Position -> image ID
        self.image_refs = []     # Keep images in memory
        self.forklift_pos = None
        self.items = []          # List of (row, col, item_info)
        self.canvas.bind("<Button-1>", self.set_starting_point)

    def load_image(self, path):
        image = Image.open(path)
        image = image.resize((self.cell_size, self.cell_size), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)

    def draw_grid(self):
        self.canvas.delete("all")
        self.icon_refs.clear()
        self.image_refs.clear()

        for i in range(self.rows):
            for j in range(self.cols):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="gray")

        # Draw crates
        for (i, j, _) in self.items:
            crate_img = random.choice(self.crate_imgs)
            self.draw_image((i, j), crate_img)

        # Draw forklift at current position
        if self.forklift_pos:
            self.draw_forklift(self.forklift_pos)


    def set_starting_point(self, event):
        row = int((event.y + self.cell_size / 2) // self.cell_size)
        col = int((event.x + self.cell_size / 2) // self.cell_size)

        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.start = (row, col)
            self.forklift_pos = self.start
            self.on_start_selected(self.start)
            self.draw_grid()

    def draw_image(self, position, img):
        i, j = position
        x = j * self.cell_size + self.cell_size // 2
        y = i * self.cell_size + self.cell_size // 2
        self.icon_refs[position] = self.canvas.create_image(x, y, image=img)
        self.image_refs.append(img)

    def draw_forklift(self, position):
        if self.forklift_pos in self.icon_refs:
            self.canvas.delete(self.icon_refs[self.forklift_pos])
            del self.icon_refs[self.forklift_pos]

        self.draw_image(position, self.forklift_img)
        self.forklift_pos = position

    def move_forklift(self, from_pos, to_pos):
        self.draw_forklift(to_pos)

    def clear_crate(self, pos):
        if pos in self.icon_refs:
            self.canvas.delete(self.icon_refs[pos])
            del self.icon_refs[pos]

        # ✅ Remove crate from internal item list
        self.items = [item for item in self.items if (item[0], item[1]) != pos]

        # ✅ Re-draw grid to reflect the removal
        self.draw_grid()


