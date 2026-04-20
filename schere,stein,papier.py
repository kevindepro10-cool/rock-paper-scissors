import tkinter as tk
import random
import platform
from typing import Literal

# ── Schrift (kein zweites Tk-Fenster, plattformbasiert) ───────────────────────
_OS = platform.system()
if _OS == "Windows":
    BIG_SYMBOL = ("Segoe UI Symbol", 52, "bold")
elif _OS == "Darwin":
    BIG_SYMBOL = ("Menlo", 48, "bold")
else:
    BIG_SYMBOL = ("DejaVu Sans", 46, "bold")

# ── Farben ────────────────────────────────────────────────────────────────────
BG       = "#06060f"
BG2      = "#0d1b3e"
GREEN    = "#00ffaa"
RED      = "#ff3366"
YELLOW   = "#ffe500"
GRAY     = "#333344"
TEXTGRAY = "#888899"
WHITE    = "#eef0ff"

# ── Schriften ─────────────────────────────────────────────────────────────────
FONT_MONO = ("Courier New", 11, "bold")
FONT_MED  = ("Courier New", 18, "bold")
FONT_SM   = ("Courier New", 10, "bold")
FONT_XS   = ("Courier New",  9)

# ── Spielkonstanten ───────────────────────────────────────────────────────────
CHOICES = [
    {"id": "schere", "label": "SCHERE", "emoji": "X", "beats": "papier"},
    {"id": "stein",  "label": "STEIN",  "emoji": "O", "beats": "schere"},
    {"id": "papier", "label": "PAPIER", "emoji": "=", "beats": "stein"},
]

CHOICE_DISPLAY = {
    "schere": "✂",
    "stein":  "●",
    "papier": "▬",
}

ERGEBNIS = {
    "gewonnen":      ("DU GEWINNST!",   GREEN),
    "verloren":      ("DU VERLIERST!",  RED),
    "unentschieden": ("UNENTSCHIEDEN!", YELLOW),
}


def get_result(player: str, computer: str) -> str:
    """Gibt 'gewonnen', 'verloren' oder 'unentschieden' zurück."""
    if player == computer:
        return "unentschieden"
    winner = next(c for c in CHOICES if c["id"] == player)
    return "gewonnen" if winner["beats"] == computer else "verloren"


# ── Kämpfer-Widget (eigene Klasse statt dynamischer Frame-Attribute) ───────────
class FighterFrame(tk.Frame):
    """Ein beschrifteter Kasten mit einem großen Symbol in der Mitte."""

    def __init__(self, parent: tk.Widget, label: str, color: str) -> None:
        super().__init__(parent, bg=BG)
        self.box_color: str = color

        tk.Label(self, text=label, font=FONT_SM, fg=color, bg=BG).pack(
            anchor="w", padx=4
        )

        self.box: tk.Frame = tk.Frame(
            self, bg=BG2,
            highlightbackground=color, highlightthickness=2,
            width=130, height=130,
        )
        self.box.pack_propagate(False)
        self.box.pack()

        self.symbol_label: tk.Label = tk.Label(
            self.box, text="?", font=BIG_SYMBOL, fg=color, bg=BG2
        )
        self.symbol_label.place(relx=0.5, rely=0.5, anchor="center")

    def show(self, choice_id: str) -> None:
        """Zeigt das Symbol für die gegebene Wahl."""
        text = CHOICE_DISPLAY.get(choice_id, "?")
        self.symbol_label.config(text=text, fg=self.box_color)
        self.box.config(highlightbackground=self.box_color)

    def reset(self) -> None:
        """Setzt den Kämpfer auf den Ausgangszustand zurück."""
        self.symbol_label.config(text="?", fg=self.box_color)
        self.box.config(highlightbackground=self.box_color)

    def blink(self, times: int) -> None:
        """Lässt den Rahmen blinken."""
        if times <= 0:
            self.box.config(highlightbackground=self.box_color)
            return
        current = str(self.box.cget("highlightbackground"))
        next_color = BG if current == self.box_color else self.box_color
        self.box.config(highlightbackground=next_color)
        self.after(80, lambda: self.blink(times - 1))

    def dim(self) -> None:
        """Dunkelt den Rahmen ab (Verlierer)."""
        self.box.config(highlightbackground=GRAY)


# ── Hauptfenster ──────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Schere - Stein - Papier")
        self.configure(bg=BG)
        self.resizable(False, False)

        self.score: dict[str, int] = {"siege": 0, "remis": 0, "nieder": 0}
        self.animating: bool = False

        self.score_labels: dict[str, tk.Label] = {}
        self.choice_buttons: list[tk.Button] = []
        self.vs_label: tk.Label
        self.result_label: tk.Label
        self.player_frame: FighterFrame
        self.cpu_frame: FighterFrame

        self._build_ui()
        self._center_window()

    # ── UI aufbauen ───────────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        # Titel
        tk.Label(
            self,
            text="  SCHERE  *  STEIN  *  PAPIER  ",
            font=("Courier New", 14, "bold"),
            fg=WHITE, bg=BG, pady=18,
        ).pack()

        # Scoreboard
        score_frame = tk.Frame(self, bg=BG)
        score_frame.pack(pady=(0, 20))

        score_defs = [
            ("SIEGE",   "siege",  GREEN),
            ("REMIS",   "remis",  YELLOW),
            ("NIEDER.", "nieder", RED),
        ]
        for title, key, color in score_defs:
            cell = tk.Frame(
                score_frame, bg=BG2,
                highlightbackground=color, highlightthickness=2,
                padx=22, pady=10,
            )
            cell.pack(side=tk.LEFT, padx=8)
            lbl = tk.Label(cell, text="0",
                           font=("Courier New", 30, "bold"),
                           fg=color, bg=BG2)
            lbl.pack()
            tk.Label(cell, text=title, font=FONT_XS,
                     fg=TEXTGRAY, bg=BG2).pack()
            self.score_labels[key] = lbl

        # Arena
        arena = tk.Frame(self, bg=BG)
        arena.pack(pady=10)

        self.player_frame = FighterFrame(arena, "DU",  GREEN)
        self.player_frame.pack(side=tk.LEFT, padx=12)

        self.vs_label = tk.Label(
            arena, text="VS",
            font=("Courier New", 20, "bold"),
            fg=GRAY, bg=BG, width=5,
        )
        self.vs_label.pack(side=tk.LEFT)

        self.cpu_frame = FighterFrame(arena, "CPU", RED)
        self.cpu_frame.pack(side=tk.LEFT, padx=12)

        # Ergebnis-Zeile
        self.result_label = tk.Label(
            self, text="Waehle deine Waffe!",
            font=FONT_MED, fg=TEXTGRAY, bg=BG, pady=14,
        )
        self.result_label.pack()

        # Wahl-Buttons
        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(pady=8)

        for c in CHOICES:
            symbol = CHOICE_DISPLAY[c["id"]]
            btn = tk.Button(
                btn_frame,
                text=f"{symbol}\n{c['label']}",
                font=FONT_MONO,
                fg=WHITE, bg=BG2,
                activeforeground=BG, activebackground=YELLOW,
                relief=tk.FLAT, bd=0,
                padx=18, pady=14, width=8,
                cursor="hand2",
                command=lambda cid=c["id"]: self._play(cid),  # type: ignore[misc]
            )
            btn.pack(side=tk.LEFT, padx=8)
            self._add_hover(btn)
            self.choice_buttons.append(btn)

        # Reset-Button
        tk.Button(
            self, text="Neu starten",
            font=FONT_XS, fg=TEXTGRAY, bg=BG,
            activeforeground=WHITE, activebackground=BG,
            relief=tk.FLAT, bd=0, pady=12, cursor="hand2",
            command=self._reset,
        ).pack(pady=(4, 16))

    # ── Spiellogik ────────────────────────────────────────────────────────────
    def _play(self, choice_id: str) -> None:
        if self.animating:
            return
        self.animating = True
        self._set_buttons_state(tk.DISABLED)

        self.player_frame.show(choice_id)
        self.player_frame.box.config(highlightbackground=self.player_frame.box_color)
        self.cpu_frame.reset()
        self.result_label.config(text="", fg=TEXTGRAY)
        self._countdown(3, choice_id)

    def _countdown(self, n: int, choice_id: str) -> None:
        if n > 0:
            color = RED if n == 1 else YELLOW
            self.vs_label.config(
                text=str(n), fg=color,
                font=("Courier New", 28, "bold"),
            )
            self.after(500, lambda: self._countdown(n - 1, choice_id))
        else:
            cpu_id: str = random.choice(CHOICES)["id"]
            result: str = get_result(choice_id, cpu_id)

            self.cpu_frame.show(cpu_id)
            self.vs_label.config(
                text="VS", fg=GRAY,
                font=("Courier New", 20, "bold"),
            )

            text, color = ERGEBNIS[result]
            self.result_label.config(text=text, fg=color)

            if result == "gewonnen":
                self.score["siege"] += 1
                self.player_frame.blink(6)
                self.cpu_frame.dim()
            elif result == "verloren":
                self.score["nieder"] += 1
                self.cpu_frame.blink(6)
                self.player_frame.dim()
            else:
                self.score["remis"] += 1

            self._refresh_score()
            self.after(700, self._enable_buttons)

    def _refresh_score(self) -> None:
        for key, lbl in self.score_labels.items():
            lbl.config(text=str(self.score[key]))

    def _reset(self) -> None:
        self.score = {"siege": 0, "remis": 0, "nieder": 0}
        self._refresh_score()
        self.player_frame.reset()
        self.cpu_frame.reset()
        self.vs_label.config(
            text="VS", fg=GRAY,
            font=("Courier New", 20, "bold"),
        )
        self.result_label.config(text="Waehle deine Waffe!", fg=TEXTGRAY)
        self.animating = False
        self._set_buttons_state(tk.NORMAL)

    def _set_buttons_state(self, state: Literal["normal", "disabled"]) -> None:
        for btn in self.choice_buttons:
            btn.config(state=state)

    def _enable_buttons(self) -> None:
        self.animating = False
        self._set_buttons_state(tk.NORMAL)

    # ── Hilfsfunktionen ───────────────────────────────────────────────────────
    def _add_hover(self, btn: tk.Button) -> None:
        def on_enter(e: tk.Event, b: tk.Button = btn) -> None:  # type: ignore[type-arg]
            if str(b.cget("state")) == tk.NORMAL:
                b.config(bg=GRAY, fg=YELLOW)

        def on_leave(e: tk.Event, b: tk.Button = btn) -> None:  # type: ignore[type-arg]
            if str(b.cget("state")) == tk.NORMAL:
                b.config(bg=BG2, fg=WHITE)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    def _center_window(self) -> None:
        """Zentriert das Fenster – winfo_req* liefert korrekte Größe vor dem Anzeigen."""
        self.update_idletasks()
        w  = self.winfo_reqwidth()
        h  = self.winfo_reqheight()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")


if __name__ == "__main__":
    app = App()
    app.mainloop()