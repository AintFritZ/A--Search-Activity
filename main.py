import tkinter as tk
from warehouse_app import WarehouseApp

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Warehouse Inventory Picker")
    app = WarehouseApp(root)
    root.mainloop()
