import tkinter as tk
from tkinter import ttk

class WordChainUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Word Chain Game")
        self.root.geometry("500x600")
        self.root.configure(bg="#f3f4f6")

        self.build_ui()

    def build_ui(self):
        # ===== TOP BAR =====
        top_frame = tk.Frame(self.root, bg="#e5e7eb", padx=10, pady=10)
        top_frame.pack(fill="x", pady=10, padx=10)

        tk.Label(top_frame, text="🏠", bg="#e5e7eb").pack(side="left")

        right_frame = tk.Frame(top_frame, bg="#e5e7eb")
        right_frame.pack(side="right")

        self.score_label = tk.Label(right_frame, text="Điểm: 0", bg="white", padx=10)
        self.score_label.pack(side="left", padx=5)

        self.skip_btn = tk.Button(right_frame, text="Bỏ qua")
        self.skip_btn.pack(side="left", padx=5)

        # ===== TIMER =====
        timer_frame = tk.Frame(self.root, bg="white", padx=15, pady=15)
        timer_frame.pack(fill="x", padx=10, pady=5)

        self.time_label = tk.Label(timer_frame, text="00:60", font=("Arial", 14, "bold"))
        self.time_label.pack(anchor="w")

        self.progress = ttk.Progressbar(timer_frame, length=400)
        self.progress.pack(pady=5)

        # ===== WORD DISPLAY =====
        word_frame = tk.Frame(self.root, bg="white", padx=20, pady=30)
        word_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(word_frame, text="ACTIVE WORD", fg="gray", bg="white").pack()

        self.word_label = tk.Label(
            word_frame,
            text="kiểu càng",
            font=("Arial", 24, "bold"),
            bg="white"
        )
        self.word_label.pack()

        # ===== INPUT =====
        input_frame = tk.Frame(self.root, bg="white", padx=15, pady=15)
        input_frame.pack(fill="x", padx=10, pady=10)

        box = tk.Frame(input_frame, bg="#ddd")
        box.pack(fill="x")

        self.prefix_label = tk.Label(box, text="càng", bg="#4f46e5", fg="white", padx=10)
        self.prefix_label.pack(side="left")

        self.input_entry = tk.Entry(box)
        self.input_entry.pack(side="left", fill="x", expand=True)

        self.send_btn = tk.Button(box, text="Gửi")
        self.send_btn.pack(side="right")

        tk.Label(input_frame, text="Enter: Gửi | Esc: Bỏ qua", fg="gray", bg="white").pack()

        # ===== LOG / CHAT =====
        log_frame = tk.Frame(self.root)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.log_box = tk.Text(log_frame, height=10)
        self.log_box.pack(fill="both", expand=True)

    # ===== HÀM UPDATE UI (để bạn gắn backend) =====
    def set_word(self, word):
        self.word_label.config(text=word)

    def set_prefix(self, prefix):
        self.prefix_label.config(text=prefix)

    def set_time(self, time_str):
        self.time_label.config(text=time_str)

    def set_score(self, score):
        self.score_label.config(text=f"Điểm: {score}")

    def log(self, message):
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
import threading
import time

# ===== TIMER =====
def test_timer(ui, start=60):
    def run():
        t = start
        while t >= 0:
            ui.set_time(f"00:{t:02}")
            t -= 1
            time.sleep(1)
    threading.Thread(target=run, daemon=True).start()


# ===== USER INPUT HANDLER =====
def bind_user_input(ui):
    current_word = ["kiểu càng"]  # dùng list để mutable

    def on_send():
        word = ui.input_entry.get().strip().lower()

        if not word:
            ui.log("Nhập từ!")
            return

        last_word = current_word[0].split()[-1]
        last_char = last_word[-1]
        first_char = word[0]

        if last_char != first_char:
            ui.log(f"Sai luật! Phải bắt đầu bằng '{last_char}'")
            return

        # hợp lệ
        new_word = last_word + " " + word
        current_word[0] = new_word

        ui.set_word(new_word)
        ui.set_prefix(word)
        ui.log(f"YOU: {word} ")

        ui.input_entry.delete(0, 'end')

    # bind nút
    ui.send_btn.config(command=on_send)

    # bind Enter
    ui.input_entry.bind("<Return>", lambda e: on_send())


# ===== RUN TEST =====
def run_ui_test(ui):
    test_timer(ui)
    bind_user_input(ui)


# ===== RUN UI =====
if __name__ == "__main__":
    root = tk.Tk()
    app = WordChainUI(root)
    root.mainloop()