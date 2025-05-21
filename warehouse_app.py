import tkinter as tk
import numpy as np
import random
from PIL import Image, ImageTk
from astar import AStarPathfinder  # Make sure you have your AStarPathfinder implemented
from grid_canvas import GridCanvas  # Your grid drawing class


class WarehouseApp:
    def __init__(self, master, rows=10, cols=10):
        self.master = master
        self.rows = rows
        self.cols = cols
        self.cell_size = 50
        self.grid = np.zeros((rows, cols), dtype=int)

        self.warehouse_path = "Images/Warehouse.png"
        self.forklift_path = "Images/Forklift.png"
        self.crate_paths = ["Images/Crates.png", "Images/Perishable.png"]

        self.start = None
        self.current_load = 0
        self.max_load = 3

        # Left frame for canvas and controls
        left_frame = tk.Frame(master)
        left_frame.pack(side=tk.LEFT)

        self.load_label = tk.Label(left_frame, text="Load: 0 / 3", font=("Arial", 14))
        self.load_label.pack(pady=5)

        self.reset_button = tk.Button(left_frame, text="Reset", command=self.reset)
        self.reset_button.pack(pady=5)

        self.canvas = GridCanvas(
            left_frame,
            rows,
            cols,
            self.cell_size,
            self.forklift_path,
            self.crate_paths,
            self.on_start_selected,
            warehouse_image_path=self.warehouse_path
        )
        self.canvas.canvas.pack()

        # Right frame for item count display and start button
        right_frame = tk.Frame(master)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        tk.Label(right_frame, text="Items Left to Collect:", font=("Arial", 12, "bold")).pack(pady=5)

        # Load crate images for display
        self.crate_images_display = []
        for path in self.crate_paths:
            img = Image.open(path)
            img = img.resize((40, 40), Image.Resampling.LANCZOS)
            self.crate_images_display.append(ImageTk.PhotoImage(img))

        # Frame for each crate type and count
        self.crate_count_frames = []
        for i, img in enumerate(self.crate_images_display):
            frame = tk.Frame(right_frame)
            frame.pack(pady=10)

            label_img = tk.Label(frame, image=img)
            label_img.pack(side=tk.LEFT)

            label_count = tk.Label(frame, text="0", font=("Arial", 14))
            label_count.pack(side=tk.LEFT, padx=10)

            self.crate_count_frames.append(label_count)

        # Start button (initially hidden)
        self.start_button = tk.Button(
            right_frame,
            text="Start",
            command=self.start_collection,
            font=("Helvetica", 16, "bold"),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            padx=20,
            pady=10,
            relief=tk.RAISED,
            bd=4
        )
        self.start_button.pack(pady=20)
        self.start_button.pack_forget()  # hide initially

        def on_enter(e):
            self.start_button['bg'] = '#45a049'

        def on_leave(e):
            self.start_button['bg'] = '#4CAF50'

        self.start_button.bind("<Enter>", on_enter)
        self.start_button.bind("<Leave>", on_leave)

        self.reset()

    def generate_random_items(self, count=8):
        positions = set()
        while len(positions) < count:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            if (row, col) == (0, 0):
                continue
            positions.add((row, col))

        items = []
        for row, col in positions:
            # 50/50 chance for perishable or regular crate
            is_perishable = random.choice([True, False])
            img_index = 1 if is_perishable else 0
            weight = random.randint(1, 2) if is_perishable else random.randint(1, 3)
            items.append((row, col, img_index, weight))
        return items

    def update_crate_counts(self):
        counts = [0] * len(self.crate_paths)
        for item in self.items:
            counts[item[2]] += 1

        for i, count_label in enumerate(self.crate_count_frames):
            count_label.config(text=str(counts[i]))

    def reset(self):
        self.items = self.generate_random_items(count=8)
        self.canvas.items = self.items.copy()
        self.canvas.forklift_pos = None
        self.start = None
        self.current_load = 0
        self.update_load_label()
        self.update_crate_counts()
        self.canvas.draw_grid()
        self.start_button.pack_forget()  # hide start button on reset

    def update_load_label(self):
        self.load_label.config(text=f"Load: {self.current_load} / {self.max_load}")

    def on_start_selected(self, position):
        self.start = position
        # Show the start button once start position selected
        self.start_button.pack(pady=20)

    def start_collection(self):
        if not self.start:
            return

        self.start_button.pack_forget()  # hide button after start

        pathfinder = AStarPathfinder(self.grid)
        current_pos = self.start
        self.current_load = 0
        self.update_load_label()

        items_left = self.items.copy()

        def collect_next():
            nonlocal current_pos, items_left

            if not items_left:
                # Return to warehouse if load remains
                if self.current_load > 0 and current_pos != (0, 0):
                    path_back = pathfinder.find_path(current_pos, (0, 0))
                    if path_back:
                        self.animate_path(path_back, finish_return)
                    else:
                        finish_return()
                else:
                    finish_collection()
                return

            # Prioritize perishable crates
            perishable_items = [item for item in items_left if item[2] == 1]
            if perishable_items:
                closest_item = min(
                    perishable_items,
                    key=lambda item: abs(item[0] - current_pos[0]) + abs(item[1] - current_pos[1])
                )
            else:
                closest_item = min(
                    items_left,
                    key=lambda item: abs(item[0] - current_pos[0]) + abs(item[1] - current_pos[1])
                )

            goal = (closest_item[0], closest_item[1])
            crate_weight = closest_item[3]

            if self.current_load + crate_weight > self.max_load:
                # Need to unload first
                path_back = pathfinder.find_path(current_pos, (0, 0))
                if path_back:
                    self.animate_path(path_back, finish_return_and_continue)
                else:
                    finish_return_and_continue()
                return

            path_to_crate = pathfinder.find_path(current_pos, goal)
            if not path_to_crate:
                # No path, skip this crate
                items_left.remove(closest_item)
                collect_next()
                return

            # Animate path to crate
            self.animate_path(path_to_crate, lambda: after_reach_crate(closest_item, path_to_crate[-1]))

        def after_reach_crate(crate, pos):
            nonlocal current_pos, items_left
            current_pos = pos
            self.current_load += crate[3]
            self.update_load_label()
            if crate in items_left:
                items_left.remove(crate)
            self.items = items_left.copy()
            self.canvas.items = self.items.copy()
            self.update_crate_counts()
            self.canvas.draw_grid()
            collect_next()

        def finish_return():
            self.current_load = 0
            self.update_load_label()
            finish_collection()

        def finish_collection():
            # Clear path highlight at end
            self.canvas.highlight_path([])
            self.canvas.draw_grid()

        def finish_return_and_continue():
            nonlocal current_pos
            current_pos = (0, 0)
            self.current_load = 0
            self.update_load_label()
            self.canvas.draw_grid()
            collect_next()

        collect_next()

    def animate_path(self, path, callback):
        # Highlight the current path (excluding start cell)
        self.canvas.highlight_path(path[1:])

        def move_step(i):
            if i >= len(path):
                # Done moving along path
                self.canvas.highlight_path([])
                callback()
                return
            from_pos = path[i - 1] if i > 0 else path[0]
            to_pos = path[i]
            self.canvas.move_forklift(from_pos, to_pos)
            self.canvas.canvas.update()
            self.master.after(250, lambda: move_step(i + 1))

        # Start moving from step 1 (first step after start)
        move_step(1)


def center_window(win, width, height):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Warehouse Inventory Picker")

    app = WarehouseApp(root)

    window_width = app.cols * app.cell_size + 150
    window_height = app.rows * app.cell_size + 100

    center_window(root, window_width, window_height)

    root.mainloop()
