import tkinter as tk

BLUE = "#2563EB"
BACKGROUND = "#F8FAFC"
WHITE = "#FFFFFF"
TEXT = "#0F172A"
GRAY = "#64748B"
BORDER = "#E2E8F0"


def create_sidebar(root, app, active):
    sidebar = tk.Frame(root, bg=WHITE, width=220)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Label(
        sidebar,
        text="SIA Utilities",
        font=("Arial", 19, "bold"),
        bg=WHITE,
        fg=TEXT
    ).pack(anchor="w", padx=24, pady=(32, 28))

    destinations = (
        ("Dashboard", "show_dashboard"),
        ("URL Shortener", "show_url_shortener"),
        ("SMS / Email", "show_messaging"),
        ("Fake Data Generator", "show_generate"),
    )
    for label, destination in destinations:
        is_active = label == active
        tk.Button(
            sidebar,
            text=label,
            font=("Arial", 10, "bold" if is_active else "normal"),
            bg="#EFF6FF" if is_active else WHITE,
            fg=BLUE if is_active else GRAY,
            activebackground="#EFF6FF",
            activeforeground=BLUE,
            relief="flat",
            anchor="w",
            padx=14,
            pady=11,
            cursor="hand2",
            state="normal" if app is not None else "disabled",
            command=getattr(app, destination, None) if app is not None else None
        ).pack(fill="x", padx=12, pady=3)

    tk.Button(
        sidebar,
        text="Sign Out",
        font=("Arial", 10),
        bg=WHITE,
        fg=GRAY,
        activebackground=BACKGROUND,
        relief="flat",
        anchor="w",
        padx=14,
        pady=11,
        cursor="hand2",
        state="normal" if app is not None else "disabled",
        command=app.show_login if app is not None else None
    ).pack(side="bottom", fill="x", padx=12, pady=16)

    main = tk.Frame(root, bg=BACKGROUND)
    main.pack(side="right", expand=True, fill="both", padx=32, pady=28)
    return main
