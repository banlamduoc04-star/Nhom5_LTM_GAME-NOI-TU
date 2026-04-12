import tkinter as tk
from UI import WordChainUI
from UI import run_ui_test 

root = tk.Tk()
app = WordChainUI(root)

run_ui_test(app)  # optional

root.mainloop()