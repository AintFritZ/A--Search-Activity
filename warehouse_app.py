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

        self.warehouse_path = "Images/Warehouse.png"   # Warehouse image path
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
            self.on_start_selected,
            warehouse_image_path=self.warehouse_path  # pass warehouse image
        )

        self.canvas.items = self.items
        self.canvas.draw_grid()

    def generate_random_items(self, count=5):
        positions = set()
        while len(positions) < count:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            if (row, col) == (0, 0):
                continue  # Prevent crates at warehouse position
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
        current_pos = self.start

        while self.items:
            # Find closest crate by Manhattan distance
            closest_item = min(
                self.items,
                key=lambda item: abs(item[0] - current_pos[0]) + abs(item[1] - current_pos[1])
            )
            goal = (closest_item[0], closest_item[1])

            path = pathfinder.find_path(current_pos, goal)
            if not path:
                # No path found; remove this item and continue
                self.items.remove(closest_item)
                self.canvas.items = self.items
                continue

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
