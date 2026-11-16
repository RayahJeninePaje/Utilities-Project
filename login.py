import tkinter as tk
from tkinter import messagebox

BLUE = "#2563EB"
BACKGROUND = "#F8FAFC"
WHITE = "#FFFFFF"
TEXT = "#0F172A"
GRAY = "#64748B"
BORDER = "#E2E8F0"
GREEN = "#10B981"


class LoginApp:
    def __init__(self, root, app=None):
        self.root = root
        self.app = app
        self.root.title("SIA Utilities | Login")
        self.root.geometry("900x560")
        self.root.resizable(False, False)
        self.root.configure(bg=BACKGROUND)

        self.create_interface()

    def create_interface(self):
        left = tk.Frame(self.root, bg=BLUE, width=380)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(
            left,
            text="SIA Utilities",
            font=("Arial", 32, "bold"),
            bg=BLUE,
            fg=WHITE
        ).place(x=45, y=155)

        tk.Label(
            left,
            text="Everyday tools in one place",
            font=("Arial", 13),
            bg=BLUE,
            fg=WHITE
        ).place(x=48, y=210)

        tk.Label(
            left,
            text="Shorten links, prepare messages,\nand generate sample data.",
            font=("Arial", 12),
            bg=BLUE,
            fg="#DBEAFE",
            justify="left"
        ).place(x=48, y=260)

        right = tk.Frame(self.root, bg=BACKGROUND)
        right.pack(side="right", expand=True, fill="both")

        form = tk.Frame(right, bg=WHITE, padx=45, pady=28)
        form.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            form,
            text="Welcome Back!",
            font=("Arial", 25, "bold"),
            bg=WHITE,
            fg=TEXT
        ).pack(anchor="w")

        tk.Label(
            form,
            text="Sign in to continue to your utilities.",
            font=("Arial", 10),
            bg=WHITE,
            fg=GRAY
        ).pack(anchor="w", pady=(5, 25))

        tk.Label(
            form,
            text="Username",
            font=("Arial", 10, "bold"),
            bg=WHITE,
            fg=TEXT
        ).pack(anchor="w")

        self.username = tk.Entry(
            form,
            font=("Arial", 11),
            width=32,
            relief="solid",
            bd=1,
            bg=WHITE,
            fg=TEXT,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=BLUE
        )
        self.username.pack(fill="x", ipady=7, pady=(7, 18))
        self.username.focus()

        tk.Label(
            form,
            text="Password",
            font=("Arial", 10, "bold"),
            bg=WHITE,
            fg=TEXT
        ).pack(anchor="w")

        self.password = tk.Entry(
            form,
            font=("Arial", 11),
            width=32,
            show="*",
            relief="solid",
            bd=1,
            bg=WHITE,
            fg=TEXT,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=BLUE
        )
        self.password.pack(fill="x", ipady=7, pady=(7, 22))

        tk.Button(
            form,
            text="Sign In",
            font=("Arial", 11, "bold"),
            bg=BLUE,
            fg=WHITE,
            activebackground="#1D4ED8",
            activeforeground=WHITE,
            relief="flat",
            cursor="hand2",
            command=self.login
        ).pack(fill="x", ipady=10, pady=(22, 0))

        register_frame = tk.Frame(form, bg=WHITE)
        register_frame.pack(pady=(16, 0))

        tk.Label(
            register_frame,
            text="Don't have an account?",
            font=("Arial", 9),
            bg=WHITE,
            fg=GRAY
        ).pack(side="left")

        tk.Button(
            register_frame,
            text="Register",
            font=("Arial", 9, "bold"),
            bg=WHITE,
            fg=BLUE,
            activebackground=WHITE,
            relief="flat",
            cursor="hand2",
            command=self.register
        ).pack(side="left", padx=4)

        self.root.bind("<Return>", lambda event: self.login())

    def login(self):
        username = self.username.get().strip()
        password = self.password.get()

        if not username or not password:
            messagebox.showwarning(
                "Missing Information",
                "Please enter your username and password."
            )
            return

        if self.app is not None:
            self.app.show_dashboard()
            return

        messagebox.showinfo(
            "Login",
            f"Welcome, {username}!\n\nLogin interface is ready."
        )

    def register(self):
        if self.app is not None:
            self.app.show_register()
            return

        messagebox.showinfo(
            "Registration",
            "Registration page will be added next."
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
