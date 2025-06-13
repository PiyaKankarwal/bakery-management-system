import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
from datetime import datetime

# Connect to MySQL
try:
    con = mysql.connector.connect(host="localhost", user="root", password="your_sql_psswd_here", database="items")
    cursor = con.cursor()
except mysql.connector.Error as err:
    messagebox.showerror("Database Error", f"Could not connect to database:\n{err}")
    exit()

# GUI Setup
root = tk.Tk()
root.title("Butter-Cup Bakes")
root.geometry("800x550")
root.configure(bg="#FFF0F5")  # Light pink background

font_heading = ("Georgia", 26, "bold")
font_sub = ("Georgia", 14, "italic")
font_label = ("Georgia", 12)
btn_color = "#FFC1CC"

# Welcome Frame
welcome_frame = tk.Frame(root, bg="#FFF6F0", bd=5, relief="groove")
welcome_frame.pack(pady=40, padx=20, fill="both", expand=True)

# Title
title = tk.Label(welcome_frame, text="🍰 Welcome to BUTTER-CUP BAKES 🍰", font=font_heading, bg="#FFF6F0", fg="#C36868")
title.pack(pady=15)

# Tagline
tagline = tk.Label(welcome_frame, text="Freshly baked happiness, just a click away!", font=font_sub, bg="#FFF6F0", fg="#A05252")
tagline.pack()

# Main Menu Actions
def open_admin():
    password = simpledialog.askstring("Admin Login", "Hello Admin. Please enter your password:", show='*')
    if password == "PASSWORD":
        messagebox.showinfo("Welcome", "HELLO, admin! You Logged In As Admin Successfully")
        show_admin_menu()
    else:
        messagebox.showerror("Access Denied", "Incorrect password. Access denied.")

def open_customer():
    name = simpledialog.askstring("Customer", "Enter your name:")
    phone = simpledialog.askstring("Customer", "Enter your phone number:")
    if not name or not phone:
        return
    show_customer_menu(name, phone)

def show_admin_menu():
    top = tk.Toplevel()
    top.title("Admin Panel")
    top.configure(bg="#FFF6F0")

    tk.Label(top, text="Admin Options", font=font_heading, bg="#FFF6F0", fg="#C36868").pack(pady=10)

    def add_item():
        sno = simpledialog.askinteger("Input", "Enter item serial number:")
        name = simpledialog.askstring("Input", "Enter item name:")
        cost = simpledialog.askinteger("Input", "Enter item cost:")
        if sno and name and cost is not None:
            cursor.execute("INSERT INTO cs VALUES (%s, %s, %s)", (sno, name, cost))
            con.commit()
            messagebox.showinfo("Success", "Item added successfully.")

    def show_items():
        show_table("SELECT * FROM cs", ("S.No", "Product", "Cost"), "Bakery Items")

    def update_cost():
        sno = simpledialog.askinteger("Input", "Enter item serial number:")
        new_cost = simpledialog.askinteger("Input", "Enter new cost:")
        if sno is None or new_cost is None:
            return
        cursor.execute("UPDATE cs SET cost = %s WHERE sno = %s", (new_cost, sno))
        con.commit()
        messagebox.showinfo("Updated", "Cost updated successfully.")

    def add_variety():
        sno = simpledialog.askinteger("Input", "Enter variety serial number:")
        name = simpledialog.askstring("Input", "Enter variety name:")
        ptype = simpledialog.askstring("Input", "Enter product type (cake/cupcake/pastery):")
        cost = simpledialog.askinteger("Input", "Enter cost:")
        if None in (sno, name, ptype, cost):
            return
        cursor.execute("INSERT INTO vip VALUES (%s, %s, %s, %s)", (sno, name, ptype, cost))
        con.commit()
        messagebox.showinfo("Added", "Variety added successfully.")

    def add_worker():
        wid = simpledialog.askinteger("Input", "Enter worker ID:")
        name = simpledialog.askstring("Input", "Enter worker name:")
        salary = simpledialog.askinteger("Input", "Enter salary:")
        if None in (wid, name, salary):
            return
        cursor.execute("INSERT INTO worker VALUES (%s, %s, %s)", (wid, name, salary))
        con.commit()
        messagebox.showinfo("Added", "Worker added successfully.")

    def show_workers():
        show_table("SELECT * FROM worker", ("ID", "Name", "Salary"), "Worker List")

    def update_salary():
        wid = simpledialog.askinteger("Input", "Enter worker ID:")
        action = simpledialog.askstring("Input", "Increase or Decrease salary? (i/d):")
        amount = simpledialog.askinteger("Input", "Enter amount:")
        if None in (wid, action, amount):
            return
        cursor.execute("SELECT salary FROM worker WHERE id = %s", (wid,))
        salary = cursor.fetchone()
        if salary:
            updated = salary[0] + amount if action == 'i' else salary[0] - amount
            cursor.execute("UPDATE worker SET salary = %s WHERE id = %s", (updated, wid))
            con.commit()
            messagebox.showinfo("Updated", "Salary updated.")
        else:
            messagebox.showerror("Error", "Worker not found.")

    options = [
        ("ADD Item", add_item),
        ("See Items", show_items),
        ("Update Item Cost", update_cost),
        ("Add Cake Varieties", add_variety),
        ("Add Worker", add_worker),
        ("View Workers", show_workers),
        ("Update Worker Salary", update_salary),
    ]

    for text, cmd in options:
        tk.Button(top, text=text, command=cmd, font=font_label, bg=btn_color).pack(pady=5)

def show_customer_menu(name, phone):
    top = tk.Toplevel()
    top.title("Customer Panel")
    top.configure(bg="#FFF6F0")

    def see_menu():
        show_table("SELECT * FROM cs", ("S.No", "Product", "Cost"), "Bakery Menu")

    def place_order():
        cursor.execute("SELECT * FROM cs")
        products = cursor.fetchall()
        sno = simpledialog.askinteger("Order", "Enter S.No to order:")
        selected = next((i for i in products if i[0] == sno), None)
        if not selected:
            messagebox.showerror("Error", "Invalid item.")
            return
        if selected[1] in ["cake", "cupcake", "pastery"]:
            cursor.execute("SELECT sno, varieties FROM vip WHERE product_type = %s", (selected[1],))
            varieties = cursor.fetchall()
            vlist = "\n".join([f"{v[0]}: {v[1]}" for v in varieties])
            vsno = simpledialog.askinteger("Variety", f"Choose variety:\n{vlist}")
            cursor.execute("SELECT varieties, cost FROM vip WHERE sno = %s", (vsno,))
            vdata = cursor.fetchone()
            if not vdata:
                return
            variety, cost = vdata
            qty = simpledialog.askinteger("Quantity", f"How many {variety} {selected[1]}?")
            if qty is None:
                return
            total = qty * cost
        else:
            qty = simpledialog.askinteger("Quantity", f"How many {selected[1]}?")
            if qty is None:
                return
            total = qty * selected[2]
            variety = "-"

        messagebox.showinfo("Bill", f"Customer: {name}\nPhone: {phone}\nItem: {selected[1]} - {variety}\nQuantity: {qty}\nTotal: ₹{total}\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tk.Button(top, text="See Menu", command=see_menu, font=font_label, bg=btn_color).pack(pady=10)
    tk.Button(top, text="Order Item", command=place_order, font=font_label, bg=btn_color).pack(pady=10)

def show_table(query, cols, title):
    win = tk.Toplevel()
    win.title(title)
    win.configure(bg="#FFF6F0")

    tree = ttk.Treeview(win, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=120)
    cursor.execute(query)
    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)
    tree.pack(pady=20)


# Buttons
tk.Button(welcome_frame, text="ADMIN", command=open_admin, font=font_label, bg=btn_color, width=25).pack(pady=20)
tk.Button(welcome_frame, text="CUSTOMER", command=open_customer, font=font_label, bg=btn_color, width=25).pack(pady=5)
tk.Button(welcome_frame, text="EXIT", command=root.destroy, font=font_label, bg=btn_color, width=25).pack(pady=5)

root.mainloop()
