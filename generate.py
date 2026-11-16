import tkinter as tk
from tkinter import ttk, messagebox

from generator import generate_multiple_users
from navigation import (
    BACKGROUND,
    BORDER,
    BLUE,
    GRAY,
    TEXT,
    WHITE,
    create_sidebar,
)

FIELD_NAMES = (
    "Full Name",
    "Address",
    "Birthdate",
    "Mobile Number",
    "Email",
    "Gender",
    "Username",
    "City",
    "Occupation",
    "Postal Code",
)

FIELD_MAPPING = {
    "Full Name": "full_name",
    "Address": "address",
    "Birthdate": "birthdate",
    "Mobile Number": "mobile_number",
    "Email": "email",
    "Gender": "gender",
    "Username": "username",
    "City": "city",
    "Occupation": "occupation",
    "Postal Code": "postal_code",
}


class GenerateApp:
    def __init__(self, root, app=None):
        self.app = app
        self.root = root
        self.root.title("SIA Utilities | Fake Data Generator")
        self.root.geometry("1100x700")
        self.root.configure(bg=BACKGROUND)
        self.root.resizable(True, True)
        self.records = []

        self.create_interface()

    def create_interface(self):
        main = create_sidebar(self.root, self.app, "Fake Data Generator")

        tk.Label(
            main,
            text="Generate Fake Data",
            font=("Arial", 24, "bold"),
            bg=BACKGROUND,
            fg=TEXT
        ).pack(anchor="w")

        tk.Label(
            main,
            text="Create realistic sample information using Faker.",
            font=("Arial", 11),
            bg=BACKGROUND,
            fg=GRAY
        ).pack(anchor="w", pady=(0, 15))

        settings = tk.Frame(
            main,
            bg=WHITE,
            padx=20,
            pady=16,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        settings.pack(fill="x")

        tk.Label(
            settings,
            text="Generation Settings",
            font=("Arial", 14, "bold"),
            bg=WHITE,
            fg=TEXT
        ).pack(anchor="w")

        tk.Label(
            settings,
            text="Number of records:",
            font=("Arial", 10, "bold"),
            bg=WHITE,
            fg=TEXT
        ).pack(anchor="w", pady=(12, 0))

        self.quantity = tk.Spinbox(
            settings,
            from_=1,
            to=1000,
            font=("Arial", 11),
            width=8
        )
        self.quantity.pack(anchor="w", pady=(7, 15), ipady=4)
        self.quantity.delete(0, "end")
        self.quantity.insert(0, "10")

        tk.Label(
            settings,
            text="Select data fields:",
            font=("Arial", 10, "bold"),
            bg=WHITE,
            fg=TEXT
        ).pack(anchor="w")

        fields_frame = tk.Frame(settings, bg=WHITE)
        fields_frame.pack(fill="x", pady=(8, 0))

        self.fields = {}
        for index, field in enumerate(FIELD_NAMES):
            variable = tk.BooleanVar(value=True)
            self.fields[field] = variable
            tk.Checkbutton(
                fields_frame,
                text=field,
                variable=variable,
                font=("Arial", 9),
                bg=WHITE,
                fg=TEXT,
                activebackground=WHITE,
                selectcolor=WHITE
            ).grid(
                row=index // 2,
                column=index % 2,
                sticky="w",
                padx=(0, 18),
                pady=4
            )

        tk.Button(
            settings,
            text="Generate Fake Data",
            font=("Arial", 11, "bold"),
            bg=BLUE,
            fg=WHITE,
            activebackground="#1D4ED8",
            activeforeground=WHITE,
            relief="flat",
            cursor="hand2",
            command=self.generate_data
        ).pack(anchor="w", pady=(16, 4), ipadx=12, ipady=6)

        tk.Label(
            main,
            text="Generated Data Preview",
            font=("Arial", 14, "bold"),
            bg=BACKGROUND,
            fg=TEXT
        ).pack(anchor="w", pady=(18, 8))

        table_frame = tk.Frame(main, bg=WHITE)
        table_frame.pack(fill="both", expand=True)

        columns = ("full_name", "email", "gender", "city", "occupation")
        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=12
        )

        for column in columns:
            self.table.heading(column, text=column.replace("_", " ").title())
            self.table.column(column, width=150)

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview
        )
        self.table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.table.pack(side="left", fill="both", expand=True)

    def generate_data(self):
        try:
            quantity = int(self.quantity.get())
        except ValueError:
            messagebox.showerror(
                "Invalid Quantity",
                "Please enter a number between 1 and 1000."
            )
            return

        if quantity < 1 or quantity > 1000:
            messagebox.showerror(
                "Invalid Quantity",
                "Please enter a number between 1 and 1000."
            )
            return

        selected_fields = [
            field for field, variable in self.fields.items() if variable.get()
        ]

        if not selected_fields:
            messagebox.showwarning(
                "No Fields Selected",
                "Please select at least one data field."
            )
            return

        preview_fields = [FIELD_MAPPING[field] for field in selected_fields]
        self.records = generate_multiple_users(quantity)

        self.table.delete(*self.table.get_children())
        self.table["columns"] = preview_fields
        self.table["displaycolumns"] = preview_fields

        for field in preview_fields:
            self.table.heading(field, text=field.replace("_", " ").title())
            self.table.column(field, width=150)

        for record in self.records:
            values = [record[field] for field in preview_fields]
            self.table.insert("", "end", values=values)

        messagebox.showinfo(
            "Success",
            f"{quantity} fake records generated successfully!"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = GenerateApp(root)
    root.mainloop()
