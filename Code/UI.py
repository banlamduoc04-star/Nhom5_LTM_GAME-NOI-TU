"""
Word Chain Game — GUI Client
Dark theme, clean layout, polished UX.
"""

import tkinter as tk
from tkinter import font as tkfont
import socket
import threading
import json

# ══════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════

SERVER_HOST = '127.0.0.1'
SERVER_PORT  = 5000

# ── Palette ───────────────────────────────────────────
BG       = "#0F1117"
BG2      = "#181B24"
BG3      = "#1E2130"
BORDER   = "#2A2F42"
ACCENT   = "#4F8EF7"
ACCENT2  = "#7B5CF7"
SUCCESS  = "#3DD68C"
WARNING  = "#F7C948"
DANGER   = "#F75A5A"
FG       = "#E8EAF0"
FG2      = "#8B91A8"
FG3      = "#4A5070"

# ── Fonts ─────────────────────────────────────────────
F_LABEL   = ("Segoe UI", 10)
F_LABEL_B = ("Segoe UI", 10, "bold")
F_SMALL   = ("Segoe UI", 8, "bold")
F_WORD    = ("Segoe UI", 18, "bold")
F_CHIP    = ("Segoe UI", 13, "bold")
F_TIMER   = ("Segoe UI", 28, "bold")
F_HISTORY = ("Consolas", 10)
F_INPUT   = ("Segoe UI", 13)
F_BTN     = ("Segoe UI", 10, "bold")


# ══════════════════════════════════════════════════════
#  FLAT BUTTON  (canvas-based, hover effect)
# ══════════════════════════════════════════════════════

class FlatButton(tk.Frame):
    def __init__(self, parent, text, command,
                 bg=ACCENT, fg=FG, hover_bg=None,
                 width=None, height=36, **kw):
        super().__init__(parent, bg=parent["bg"] if "bg" in parent.keys() else BG, **kw)
        self._bg       = bg
        self._hover_bg = hover_bg or self._darken(bg)
        self._fg       = fg
        self._cmd      = command
        self._text     = text
        self._hovered  = False

        cfg = dict(bg=BG, highlightthickness=0, cursor="hand2", height=height)
        if width:
            cfg["width"] = width
        self._c = tk.Canvas(self, **cfg)
        self._c.pack(fill="both", expand=True)

        self._c.bind("<Configure>",       self._draw)
        self._c.bind("<Enter>",           lambda _: self._hover(True))
        self._c.bind("<Leave>",           lambda _: self._hover(False))
        self._c.bind("<ButtonRelease-1>", lambda _: self._cmd and self._cmd())

    @staticmethod
    def _darken(h):
        r, g, b = int(h[1:3],16), int(h[3:5],16), int(h[5:7],16)
        return "#{:02x}{:02x}{:02x}".format(
            max(0,int(r*.78)), max(0,int(g*.78)), max(0,int(b*.78)))

    def _hover(self, on):
        self._hovered = on
        self._draw()

    def _draw(self, _=None):
        c = self._c
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        if w < 2: return
        fill = self._hover_bg if self._hovered else self._bg
        r = 6
        c.create_polygon(
            r,0, w-r,0, w,0, w,r, w,h-r, w,h,
            w-r,h, r,h, 0,h, 0,h-r, 0,r, 0,0,
            smooth=True, fill=fill, outline="")
        c.create_text(w//2, h//2, text=self._text, fill=self._fg, font=F_BTN)


# ══════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════

class GameUI:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Nối Từ")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.sock         = None
        self.name         = None
        self.running      = False
        self.current_word = None
        self.next_letter  = ""
        self.your_turn    = False
        self.timer        = 30
        self.timer_job    = None
        self._dot_job     = None

        self._build_login()

    # ─── lifecycle ────────────────────────────────────

    def on_close(self):
        self.running = False
        self._close_socket()
        self.root.destroy()

    def _close_socket(self):
        if self.sock:
            try: self.sock.close()
            except Exception: pass
            self.sock = None

    def _clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    # ── layout helpers ────────────────────────────────

    @staticmethod
    def _card(parent, accent_color=ACCENT, padx=24, pady=20):
        outer = tk.Frame(parent, bg=BG2)
        tk.Frame(outer, bg=accent_color, height=2).pack(fill="x")
        inner = tk.Frame(outer, bg=BG2, padx=padx, pady=pady)
        inner.pack(fill="both", expand=True)
        return outer, inner

    @staticmethod
    def _label(parent, text, font=F_LABEL, fg=FG, bg=BG2, **kw):
        return tk.Label(parent, text=text, font=font, fg=fg, bg=bg, **kw)

    @staticmethod
    def _row(parent, bg=BG):
        f = tk.Frame(parent, bg=bg)
        f.pack(fill="x")
        return f

    @staticmethod
    def _divider(parent, color=BORDER):
        tk.Frame(parent, bg=color, height=1).pack(fill="x")

    @staticmethod
    def _gap(parent, h=8, bg=BG):
        tk.Frame(parent, bg=bg, height=h).pack()

    @staticmethod
    def _styled_entry(parent):
        """Bordered entry field."""
        wrap = tk.Frame(parent, bg=BORDER, pady=1)
        wrap.pack(fill="x")
        inner = tk.Frame(wrap, bg=BG3, padx=1, pady=1)
        inner.pack(fill="x")
        e = tk.Entry(inner, font=F_INPUT, bg=BG3, fg=FG,
                     insertbackground=ACCENT, relief="flat", bd=0,
                     disabledbackground=BG3, disabledforeground=FG3)
        e.pack(fill="x", ipady=8, padx=8)
        return e, wrap
    
    def _build_waiting(self):
        self._clear()
        self.root.geometry("400x500")

        tk.Frame(self.root, bg=ACCENT, height=3).pack(fill="x")

        body = tk.Frame(self.root, bg=BG, padx=30, pady=30)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="🔍", font=("Segoe UI", 40), bg=BG).pack(pady=10)

        tk.Label(body, text="ĐANG TÌM ĐỐI THỦ",
                font=("Segoe UI", 16, "bold"),
                bg=BG, fg=FG).pack()

        self._waiting_var = tk.StringVar()
        tk.Label(body, textvariable=self._waiting_var,
                font=F_LABEL, bg=BG, fg=FG2).pack(pady=10)

        FlatButton(body, "HUỶ TÌM TRẬN", self._cancel_waiting, bg=BG3, fg=FG2, height=45).pack(fill="x", pady=20)

        self._start_waiting_anim()
        
    def _start_waiting_anim(self):
        self._wait_step = 0
        self._animate_waiting()

    def _animate_waiting(self):
        if not self.running:
            return

        frames = ["●○○", "●●○", "●●●", "○●●", "○○●"]
        frame = frames[self._wait_step % len(frames)]

        if hasattr(self, '_waiting_var'):
            self._waiting_var.set(f"Đang tìm đối thủ  {frame}")

        self._wait_step += 1
        self._dot_job = self.root.after(400, self._animate_waiting)
    
    def _cancel_waiting(self):
        self.running = False
        self._close_socket()
        self._build_login()

    # ══════════════════════════════════════════════════
    #  SCREEN: LOGIN
    # ══════════════════════════════════════════════════

    def _build_login(self):
        self._clear()
        self.stop_timer()
        if self._dot_job:
            self.root.after_cancel(self._dot_job)
        self.root.geometry("380x440")

        # accent stripe at top
        tk.Frame(self.root, bg=ACCENT, height=3).pack(fill="x")

        # logo block
        logo = tk.Frame(self.root, bg=BG, pady=28)
        logo.pack()

        cv = tk.Canvas(logo, width=64, height=64, bg=BG, highlightthickness=0)
        cv.pack()
        cv.create_polygon(32,2, 58,16, 58,48, 32,62, 6,48, 6,16,
                          fill=BG2, outline=ACCENT, width=2)
        cv.create_text(32, 32, text="🔗", font=("Segoe UI", 20))

        tk.Label(logo, text="NỐI TỪ", font=("Segoe UI", 24, "bold"),
                 bg=BG, fg=FG).pack(pady=(8,2))
        tk.Label(logo, text="Vietnamese Word Chain", font=("Segoe UI", 10),
                 bg=BG, fg=FG2).pack()

        # form card
        outer, form = self._card(self.root, ACCENT, padx=28, pady=22)
        outer.pack(fill="x", padx=28)

        self._label(form, "TÊN NGƯỜI CHƠI", F_SMALL, FG3).pack(anchor="w")
        self._gap(form, 4, BG2)
        self._name_entry, _ = self._styled_entry(form)
        self._name_entry.bind("<Return>", lambda _: self._do_connect())
        self._name_entry.focus()

        self._gap(form, 14, BG2)
        FlatButton(form, "  TÌM TRẬN  ", self._do_connect,
                   bg=ACCENT, height=40).pack(fill="x")

        self._status_var = tk.StringVar()
        self._status_lbl = tk.Label(self.root, textvariable=self._status_var,
                                    font=F_LABEL, bg=BG, fg=FG2)
        self._status_lbl.pack(pady=10)

        tk.Label(self.root, text=f"{SERVER_HOST}:{SERVER_PORT}",
                 font=("Segoe UI", 9), bg=BG, fg=FG3).pack(side="bottom", pady=10)

    # ══════════════════════════════════════════════════
    #  SCREEN: GAME
    # ══════════════════════════════════════════════════

    def _build_game(self):
        self._clear()
        self.root.geometry("460x590")

        # ── top bar ──────────────────────────────────
        bar = tk.Frame(self.root, bg=BG2)
        bar.pack(fill="x")
        tk.Frame(bar, bg=ACCENT, height=2).pack(fill="x")
        bar_inner = tk.Frame(bar, bg=BG2, padx=16, pady=9)
        bar_inner.pack(fill="x")
        tk.Label(bar_inner, text="🔗  NỐI TỪ", font=("Segoe UI", 11, "bold"),
                 bg=BG2, fg=FG).pack(side="left")
        self._turn_badge = tk.Label(bar_inner, text="", font=("Segoe UI", 9, "bold"),
                                     bg=BG3, fg=FG2, padx=10, pady=3)
        self._turn_badge.pack(side="right")

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")

        # ── body ─────────────────────────────────────
        body = tk.Frame(self.root, bg=BG, padx=18, pady=4)
        body.pack(fill="both", expand=True)

        # word card
        outer, wcard = self._card(body, ACCENT2, padx=18, pady=14)
        outer.pack(fill="x", pady=(10, 6))
        self._label(wcard, "TỪ HIỆN TẠI", F_SMALL, FG3).pack()
        self._word_lbl = tk.Label(wcard, text="—", font=F_WORD, bg=BG2, fg=FG)
        self._word_lbl.pack(pady=(6, 10))

        chip_row = tk.Frame(wcard, bg=BG2)
        chip_row.pack()
        self._label(chip_row, "TIẾP THEO", F_SMALL, FG3, BG2).pack(side="left", padx=(0,8))
        self._chip = tk.Label(chip_row, text="—", font=F_CHIP,
                               bg=ACCENT2, fg=FG, padx=12, pady=2)
        self._chip.pack(side="left")

        # timer row
        trow = tk.Frame(body, bg=BG)
        trow.pack(fill="x", pady=(8, 2))
        tk.Label(trow, text="⏱", font=("Segoe UI", 12), bg=BG, fg=FG2).pack(side="left")
        self._timer_lbl = tk.Label(trow, text="30", font=F_TIMER, bg=BG, fg=SUCCESS)
        self._timer_lbl.pack(side="left", padx=4)
        tk.Label(trow, text="giây", font=F_LABEL, bg=BG, fg=FG2).pack(side="left")
        self._turn_info = tk.Label(trow, text="", font=("Segoe UI", 10, "bold"), bg=BG, fg=FG2)
        self._turn_info.pack(side="right")

        # history
        self._label(body, "LỊCH SỬ", F_SMALL, FG3, BG).pack(anchor="w", pady=(6,2))
        hist_wrap = tk.Frame(body, bg=BORDER, pady=1, padx=1)
        hist_wrap.pack(fill="x")
        hist_inner = tk.Frame(hist_wrap, bg=BG3)
        hist_inner.pack(fill="both")
        self._hist = tk.Text(hist_inner, height=7, font=F_HISTORY, bg=BG3, fg=FG2,
                              relief="flat", bd=0, selectbackground=ACCENT,
                              padx=10, pady=8, state="disabled")
        sc = tk.Scrollbar(hist_inner, command=self._hist.yview,
                           bg=BG3, troughcolor=BG3, activebackground=BORDER)
        self._hist.configure(yscrollcommand=sc.set)
        self._hist.pack(side="left", fill="both", expand=True)
        sc.pack(side="right", fill="y")

        # input
        irow = tk.Frame(body, bg=BG)
        irow.pack(fill="x", pady=(10,4))
        self._entry, _ = self._styled_entry(irow)
        _ .pack_configure(side="left", expand=True, fill="x")
        self._entry.bind("<Return>", lambda _: self._send_word())
        FlatButton(irow, "GỬI", self._send_word,
                   bg=SUCCESS, fg="#0F1117", width=68, height=40).pack(side="left", padx=(6,0))

        # error
        self._error_var = tk.StringVar()
        tk.Label(body, textvariable=self._error_var,
                 font=F_LABEL, bg=BG, fg=DANGER).pack(anchor="w")

        # give up
        self._divider(body)
        FlatButton(body, "ĐẦU HÀNG", self._give_up,
                   bg=BG3, fg=FG3, hover_bg=DANGER, height=30).pack(fill="x", pady=6)

    # ══════════════════════════════════════════════════
    #  SCREEN: GAME OVER
    # ══════════════════════════════════════════════════

    def _build_end(self, you_win, reason, score):
        self._clear()
        self.root.geometry("400x500")

        stripe = SUCCESS if you_win else DANGER
        tk.Frame(self.root, bg=stripe, height=4).pack(fill="x")

        body = tk.Frame(self.root, bg=BG, padx=36)
        body.pack(fill="both", expand=True)
        self._gap(body, 24)

        icon  = "🏆" if you_win else "💀"
        title = "CHIẾN THẮNG" if you_win else "THẤT BẠI"
        color = SUCCESS if you_win else DANGER

        tk.Label(body, text=icon, font=("Segoe UI", 44), bg=BG).pack()
        tk.Label(body, text=title, font=("Segoe UI", 22, "bold"), bg=BG, fg=color).pack(pady=(4,0))
        if reason:
            tk.Label(body, text=reason, font=("Segoe UI", 10), bg=BG, fg=FG2,
                     wraplength=300, justify="center").pack(pady=4)

        self._divider(body)
        self._gap(body, 6)

        if score:
            for player, pts in score.items():
                row = tk.Frame(body, bg=BG2, padx=14, pady=8)
                row.pack(fill="x", pady=2)
                tk.Label(row, text=player, font=F_LABEL_B, bg=BG2, fg=FG).pack(side="left")
                tk.Label(row, text=f"{pts} từ", font=F_LABEL, bg=BG2, fg=ACCENT).pack(side="right")
            self._gap(body, 8)

        FlatButton(body, "  CHƠI LẠI  ", self._rematch, bg=ACCENT, height=40).pack(fill="x", pady=(0,6))
        FlatButton(body, "  THOÁT  ", self.on_close, bg=BG3, fg=FG2, height=34).pack(fill="x")
        self._gap(body, 14)

    # ══════════════════════════════════════════════════
    #  NETWORK
    # ══════════════════════════════════════════════════

    def _do_connect(self):
        self.name = self._name_entry.get().strip()
        if not self.name:
            self._set_status("⚠  Vui lòng nhập tên!", WARNING)
            return

        self._close_socket()
        self.running = False

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5)
            self.sock.connect((SERVER_HOST, SERVER_PORT))
            self.sock.settimeout(None)
        except Exception as e:
            self._set_status(f"✗  Không kết nối được: {e}", DANGER)
            self._close_socket()
            return

        self._send_raw({"type": "name", "value": self.name})
        self.running = True
        threading.Thread(target=self._listen, daemon=True).start()
        self._start_dot_anim()

    def _listen(self):
        buf = ""
        while self.running:
            try:
                data = self.sock.recv(4096)
                if not data: break
                buf += data.decode("utf-8")
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    line = line.strip()
                    if line:
                        try: self._handle(json.loads(line))
                        except json.JSONDecodeError: pass
            except Exception:
                break

        if self.running:
            self.running = False
            self.root.after(0, self._on_disconnected)

    def _on_disconnected(self):
        self.stop_timer()
        self._build_login()
        self._set_status("✗  Mất kết nối tới server", DANGER)

    def _send_raw(self, data):
        if self.sock:
            try:
                self.sock.sendall(
                    (json.dumps(data, ensure_ascii=False) + "\n").encode("utf-8"))
            except Exception: pass

    # ══════════════════════════════════════════════════
    #  HANDLER
    # ══════════════════════════════════════════════════

    def _handle(self, msg):
        t = msg.get("type")

        if t == "game_start":
            self.current_word = msg.get("current_word")
            self.next_letter  = msg.get("next_letter", "")
            self.your_turn    = msg.get("your_turn", False)
            if self._dot_job:
                self.root.after_cancel(self._dot_job)
            self.root.after(0, self._build_game)
            self.root.after(80, self._refresh_ui)
            cw = self.current_word
            if cw:
                self.root.after(80, lambda: self._push_history("📌 Từ mở đầu", cw, "starter"))
            self.root.after(80, self.reset_timer)

        elif t == "word_accepted":
            self.current_word = msg.get("word", "")
            self.next_letter  = msg.get("next_letter", "")
            self.your_turn    = msg.get("your_turn", False)
            player = msg.get("player", "?")
            word   = self.current_word
            tag    = "me" if player == self.name else "opp"
            self.root.after(0, lambda: self._push_history(player, word, tag))
            self.root.after(0, self._refresh_ui)
            self.root.after(0, self.reset_timer)
            self.root.after(0, lambda: self._error_var.set("") if hasattr(self,'_error_var') else None)

        elif t == "game_over":
            self.stop_timer()
            self.running = False
            yw = msg.get("you_win", False)
            rs = msg.get("reason", "")
            sc = msg.get("score", {})
            self.root.after(0, lambda: self._build_end(yw, rs, sc))

        elif t == "error":
                    err = msg.get("message", "Lỗi")
                    if not self.current_word:
                        self.running = False
                        self._close_socket()
                        self.root.after(0, self._build_login)
                        self.root.after(100, lambda: self._set_status(f"x {err}", DANGER))
                    else:
                        self.root.after(0, lambda: self._error_var.set(f"⚠  {err}") if hasattr(self,'_error_var') else None)

        elif t in ("opponent_disconnected", "opponent_eliminated"):
            self.stop_timer()
            self.running = False
            reason = msg.get("message", "Đối thủ đã thoát")
            self.root.after(0, lambda: self._build_end(True, reason, {}))

    # ══════════════════════════════════════════════════
    #  UI HELPERS
    # ══════════════════════════════════════════════════

    def _refresh_ui(self):
        if not hasattr(self, '_word_lbl') or not self._word_lbl.winfo_exists():
            return

        self._word_lbl.config(text=f"«  {self.current_word}  »" if self.current_word else "—")
        self._chip.config(text=f" {self.next_letter} " if self.next_letter else "—")

        if self.your_turn:
            self._turn_badge.config(text=" Lượt của bạn ", bg=ACCENT, fg=FG)
            self._turn_info.config(text="✏  Nhập từ", fg=ACCENT)
            self._entry.config(state="normal")
            self._entry.focus()
        else:
            self._turn_badge.config(text=" Chờ đối thủ ", bg=BG3, fg=FG2)
            self._turn_info.config(text="⏳  Đang chờ", fg=FG2)
            self._entry.config(state="disabled")

    def _push_history(self, player, word, tag="opp"):
        if not hasattr(self, '_hist') or not self._hist.winfo_exists():
            return
        self._hist.config(state="normal")
        self._hist.tag_config("starter", foreground=WARNING,  font=("Consolas", 10, "bold"))
        self._hist.tag_config("me",      foreground=SUCCESS)
        self._hist.tag_config("opp",     foreground=FG2)

        prefix = {"starter": "📌", "me": "✅", "opp": "🔵"}.get(tag, "▸")
        self._hist.insert(tk.END, f"  {prefix}  {player}  →  {word}\n", tag)
        self._hist.config(state="disabled")
        self._hist.see(tk.END)

    def _send_word(self):
        if not self.your_turn: return
        word = self._entry.get().strip()
        if hasattr(self, '_error_var'): self._error_var.set("")
        if not word:
            if hasattr(self, '_error_var'): self._error_var.set("⚠  Chưa nhập từ!")
            return
        if len(word.split()) < 2:
            if hasattr(self, '_error_var'): self._error_var.set("⚠  Nhập cụm từ ít nhất 2 tiếng (vd: xe máy)")
            return
        self._send_raw({"type": "word", "value": word})
        self._entry.delete(0, tk.END)

    def _give_up(self):
        self._send_raw({"type": "giveup"})

    def _rematch(self):
        self.running = False
        self._close_socket()

        # hiện màn chờ
        self._build_waiting()

        # reconnect
        self._do_reconnect()
    
    def _do_reconnect(self):
        if not self.name:
            self._build_login()
            return

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5)
            self.sock.connect((SERVER_HOST, SERVER_PORT))
            self.sock.settimeout(None)
        except Exception as e:
            self._set_status(f"✗  Không kết nối được: {e}", DANGER)
            self._close_socket()
            return

        # 🔥 gửi lại tên cũ
        self._send_raw({"type": "name", "value": self.name})

        self.running = True
        threading.Thread(target=self._listen, daemon=True).start()
        

    def _set_status(self, text, color=FG2):
        if hasattr(self, '_status_var'):
            self._status_var.set(text)
            self._status_lbl.config(fg=color)

    # ── dot animation while waiting ───────────────────

    def _start_dot_anim(self):
        self._dot_step = 0
        self._animate()

    def _animate(self):
        if not self.running or not hasattr(self, '_status_var'):
            return
        frames = ["●○○", "●●○", "●●●", "○●●", "○○●", "○○○"]
        frame = frames[self._dot_step % len(frames)]
        self._set_status(f"Đang tìm đối thủ  {frame}")
        self._dot_step += 1
        self._dot_job = self.root.after(350, self._animate)

    # ── timer ─────────────────────────────────────────

    def reset_timer(self):
        self.stop_timer()
        self.timer = 30
        self._tick()

    def _tick(self):
        if not hasattr(self, '_timer_lbl') or not self._timer_lbl.winfo_exists():
            return
        color = SUCCESS if self.timer > 15 else WARNING if self.timer > 7 else DANGER
        self._timer_lbl.config(text=str(self.timer), fg=color)
        if self.timer <= 0: return
        self.timer -= 1
        self.timer_job = self.root.after(1000, self._tick)

    def stop_timer(self):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None


# ══════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════

if __name__ == "__main__":
    try:                                   # Windows DPI fix
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    root = tk.Tk()
    app  = GameUI(root)
    root.mainloop()
