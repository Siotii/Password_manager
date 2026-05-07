import os
import re
import secrets
import string
import tkinter as tk
from tkinter import messagebox, ttk

from PIL import Image, ImageTk

import database

database.init_db()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BG_COLOR = "#1e1e2f"
FIELD_COLOR = "#2b2b3c"
BUTTON_COLOR = "#4CAF50"
SECONDARY_COLOR = "#3a3a4f"
TEXT_MUTED = "#bfbfbf"
WINDOW_WIDTH = 950
WINDOW_HEIGHT = 760
PAGE_WIDTH = 680
PAGE_HEIGHT = 520
REQUIREMENTS_TEXT = (
    "Minimum: 8+ characters, uppercase, lowercase, number, and symbol (!@#$%^&*)"
)



def password_requirements(password):
    checks = {
        "At least 8 characters": len(password) >= 8,
        "Uppercase letter": bool(re.search(r"[A-Z]", password)),
        "Lowercase letter": bool(re.search(r"[a-z]", password)),
        "Number": bool(re.search(r"\d", password)),
        "Symbol (!@#$%^&*)": bool(re.search(r"[!@#$%^&*]", password)),
    }
    return checks


def password_meets_requirements(password):
    return all(password_requirements(password).values())


def check_password_strength(password):
    score = sum(password_requirements(password).values())

    if score <= 2:
        return "Weak", "#ff6961"
    if score <= 4:
        return "Medium", "#ffb347"
    return "Strong", "#77dd77"


def generate_password(length=14):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%^&*"),
    ]
    password.extend(secrets.choice(chars) for _ in range(length - len(password)))
    secrets.SystemRandom().shuffle(password)
    return "".join(password)


def generate_memorable_password():
    words = [
        "River", "Cloud", "Pixel", "Garden", "Silver", "Nova",
        "Maple", "Rocket", "Velvet", "Anchor", "Sunset", "Marble",
    ]
    symbol = secrets.choice("!@#$%^&*")
    number = secrets.randbelow(90) + 10
    return f"{secrets.choice(words)}-{secrets.choice(words)}{number}{symbol}"



def styled_label(parent, text, **kwargs):
    return tk.Label(
        parent,
        text=text,
        fg=TEXT_MUTED,
        bg=BG_COLOR,
        font=("Segoe UI", 11, "bold"),
        **kwargs,
    )


def styled_entry(parent, show=None):
    return tk.Entry(
        parent,
        show=show,
        bg=FIELD_COLOR,
        fg="white",
        insertbackground="white",
        relief="flat",
        width=32,
        font=("Segoe UI", 10),
    )


def styled_button(parent, text, command, color=BUTTON_COLOR, width=25):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=color,
        fg="white",
        activebackground=color,
        activeforeground="white",
        relief="flat",
        width=width,
        cursor="hand2",
        font=("Segoe UI", 10, "bold"),
    )



class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("PadFlock Password Manager")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.user_id = None

        self.canvas = tk.Canvas(
            self,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        bg_path = os.path.join(BASE_DIR, "Padflockbg.jpeg")
        logo_path = os.path.join(BASE_DIR, "Padflock logo.png")

        bg_img = Image.open(bg_path).resize((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.bg = ImageTk.PhotoImage(bg_img)

        logo_img = Image.open(logo_path).resize((100, 100))
        self.logo = ImageTk.PhotoImage(logo_img)

        self.canvas.create_image(0, 0, image=self.bg, anchor="nw")
        center_x = WINDOW_WIDTH // 2
        self.canvas.create_image(center_x, 98, image=self.logo)
        self.canvas.create_text(
            center_x, 184,
            text="PadFlock",
            fill="white",
            font=("Segoe UI", 24, "bold")
        )

        self.frame_container = tk.Frame(
            self.canvas,
            bg=BG_COLOR,
            width=PAGE_WIDTH,
            height=PAGE_HEIGHT,
        )
        self.frame_container.grid_propagate(False)
        self.frame_container.grid_rowconfigure(0, weight=1)
        self.frame_container.grid_columnconfigure(0, weight=1)
        self.canvas.create_window(center_x, 470, window=self.frame_container)

        self.login_page = LoginPage(self.frame_container, self)
        self.register_page = RegisterPage(self.frame_container, self)
        self.vault_page = VaultPage(self.frame_container, self)

        for page in (self.login_page, self.register_page, self.vault_page):
            page.grid(row=0, column=0, sticky="nsew")

        self.show_login()

    def show_login(self):
        self.login_page.clear()
        self.login_page.tkraise()

    def show_register(self):
        self.register_page.clear()
        self.register_page.tkraise()

    def show_vault(self):
        self.vault_page.load_data()
        self.vault_page.tkraise()

    def logout(self):
        self.user_id = None
        self.vault_page.clear()
        self.show_login()


class LoginPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(
            parent,
            bg=BG_COLOR,
            width=PAGE_WIDTH,
            height=PAGE_HEIGHT,
            padx=42,
            pady=36,
        )
        self.app = app

        tk.Label(
            self,
            text="Welcome Back",
            font=("Segoe UI", 18, "bold"),
            fg="white",
            bg=BG_COLOR,
        ).pack(pady=(0, 18))

        form = tk.Frame(self, bg=BG_COLOR)
        form.pack()

        styled_label(form, "Username").pack(anchor="w")
        self.username = styled_entry(form)
        self.username.pack(pady=8, ipady=7)

        styled_label(form, "Password").pack(anchor="w")
        self.password = styled_entry(form, show="*")
        self.password.pack(pady=8, ipady=7)
        self.password.bind("<Return>", lambda _event: self.login())

        styled_button(form, "Login", self.login).pack(pady=(16, 8), ipady=7)
        styled_button(
            form,
            "Create Account",
            self.app.show_register,
            color=SECONDARY_COLOR,
        ).pack(ipady=6)

    def clear(self):
        self.password.delete(0, tk.END)

    def login(self):
        username = self.username.get().strip()
        password = self.password.get()

        if not username or not password:
            messagebox.showerror("Missing Details", "Enter your username and password.")
            return

        user_id = database.login_user(username, password)
        if user_id:
            self.app.user_id = user_id
            self.app.show_vault()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")


class RegisterPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(
            parent,
            bg=BG_COLOR,
            width=PAGE_WIDTH,
            height=PAGE_HEIGHT,
            padx=42,
            pady=28,
        )
        self.app = app

        tk.Label(
            self,
            text="Create Account",
            font=("Segoe UI", 18, "bold"),
            fg="white",
            bg=BG_COLOR,
        ).pack(pady=(0, 12))

        form = tk.Frame(self, bg=BG_COLOR)
        form.pack()

        styled_label(form, "Username").pack(anchor="w")
        self.username = styled_entry(form)
        self.username.pack(pady=7, ipady=7)

        styled_label(form, "Master Password").pack(anchor="w")
        self.password = styled_entry(form, show="*")
        self.password.pack(pady=7, ipady=7)
        self.password.bind("<KeyRelease>", lambda _event: self.update_strength())

        self.strength_label = tk.Label(
            form,
            text=REQUIREMENTS_TEXT,
            fg=TEXT_MUTED,
            bg=BG_COLOR,
            wraplength=285,
            justify="left",
            font=("Segoe UI", 8),
        )
        self.strength_label.pack(anchor="w", pady=(0, 8))

        styled_label(form, "Confirm Password").pack(anchor="w")
        self.confirm = styled_entry(form, show="*")
        self.confirm.pack(pady=7, ipady=7)

        styled_button(form, "Register", self.register, color="#2196F3").pack(
            pady=(14, 8),
            ipady=7,
        )
        styled_button(form, "Back to Login", self.app.show_login, color=SECONDARY_COLOR).pack(
            ipady=6
        )

    def clear(self):
        for field in (self.username, self.password, self.confirm):
            field.delete(0, tk.END)
        self.strength_label.config(text=REQUIREMENTS_TEXT, fg=TEXT_MUTED)

    def update_strength(self):
        password = self.password.get()
        strength, color = check_password_strength(password)
        missing = [
            label for label, passed in password_requirements(password).items()
            if not passed
        ]

        if not password:
            self.strength_label.config(text=REQUIREMENTS_TEXT, fg=TEXT_MUTED)
        elif missing:
            self.strength_label.config(
                text=f"Strength: {strength}. Missing: {', '.join(missing)}",
                fg=color,
            )
        else:
            self.strength_label.config(text="Strength: Strong. Requirements met.", fg=color)

    def register(self):
        username = self.username.get().strip()
        password = self.password.get()

        if not username:
            messagebox.showerror("Missing Username", "Enter a username.")
            return
        if password != self.confirm.get():
            messagebox.showerror("Password Mismatch", "Passwords do not match.")
            return
        if not password_meets_requirements(password):
            messagebox.showerror("Weak Password", REQUIREMENTS_TEXT)
            return

        if database.register_user(username, password):
            messagebox.showinfo("Account Created", "Your account is ready. Please log in.")
            self.app.show_login()
        else:
            messagebox.showerror("Username Taken", "That username already exists.")


class VaultPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(
            parent,
            bg=BG_COLOR,
            width=PAGE_WIDTH,
            height=PAGE_HEIGHT,
            padx=36,
            pady=22,
        )
        self.app = app

        header = tk.Frame(self, bg=BG_COLOR)
        header.pack(fill="x", pady=(0, 10))

        tk.Label(
            header,
            text="Password Vault",
            font=("Segoe UI", 18, "bold"),
            fg="white",
            bg=BG_COLOR,
        ).pack(side="left")

        styled_button(header, "Logout", self.app.logout, color=SECONDARY_COLOR, width=9).pack(
            side="right"
        )

        form = tk.Frame(self, bg=BG_COLOR)
        form.pack(fill="x")

        styled_label(form, "Site / App").grid(row=0, column=0, sticky="w")
        styled_label(form, "Username / Email").grid(row=0, column=1, sticky="w", padx=(14, 0))

        self.site = styled_entry(form)
        self.site.config(width=22)
        self.site.grid(row=1, column=0, pady=6, ipady=7, sticky="w")

        self.username = styled_entry(form)
        self.username.config(width=28)
        self.username.grid(row=1, column=1, padx=(14, 0), pady=6, ipady=7, sticky="w")

        styled_label(form, "Password").grid(row=2, column=0, sticky="w", pady=(6, 0))
        self.password = styled_entry(form)
        self.password.config(width=44)
        self.password.grid(row=3, column=0, columnspan=2, pady=6, ipady=7, sticky="we")
        self.password.bind("<KeyRelease>", lambda _event: self.update_password_status())

        self.status = tk.Label(
            form,
            text=REQUIREMENTS_TEXT,
            fg=TEXT_MUTED,
            bg=BG_COLOR,
            wraplength=550,
            justify="left",
            font=("Segoe UI", 8),
        )
        self.status.grid(row=4, column=0, columnspan=2, sticky="w", pady=(0, 8))

        actions = tk.Frame(form, bg=BG_COLOR)
        actions.grid(row=5, column=0, columnspan=2, sticky="we", pady=(3, 12))

        styled_button(actions, "Generate Strong", self.generate, color="#2196F3", width=15).pack(
            side="left",
            ipady=6,
        )
        styled_button(
            actions,
            "Memorable",
            self.generate_memorable,
            color=SECONDARY_COLOR,
            width=12,
        ).pack(side="left", padx=8, ipady=6)
        styled_button(actions, "Save", self.save, width=11).pack(side="left", ipady=6)

        tk.Label(
            self,
            text="Saved Passwords",
            font=("Segoe UI", 11, "bold"),
            fg="white",
            bg=BG_COLOR,
        ).pack(anchor="w", pady=(2, 4))

        table_frame = tk.Frame(self, bg=BG_COLOR)
        table_frame.pack(fill="both")

        columns = ("site", "username", "password")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        self.table.heading("site", text="Site")
        self.table.heading("username", text="Username")
        self.table.heading("password", text="Password")
        self.table.column("site", width=170, anchor="w")
        self.table.column("username", width=190, anchor="w")
        self.table.column("password", width=240, anchor="w")
        self.table.pack(side="left")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        scrollbar.pack(side="right", fill="y")
        self.table.configure(yscrollcommand=scrollbar.set)

    def clear(self):
        for field in (self.site, self.username, self.password):
            field.delete(0, tk.END)
        self.status.config(text=REQUIREMENTS_TEXT, fg=TEXT_MUTED)
        for item in self.table.get_children():
            self.table.delete(item)

    def update_password_status(self):
        password = self.password.get()
        strength, color = check_password_strength(password)
        missing = [
            label for label, passed in password_requirements(password).items()
            if not passed
        ]

        if not password:
            self.status.config(text=REQUIREMENTS_TEXT, fg=TEXT_MUTED)
        elif missing:
            self.status.config(
                text=f"Strength: {strength}. Missing: {', '.join(missing)}",
                fg=color,
            )
        else:
            self.status.config(text="Strength: Strong. Requirements met.", fg=color)

    def generate(self):
        self.password.delete(0, tk.END)
        self.password.insert(0, generate_password())
        self.update_password_status()

    def generate_memorable(self):
        self.password.delete(0, tk.END)
        self.password.insert(0, generate_memorable_password())
        self.update_password_status()

    def save(self):
        site = self.site.get().strip()
        username = self.username.get().strip()
        password = self.password.get()

        if not site or not username or not password:
            messagebox.showerror("Missing Details", "Site, username, and password are required.")
            return
        if not password_meets_requirements(password):
            messagebox.showerror("Weak Password", REQUIREMENTS_TEXT)
            return
        if database.is_duplicate(self.app.user_id, password):
            messagebox.showwarning(
                "Duplicate Password",
                "This password is already saved. Use a unique password for better security.",
            )
            return

        try:
            database.save_password(self.app.user_id, site, username, password)
        except ValueError as error:
            messagebox.showerror("Unable to Save", str(error))
            return

        messagebox.showinfo("Saved", "Password saved securely.")
        self.site.delete(0, tk.END)
        self.username.delete(0, tk.END)
        self.password.delete(0, tk.END)
        self.update_password_status()
        self.load_data()

    def load_data(self):
        for item in self.table.get_children():
            self.table.delete(item)

        if not self.app.user_id:
            return

        for site, user, password in database.get_passwords(self.app.user_id):
            self.table.insert("", tk.END, values=(site, user, password))



if __name__ == "__main__":
    App().mainloop()
