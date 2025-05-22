import tkinter as tk
import numpy as np
import random
import time
import tkinter.messagebox as messagebox
from PIL import Image, ImageTk
from astar import AStarPathfinder
from astar_no_heuristic import AStarPathfinderNoHeuristic
from grid_canvas import GridCanvas


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

        self.is_running = False

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

        right_frame = tk.Frame(master)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        tk.Label(right_frame, text="Items Left to Collect:", font=("Arial", 12, "bold")).pack(pady=5)

        self.crate_images_display = []
        for path in self.crate_paths:
            img = Image.open(path)
            img = img.resize((40, 40), Image.Resampling.LANCZOS)
            self.crate_images_display.append(ImageTk.PhotoImage(img))

        self.crate_count_frames = []
        for i, img in enumerate(self.crate_images_display):
            frame = tk.Frame(right_frame)
            frame.pack(pady=10)

            label_img = tk.Label(frame, image=img)
            label_img.pack(side=tk.LEFT)

            label_count = tk.Label(frame, text="0", font=("Arial", 14))
            label_count.pack(side=tk.LEFT, padx=10)

            self.crate_count_frames.append(label_count)

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
        self.start_button.pack(pady=10)
        self.start_button.pack_forget()

        def on_enter(e):
            self.start_button['bg'] = '#45a049'

        def on_leave(e):
            self.start_button['bg'] = '#4CAF50'

        self.start_button.bind("<Enter>", on_enter)
        self.start_button.bind("<Leave>", on_leave)

        # Dropdown for algorithm selection
        tk.Label(right_frame, text="Choose Algorithm:", font=("Arial", 12, "bold")).pack(pady=(20, 5))
        self.algorithm_var = tk.StringVar(value="A*")
        self.algorithm_dropdown = tk.OptionMenu(right_frame, self.algorithm_var, "A*", "Dijkstra (No Heuristic)")
        self.algorithm_dropdown.config(font=("Arial", 12))
        self.algorithm_dropdown.pack()

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
        self.is_running = False
        self.items = self.generate_random_items(count=8)
        self.canvas.items = self.items.copy()
        self.canvas.highlighted_path = []
        self.canvas.forklift_pos = None
        self.start = None
        self.current_load = 0
        self.update_load_label()
        self.update_crate_counts()
        self.canvas.draw_grid()
        self.start_button.pack_forget()

    def update_load_label(self):
        self.load_label.config(text=f"Load: {self.current_load} / {self.max_load}")

    def on_start_selected(self, position):
        self.start = position
        self.start_button.pack(pady=10)

    def start_collection(self):
        if self.is_running or not self.start:
            return

        self.is_running = True

        # Select algorithm & prioritization based on dropdown
        if self.algorithm_var.get() == "A*":
            pathfinder = AStarPathfinder(self.grid)
            prioritize_perishable = True
        else:
            pathfinder = AStarPathfinderNoHeuristic(self.grid)
            prioritize_perishable = False

        current_pos = self.start
        self.current_load = 0
        self.update_load_label()

        start_time = time.time()

        while self.items and self.is_running:
            if prioritize_perishable:
                perishable_items = [item for item in self.items if item[2] == 1]
                if perishable_items:
                    closest_item = min(
                        perishable_items,
                        key=lambda item: abs(item[0] - current_pos[0]) + abs(item[1] - current_pos[1])
                    )
                else:
                    closest_item = min(
                        self.items,
                        key=lambda item: abs(item[0] - current_pos[0]) + abs(item[1] - current_pos[1])
                    )
            else:
                closest_item = min(
                    self.items,
                    key=lambda item: abs(item[0] - current_pos[0]) + abs(item[1] - current_pos[1])
                )

            goal = (closest_item[0], closest_item[1])
            crate_weight = closest_item[3]

            if not self.is_running:
                break

            if self.current_load + crate_weight > self.max_load:
                path_back = pathfinder.find_path(current_pos, (0, 0))
                if path_back:
                    self.highlight_and_move_path(path_back, current_pos)
                    current_pos = (0, 0)
                self.current_load = 0
                self.update_load_label()

            if not self.is_running:
                break

            path = pathfinder.find_path(current_pos, goal)
            if not path:
                self.items.remove(closest_item)
                self.canvas.items = self.items
                self.update_crate_counts()
                continue

            self.highlight_and_move_path(path, current_pos)
            current_pos = goal

            self.current_load += crate_weight
            self.update_load_label()

            self.canvas.clear_crate(goal)
            self.items = [i for i in self.items if (i[0], i[1]) != goal]
            self.canvas.items = self.items
            self.update_crate_counts()

            self.canvas.canvas.update()
            self.master.after(150)

        if self.is_running and self.current_load > 0 and current_pos != (0, 0):
            path_back = pathfinder.find_path(current_pos, (0, 0))
            if path_back:
                self.highlight_and_move_path(path_back, current_pos)
                current_pos = (0, 0)
            self.current_load = 0
            self.update_load_label()

        self.is_running = False

        elapsed_time = time.time() - start_time
        messagebox.showinfo("Performance", f"Collection completed in {elapsed_time:.2f} seconds.")

    def highlight_and_move_path(self, path, start_pos):
        self.canvas.highlighted_path = path[1:]
        self.canvas.draw_grid()
        self.canvas.canvas.update()
        self.master.after(800)

        current_pos = start_pos
        for step in path[1:]:
            if not self.is_running:
                break
            self.canvas.move_forklift(current_pos, step)
            self.canvas.canvas.update()
            self.master.after(150)
            current_pos = step

        self.canvas.highlighted_path = []
        self.canvas.draw_grid()


def center_window(win, width, height):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Warehouse Collection App")
    center_window(root, 1000, 650)
    app = WarehouseApp(root)
    root.mainloop()
