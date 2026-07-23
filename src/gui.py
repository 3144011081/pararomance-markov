"""
gui.py
------
Desktop GUI (Tkinter, stdlib only — no install needed) for the
Paranormal Romance Title Generator.

Usage:
    python src/gui.py
"""

import sys
import tkinter as tk
from pathlib import Path
from tkinter import font as tkfont
from tkinter import messagebox, ttk

from markov_model import MarkovChain, load_titles

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT_DIR / "data" / "pararomance_titles.txt"
MODEL_PATH = ROOT_DIR / "model.json"

BG = "#1b1024"
PANEL = "#2a1636"
ACCENT = "#b83280"
ACCENT_HOVER = "#d63aa0"
TEXT = "#f5e9ff"
SUBTEXT = "#c7aee0"


class TitleGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Paranormal Romance Title Generator")
        self.geometry("640x560")
        self.configure(bg=BG)
        self.minsize(520, 460)

        self.chain: MarkovChain | None = None
        self.status_var = tk.StringVar(value="No model loaded yet.")
        self.count_var = tk.IntVar(value=8)
        self.order_var = tk.IntVar(value=2)

        self._build_fonts()
        self._build_layout()
        self._load_or_train_model(initial=True)

    # ---------- UI construction ----------

    def _build_fonts(self):
        self.font_title = tkfont.Font(family="Georgia", size=20, weight="bold")
        self.font_body = tkfont.Font(family="Helvetica", size=11)
        self.font_small = tkfont.Font(family="Helvetica", size=9)
        self.font_result = tkfont.Font(family="Georgia", size=13)

    def _build_layout(self):
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=24, pady=(20, 8))

        tk.Label(
            header, text="🌙 Paranormal Romance Title Generator", font=self.font_title,
            bg=BG, fg=TEXT,
        ).pack(anchor="w")
        tk.Label(
            header, text="A Markov chain trained on 4,000 real paranormal-romance titles.",
            font=self.font_small, bg=BG, fg=SUBTEXT,
        ).pack(anchor="w", pady=(2, 0))

        controls = tk.Frame(self, bg=PANEL)
        controls.pack(fill="x", padx=24, pady=12)
        for i in range(4):
            controls.grid_columnconfigure(i, weight=1)

        tk.Label(controls, text="How many titles", bg=PANEL, fg=SUBTEXT, font=self.font_small).grid(
            row=0, column=0, sticky="w", padx=12, pady=(10, 0)
        )
        count_spin = ttk.Spinbox(controls, from_=1, to=50, textvariable=self.count_var, width=6)
        count_spin.grid(row=1, column=0, sticky="w", padx=12, pady=(0, 10))

        tk.Label(controls, text="Chain order", bg=PANEL, fg=SUBTEXT, font=self.font_small).grid(
            row=0, column=1, sticky="w", padx=12, pady=(10, 0)
        )
        order_spin = ttk.Spinbox(
            controls, from_=1, to=3, textvariable=self.order_var, width=6,
            command=self._on_order_change,
        )
        order_spin.grid(row=1, column=1, sticky="w", padx=12, pady=(0, 10))

        gen_btn = tk.Button(
            controls, text="✨ Generate", command=self.on_generate,
            bg=ACCENT, fg="white", activebackground=ACCENT_HOVER, activeforeground="white",
            font=self.font_body, relief="flat", padx=16, pady=6, cursor="hand2",
        )
        gen_btn.grid(row=1, column=2, sticky="w", padx=12, pady=(0, 10))

        retrain_btn = tk.Button(
            controls, text="↻ Retrain model", command=self.on_retrain,
            bg=PANEL, fg=TEXT, activebackground="#3a2148", activeforeground="white",
            font=self.font_small, relief="flat", padx=10, pady=6, cursor="hand2",
            highlightbackground=ACCENT, highlightthickness=1,
        )
        retrain_btn.grid(row=1, column=3, sticky="e", padx=12, pady=(0, 10))

        # Results list
        results_frame = tk.Frame(self, bg=BG)
        results_frame.pack(fill="both", expand=True, padx=24, pady=(0, 8))

        self.listbox = tk.Listbox(
            results_frame, bg=PANEL, fg=TEXT, font=self.font_result,
            selectbackground=ACCENT, selectforeground="white",
            relief="flat", highlightthickness=0, activestyle="none",
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.configure(yscrollcommand=scrollbar.set)

        # Footer / status + save
        footer = tk.Frame(self, bg=BG)
        footer.pack(fill="x", padx=24, pady=(0, 18))
        tk.Label(footer, textvariable=self.status_var, bg=BG, fg=SUBTEXT, font=self.font_small).pack(
            side="left"
        )
        save_btn = tk.Button(
            footer, text="Save results to file", command=self.on_save,
            bg=PANEL, fg=TEXT, activebackground="#3a2148", activeforeground="white",
            font=self.font_small, relief="flat", padx=10, pady=4, cursor="hand2",
        )
        save_btn.pack(side="right")

    # ---------- model lifecycle ----------

    def _load_or_train_model(self, initial: bool = False):
        try:
            if MODEL_PATH.exists():
                self.chain = MarkovChain.load(MODEL_PATH)
                if self.chain.order != self.order_var.get():
                    # Model on disk was trained at a different order; keep it,
                    # just reflect its real order in the UI.
                    self.order_var.set(self.chain.order)
                self.status_var.set(f"Loaded model ({len(self.chain.table)} states, order {self.chain.order}).")
                self.on_generate()
            else:
                self.on_retrain()
        except Exception as e:
            messagebox.showerror("Failed to load model", str(e))
            self.status_var.set("Failed to load model.")

    def on_retrain(self):
        try:
            order = self.order_var.get()
            self.status_var.set("Training model...")
            self.update_idletasks()
            titles = load_titles(DATA_PATH)
            chain = MarkovChain(order=order).fit(titles)
            chain.save(MODEL_PATH)
            self.chain = chain
            self.status_var.set(
                f"Trained on {len(titles)} titles → {len(chain.table)} states (order {order})."
            )
            self.on_generate()
        except FileNotFoundError:
            messagebox.showerror(
                "Dataset not found",
                f"Couldn't find the training data at:\n{DATA_PATH}",
            )
        except Exception as e:
            messagebox.showerror("Training failed", str(e))

    def _on_order_change(self):
        # Changing order requires retraining (the saved model is order-specific).
        self.on_retrain()

    # ---------- actions ----------

    def on_generate(self):
        if not self.chain:
            return
        n = max(1, self.count_var.get())
        titles = self.chain.generate_many(n)
        self.listbox.delete(0, tk.END)
        if not titles:
            self.listbox.insert(tk.END, "Couldn't generate titles — try a lower chain order.")
            return
        for t in titles:
            self.listbox.insert(tk.END, f"📖  {t}")

    def on_save(self):
        items = self.listbox.get(0, tk.END)
        if not items:
            messagebox.showinfo("Nothing to save", "Generate some titles first.")
            return
        out_path = ROOT_DIR / "generated_titles.txt"
        cleaned = [item.replace("📖  ", "") for item in items]
        out_path.write_text("\n".join(cleaned), encoding="utf-8")
        messagebox.showinfo("Saved", f"Saved {len(cleaned)} titles to:\n{out_path}")


def main():
    app = TitleGeneratorApp()
    app.mainloop()


if __name__ == "__main__":
    try:
        main()
    except tk.TclError as e:
        print(
            "Could not start the GUI (no display available).\n"
            f"Details: {e}\n\n"
            "If you're on a headless server/SSH session, run this on a machine "
            "with a desktop environment, or use X11 forwarding / VNC.",
            file=sys.stderr,
        )
        sys.exit(1)
