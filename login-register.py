import tkinter as tk
from PIL import Image, ImageTk


def check_login():
    username = username_entry.get()
    password = password_entry.get()

    print("Login clicked")

def register():
    print("Register clicked")

root = tk.Tk()
root.title("PadFlock")
root.geometry("500x500")
root.resizable(False, False)


bg_img = Image.open(r"C:\Users\cymon\WebProgramming\Password\Padflockbg.jpeg")
bg_img = bg_img.resize((500, 500))
bg = ImageTk.PhotoImage(bg_img)

canvas = tk.Canvas(root, width=500, height=500, highlightthickness=0)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg, anchor="nw")


logo_img = Image.open(r"C:\Users\cymon\WebProgramming\Password\Padflock logo.png")
logo_img = logo_img.resize((80, 80))
logo = ImageTk.PhotoImage(logo_img)

canvas.create_image(250, 80, image=logo)
canvas.create_text(250, 140, text="PadFlock", fill="white",
                   font=("Georgia", 16))


canvas.create_text(150, 200, text="Username:",
                   fill="white", font=("Georgia", 12))

username_entry = tk.Entry(root, bd=0, highlightthickness=0,
                          width=25, bg="#d9d9d9")
canvas.create_window(320, 200, window=username_entry)


canvas.create_text(150, 250, text="Password:",
                   fill="white", font=("Georgia", 12))

password_entry = tk.Entry(root, bd=0, highlightthickness=0,
                          width=25, show="*", bg="#d9d9d9")
canvas.create_window(320, 250, window=password_entry)


login_btn = tk.Button(root, text="Log in", width=12, command=check_login)
register_btn = tk.Button(root, text="Register", width=12, command=register)

canvas.create_window(200, 320, window=login_btn)
canvas.create_window(350, 320, window=register_btn)

root.mainloop()