import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path
from PIL import Image

# gradasi karakter
RAMP = "@%#*+=-:. "

def resize_with_aspect(img: Image.Image, width: int) -> Image.Image:
    w, h = img.size
    aspect = h / w
    new_h = max(1, int(width * aspect * 0.55))
    return img.resize((width, new_h))

def rgb_to_gray(r, g, b):
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def pixel_to_char(gray: float, invert: bool) -> str:
    idx = int(gray / 255 * (len(RAMP) - 1))
    if invert:
        idx = (len(RAMP) - 1) - idx
    return RAMP[idx]

def to_ascii(img: Image.Image, invert=False) -> str:
    pixels = img.load()
    w, h = img.size
    lines = []
    for y in range(h):
        row_chars = []
        for x in range(w):
            r, g, b = pixels[x, y]
            ch = pixel_to_char(rgb_to_gray(r, g, b), invert)
            row_chars.append(ch * 2)
        lines.append("".join(row_chars))
    return "\n".join(lines)

def open_image():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.webp *.gif")]
    )
    if not file_path:
        return

    try:
        img = Image.open(file_path).convert("RGB")
        img = resize_with_aspect(img, width=100)
        ascii_art = to_ascii(img, invert=False)

        # tampilkan di text box
        text_box.delete(1.0, tk.END)
        text_box.insert(tk.END, ascii_art)

        # simpan ke file .txt
        output_file = Path(file_path).with_suffix(".txt")
        output_file.write_text(ascii_art, encoding="utf-8")
        messagebox.showinfo("Sukses", f"ASCII art disimpan ke {output_file}")

    except Exception as e:
        messagebox.showerror("Error", f"Gagal buka gambar: {e}")

# ============================
# 🎨 GUI
# ============================
root = tk.Tk()
root.title("🖼️ Image to ASCII Converter")
root.geometry("800x600")

btn_open = tk.Button(root, text="Pilih Gambar", command=open_image, font=("Arial", 12))
btn_open.pack(pady=10)

text_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", 8))
text_box.pack(expand=True, fill="both", padx=10, pady=10)

root.mainloop()
