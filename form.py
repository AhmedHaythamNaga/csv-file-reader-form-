import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import requests
import re
import os
from io import StringIO


# Function to create gradient background
def create_gradient(canvas, color1, color2, width, height):
    for i in range(height):
        r = int(color1[1:3], 16) + i * (int(color2[1:3], 16) - int(color1[1:3], 16)) // height
        g = int(color1[3:5], 16) + i * (int(color2[3:5], 16) - int(color1[3:5], 16)) // height
        b = int(color1[5:7], 16) + i * (int(color2[5:7], 16) - int(color1[5:7], 16)) // height
        color = f'#{r:02x}{g:02x}{b:02x}'
        canvas.create_line(0, i, width, i, fill=color)


# Function to open a file dialog to select a CSV file
def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    entry_field.delete(0, tk.END)
    entry_field.insert(0, file_path)


# Function to validate the CSV file
def read_csv():
    file_path = entry_field.get()
    if file_path:
        try:
            if file_path.startswith('http://') or file_path.startswith('https://'):
                # Handling URL
                response = requests.get(file_path)
                if len(response.content) > 1_000_000:
                    messagebox.showerror("Error", "File size exceeds 1MB limit.")
                    return
                content = response.content.decode('utf-8')
            else:
                # Handling local file path
                if os.path.getsize(file_path) > 1_000_000:
                    messagebox.showerror("Error", "File size exceeds 1MB limit.")
                    return
                with open(file_path, newline='') as csvfile:
                    content = csvfile.read()

            reader = csv.DictReader(StringIO(content))
            headers = reader.fieldnames

            required_fields = ['name', 'gender', 'phone number', 'date of birth']
            missing_fields = [field for field in required_fields if field not in headers]

            if missing_fields:
                messagebox.showerror("Error", f"Missing fields: {', '.join(missing_fields)}")
                return

            for row in reader:
                if row['gender'].lower() not in ['male', 'female']:
                    messagebox.showerror("Error", "Invalid gender value. Must be 'male' or 'female'.")
                    return

                if not re.match(r'^\+?\d[\d\s-]{7,}\d$', row['phone number']):
                    messagebox.showerror("Error", "Invalid phone number format.")
                    return

                if not re.match(r'^\d{2}/\d{2}/\d{4}$', row['date of birth']):
                    messagebox.showerror("Error", "Invalid date of birth format. Must be 'day/month/year'.")
                    return

            messagebox.showinfo("CSV Data", "CSV file is valid.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read CSV file: {e}")
    else:
        messagebox.showwarning("Input Error", "Please select a CSV file")


# Create the main window
root = tk.Tk()
root.title("CSV File Reader")
root.geometry("800x600")

# Create a canvas to draw the gradient
canvas = tk.Canvas(root, width=800, height=600, highlightthickness=0)
canvas.pack(fill="both", expand=True)


# Calculate coordinates for rounded rectangle
def draw_rounded_rectangle(canvas, x1, y1, x2, y2, radius):
    canvas.create_arc(x1, y1, x1 + 2 * radius, y1 + 2 * radius, start=90, extent=90, outline="", fill="white")
    canvas.create_arc(x2 - 2 * radius, y1, x2, y1 + 2 * radius, start=0, extent=90, outline="", fill="white")
    canvas.create_arc(x1, y2 - 2 * radius, x1 + 2 * radius, y2, start=180, extent=90, outline="", fill="white")
    canvas.create_arc(x2 - 2 * radius, y2 - 2 * radius, x2, y2, start=270, extent=90, outline="", fill="white")
    canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2, outline="", fill="white")
    canvas.create_rectangle(x1, y1 + radius, x2, y2 - radius, outline="", fill="white")


# Create gradient background on window resize
def on_resize(event):
    canvas.delete("all")
    create_gradient(canvas, "#7f7fd5", "#86a8e7", event.width, event.height)

    # Recalculate frame coordinates
    global frame_x1, frame_y1, frame_x2, frame_y2
    frame_x1 = (event.width - frame_width) // 2
    frame_y1 = (event.height - frame_height) // 2
    frame_x2 = frame_x1 + frame_width
    frame_y2 = frame_y1 + frame_height

    # Redraw rounded rectangle
    draw_rounded_rectangle(canvas, frame_x1, frame_y1, frame_x2, frame_y2, frame_radius)

    # Reposition title label
    title_label.place(relx=0.5, rely=0.3, anchor="center")


# Bind the resize event to the root window
root.bind("<Configure>", on_resize)

# Create a frame-like area with rounded corners
frame_width = 500
frame_height = 300
frame_radius = 20

frame_x1 = (800 - frame_width) // 2
frame_y1 = (600 - frame_height) // 2
frame_x2 = frame_x1 + frame_width
frame_y2 = frame_y1 + frame_height

# Draw the rounded rectangle on the canvas
draw_rounded_rectangle(canvas, frame_x1, frame_y1, frame_x2, frame_y2, frame_radius)

# Create a label
title_label = tk.Label(root, text="CSV File Reader", font=("Helvetica", 24, "bold"), bg="white", fg="blue")
title_label.place(relx=0.5, rely=0.3, anchor="center")


# Placeholder functionality for the entry field
def set_placeholder(event):
    if entry_field.get() == "":
        entry_field.insert(0, "Add CSV file link")
        entry_field.config(fg="grey")


def clear_placeholder(event):
    if entry_field.get() == "Add CSV file link":
        entry_field.delete(0, tk.END)
        entry_field.config(fg="black")


# Create an entry field with padding and flat border
entry_field = tk.Entry(root, width=50, font=("Helvetica", 14), bg="white", fg="grey", bd=1, relief="flat",
                       highlightthickness=1, highlightbackground="grey", highlightcolor="grey", insertwidth=1)
entry_field.insert(0, "Add CSV file link")
entry_field.bind("<FocusIn>", clear_placeholder)
entry_field.bind("<FocusOut>", set_placeholder)
entry_field.place(relx=0.5, rely=0.4, anchor="center", relwidth=0.5, relheight=0.06)


# Custom button class with rounded corners
class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, **kwargs):
        tk.Canvas.__init__(self, parent, highlightthickness=0, **kwargs)
        self.command = command
        self.radius = 20
        self.text = text
        self.create_rounded_button()
        self.configure(bg='white')  # Set background to white

    def create_rounded_button(self):
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        self.create_oval((0, 0, self.radius * 2, self.radius * 2), fill="#007bff", outline="#007bff")
        self.create_oval((width - self.radius * 2, 0, width, self.radius * 2), fill="#007bff", outline="#007bff")
        self.create_oval((0, height - self.radius * 2, self.radius * 2, height), fill="#007bff", outline="#007bff")
        self.create_oval((width - self.radius * 2, height - self.radius * 2, width, height), fill="#007bff",
                         outline="#007bff")
        self.create_rectangle((self.radius, 0, width - self.radius, height), fill="#007bff", outline="#007bff")
        self.create_rectangle((0, self.radius, width, height - self.radius), fill="#007bff", outline="#007bff")
        self.create_text(width / 2, height / 2, text=self.text, fill="white", font=("Helvetica", 12))
        self.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        self.command()


# Create custom rounded buttons
browse_button = RoundedButton(root, text="Upload file", command=open_file, width=150, height=40)
browse_button.place(relx=0.5, rely=0.5, anchor="center")

submit_button = RoundedButton(root, text="Submit", command=read_csv, width=150, height=40)
submit_button.place(relx=0.5, rely=0.6, anchor="center")

root.mainloop()
