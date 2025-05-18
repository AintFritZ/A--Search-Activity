import tkinter as tk
import numpy as np
import random
from astar import AStarPathfinder
from grid_canvas import GridCanvas


class WarehouseApp:
    def __init__(self, master, rows=10, cols=10):
        self.master = master
        self.rows = rows
        self.cols = cols
        self.cell_size = 50
        self.grid = np.zeros((rows, cols), dtype=int)

        self.forklift_path = "Images/Forklift.png"
        self.crate_paths = ["Images/Crates.png"]

        self.items = self.generate_random_items(count=5)
        self.start = None

        self.canvas = GridCanvas(
            master,
            rows,
            cols,
            self.cell_size,
            self.forklift_path,
            self.crate_paths,
            self.on_start_selected
        )

        self.canvas.items = self.items
        self.canvas.draw_grid()

    def generate_random_items(self, count=5):
        positions = set()
        while len(positions) < count:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            positions.add((row, col))
        # Use index for crate image: 0 or 1
        return [(row, col, random.randint(0, len(self.crate_paths) - 1)) for (row, col) in positions]

    def on_start_selected(self, position):
        self.start = position
        self.plan_route()

    def plan_route(self):
        if not self.start:
            return

        pathfinder = AStarPathfinder(self.grid)
        sorted_items = sorted(self.items, key=lambda x: -x[2])  # Based on priority/image index
        current_pos = self.start

        for item in sorted_items:
            goal = (item[0], item[1])
            path = pathfinder.find_path(current_pos, goal)

            for step in path[1:]:
                self.canvas.move_forklift(current_pos, step)
                self.canvas.canvas.update()
                self.master.after(150)
                current_pos = step

            # Remove crate from canvas and internal lists
            self.canvas.clear_crate(goal)
            self.items = [i for i in self.items if (i[0], i[1]) != goal]
            self.canvas.items = self.items  # Sync internal canvas state

            self.canvas.canvas.update()
            self.master.after(150)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Warehouse Inventory Picker")
    app = WarehouseApp(root)
    root.mainloop()
