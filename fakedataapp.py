"""
ITL313-18 (SIA 2 LAB) - Final Term Mini Project
Function chosen: 3B.3 Fake Data Generation

Components
  1. GUI ............ Tkinter (ttk)
  2. Login system ... SQLite + hashlib (PBKDF2-HMAC-SHA256, per-user random salt)
  3. Function ....... Fake data generator: 10 fields per record, stored in SQLite

Run:  python fake_data_app.py
No third-party packages needed.
"""

import csv
import hashlib
import hmac
import os
import random
import sqlite3
import tkinter as tk
from datetime import date, timedelta
from tkinter import filedialog, messagebox, ttk

DB_FILE = "app.db"
PBKDF2_ROUNDS = 200_000


# --------------------------------------------------------------------------
# Database layer
# --------------------------------------------------------------------------
def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS users (
                   id            INTEGER PRIMARY KEY AUTOINCREMENT,
                   username      TEXT UNIQUE NOT NULL,
                   salt          TEXT NOT NULL,
                   password_hash TEXT NOT NULL
               )"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS fake_records (
                   id            INTEGER PRIMARY KEY AUTOINCREMENT,
                   user_id       INTEGER NOT NULL,
                   full_name     TEXT,
                   sex           TEXT,
                   birthdate     TEXT,
                   age           INTEGER,
                   address       TEXT,
                   zip_code      TEXT,
                   email         TEXT,
                   mobile_number TEXT,
                   occupation    TEXT,
                   civil_status  TEXT,
                   FOREIGN KEY (user_id) REFERENCES users(id)
               )"""
        )


# --------------------------------------------------------------------------
# Authentication (hashlib)
# --------------------------------------------------------------------------
def hash_password(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ROUNDS
    ).hex()


def register_user(username: str, password: str):
    """Returns (ok, message)."""
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    salt = os.urandom(16)
    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO users (username, salt, password_hash) VALUES (?, ?, ?)",
                (username, salt.hex(), hash_password(password, salt)),
            )
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    return True, "Account created. You can now log in."


def verify_login(username: str, password: str):
    """Returns user id if credentials are valid, otherwise None."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, salt, password_hash FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    if row is None:
        return None
    attempt = hash_password(password, bytes.fromhex(row["salt"]))
    if hmac.compare_digest(attempt, row["password_hash"]):
        return row["id"]
    return None


# --------------------------------------------------------------------------
# Fake data generator (10 fields)
# --------------------------------------------------------------------------
FIRST_M = ["Juan", "Jose", "Mark", "John", "Carlo", "Miguel", "Paolo", "Rafael",
           "Daniel", "Gabriel", "Joshua", "Angelo", "Christian", "Kevin"]
FIRST_F = ["Maria", "Ana", "Angelica", "Jasmine", "Kristine", "Patricia", "Bea",
           "Camille", "Danica", "Erika", "Isabel", "Nicole", "Sofia", "Trisha"]
LAST = ["Santos", "Reyes", "Cruz", "Bautista", "Garcia", "Mendoza", "Torres",
        "Flores", "Ramos", "Dela Cruz", "Aquino", "Villanueva", "Castillo",
        "Navarro", "Domingo", "Pascual"]
STREETS = ["Rizal St.", "Mabini St.", "Bonifacio Ave.", "Quezon Ave.", "Luna St.",
           "Aguinaldo Hwy.", "Katipunan Ave.", "Commonwealth Ave.", "Sampaguita St.",
           "Narra St.", "Mahogany St.", "Maginhawa St."]
# (city, province/region, zip prefix)
CITIES = [("Quezon City", "Metro Manila", "11"), ("Manila", "Metro Manila", "10"),
          ("Makati", "Metro Manila", "12"), ("Cebu City", "Cebu", "60"),
          ("Davao City", "Davao del Sur", "80"), ("Baguio", "Benguet", "26"),
          ("Iloilo City", "Iloilo", "50"), ("Cagayan de Oro", "Misamis Oriental", "90"),
          ("Angeles", "Pampanga", "20"), ("Batangas City", "Batangas", "42")]
JOBS = ["Software Developer", "Teacher", "Nurse", "Accountant", "Civil Engineer",
        "Graphic Designer", "Call Center Agent", "Electrician", "Chef",
        "Sales Associate", "Pharmacist", "Architect", "Police Officer", "Student"]
CIVIL = ["Single", "Married", "Widowed", "Separated"]
DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "mail.com"]
MOBILE_PREFIX = ["0917", "0918", "0920", "0927", "0935", "0945", "0956", "0966", "0995"]

COLUMNS = ["full_name", "sex", "birthdate", "age", "address", "zip_code",
           "email", "mobile_number", "occupation", "civil_status"]
HEADINGS = ["Full Name", "Sex", "Birthdate", "Age", "Address", "ZIP Code",
            "Email", "Mobile Number", "Occupation", "Civil Status"]


def generate_record() -> dict:
    sex = random.choice(["Male", "Female"])
    first = random.choice(FIRST_M if sex == "Male" else FIRST_F)
    last = random.choice(LAST)

    today = date.today()
    birth = today - timedelta(days=random.randint(18 * 365, 70 * 365))
    age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))

    city, province, zip_prefix = random.choice(CITIES)
    address = f"{random.randint(1, 999)} {random.choice(STREETS)}, {city}, {province}"

    handle = f"{first}.{last}".lower().replace(" ", "") + str(random.randint(1, 99))
    return {
        "full_name": f"{first} {last}",
        "sex": sex,
        "birthdate": birth.isoformat(),
        "age": age,
        "address": address,
        "zip_code": f"{zip_prefix}{random.randint(0, 99):02d}",
        "email": f"{handle}@{random.choice(DOMAINS)}",
        "mobile_number": f"{random.choice(MOBILE_PREFIX)}{random.randint(0, 9999999):07d}",
        "occupation": random.choice(JOBS),
        "civil_status": "Single" if age < 21 else random.choice(CIVIL),
    }


def save_records(user_id: int, records: list):
    placeholders = ", ".join("?" * (len(COLUMNS) + 1))
    sql = f"INSERT INTO fake_records (user_id, {', '.join(COLUMNS)}) VALUES ({placeholders})"
    with get_conn() as conn:
        conn.executemany(sql, [(user_id, *[r[c] for c in COLUMNS]) for r in records])


def load_records(user_id: int):
    with get_conn() as conn:
        return conn.execute(
            f"SELECT id, {', '.join(COLUMNS)} FROM fake_records WHERE user_id = ? ORDER BY id",
            (user_id,),
        ).fetchall()


def delete_records(ids: list):
    with get_conn() as conn:
        conn.executemany("DELETE FROM fake_records WHERE id = ?", [(i,) for i in ids])


def clear_records(user_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM fake_records WHERE user_id = ?", (user_id,))


# --------------------------------------------------------------------------
# GUI
# --------------------------------------------------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pekeng Data Generator")
        self.geometry("420x300")
        self.resizable(False, False)
        self.user_id = None
        self.username = None
        self.frame = None
        self.show_login()

    def _swap(self, frame):
        if self.frame is not None:
            self.frame.destroy()
        self.frame = frame
        self.frame.pack(fill="both", expand=True)

    def show_login(self):
        self.user_id = self.username = None
        self.geometry("420x300")
        self.resizable(False, False)
        self.title("Pekeng Data Generator - Login")
        self._swap(LoginFrame(self))

    def show_main(self, user_id, username):
        self.user_id, self.username = user_id, username
        self.geometry("1250x560")
        self.resizable(True, True)
        self.title(f"Pekeng Data Generator - {username}")
        self._swap(MainFrame(self))


class LoginFrame(ttk.Frame):
    def __init__(self, app: App):
        super().__init__(app, padding=30)
        self.app = app
        self.username = tk.StringVar()
        self.password = tk.StringVar()

        ttk.Label(self, text="Pekeng Data Generator", font=("Segoe UI", 16, "bold")).pack(pady=(0, 15))

        ttk.Label(self, text="Username").pack(anchor="w")
        user_entry = ttk.Entry(self, textvariable=self.username)
        user_entry.pack(fill="x", pady=(0, 8))

        ttk.Label(self, text="Password").pack(anchor="w")
        pw_entry = ttk.Entry(self, textvariable=self.password, show="*")
        pw_entry.pack(fill="x", pady=(0, 15))

        row = ttk.Frame(self)
        row.pack(fill="x")
        ttk.Button(row, text="Login", command=self.login).pack(side="left", expand=True, fill="x", padx=(0, 4))
        ttk.Button(row, text="Register", command=self.register).pack(side="left", expand=True, fill="x", padx=(4, 0))

        user_entry.focus()
        pw_entry.bind("<Return>", lambda e: self.login())

    def login(self):
        username, password = self.username.get().strip(), self.password.get()
        if not username or not password:
            messagebox.showwarning("Login", "Please enter your username and password.")
            return
        uid = verify_login(username, password)
        if uid is None:
            messagebox.showerror("Login failed", "Invalid username or password.")
            self.password.set("")
            return
        self.app.show_main(uid, username)

    def register(self):
        ok, msg = register_user(self.username.get().strip(), self.password.get())
        (messagebox.showinfo if ok else messagebox.showerror)("Register", msg)
        if ok:
            self.password.set("")


class MainFrame(ttk.Frame):
    def __init__(self, app: App):
        super().__init__(app, padding=10)
        self.app = app
        self.count = tk.IntVar(value=10)

        # top bar
        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=(0, 8))
        ttk.Label(bar, text=f"Logged in as: {app.username}", font=("Segoe UI", 10, "bold")).pack(side="left")
        ttk.Button(bar, text="Logout", command=app.show_login).pack(side="right")

        # controls
        ctl = ttk.Frame(self)
        ctl.pack(fill="x", pady=(0, 8))
        ttk.Label(ctl, text="Number of records:").pack(side="left")
        ttk.Spinbox(ctl, from_=1, to=1000, width=6, textvariable=self.count).pack(side="left", padx=(4, 10))
        ttk.Button(ctl, text="Generate & Save", command=self.generate).pack(side="left", padx=2)
        ttk.Button(ctl, text="Delete Selected", command=self.delete_selected).pack(side="left", padx=2)
        ttk.Button(ctl, text="Clear All", command=self.clear_all).pack(side="left", padx=2)
        ttk.Button(ctl, text="Export CSV", command=self.export_csv).pack(side="left", padx=2)

        # table
        wrap = ttk.Frame(self)
        wrap.pack(fill="both", expand=True)
        cols = ["id"] + COLUMNS
        self.tree = ttk.Treeview(wrap, columns=cols, show="headings", selectmode="extended")
        widths = [40, 150, 60, 90, 40, 300, 70, 210, 110, 150, 90]
        for col, head, w in zip(cols, ["ID"] + HEADINGS, widths):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=w, anchor="w", stretch=col == "address")
        ysb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        xsb = ttk.Scrollbar(wrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        ysb.grid(row=0, column=1, sticky="ns")
        xsb.grid(row=1, column=0, sticky="ew")
        wrap.rowconfigure(0, weight=1)
        wrap.columnconfigure(0, weight=1)

        self.status = tk.StringVar()
        ttk.Label(self, textvariable=self.status).pack(anchor="w", pady=(6, 0))
        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        rows = load_records(self.app.user_id)
        for r in rows:
            self.tree.insert("", "end", iid=str(r["id"]), values=tuple(r))
        self.status.set(f"{len(rows)} record(s) stored in the database.")

    def generate(self):
        try:
            n = int(self.count.get())
        except (tk.TclError, ValueError):
            messagebox.showerror("Generate", "Enter a valid number of records.")
            return
        if not 1 <= n <= 1000:
            messagebox.showerror("Generate", "Choose between 1 and 1000 records.")
            return
        save_records(self.app.user_id, [generate_record() for _ in range(n)])
        self.refresh()

    def delete_selected(self):
        ids = [int(i) for i in self.tree.selection()]
        if not ids:
            messagebox.showinfo("Delete", "Select one or more rows first.")
            return
        delete_records(ids)
        self.refresh()

    def clear_all(self):
        if messagebox.askyesno("Clear all", "Delete all of your generated records?"):
            clear_records(self.app.user_id)
            self.refresh()

    def export_csv(self):
        rows = load_records(self.app.user_id)
        if not rows:
            messagebox.showinfo("Export", "No records to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV file", "*.csv")])
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(HEADINGS)
            for r in rows:
                w.writerow([r[c] for c in COLUMNS])
        messagebox.showinfo("Export", f"Saved {len(rows)} record(s) to:\n{path}")


if __name__ == "__main__":
    init_db()
    App().mainloop()