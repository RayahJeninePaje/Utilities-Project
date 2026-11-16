import tkinter as tk

from navigation import (
    BACKGROUND,
    BORDER,
    BLUE,
    GRAY,
    TEXT,
    WHITE,
    create_sidebar,
)


class DashboardApp:
    def __init__(self, root, app=None):
        self.root = root
        self.app = app
        self.root.title("SIA Utilities | Dashboard")
        self.root.geometry("1100x700")
        self.root.resizable(True, True)
        self.root.configure(bg=BACKGROUND)

        self.create_interface()

    def create_interface(self):
        main = create_sidebar(self.root, self.app, "Dashboard")

        tk.Label(
            main,
            text="Utilities",
            font=("Arial", 25, "bold"),
            bg=BACKGROUND,
            fg=TEXT
        ).pack(anchor="w")
        tk.Label(
            main,
            text="Choose a tool to get started.",
            font=("Arial", 11),
            bg=BACKGROUND,
            fg=GRAY
        ).pack(anchor="w", pady=(5, 28))

        tools = tk.Frame(main, bg=BACKGROUND)
        tools.pack(fill="x")

        self.create_tool_card(
            tools,
            "URL Shortener",
            "Create and manage shorter links for long URLs.",
            "Setup required",
            self.open_url_shortener
        )
        self.create_tool_card(
            tools,
            "SMS / Email",
            "Prepare a message to send by text or email.",
            "Setup required",
            self.open_messaging
        )
        self.create_tool_card(
            tools,
            "Fake Data Generator",
            "Generate sample records and preview the results.",
            "Available",
            self.generate_data
        )

        tk.Label(
            main,
            text="URL shortening and message delivery need an external service. "
                 "Those screens are included for navigation, but are not connected.",
            font=("Arial", 10),
            bg=BACKGROUND,
            fg=GRAY,
            wraplength=760,
            justify="left"
        ).pack(anchor="w", pady=(24, 0))

    def create_tool_card(self, parent, title, description, status, command):
        card = tk.Frame(
            parent,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=18,
            pady=18
        )
        card.pack(side="left", expand=True, fill="both", padx=(0, 12))

        tk.Label(
            card,
            text=title,
            font=("Arial", 14, "bold"),
            bg=WHITE,
            fg=TEXT,
            wraplength=200,
            justify="left"
        ).pack(anchor="w")
        tk.Label(
            card,
            text=description,
            font=("Arial", 10),
            bg=WHITE,
            fg=GRAY,
            wraplength=200,
            justify="left"
        ).pack(anchor="w", pady=(10, 16))
        tk.Label(
            card,
            text=status,
            font=("Arial", 9),
            bg=WHITE,
            fg=BLUE if status == "Available" else GRAY
        ).pack(anchor="w")
        tk.Button(
            card,
            text="Open",
            font=("Arial", 10, "bold"),
            bg=BLUE,
            fg=WHITE,
            activebackground="#1D4ED8",
            activeforeground=WHITE,
            relief="flat",
            cursor="hand2",
            command=command
        ).pack(anchor="w", pady=(16, 0), ipadx=14, ipady=5)

    def open_url_shortener(self):
        if self.app is not None:
            self.app.show_url_shortener()

    def open_messaging(self):
        if self.app is not None:
            self.app.show_messaging()

    def generate_data(self):
        if self.app is not None:
            self.app.show_generate()


if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()
