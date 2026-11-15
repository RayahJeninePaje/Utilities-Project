"""
ITL313-18 (SIA 2 LAB) - Final Term Mini Project
Category 3B: Utilities
  3B.1 URL Shortening
  3B.2 SMS and Email
  3B.3 Fake Data Generation (10 fields, 10+ records, stored in SQLite)

Requirements:  pip install faker
Run:           python utilities_app.py
"""
import csv
import hashlib
import hmac
import json
import os
import random
import re
import smtplib
import sqlite3
import string
import tkinter as tk
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from datetime import datetime
from email.message import EmailMessage
from tkinter import filedialog, messagebox, ttk

try:
    from faker import Faker
except ImportError:  # handled when the user clicks Generate
    Faker = None

DB_FILE = "utilities.db"
SHORT_DOMAIN = "http://short.ly/"  # local demo domain
ITERATIONS = 200_000


PH_PREFIXES = ["905", "906", "915", "916", "917", "926", "927", "935", "936",
               "945", "955", "956", "965", "966", "975", "977", "995", "997"]


def ph_mobile():
    """Random Philippine mobile number, e.g. 0917 123 4567."""
    n = f"{random.randint(0, 9999999):07d}"
    return f"0{random.choice(PH_PREFIXES)} {n[:3]} {n[3:]}"


EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "yahoo.com.ph"]
NAME_SKIP = {"mr", "mrs", "ms", "dr", "jr", "sr", "ii", "iii", "iv", "md", "phd", "dds", "dvm"}


def make_login(name):
    """Build a username and email that match the person's name."""
    parts = [re.sub(r"[^a-z]", "", w.lower()) for w in name.replace(",", " ").split()]
    parts = [w for w in parts if w and w not in NAME_SKIP]
    first, last = parts[0], parts[-1]
    num = random.randint(1, 99)
    username = f"{first}.{last}{num}"
    email = f"{first}.{last}{random.choice(['', str(num)])}@{random.choice(EMAIL_DOMAINS)}"
    return username, email


def smtp_send_gmail(sender, password, msg):
    """Send through Gmail. Tries SSL on 465, then STARTTLS on 587 (some networks block 465)."""
    last = None
    for port, use_ssl in ((465, True), (587, False)):
        try:
            cls = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP
            with cls("smtp.gmail.com", port, timeout=15) as server:
                if not use_ssl:
                    server.starttls()
                server.login(sender, password)
                server.send_message(msg)
            return
        except smtplib.SMTPAuthenticationError:
            raise  # wrong credentials: retrying another port will not help
        except (smtplib.SMTPException, OSError) as ex:
            last = ex
    raise last


def brevo_send(sender, api_key, to, subject, body):
    """Send email through Brevo's HTTPS API (no SMTP ports needed)."""
    payload = json.dumps({"sender": {"email": sender}, "to": [{"email": to}],
                          "subject": subject, "textContent": body}).encode()
    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email", data=payload, method="POST",
        headers={"api-key": api_key, "content-type": "application/json",
                 "accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            r.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:300]
        raise RuntimeError(f"Brevo rejected the request ({e.code}): {detail}") from None


# ---------------------------------------------------------------- DATABASE
def get_conn():
    return sqlite3.connect(DB_FILE)


def init_db():
    with get_conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            salt BLOB NOT NULL,
            password_hash BLOB NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS urls(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            original TEXT NOT NULL,
            owner TEXT NOT NULL,
            created_at TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS fake_people(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, address TEXT, birthdate TEXT, mobile TEXT,
            email TEXT, job TEXT, company TEXT, username TEXT,
            gender TEXT, city TEXT)""")


# ---------------------------------------------------------------- PASSWORDS
def hash_password(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)


def register_user(username, password):
    salt = os.urandom(16)
    try:
        with get_conn() as c:
            c.execute("INSERT INTO users(username, salt, password_hash) VALUES(?,?,?)",
                      (username, salt, hash_password(password, salt)))
        return True
    except sqlite3.IntegrityError:
        return False


def verify_user(username, password):
    with get_conn() as c:
        row = c.execute("SELECT salt, password_hash FROM users WHERE username=?",
                        (username,)).fetchone()
    if not row:
        return False
    return hmac.compare_digest(hash_password(password, row[0]), row[1])


# ---------------------------------------------------------------- LOGIN UI
class LoginFrame(ttk.Frame):
    def __init__(self, master, on_success):
        super().__init__(master, padding=30)
        self.on_success = on_success
        self.mode = "login"

        self.title = ttk.Label(self, text="Login", font=("Segoe UI", 20, "bold"))
        self.title.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        ttk.Label(self, text="Username").grid(row=1, column=0, sticky="e", pady=5)
        self.user = ttk.Entry(self, width=28)
        self.user.grid(row=1, column=1, pady=5)

        ttk.Label(self, text="Password").grid(row=2, column=0, sticky="e", pady=5)
        self.pw = ttk.Entry(self, width=28, show="*")
        self.pw.grid(row=2, column=1, pady=5)

        self.confirm_lbl = ttk.Label(self, text="Confirm")
        self.confirm = ttk.Entry(self, width=28, show="*")

        self.submit = ttk.Button(self, text="Login", command=self.submit_form)
        self.submit.grid(row=4, column=0, columnspan=2, pady=(15, 5), sticky="ew")
        self.switch = ttk.Button(self, text="No account? Register", command=self.toggle)
        self.switch.grid(row=5, column=0, columnspan=2, sticky="ew")

        self.user.focus()
        master.bind("<Return>", lambda e: self.submit_form())

    def toggle(self):
        if self.mode == "login":
            self.mode = "register"
            self.title.config(text="Register")
            self.confirm_lbl.grid(row=3, column=0, sticky="e", pady=5)
            self.confirm.grid(row=3, column=1, pady=5)
            self.submit.config(text="Create Account")
            self.switch.config(text="Back to Login")
        else:
            self.mode = "login"
            self.title.config(text="Login")
            self.confirm_lbl.grid_remove()
            self.confirm.grid_remove()
            self.submit.config(text="Login")
            self.switch.config(text="No account? Register")

    def submit_form(self):
        u, p = self.user.get().strip(), self.pw.get()
        if not u or not p:
            return messagebox.showwarning("Missing", "Enter username and password.")
        if self.mode == "register":
            if len(u) < 3 or len(p) < 6:
                return messagebox.showwarning(
                    "Weak", "Username min 3 chars, password min 6 chars.")
            if p != self.confirm.get():
                return messagebox.showerror("Mismatch", "Passwords do not match.")
            if register_user(u, p):
                messagebox.showinfo("Success", "Account created. You can log in now.")
                self.confirm.delete(0, "end")
                self.pw.delete(0, "end")
                self.toggle()
            else:
                messagebox.showerror("Taken", "Username already exists.")
        else:
            if verify_user(u, p):
                self.on_success(u)
            else:
                messagebox.showerror("Failed", "Invalid username or password.")


# ---------------------------------------------------------------- 3B.1 URL SHORTENER
class UrlTab(ttk.Frame):
    def __init__(self, master, username):
        super().__init__(master, padding=15)
        self.username = username

        ttk.Label(self, text="Long URL").grid(row=0, column=0, sticky="w")
        self.url = ttk.Entry(self, width=60)
        self.url.grid(row=1, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(self, text="Shorten", command=self.shorten).grid(row=1, column=1)

        self.result = tk.StringVar()
        ttk.Label(self, textvariable=self.result, foreground="#0a7").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=8)

        cols = ("code", "short", "original", "created")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        for col, w in zip(cols, (80, 160, 360, 140)):
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=w)
        self.tree.grid(row=3, column=0, columnspan=2, sticky="nsew")

        bar = ttk.Frame(self)
        bar.grid(row=4, column=0, columnspan=2, pady=8, sticky="w")
        ttk.Button(bar, text="Copy Short URL", command=self.copy).pack(side="left", padx=3)
        ttk.Button(bar, text="Open Original", command=self.open_original).pack(side="left", padx=3)
        ttk.Button(bar, text="Delete", command=self.delete).pack(side="left", padx=3)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        self.load()

    def make_code(self):
        chars = string.ascii_letters + string.digits
        with get_conn() as c:
            while True:
                code = "".join(random.choices(chars, k=6))
                if not c.execute("SELECT 1 FROM urls WHERE code=?", (code,)).fetchone():
                    return code

    def shorten(self):
        link = self.url.get().strip()
        parsed = urllib.parse.urlparse(link)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            return messagebox.showerror("Invalid", "Enter a valid URL starting with http:// or https://")
        code = self.make_code()
        with get_conn() as c:
            c.execute("INSERT INTO urls(code, original, owner, created_at) VALUES(?,?,?,?)",
                      (code, link, self.username, datetime.now().strftime("%Y-%m-%d %H:%M")))
        self.result.set(f"Short URL: {SHORT_DOMAIN}{code}")
        self.url.delete(0, "end")
        self.load()

    def load(self):
        self.tree.delete(*self.tree.get_children())
        with get_conn() as c:
            rows = c.execute("SELECT code, original, created_at FROM urls WHERE owner=? "
                             "ORDER BY id DESC", (self.username,)).fetchall()
        for code, orig, created in rows:
            self.tree.insert("", "end", values=(code, SHORT_DOMAIN + code, orig, created))

    def selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a row first.")
            return None
        return self.tree.item(sel[0])["values"]

    def copy(self):
        v = self.selected()
        if v:
            self.clipboard_clear()
            self.clipboard_append(v[1])
            self.result.set("Copied: " + v[1])

    def open_original(self):
        v = self.selected()
        if v:
            webbrowser.open(v[2])

    def delete(self):
        v = self.selected()
        if v and messagebox.askyesno("Delete", "Delete this short link?"):
            with get_conn() as c:
                c.execute("DELETE FROM urls WHERE code=?", (str(v[0]),))
            self.load()


# ---------------------------------------------------------------- 3B.2 SMS & EMAIL
class MessageTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=10)
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)
        self.email_f = ttk.Frame(nb, padding=15)
        self.sms_f = ttk.Frame(nb, padding=15)
        nb.add(self.email_f, text="Email")
        nb.add(self.sms_f, text="SMS")
        self.build_email()
        self.build_sms()

    # ---- Email (Brevo HTTPS API or Gmail SMTP)
    TIPS = {
        0: "Brevo: make a free account, verify your sender email (Senders & IP), "
           "then create an API key (SMTP & API > API Keys).",
        1: "Gmail: use a 16-character App Password (Google Account > Security > "
           "2-Step Verification). May fail on networks that block SMTP.",
    }

    def build_email(self):
        f = self.email_f
        self.e = {}
        ttk.Label(f, text="Method").grid(row=0, column=0, sticky="e", pady=4)
        self.method = ttk.Combobox(f, state="readonly", width=47,
                                   values=["Brevo API (HTTPS)", "Gmail SMTP"])
        self.method.current(0)
        self.method.grid(row=0, column=1, sticky="w", pady=4)
        self.method.bind("<<ComboboxSelected>>", self.update_email_labels)

        for i, (label, key, show) in enumerate([
                ("Sender email", "sender", None), ("API Key", "key", "*"),
                ("To", "to", None), ("Subject", "subject", None)], start=1):
            lbl = ttk.Label(f, text=label)
            lbl.grid(row=i, column=0, sticky="e", pady=4)
            self.e[key] = ttk.Entry(f, width=50, show=show)
            self.e[key].grid(row=i, column=1, sticky="w", pady=4)
            if key == "key":
                self.key_label = lbl
        ttk.Label(f, text="Message").grid(row=5, column=0, sticky="ne", pady=4)
        self.body = tk.Text(f, width=50, height=8)
        self.body.grid(row=5, column=1, pady=4, sticky="w")
        ttk.Button(f, text="Send Email", command=self.send_email).grid(
            row=6, column=1, sticky="w", pady=8)
        self.tip = ttk.Label(f, text=self.TIPS[0], foreground="gray", wraplength=620)
        self.tip.grid(row=7, column=0, columnspan=2, sticky="w")

    def update_email_labels(self, _event=None):
        i = self.method.current()
        self.key_label.config(text="API Key" if i == 0 else "App Password")
        self.tip.config(text=self.TIPS[i])

    def send_email(self):
        use_brevo = self.method.current() == 0
        sender, key = self.e["sender"].get().strip(), self.e["key"].get().strip()
        if not use_brevo:
            key = key.replace(" ", "")
        to, subj = self.e["to"].get().strip(), self.e["subject"].get().strip()
        body = self.body.get("1.0", "end").strip()
        if not all([sender, key, to, body]):
            return messagebox.showwarning("Missing", "Fill in all fields.")
        email_re = r"[^@\s]+@[^@\s]+\.[^@\s]+"
        if not re.fullmatch(email_re, to) or not re.fullmatch(email_re, sender):
            return messagebox.showerror("Invalid", "Sender or recipient email is not valid.")
        self.config(cursor="watch")
        self.update_idletasks()
        try:
            if use_brevo:
                brevo_send(sender, key, to, subj or "(no subject)", body)
            else:
                msg = EmailMessage()
                msg["From"], msg["To"], msg["Subject"] = sender, to, subj or "(no subject)"
                msg.set_content(body)
                smtp_send_gmail(sender, key, msg)
            messagebox.showinfo("Sent", "Email sent successfully.")
        except smtplib.SMTPAuthenticationError:
            messagebox.showerror("Login failed",
                                 "Gmail rejected the login.\nUse a 16-character App Password "
                                 "(not your normal Gmail password).")
        except Exception as ex:
            messagebox.showerror("Error", f"Could not send email:\n{ex}")
        finally:
            self.config(cursor="")

    # ---- SMS (Semaphore - Philippine SMS API)
    def build_sms(self):
        f = self.sms_f
        self.s = {}
        for i, (label, key) in enumerate([("API Key", "key"), ("Mobile (09XXXXXXXXX)", "num"),
                                          ("Sender Name (optional)", "sender")]):
            ttk.Label(f, text=label).grid(row=i, column=0, sticky="e", pady=4)
            self.s[key] = ttk.Entry(f, width=45)
            self.s[key].grid(row=i, column=1, sticky="w", pady=4)
        ttk.Label(f, text="Message").grid(row=3, column=0, sticky="ne", pady=4)
        self.sms_body = tk.Text(f, width=45, height=5)
        self.sms_body.grid(row=3, column=1, pady=4, sticky="w")
        ttk.Button(f, text="Send SMS", command=self.send_sms).grid(row=4, column=1, sticky="w", pady=8)
        ttk.Label(f, text="Get an API key at semaphore.co (uses SMS credits).",
                  foreground="gray").grid(row=5, column=0, columnspan=2, sticky="w")

    def send_sms(self):
        key, num = self.s["key"].get().strip(), self.s["num"].get().strip()
        text = self.sms_body.get("1.0", "end").strip()
        if not (key and num and text):
            return messagebox.showwarning("Missing", "API key, number and message are required.")
        if not re.fullmatch(r"(09|\+639|639)\d{9}", num):
            return messagebox.showerror("Invalid", "Enter a valid PH mobile number.")
        data = {"apikey": key, "number": num, "message": text}
        if self.s["sender"].get().strip():
            data["sendername"] = self.s["sender"].get().strip()
        req = urllib.request.Request("https://api.semaphore.co/api/v4/messages",
                                     data=urllib.parse.urlencode(data).encode())
        self.config(cursor="watch")
        self.update_idletasks()
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                json.loads(r.read().decode())
            messagebox.showinfo("Sent", "SMS submitted successfully.")
        except Exception as ex:
            messagebox.showerror("Error", f"Could not send SMS:\n{ex}")
        finally:
            self.config(cursor="")


# ---------------------------------------------------------------- 3B.3 FAKE DATA
class FakeDataTab(ttk.Frame):
    FIELDS = ("name", "address", "birthdate", "mobile", "email",
              "job", "company", "username", "gender", "city")
    WIDTHS = {"name": 140, "address": 260, "birthdate": 90, "mobile": 115,
              "email": 220, "job": 180, "company": 200, "username": 150,
              "gender": 65, "city": 110}

    def __init__(self, master):
        super().__init__(master, padding=12)
        self.sort_rev = {}

        # ---- toolbar
        top = ttk.Frame(self)
        top.pack(fill="x")
        ttk.Label(top, text="Records:").pack(side="left")
        self.count = tk.IntVar(value=10)
        ttk.Spinbox(top, from_=10, to=500, width=6, textvariable=self.count).pack(side="left", padx=5)
        ttk.Button(top, text="Generate & Save", command=self.generate).pack(side="left", padx=4)
        ttk.Button(top, text="Export CSV", command=self.export).pack(side="left", padx=4)
        ttk.Button(top, text="Delete Selected", command=self.delete_selected).pack(side="left", padx=4)
        ttk.Button(top, text="Clear All", command=self.clear).pack(side="left", padx=4)

        self.search = tk.StringVar()
        self.search.trace_add("write", lambda *a: self.load())
        ttk.Entry(top, textvariable=self.search, width=22).pack(side="right")
        ttk.Label(top, text="Search:").pack(side="right", padx=(0, 5))

        self.status = ttk.Label(self, text="", foreground="gray")
        self.status.pack(anchor="w", pady=(6, 0))

        # ---- table
        wrap = ttk.Frame(self)
        wrap.pack(fill="both", expand=True, pady=6)
        self.tree = ttk.Treeview(wrap, columns=self.FIELDS, show="headings", height=12)
        for f in self.FIELDS:
            self.tree.heading(f, text=f.title(), command=lambda c=f: self.sort_by(c))
            self.tree.column(f, width=self.WIDTHS[f], minwidth=60, anchor="w")
        self.tree.tag_configure("odd", background="#f3f6fa")
        self.tree.tag_configure("even", background="#ffffff")
        xs = ttk.Scrollbar(wrap, orient="horizontal", command=self.tree.xview)
        ys = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(xscrollcommand=xs.set, yscrollcommand=ys.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        ys.grid(row=0, column=1, sticky="ns")
        xs.grid(row=1, column=0, sticky="ew")
        wrap.rowconfigure(0, weight=1)
        wrap.columnconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", self.show_details)

        # ---- detail panel (full record of the selected row)
        box = ttk.LabelFrame(self, text="Selected record", padding=8)
        box.pack(fill="x")
        self.details = tk.StringVar(value="Click a row to see the full record.")
        ttk.Label(box, textvariable=self.details, justify="left",
                  wraplength=1100).pack(anchor="w")
        self.load()

    # ---- actions
    def generate(self):
        if Faker is None:
            return messagebox.showerror("Missing library", "Run: pip install faker")
        try:
            n = int(self.count.get())
        except (tk.TclError, ValueError):
            return messagebox.showerror("Invalid", "Enter a whole number.")
        if n < 10:
            return messagebox.showwarning("Minimum", "Generate at least 10 records.")
        fake = Faker("en_PH")
        rows = []
        for _ in range(n):
            gender = random.choice(["Male", "Female"])
            name = fake.name_male() if gender == "Male" else fake.name_female()
            username, email = make_login(name)
            rows.append((name, fake.address().replace("\n", ", "),
                         fake.date_of_birth(minimum_age=18, maximum_age=70).isoformat(),
                         ph_mobile(), email, fake.job(),
                         fake.company(), username, gender, fake.city()))
        with get_conn() as c:
            c.executemany("INSERT INTO fake_people(" + ",".join(self.FIELDS) +
                          ") VALUES(?,?,?,?,?,?,?,?,?,?)", rows)
        self.search.set("")
        self.load()

    def load(self):
        term = self.search.get().strip()
        query = "SELECT id," + ",".join(self.FIELDS) + " FROM fake_people"
        params = ()
        if term:
            query += " WHERE " + " OR ".join(f"{f} LIKE ?" for f in self.FIELDS)
            params = (f"%{term}%",) * len(self.FIELDS)
        query += " ORDER BY id DESC"
        with get_conn() as c:
            rows = c.execute(query, params).fetchall()
            total = c.execute("SELECT COUNT(*) FROM fake_people").fetchone()[0]
        self.tree.delete(*self.tree.get_children())
        for i, r in enumerate(rows):
            self.tree.insert("", "end", iid=str(r[0]), values=r[1:],
                             tags=("odd" if i % 2 else "even",))
        self.status.config(text=f"{len(rows)} shown of {total} stored records"
                           if term else f"{total} records stored")
        self.details.set("Click a row to see the full record.")

    def show_details(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0])["values"]
        self.details.set(
            f"Name: {v[0]}     Gender: {v[8]}     Birthdate: {v[2]}     Mobile: {v[3]}\n"
            f"Address: {v[1]}, {v[9]}\n"
            f"Email: {v[4]}     Username: {v[7]}\n"
            f"Job: {v[5]}     Company: {v[6]}")

    def sort_by(self, col):
        reverse = self.sort_rev.get(col, False)
        items = [(self.tree.set(i, col).lower(), i) for i in self.tree.get_children("")]
        items.sort(reverse=reverse)
        for idx, (_, iid) in enumerate(items):
            self.tree.move(iid, "", idx)
            self.tree.item(iid, tags=("odd" if idx % 2 else "even",))
        self.sort_rev[col] = not reverse

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showinfo("Select", "Select one or more rows first.")
        if messagebox.askyesno("Delete", f"Delete {len(sel)} selected record(s)?"):
            with get_conn() as c:
                c.executemany("DELETE FROM fake_people WHERE id=?", [(i,) for i in sel])
            self.load()

    def export(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        with get_conn() as c:
            rows = c.execute("SELECT " + ",".join(self.FIELDS) +
                             " FROM fake_people ORDER BY id").fetchall()
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(self.FIELDS)
            w.writerows(rows)
        messagebox.showinfo("Exported", f"{len(rows)} records saved to {path}")

    def clear(self):
        if messagebox.askyesno("Clear", "Delete all stored records?"):
            with get_conn() as c:
                c.execute("DELETE FROM fake_people")
            self.load()


# ---------------------------------------------------------------- MAIN APP
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SIA 2 Lab - Utilities Mini Project")
        self.geometry("460x330")
        self.show_login()

    def clear(self):
        for w in self.winfo_children():
            w.destroy()

    def show_login(self):
        self.clear()
        self.geometry("460x330")
        self.unbind("<Return>")
        LoginFrame(self, self.show_dashboard).pack(expand=True)

    def show_dashboard(self, username):
        self.clear()
        self.unbind("<Return>")
        self.geometry("1200x680")
        header = ttk.Frame(self, padding=(15, 8))
        header.pack(fill="x")
        ttk.Label(header, text=f"Welcome, {username}", font=("Segoe UI", 12, "bold")).pack(side="left")
        ttk.Button(header, text="Logout", command=self.show_login).pack(side="right")
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        nb.add(UrlTab(nb, username), text="URL Shortener")
        nb.add(MessageTab(nb), text="SMS & Email")
        nb.add(FakeDataTab(nb), text="Fake Data Generator")


if __name__ == "__main__":
    init_db()
    App().mainloop()