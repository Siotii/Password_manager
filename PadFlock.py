import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import hashlib
import sqlite3

def conn2db():
    conn = sqlite3.connect('crowsnest.db')
    cursor = conn.cursor()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

STORED_HASH = hash_password("password123")

def check_password():
    entered = password_entry.get()
    entered_hash = hash_password(entered)

    if entered_hash == STORED_HASH:
        messagebox.showinfo("Login", "Access Granted")
    else:
        messagebox.showerror("Login", "Access Denied")

    password_entry.delete(0, tk.END)


root = tk.Tk()
root.title("Password Login")
root.geometry("450x350")

canvas = tk.Canvas(root, width=450, height=350, highlightthickness=0)
canvas.pack(fill="both", expand=True)

bg_image = Image.open(r"C:\Users\cymon\WebProgramming\Password\Padflockbg.jpeg")
bg_image = bg_image.resize((450, 350))
bg = ImageTk.PhotoImage(bg_image)
canvas.create_image(0, 0, image=bg, anchor="nw")


logo_img = Image.open(r"C:\Users\cymon\WebProgramming\Password\Padflock logo.png")
logo_img = logo_img.resize((80, 80))
logo = ImageTk.PhotoImage(logo_img)
canvas.create_image(225, 60, image=logo)

canvas.create_text(225, 140,
                   text="Enter Master Password:",
                   fill="white",
                   font=("Arial", 12, "bold"))


password_entry = tk.Entry(root, width=25, show="*", bd=0)
canvas.create_window(225, 170, window=password_entry)


login_btn = tk.Button(root, text="Login", command=check_password)
canvas.create_window(225, 210, window=login_btn)

root.mainloop()

print("hello")
print("1")