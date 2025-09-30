import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from pathlib import Path
from PIL import Image, ImageEnhance
import numpy as np

# Berbagai set karakter ASCII dengan kualitas berbeda
ASCII_SETS = {
    "Standard": "@%#*+=-:. ",
    "Dense": "█▉▊▋▌▍▎▏ ",
    "Detailed": "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
    "Simple": "█▓▒░ ",
    "Classic": "@&#*+=:-. "
}

def resize_with_aspect(img: Image.Image, width: int) -> Image.Image:
    w, h = img.size
    aspect = h / w
    # Improved aspect ratio calculation for better proportions
    new_h = max(1, int(width * aspect * 0.45))  # Adjusted ratio for better results
    return img.resize((width, new_h), Image.Resampling.LANCZOS)

def rgb_to_gray(r, g, b):
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def enhance_image(img: Image.Image, contrast: float = 1.0, brightness: float = 1.0) -> Image.Image:
    """Enhance image contrast and brightness for better ASCII conversion"""
    if contrast != 1.0:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast)
    if brightness != 1.0:
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(brightness)
    return img

def pixel_to_char(gray: float, invert: bool, char_set: str) -> str:
    """Convert pixel brightness to ASCII character with improved mapping"""
    # Use gamma correction for better visual perception
    normalized = (gray / 255.0) ** 0.8
    idx = int(normalized * (len(char_set) - 1))
    idx = max(0, min(len(char_set) - 1, idx))  # Clamp to valid range
    
    if invert:
        idx = (len(char_set) - 1) - idx
    return char_set[idx]

def to_ascii(img: Image.Image, char_set: str = "@%#*+=-:. ", invert: bool = False, 
             contrast: float = 1.0, brightness: float = 1.0, double_width: bool = True) -> str:
    """Convert image to ASCII with enhanced quality options"""
    # Apply image enhancements
    img = enhance_image(img, contrast, brightness)
    
    # Convert to numpy array for faster processing
    img_array = np.array(img)
    h, w = img_array.shape[:2]
    
    lines = []
    for y in range(h):
        row_chars = []
        for x in range(w):
            if len(img_array.shape) == 3:  # RGB image
                r, g, b = img_array[y, x]
                gray = rgb_to_gray(r, g, b)
            else:  # Grayscale image
                gray = img_array[y, x]
            
            ch = pixel_to_char(gray, invert, char_set)
            # Option to double character width for better aspect ratio
            row_chars.append(ch * 2 if double_width else ch)
        lines.append("".join(row_chars))
    return "\n".join(lines)

def generate_ascii():
    """Generate ASCII art with current settings"""
    if not hasattr(generate_ascii, 'current_image'):
        messagebox.showwarning("Peringatan", "Pilih gambar terlebih dahulu!")
        return
    
    try:
        img = generate_ascii.current_image.copy()
        
        # Get current settings
        width = int(width_var.get())
        char_set = ASCII_SETS[charset_var.get()]
        invert = invert_var.get()
        contrast = contrast_var.get()
        brightness = brightness_var.get()
        double_width = double_width_var.get()
        
        # Resize and convert
        img = resize_with_aspect(img, width=width)
        ascii_art = to_ascii(img, char_set=char_set, invert=invert, 
                           contrast=contrast, brightness=brightness, 
                           double_width=double_width)
        
        # Display in text box
        text_box.delete(1.0, tk.END)
        text_box.insert(tk.END, ascii_art)
        
        # Update status
        status_label.config(text=f"ASCII Generated: {img.size[0]}x{img.size[1]} → {len(ascii_art.split()[0]) if ascii_art else 0}x{len(ascii_art.split())}")
        
    except Exception as e:
        messagebox.showerror("Error", f"Gagal generate ASCII: {e}")

def open_image():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.webp *.gif")]
    )
    if not file_path:
        return

    try:
        img = Image.open(file_path).convert("RGB")
        generate_ascii.current_image = img
        generate_ascii.current_path = file_path
        
        # Auto-generate with default settings
        generate_ascii()
        
        # Update file label
        file_label.config(text=f"File: {Path(file_path).name}")

    except Exception as e:
        messagebox.showerror("Error", f"Gagal buka gambar: {e}")

def save_ascii():
    """Save current ASCII art to file"""
    if not text_box.get(1.0, tk.END).strip():
        messagebox.showwarning("Peringatan", "Tidak ada ASCII art untuk disimpan!")
        return
    
    try:
        if hasattr(generate_ascii, 'current_path'):
            default_name = Path(generate_ascii.current_path).stem + "_ascii.txt"
        else:
            default_name = "ascii_art.txt"
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialvalue=default_name,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            ascii_content = text_box.get(1.0, tk.END)
            Path(file_path).write_text(ascii_content, encoding="utf-8")
            messagebox.showinfo("Sukses", f"ASCII art disimpan ke {file_path}")
            
    except Exception as e:
        messagebox.showerror("Error", f"Gagal simpan file: {e}")

# ============================
# 🎨 Enhanced GUI
# ============================
root = tk.Tk()
root.title("🖼️ Enhanced Image to ASCII Converter")
root.geometry("1000x700")
root.configure(bg='#f0f0f0')

# Variables for controls
width_var = tk.IntVar(value=100)
charset_var = tk.StringVar(value="Standard")
invert_var = tk.BooleanVar(value=False)
contrast_var = tk.DoubleVar(value=1.0)
brightness_var = tk.DoubleVar(value=1.0)
double_width_var = tk.BooleanVar(value=True)

# Main frame
main_frame = ttk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Control panel frame
control_frame = ttk.LabelFrame(main_frame, text="🎛️ Controls", padding=10)
control_frame.pack(fill="x", pady=(0, 10))

# File controls
file_frame = ttk.Frame(control_frame)
file_frame.pack(fill="x", pady=(0, 10))

ttk.Button(file_frame, text="📁 Pilih Gambar", command=open_image).pack(side="left", padx=(0, 10))
ttk.Button(file_frame, text="🔄 Generate", command=generate_ascii).pack(side="left", padx=(0, 10))
ttk.Button(file_frame, text="💾 Simpan ASCII", command=save_ascii).pack(side="left", padx=(0, 10))

file_label = ttk.Label(file_frame, text="File: Belum dipilih", foreground="gray")
file_label.pack(side="left", padx=(20, 0))

# Settings frame
settings_frame = ttk.Frame(control_frame)
settings_frame.pack(fill="x", pady=(0, 10))

# Width control
ttk.Label(settings_frame, text="Lebar:").grid(row=0, column=0, sticky="w", padx=(0, 5))
width_scale = ttk.Scale(settings_frame, from_=20, to=200, variable=width_var, orient="horizontal", length=150)
width_scale.grid(row=0, column=1, padx=(0, 10))
width_label = ttk.Label(settings_frame, text="100")
width_label.grid(row=0, column=2, padx=(0, 20))

def update_width_label(*args):
    width_label.config(text=str(int(width_var.get())))
width_var.trace('w', update_width_label)

# Character set control
ttk.Label(settings_frame, text="Karakter:").grid(row=0, column=3, sticky="w", padx=(0, 5))
charset_combo = ttk.Combobox(settings_frame, textvariable=charset_var, values=list(ASCII_SETS.keys()), state="readonly", width=12)
charset_combo.grid(row=0, column=4, padx=(0, 20))

# Checkboxes
ttk.Checkbutton(settings_frame, text="Invert", variable=invert_var).grid(row=0, column=5, padx=(0, 10))
ttk.Checkbutton(settings_frame, text="Double Width", variable=double_width_var).grid(row=0, column=6)

# Enhancement controls
enhance_frame = ttk.Frame(control_frame)
enhance_frame.pack(fill="x")

# Contrast control
ttk.Label(enhance_frame, text="Kontras:").grid(row=0, column=0, sticky="w", padx=(0, 5))
contrast_scale = ttk.Scale(enhance_frame, from_=0.5, to=2.0, variable=contrast_var, orient="horizontal", length=120)
contrast_scale.grid(row=0, column=1, padx=(0, 10))
contrast_label = ttk.Label(enhance_frame, text="1.0")
contrast_label.grid(row=0, column=2, padx=(0, 20))

def update_contrast_label(*args):
    contrast_label.config(text=f"{contrast_var.get():.1f}")
contrast_var.trace('w', update_contrast_label)

# Brightness control
ttk.Label(enhance_frame, text="Kecerahan:").grid(row=0, column=3, sticky="w", padx=(0, 5))
brightness_scale = ttk.Scale(enhance_frame, from_=0.5, to=2.0, variable=brightness_var, orient="horizontal", length=120)
brightness_scale.grid(row=0, column=4, padx=(0, 10))
brightness_label = ttk.Label(enhance_frame, text="1.0")
brightness_label.grid(row=0, column=5, padx=(0, 20))

def update_brightness_label(*args):
    brightness_label.config(text=f"{brightness_var.get():.1f}")
brightness_var.trace('w', update_brightness_label)

# Auto-update button
ttk.Button(enhance_frame, text="🔄 Auto Update", command=lambda: generate_ascii() if hasattr(generate_ascii, 'current_image') else None).grid(row=0, column=6, padx=(20, 0))

# Text display area
text_frame = ttk.LabelFrame(main_frame, text="📄 ASCII Output", padding=5)
text_frame.pack(fill="both", expand=True)

text_box = scrolledtext.ScrolledText(text_frame, wrap=tk.NONE, font=("Consolas", 7), bg="black", fg="white")
text_box.pack(fill="both", expand=True)

# Status bar
status_label = ttk.Label(root, text="Ready - Pilih gambar untuk memulai", relief="sunken", anchor="w")
status_label.pack(fill="x", side="bottom")

# Bind scale changes to auto-update
def on_setting_change(*args):
    if hasattr(generate_ascii, 'current_image'):
        root.after(100, generate_ascii)  # Delay to avoid too frequent updates

width_var.trace('w', on_setting_change)
charset_var.trace('w', on_setting_change)
invert_var.trace('w', on_setting_change)
contrast_var.trace('w', on_setting_change)
brightness_var.trace('w', on_setting_change)
double_width_var.trace('w', on_setting_change)

root.mainloop()
