"""Minimal Tkinter desktop app for the CWA-28 installer spike."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from companion_welfare_ai.core.repositories import SQLiteHelloRepository


class HelloWorldApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.repository = SQLiteHelloRepository()
        root.title("Companion Welfare AI — Hello World")
        root.geometry("520x300")
        root.minsize(460, 260)

        container = tk.Frame(root, padx=28, pady=24)
        container.pack(fill="both", expand=True)

        tk.Label(
            container,
            text="Companion Welfare AI",
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w")
        tk.Label(
            container,
            text="CWA-28 packaging and local-storage smoke test",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 18))

        tk.Label(container, text="Provisional D1 desktop UI: Python + Tkinter").pack(anchor="w")
        tk.Label(container, text="Provisional D4 storage: local SQLite database").pack(anchor="w")

        self.status = tk.StringVar(value="Select the button to write and read a local test record.")
        tk.Label(container, textvariable=self.status, wraplength=440, justify="left").pack(
            anchor="w", pady=(18, 12)
        )
        tk.Button(
            container,
            text="Run local storage check",
            command=self.run_storage_check,
            padx=12,
            pady=7,
        ).pack(anchor="w")

    def run_storage_check(self) -> None:
        try:
            count = self.repository.add_greeting()
            self.status.set(
                f"PASS: record saved and read from the local database. "
                f"Database: {self.repository.database_path} | Records: {count}"
            )
        except Exception as error:
            self.status.set("FAIL: the local storage check did not complete.")
            messagebox.showerror("Storage check failed", f"{type(error).__name__}: {error}")


def main() -> None:
    root = tk.Tk()
    HelloWorldApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
