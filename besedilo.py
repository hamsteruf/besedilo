import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import sys

current_file = None

def save_to_file(text, filename):
    characters = {}
    for i, char in enumerate(text):
        if char not in characters:
            characters[char] = []
        characters[char].append(i)
    
    with open(f"{filename}.besedilo", "w", encoding="utf-8") as f:
        for char, positions in characters.items():
            if char == '\n':
                char = '\\n'  # Replace newline character with \n
            elif char == ' ':
                char = '\\s'  # Replace space character with \s
            positions_str = ','.join(map(str, positions))
            f.write(f"{char}:{positions_str}\n")

def read_from_file(filename):
    content = {}
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if ':' not in line:
                continue
            char, positions_str = line.split(':', 1)
            if char == '\\n':
                char = '\n'  # Restore newline character
            elif char == '\\s':
                char = ' '   # Restore space character
            positions = list(map(int, positions_str.split(',')))
            content[char] = positions
    
    max_position = max(max(positions) for positions in content.values()) if content else 0
    text = [''] * (max_position + 1)
    for char, positions in content.items():
        for pos in positions:
            text[pos] = char
    
    return ''.join(text)

def open_file(filepath=None):
    global current_file
    if not filepath:
        filepath = filedialog.askopenfilename(filetypes=[("Besedilo Files", "*.besedilo")])
        if not filepath:
            return
    
    try:
        content = read_from_file(filepath)
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, content)
        root.title(f"Besedilo Editor - {os.path.basename(filepath)}")
        current_file = filepath
        global text_modified
        text_modified = False
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open file: {e}")

def save_file():
    global current_file
    if current_file:
        try:
            content = text_area.get(1.0, tk.END).strip()
            save_to_file(content, os.path.splitext(current_file)[0])
            root.title(f"Besedilo Editor - {os.path.basename(current_file)}")
            global text_modified
            text_modified = False
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")
    else:
        save_as_file()

def save_as_file():
    global current_file
    filepath = filedialog.asksaveasfilename(defaultextension=".besedilo", filetypes=[("Besedilo Files", "*.besedilo")])
    if not filepath:
        return
    
    try:
        content = text_area.get(1.0, tk.END).strip()
        save_to_file(content, os.path.splitext(filepath)[0])
        root.title(f"Besedilo Editor - {os.path.basename(filepath)}")
        current_file = filepath
        global text_modified
        text_modified = False
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save file: {e}")

def on_closing():
    if text_modified:
        result = messagebox.askyesnocancel("Opozorilo", "Datoteka ni shranjena. Ali želite shraniti spremembe?")
        if result is True:
            save_file()
            if not text_modified:  # Check if save was successful
                root.destroy()
        elif result is False:
            root.destroy()
    else:
        root.destroy()

def text_modified_event(event):
    global text_modified
    text_modified = True

def toggle_theme():
    global theme
    theme = "dark" if theme == "light" else "light"
    apply_theme()

def apply_theme():
    if theme == "dark":
        root.config(bg="black")
        text_area.config(bg="black", fg="white", insertbackground="white", selectbackground="gray")
    else:
        root.config(bg="white")
        text_area.config(bg="white", fg="black", insertbackground="black", selectbackground="lightgray")

def increase_font_size():
    current_font = text_area.cget("font")
    font_name, font_size = current_font.split()[0], int(current_font.split()[1])
    text_area.config(font=(font_name, font_size + 2))

def decrease_font_size():
    current_font = text_area.cget("font")
    font_name, font_size = current_font.split()[0], int(current_font.split()[1])
    text_area.config(font=(font_name, font_size - 2))

def find_text():
    search_query = simpledialog.askstring("Najdi", "Vnesite iskano besedilo:")
    if search_query:
        start_pos = '1.0'
        text_area.tag_remove('found', '1.0', tk.END)
        count = 0
        while True:
            start_pos = text_area.search(search_query, start_pos, stopindex=tk.END)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(search_query)}c"
            text_area.tag_add('found', start_pos, end_pos)
            start_pos = end_pos
            count += 1
        text_area.tag_config('found', background='yellow', foreground='black')
        messagebox.showinfo("Rezultati iskanja", f"Najdenih zadetkov: {count}")

def check_unsaved_changes():
    if text_modified:
        return messagebox.askyesnocancel("Opozorilo", "Datoteka ni shranjena. Ali želite shraniti spremembe?")
    return None

# Create the main window
root = tk.Tk()
root.title("Besedilo Editor")

# Create the text area
text_area = tk.Text(root, wrap=tk.WORD, undo=True)
text_area.pack(expand=1, fill=tk.BOTH)

# Bind text modification event
text_area.bind('<<Modified>>', text_modified_event)

# Create the menu
menu = tk.Menu(root)
root.config(menu=menu)

# Create the File menu
file_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Datoteka", menu=file_menu)
file_menu.add_command(label="Odpri", command=open_file, accelerator="Ctrl+O")
file_menu.add_command(label="Shrani", command=save_file, accelerator="Ctrl+S")
file_menu.add_command(label="Shrani kot", command=save_as_file, accelerator="Ctrl+Shift+S")
file_menu.add_separator()
file_menu.add_command(label="Izhod", command=on_closing, accelerator="Ctrl+Q")

# Create the Edit menu
edit_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Uredi", menu=edit_menu)
edit_menu.add_command(label="Najdi", command=find_text, accelerator="Ctrl+F")

# Create the View menu
view_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Pogled", menu=view_menu)
view_menu.add_command(label="Povečaj", command=increase_font_size, accelerator="Ctrl++")
view_menu.add_command(label="Pomanjšaj", command=decrease_font_size, accelerator="Ctrl+-")
view_menu.add_command(label="Preklopi temo", command=toggle_theme, accelerator="Ctrl+T")

# Bind shortcuts
root.bind("<Control-o>", lambda event: open_file())
root.bind("<Control-s>", lambda event: save_file())
root.bind("<Control-S>", lambda event: save_as_file())
root.bind("<Control-q>", lambda event: on_closing())
root.bind("<Control-f>", lambda event: find_text())
root.bind("<Control-+>", lambda event: increase_font_size())
root.bind("<Control-minus>", lambda event: decrease_font_size())
root.bind("<Control-t>", lambda event: toggle_theme())

# Handle window close event
root.protocol("WM_DELETE_WINDOW", on_closing)

# Initialize theme and text modification flag
theme = "light"
text_modified = False

# Check if a file was passed as an argument
if len(sys.argv) > 1:
    file_to_open = sys.argv[1]
    open_file(file_to_open)

# Apply initial theme
apply_theme()

# Run the application
root.mainloop()
