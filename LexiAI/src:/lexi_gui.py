#!/usr/bin/env python3
from __future__ import annotations

import json
import threading
from datetime import datetime
from pathlib import Path
from tkinter import BOTH, END, LEFT, RIGHT, X, Button, Entry, Frame, Label, Tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

from lexi_backend import OllamaBigDaddyDrewClient, BigDaddyDrewBackendError

ROOT = Path(__file__).resolve().parent.parent
CHAT_LOG_DIR = ROOT / "chat_logs"
CHAT_LOG_DIR.mkdir(exist_ok=True)


class BigDaddyDrewApp:
    def __init__(self) -> None:
        self.client = OllamaBigDaddyDrewClient.from_disk()
        self.messages = []

        self.root = Tk()
        self.root.title(self.client.config.window_title)
        self.root.geometry("900x650")

        self.status = Label(self.root, text="Starting…", anchor="w")
        self.status.pack(fill=X, padx=10, pady=(10, 0))

        self.output = ScrolledText(self.root, wrap="word", font=("Menlo", 12))
        self.output.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.output.insert(END, "BigDaddyDrew is booting...\n")
        self.output.configure(state="disabled")

        control_row = Frame(self.root)
        control_row.pack(fill=X, padx=10, pady=(0, 10))

        self.entry = Entry(control_row, font=("Menlo", 12))
        self.entry.pack(side=LEFT, fill=X, expand=True)
        self.entry.bind("<Return>", self._send_event)

        self.send_button = Button(control_row, text="Send", command=self.send_message)
        self.send_button.pack(side=RIGHT, padx=(8, 0))

        self.save_button = Button(control_row, text="Save Chat", command=self.save_chat)
        self.save_button.pack(side=RIGHT)

        self.root.after(100, self.startup_check)

    def append_text(self, speaker: str, text: str) -> None:
        self.output.configure(state="normal")
        self.output.insert(END, f"{speaker}: {text}\n\n")
        self.output.see(END)
        self.output.configure(state="disabled")

    def set_status(self, text: str) -> None:
        self.status.config(text=text)

    def startup_check(self) -> None:
        def task() -> None:
            try:
                self.client.ping()
                self.root.after(0, lambda: self.set_status("Connected to Ollama."))
                self.root.after(0, lambda: self.append_text("System", "BigDaddyDrew is online."))
            except BigDaddyDrewBackendError as exc:
                self.root.after(0, lambda: self.set_status("Startup problem."))
                self.root.after(0, lambda: self.append_text("System", str(exec)))

        threading.Thread(target=task, daemon=True).start()

    def _send_event(self, _event) -> None:
        self.send_message()

    def send_message(self) -> None:
        user_text = self.entry.get().strip()
        if not user_text:
            return

        self.entry.delete(0, END)
        self.messages.append({"role": "user", "content": user_text})
        self.append_text("You", user_text)
        self.set_status("BigDaddyDrew is thinking…")
        self.send_button.config(state="disabled")

        def task() -> None:
            try:
                reply = self.client.chat(self.messages)
                self.messages.append({"role": "assistant", "content": reply})
                self.root.after(0, lambda: self.append_text("BigDaddyDrew", reply))
                self.root.after(0, lambda: self.set_status("Connected to Ollama."))
            except BigDaddyDrewBackendError as exc:
                self.root.after(0, lambda: self.append_text("System", str(exc)))
                self.root.after(0, lambda: self.set_status("Error talking to Ollama."))
            finally:
                self.root.after(0, lambda: self.send_button.config(state="normal"))

        threading.Thread(target=task, daemon=True).start()

    def save_chat(self) -> None:
        if not self.messages:
            messagebox.showinfo("BigDaddyDrew AI", "No conversation to save yet.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = CHAT_LOG_DIR / f"lexi_chat_{timestamp}.json"
        out_path.write_text(json.dumps(self.messages, indent=2), encoding="utf-8")
        messagebox.showinfo("BigDaddyDrew AI", f"Saved chat to:\n{out_path}")

    def run(self) -> None:
        self.entry.focus_set()
        self.root.mainloop()


def main() -> int:
    app = BigDaddyDrewApp()
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
