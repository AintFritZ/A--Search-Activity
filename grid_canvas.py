import tkinter as tk
import numpy as np
from PIL import Image, ImageTk


class GridCanvas:
    def __init__(self, master, rows, cols, cell_size, forklift_path, crate_paths, on_start_selected, warehouse_image_path=None):
        self.master = master
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.canvas = tk.Canvas(master, width=cols * cell_size, height=rows * cell_size)
        self.canvas.pack()

        self.grid = np.zeros((rows, cols), dtype=int)
        self.on_start_selected = on_start_selected
        self.start = None

        self.forklift_img = self.load_image(forklift_path)
        self.crate_imgs = [self.load_image(p) for p in crate_paths]
        self.warehouse_image = self.load_image(warehouse_image_path) if warehouse_image_path else None

        self.icon_refs = {}
        self.image_refs = []
        self.forklift_pos = None
        self.items = []  # (row, col, crate_img_index, weight)
        self.highlighted_path = []

        self.canvas.bind("<Button-1>", self.set_starting_point)

    def load_image(self, path):
        image = Image.open(path)
        image = image.resize((self.cell_size, self.cell_size), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)

    def draw_grid(self):
        self.canvas.delete("all")
        self.icon_refs.clear()
        self.image_refs.clear()

        # 1. Draw warehouse background image first (bottom layer)
        if self.warehouse_image:
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.warehouse_image)

        # 2. Draw grid cells (optional - drawn over warehouse)
        for i in range(self.rows):
            for j in range(self.cols):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="", outline="gray")

        # 3. Draw highlighted path ABOVE warehouse and grid cells
        for (i, j) in self.highlighted_path:
            x1 = j * self.cell_size
            y1 = i * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="lightblue", outline="blue")

        # 4. Draw items (crates) on top of highlighted path
        for (i, j, img_index, weight) in self.items:
            if (i, j) == (0, 0):
                continue
            crate_img = self.crate_imgs[img_index]
            self.draw_image((i, j), crate_img)
            x = j * self.cell_size + self.cell_size // 2
            y = i * self.cell_size + self.cell_size // 2 - 10
            self.canvas.create_text(x, y, text=str(weight), fill="black", font=("Arial", 12, "bold"))

        # 5. Draw forklift on top of everything
        if self.forklift_pos:
            self.draw_forklift(self.forklift_pos)

    def set_starting_point(self, event):
        row = int(event.y // self.cell_size)
        col = int(event.x // self.cell_size)

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
        # Remove previous forklift image if exists
        if self.forklift_pos in self.icon_refs:
            self.canvas.delete(self.icon_refs[self.forklift_pos])
            del self.icon_refs[self.forklift_pos]

        self.draw_image(position, self.forklift_img)
        self.forklift_pos = position

    def move_forklift(self, from_pos, to_pos):
        self.draw_forklift(to_pos)

    def clear_crate(self, pos):
        # Remove crate image on canvas
        if pos in self.icon_refs:
            self.canvas.delete(self.icon_refs[pos])
            del self.icon_refs[pos]

        # Remove crate from items list
        self.items = [item for item in self.items if (item[0], item[1]) != pos]
        self.draw_grid()

    def highlight_path(self, path):
        self.highlighted_path = path
        self.draw_grid()

    def highlight_path_cell(self, position):
        i, j = position
        x1 = j * self.cell_size
        y1 = i * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="#3B90F1", stipple="gray25", outline="")
