import tkinter as tk
from tkinter import messagebox
import socket
import threading
import json

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000


class GameUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Word Chain Game")

        self.sock = None
        self.name = ""
        self.running = False

        self.current_word = None
        self.next_letter = ""
        self.your_turn = False

        self.timer = 30
        self.timer_job = None

        self.build_login()

    # ================= UI =================
    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def build_login(self):
        self.clear()

        tk.Label(self.root, text="Nhập tên").pack()
        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack()

        tk.Button(self.root, text="Tìm trận", command=self.connect).pack()
        self.status = tk.Label(self.root, text="")
        self.status.pack()

    def build_game(self):
        self.clear()

        self.info = tk.Label(self.root, text="")
        self.info.pack()

        self.word_label = tk.Label(self.root, text="", font=("Arial", 16))
        self.word_label.pack()

        self.timer_label = tk.Label(self.root, text="Time: 30")
        self.timer_label.pack()

        self.history = tk.Text(self.root, height=10, width=40)
        self.history.pack()
        self.history.config(state='disabled')

        self.entry = tk.Entry(self.root)
        self.entry.pack()
        self.entry.bind("<Return>", lambda event: self.send_word())
        self.error_label = tk.Label(self.root, text="", fg="red")
        self.error_label.pack()

        tk.Button(self.root, text="Gửi", command=self.send_word).pack()
        tk.Button(self.root, text="Đầu hàng", command=self.give_up).pack()

    def build_end(self, text):
        self.clear()

        tk.Label(self.root, text=text).pack()
        tk.Button(self.root, text="Chơi lại", command=self.rematch).pack()
        tk.Button(self.root, text="Thoát", command=self.root.quit).pack()

    # ================= NETWORK =================
    def connect(self):
        self.name = self.name_entry.get().strip()
        if not self.name:
            messagebox.showerror("Lỗi", "Nhập tên!")
            return

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((SERVER_HOST, SERVER_PORT))

        self.send({"type": "name", "value": self.name})

        self.status.config(text="Đang tìm trận...")
        self.running = True

        threading.Thread(target=self.listen, daemon=True).start()

    def listen(self):
        buffer = ""
        while self.running:
            try:
                data = self.sock.recv(1024).decode()
                if not data:
                    break

                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        self.handle(json.loads(line))
            except:
                break

    def send(self, data):
        self.sock.sendall((json.dumps(data) + '\n').encode())

    # ================= GAME =================
    def handle(self, msg):
        t = msg.get("type")

        if t == "game_start":
            self.current_word = None
            self.your_turn = msg["your_turn"]

            self.root.after(0, self.build_game)
            self.root.after(100, self.update_ui)
            self.reset_timer()

        elif t == "word_accepted":
            self.current_word = msg["word"]
            self.next_letter = msg["next_letter"]
            self.your_turn = msg["your_turn"]

            player = msg.get("player", "???")
            self.root.after(0, lambda: self.add_history(player, self.current_word))

            self.root.after(0, self.update_ui)
            self.reset_timer()

        elif t == "game_over":
            result = "Bạn thắng!" if msg.get("you_win") else "Bạn thua!"
            reason = msg.get("reason", "")

            self.stop_timer()
            self.root.after(0, lambda: self.build_end(f"{result}\n{reason}"))

        elif t == "error":
            error_msg = msg.get("message")
            self.root.after(0, lambda: self.error_label.config(text=error_msg))

    def update_ui(self):
        if self.current_word is None:
            self.word_label.config(text=" Nhập từ bắt đầu (2 từ)")
        else:
            self.word_label.config(
                text=f"Từ: {self.current_word}\nNối bằng: {self.next_letter}"
            )

        self.info.config(
            text=" Lượt bạn" if self.your_turn else " Chờ đối thủ"
        )

    def add_history(self, player, word):
        self.history.config(state='normal')
        self.history.insert(tk.END, f"{player}: {word}\n")
        self.history.config(state='disabled')
        self.history.see(tk.END)

    def send_word(self):
        if not self.your_turn:
            messagebox.showwarning("Lỗi", "Chưa tới lượt bạn!")
            return

        word = self.entry.get().strip()
        self.error_label.config(text="")

        if len(word.split()) < 2:
            messagebox.showwarning("Lỗi", "Phải nhập 2 từ!")
            return

        self.send({"type": "word", "value": word})
        self.entry.delete(0, tk.END)

    def give_up(self):
        self.send({"type": "giveup"})

    def rematch(self):
        self.send({"type": "rematch"})
        self.build_login()

    # ================= TIMER =================
    def reset_timer(self):
        self.stop_timer()
        self.timer = 30
        self.run_timer()

    def run_timer(self):
        self.timer_label.config(text=f"Time: {self.timer}")

        if self.timer <= 0:
            return

        self.timer -= 1
        self.timer_job = self.root.after(1000, self.run_timer)

    def stop_timer(self):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None


# ================= MAIN =================
if __name__ == "__main__":
    root = tk.Tk()
    app = GameUI(root)
    root.mainloop()