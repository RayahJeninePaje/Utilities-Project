import tkinter as tk
from tkinter import ttk

from navigation import (
    BACKGROUND,
    GRAY,
    TEXT,
    WHITE,
    create_sidebar,
)


class UtilityScreen:
    def __init__(self, root, app, utility):
        self.root = root
        self.app = app
        self.utility = utility
        self.is_url_shortener = utility == "URL Shortener"

        self.root.title(f"SIA Utilities | {utility}")
        self.root.geometry("1100x700")
        self.root.configure(bg=BACKGROUND)

        self.create_interface()

    def create_interface(self):
        main = create_sidebar(self.root, self.app, self.utility)

        tk.Label(
            main,
            text=self.utility,
            font=("Arial", 25, "bold"),
            bg=BACKGROUND,
            fg=TEXT
        ).pack(anchor="w")

        description = (
            "Enter a destination URL to create a shorter link."
            if self.is_url_shortener
            else "Compose a message for an email or SMS recipient."
        )
        tk.Label(
            main,
            text=description,
            font=("Arial", 11),
            bg=BACKGROUND,
            fg=GRAY
        ).pack(anchor="w", pady=(5, 24))

        form = tk.Frame(main, bg=WHITE, padx=22, pady=20)
        form.pack(fill="x", anchor="n")

        if self.is_url_shortener:
            self.create_label(form, "Destination URL")
            tk.Entry(form, font=("Arial", 11), relief="solid", bd=1).pack(
                fill="x", ipady=7, pady=(6, 18)
            )
            self.create_label(form, "Short URL")
            result = tk.Entry(form, font=("Arial", 11), relief="solid", bd=1)
            result.pack(fill="x", ipady=7, pady=(6, 18))
            result.configure(state="disabled")
            button_text = "Shorten URL"
        else:
            self.create_label(form, "Message type")
            ttk.Combobox(
                form,
                values=("Email", "SMS"),
                state="readonly",
                font=("Arial", 10)
            ).pack(fill="x", ipady=4, pady=(6, 18))
            self.create_label(form, "Recipient email or phone number")
            tk.Entry(form, font=("Arial", 11), relief="solid", bd=1).pack(
                fill="x", ipady=7, pady=(6, 18)
            )
            self.create_label(form, "Message")
            tk.Text(form, height=5, font=("Arial", 11), relief="solid", bd=1).pack(
                fill="x", pady=(6, 18)
            )
            button_text = "Send Message"

        tk.Button(
            form,
            text=button_text,
            font=("Arial", 10, "bold"),
            bg="#CBD5E1",
            fg=WHITE,
            relief="flat",
            state="disabled"
        ).pack(anchor="w", ipadx=14, ipady=7)

        tk.Label(
            main,
            text="Not connected: configure a URL-shortening or messaging "
                 "service before using this tool.",
            font=("Arial", 10),
            bg=BACKGROUND,
            fg=GRAY,
            wraplength=760,
            justify="left"
        ).pack(anchor="w", pady=(16, 0))

    @staticmethod
    def create_label(parent, text):
        tk.Label(
            parent,
            text=text,
            font=("Arial", 10, "bold"),
            bg=WHITE,
            fg=TEXT
        ).pack(anchor="w")
