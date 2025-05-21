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
        self.items = []  # list of tuples: (row, col, crate_img_index, weight)
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

        # Draw background grid
        for row in range(self.rows):
            for col in range(self.cols):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="gray")

        # Draw highlighted path cells
        for (i, j) in self.highlighted_path:
            x1 = j * self.cell_size
            y1 = i * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="lightblue", outline="blue")

        # Draw warehouse image at (0,0)
        if self.warehouse_image:
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.warehouse_image)

        # Draw crates with weights above them
        for item in self.items:
            r, c, img_index, weight = item
            if (r, c) == (0, 0):
                continue
            x = c * self.cell_size
            y = r * self.cell_size
            crate_img = self.crate_imgs[img_index]
            self.canvas.create_image(x, y, anchor=tk.NW, image=crate_img)
            self.image_refs.append(crate_img)
            # Display weight text above the crate (top center of cell)
            text_x = x + self.cell_size // 2
            text_y = y + 10  # 10 pixels from top of cell
            self.canvas.create_text(text_x, text_y, text=str(weight), fill="black", font=("Arial", 12, "bold"))

        # Draw forklift once and store reference
        if self.forklift_pos:
            r, c = self.forklift_pos
            x = c * self.cell_size
            y = r * self.cell_size
            forklift_id = self.canvas.create_image(x, y, anchor=tk.NW, image=self.forklift_img)
            self.icon_refs['forklift'] = forklift_id

    def set_starting_point(self, event):
        row = int((event.y + self.cell_size / 2) // self.cell_size)
        col = int((event.x + self.cell_size / 2) // self.cell_size)

        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.start = (row, col)
            self.forklift_pos = self.start
            self.on_start_selected(self.start)
            self.draw_grid()

    def move_forklift(self, from_pos, to_pos):
        # Delete old forklift image before drawing new one
        if 'forklift' in self.icon_refs:
            self.canvas.delete(self.icon_refs['forklift'])
            del self.icon_refs['forklift']

        r, c = to_pos
        x = c * self.cell_size
        y = r * self.cell_size
        forklift_id = self.canvas.create_image(x, y, anchor=tk.NW, image=self.forklift_img)
        self.icon_refs['forklift'] = forklift_id
        self.forklift_pos = to_pos

    def clear_crate(self, pos):
        # Remove crate image if exists
        if pos in self.icon_refs:
            self.canvas.delete(self.icon_refs[pos])
            del self.icon_refs[pos]

        # Remove crate from items and redraw grid
        self.items = [item for item in self.items if (item[0], item[1]) != pos]
        self.draw_grid()

    def highlight_path(self, path):
        self.highlighted_path = path
        self.draw_grid()
    
    def highlight_path_cell(self, position):
        # Optional: you can highlight individual cells dynamically
        i, j = position
        x1 = j * self.cell_size
        y1 = i * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="#3B90F1", stipple="gray25", outline="")
