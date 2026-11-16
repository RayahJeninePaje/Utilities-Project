
import tkinter as tk
from tkinter import messagebox

# Clean Enterprise color palette
BLUE = "#2563EB"
BACKGROUND = "#F8FAFC"
WHITE = "#FFFFFF"
TEXT = "#0F172A"
GRAY = "#64748B"
BORDER = "#E2E8F0"


class RegisterApp:
    def __init__(self, root, app=None):
        self.root = root
        self.app = app
        self.root.title("SIA Utilities | Create Account")
        self.root.geometry("900x560")
        self.root.resizable(False, False)
        self.root.configure(bg=BACKGROUND)

        self.create_interface()

    def create_interface(self):
        # Left branding panel
        left = tk.Frame(self.root, bg=BLUE, width=380)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(
            left,
            text="Join DataGen",
            font=("Arial", 30, "bold"),
            bg=BLUE,
            fg=WHITE
        ).place(x=45, y=155)

        tk.Label(
            left,
            text="Create your account",
            font=("Arial", 13),
            bg=BLUE,
            fg=WHITE
        ).place(x=48, y=210)

        tk.Label(
            left,
            text="Access useful tools from\none simple workspace.",
            font=("Arial", 12),
            bg=BLUE,
            fg="#DBEAFE",
            justify="left"
        ).place(x=48, y=260)

        # Right registration panel
        right = tk.Frame(self.root, bg=BACKGROUND)
        right.pack(side="right", expand=True, fill="both")

        form = tk.Frame(right, bg=WHITE, padx=45, pady=28)
        form.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            form,
            text="Create Account",
            font=("Arial", 24, "bold"),
            bg=WHITE,
            fg=TEXT
        ).pack(anchor="w")

        tk.Label(
            form,
            text="Fill in your details to get started.",
            font=("Arial", 10),
            bg=WHITE,
            fg=GRAY
        ).pack(anchor="w", pady=(5, 18))

        # Username field
        self.username = self.create_field(form, "Username")

        # Password field
        self.password = self.create_field(form, "Password", show="*")

        # Confirm password field
        self.confirm_password = self.create_field(
            form, "Confirm Password", show="*"
        )

        # Register button
        tk.Button(
            form,
            text="Create Account",
            font=("Arial", 11, "bold"),
            bg=BLUE,
            fg=WHITE,
            activebackground="#1D4ED8",
            activeforeground=WHITE,
            relief="flat",
            cursor="hand2",
            command=self.register
        ).pack(fill="x", ipady=10, pady=(8, 15))

        # Login link
        bottom = tk.Frame(form, bg=WHITE)
        bottom.pack()

        tk.Label(
            bottom,
            text="Already have an account?",
            font=("Arial", 9),
            bg=WHITE,
            fg=GRAY
        ).pack(side="left")

        tk.Button(
            bottom,
            text="Sign In",
            font=("Arial", 9, "bold"),
            bg=WHITE,
            fg=BLUE,
            activebackground=WHITE,
            relief="flat",
            cursor="hand2",
            command=self.back_to_login
        ).pack(side="left", padx=4)

    def create_field(self, parent, label, show=""):
        tk.Label(
            parent,
            text=label,
            font=("Arial", 10, "bold"),
            bg=WHITE,
            fg=TEXT
        ).pack(anchor="w")

        entry = tk.Entry(
            parent,
            font=("Arial", 11),
            width=32,
            show=show,
            relief="solid",
            bd=1,
            bg=WHITE,
            fg=TEXT,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=BLUE
        )
        entry.pack(fill="x", ipady=7, pady=(5, 13))

        return entry

    def register(self):
        username = self.username.get().strip()
        password = self.password.get()
        confirm = self.confirm_password.get()

        if not username or not password or not confirm:
            messagebox.showwarning(
                "Missing Information",
                "Please complete all fields."
            )
            return

        if password != confirm:
            messagebox.showerror(
                "Password Error",
                "Passwords do not match."
            )
            return

        messagebox.showinfo(
            "Registration",
            "Registration interface is ready!"
        )

    def back_to_login(self):
        if self.app is not None:
            self.app.show_login()
            return

        messagebox.showinfo(
            "Login",
            "You can return to the login screen."
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = RegisterApp(root)
    root.mainloop()
