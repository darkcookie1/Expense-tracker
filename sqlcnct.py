import mysql.connector
from mysql.connector import Error
from tkinter import Tk, Label, Entry, Button, Listbox, END, messagebox, Frame, Scrollbar, VERTICAL, RIGHT, Y
from tkinter.font import Font
from datetime import datetime

# Set a default monthly expense limit
monthly_limit = 1000  # Set this as needed; users can also change it in the app.

# Set your default table name here
table_name = "money"  # Change this to your actual table name

# Connect to MySQL Database
def connect_to_mysql():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',     # Replace with your MySQL username
            password='Suraj@123', # Replace with your MySQL password
            database='expense_tracker'  # Replace with your MySQL database name
        )
        return connection
    except Error as e:
        print("Error while connecting to MySQL", e)
        return None

# Update the monthly limit from user input
def set_monthly_limit():
    global monthly_limit
    try:
        limit = float(monthly_limit_entry.get())
        monthly_limit = limit
        messagebox.showinfo("Limit Set", f"Monthly limit set to ${limit:.2f}.")
        check_monthly_expenses()  # Check expenses after setting a new limit
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number for the monthly limit.")

# Check total monthly expenses and send a warning if limit is close to being crossed or has been crossed
def check_monthly_expenses():
    connection = connect_to_mysql()
    if connection:
        cursor = connection.cursor()
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        query = f"SELECT SUM(amount) FROM {table_name} WHERE MONTH(date) = %s AND YEAR(date) = %s"
        cursor.execute(query, (current_month, current_year))
        total_expenses = cursor.fetchone()[0] or 0
        cursor.close()
        connection.close()

        if total_expenses > monthly_limit:
            messagebox.showwarning("Limit Exceeded", f"Warning: Monthly expense limit of ${monthly_limit:.2f} has been crossed!")
        elif total_expenses >= 0.8 * monthly_limit:
            messagebox.showwarning("Approaching Limit", f"Warning: Monthly expenses have reached 80% of your limit (${monthly_limit:.2f}).")

# Insert an expense into the specified table
def add_expense():
    date = date_entry.get()
    amount = amount_entry.get()
    category = category_entry.get()
    description = description_entry.get()

    if not (date and amount and category):
        messagebox.showwarning("Input Error", "Please fill in all fields.")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Input Error", "Amount should be a number.")
        return

    connection = connect_to_mysql()
    if connection:
        cursor = connection.cursor()
        try:
            query = f"INSERT INTO {table_name} (date, amount, category, description) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (date, amount, category, description))
            connection.commit()
            messagebox.showinfo("Success", "Expense added successfully.")
            clear_textboxes()  # Clear input fields after successful addition
        except Error as e:
            messagebox.showerror("Database Error", f"Error while inserting expense: {e}")
        finally:
            cursor.close()
            connection.close()
        
        display_expenses()
        check_monthly_expenses()  # Check expenses after adding a new one

# Function to update the selected expense
def update_expense():
    selected_item = expenses_listbox.curselection()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select an expense to update.")
        return

    selected_index = selected_item[0]
    expense_data = expenses_listbox.get(selected_index).split(" - ")
    
    # Update the text boxes with the selected expense's details
    date_entry.delete(0, END)
    date_entry.insert(0, expense_data[1])
    amount_entry.delete(0, END)
    amount_entry.insert(0, expense_data[2].replace('$', ''))
    category_entry.delete(0, END)
    category_entry.insert(0, expense_data[3])
    description_entry.delete(0, END)
    description_entry.insert(0, expense_data[4])
    
    # Button to confirm update
    Button(input_frame, text="Confirm Update", command=lambda: confirm_update(expense_data[0]), font=button_font, bg="#ff9900", fg="white").grid(row=8, column=0, columnspan=3, pady=5)

def confirm_update(expense_id):
    date = date_entry.get()
    amount = amount_entry.get()
    category = category_entry.get()
    description = description_entry.get()

    if not (date and amount and category):
        messagebox.showwarning("Input Error", "Please fill in all fields.")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Input Error", "Amount should be a number.")
        return

    connection = connect_to_mysql()
    if connection:
        cursor = connection.cursor()
        try:
            query = f"UPDATE {table_name} SET date = %s, amount = %s, category = %s, description = %s WHERE id = %s"
            cursor.execute(query, (date, amount, category, description, expense_id))
            connection.commit()
            messagebox.showinfo("Success", "Expense updated successfully.")
            clear_textboxes()  # Clear input fields after successful update
        except Error as e:
            messagebox.showerror("Database Error", f"Error while updating expense: {e}")
        finally:
            cursor.close()
            connection.close()
        
        display_expenses()
        check_monthly_expenses()  # Check expenses after updating

# Function to delete the selected expense
def delete_expense():
    selected_item = expenses_listbox.curselection()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select an expense to delete.")
        return

    expense_id = expenses_listbox.get(selected_item[0]).split(" - ")[0]
    
    connection = connect_to_mysql()
    if connection:
        cursor = connection.cursor()
        try:
            query = f"DELETE FROM {table_name} WHERE id = %s"
            cursor.execute(query, (expense_id,))
            connection.commit()
            messagebox.showinfo("Success", "Expense deleted successfully.")
        except Error as e:
            messagebox.showerror("Database Error", f"Error while deleting expense: {e}")
        finally:
            cursor.close()
            connection.close()
        
        display_expenses()
        check_monthly_expenses()  # Check expenses after deleting

# Function to clear all input fields
def clear_textboxes():
    date_entry.delete(0, END)
    amount_entry.delete(0, END)
    category_entry.delete(0, END)
    description_entry.delete(0, END)
    monthly_limit_entry.delete(0, END)

# Display expenses in the Listbox
def display_expenses():
    expenses_listbox.delete(0, END)

    connection = connect_to_mysql()
    if connection:
        cursor = connection.cursor()
        try:
            query = f"SELECT id, date, amount, category, description FROM {table_name} ORDER BY date DESC"
            cursor.execute(query)
            records = cursor.fetchall()
            for record in records:
                expenses_listbox.insert(END, f"{record[0]} - {record[1]} - ${record[2]} - {record[3]} - {record[4]}")
        except Error as e:
            messagebox.showerror("Database Error", f"Error while fetching expenses: {e}")
        finally:
            cursor.close()
            connection.close()

# Tkinter UI setup
root = Tk()
root.title("Expense Tracker")
root.geometry("500x600")
root.config(bg="#2e3f4f")

# Styling
header_font = Font(family="Helvetica", size=16, weight="bold")
label_font = Font(family="Helvetica", size=12)
button_font = Font(family="Helvetica", size=12, weight="bold")

# Frame for inputs
input_frame = Frame(root, bg="#34495e", padx=10, pady=10)
input_frame.pack(pady=10, padx=10, fill="both", expand=True)

Label(input_frame, text="Expense Tracker", font=header_font, fg="white", bg="#34495e").grid(row=0, column=0, columnspan=3, pady=10)

# Monthly limit
Label(input_frame, text="Monthly Limit ($):", font=label_font, bg="#34495e", fg="white").grid(row=1, column=0, padx=5, pady=5, sticky="e")
monthly_limit_entry = Entry(input_frame)
monthly_limit_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

Button(input_frame, text="Set Limit", command=set_monthly_limit, font=button_font, bg="#007acc", fg="white").grid(row=1, column=2, padx=5, pady=5)

# Labels and Entries for expenses
Label(input_frame, text="Date (YYYY-MM-DD):", font=label_font, bg="#34495e", fg="white").grid(row=2, column=0, padx=5, pady=5, sticky="e")
date_entry = Entry(input_frame)
date_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

Label(input_frame, text="Amount:", font=label_font, bg="#34495e", fg="white").grid(row=3, column=0, padx=5, pady=5, sticky="e")
amount_entry = Entry(input_frame)
amount_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

Label(input_frame, text="Category:", font=label_font, bg="#34495e", fg="white").grid(row=4, column=0, padx=5, pady=5, sticky="e")
category_entry = Entry(input_frame)
category_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

Label(input_frame, text="Description:", font=label_font, bg="#34495e", fg="white").grid(row=5, column=0, padx=5, pady=5, sticky="e")
description_entry = Entry(input_frame)
description_entry.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

# Buttons
Button(input_frame, text="Add Expense", command=add_expense, font=button_font, bg="#ff9900", fg="white").grid(row=6, column=0, columnspan=3, pady=10, sticky="nsew")

# Place Update and Delete buttons in separate rows
Button(input_frame, text="Update Expense", command=update_expense, font=button_font, bg="#007acc", fg="white").grid(row=7, column=0, padx=5, pady=5, sticky="nsew")
Button(input_frame, text="Delete Expense", command=delete_expense, font=button_font, bg="#dc3545", fg="white").grid(row=7, column=1, padx=5, pady=5, sticky="nsew")

Button(input_frame, text="Show Expenses", command=display_expenses, font=button_font, bg="#007acc", fg="white").grid(row=8, column=0, columnspan=3, pady=5, sticky="nsew")

# Listbox to display expenses with scrollbar
listbox_frame = Frame(root, bg="#2e3f4f")
listbox_frame.pack(pady=10, padx=10, fill="both", expand=True)

scrollbar = Scrollbar(listbox_frame, orient=VERTICAL)
expenses_listbox = Listbox(listbox_frame, width=50, height=10, yscrollcommand=scrollbar.set, bg="#34495e", fg="white", font=label_font, selectbackground="#4CAF50", selectforeground="black")
scrollbar.config(command=expenses_listbox.yview)
scrollbar.pack(side=RIGHT, fill=Y)
expenses_listbox.pack(fill="both", expand=True)

# Initialize the app with existing expenses
display_expenses()
check_monthly_expenses()  # Check expenses on startup

# Run the Tkinter main loop
root.mainloop()
