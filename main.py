
import tkinter as tk
from login import LoginApp
from register import RegisterApp
from dashboard import DashboardApp
from generate import GenerateApp
from utilities import UtilityScreen


class DataGenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SIA Utilities")
        self.root.geometry("1100x700")
        self.root.configure(bg="#F8FAFC")

        self.show_login()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_screen()
        LoginApp(self.root, self)

    def show_register(self):
        self.clear_screen()
        RegisterApp(self.root, self)

    def show_dashboard(self):
        self.clear_screen()
        DashboardApp(self.root, self)

    def show_generate(self):
        self.clear_screen()
        GenerateApp(self.root, self)

    def show_url_shortener(self):
        self.clear_screen()
        UtilityScreen(self.root, self, "URL Shortener")

    def show_messaging(self):
        self.clear_screen()
        UtilityScreen(self.root, self, "SMS / Email")


if __name__ == "__main__":
    root = tk.Tk()
    app = DataGenApp(root)
    root.mainloop()