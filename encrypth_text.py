import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter


# --- Fungsi substitusi sederhana ---
def generate_key():
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    key = "QWERTYUIOPASDFGHJKLZXCVBNM"  # contoh key
    return dict(zip(alphabet, key))


def encrypt(plain_text, key_map):
    plain_text = plain_text.upper()
    return "".join([key_map.get(c, c) for c in plain_text])


# --- Plot gabungan (single plot) ---
def plot_single(plain_text, cipher_text):
    alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    plain_counter = Counter([c for c in plain_text.upper() if c in alphabet])
    cipher_counter = Counter([c for c in cipher_text.upper() if c in alphabet])

    plain_sorted = sorted(plain_counter.items(), key=lambda x: x[1], reverse=True)
    cipher_mapped = [
        (cipher_counter.get(generate_key()[ch], 0), generate_key()[ch])
        for ch, _ in plain_sorted
    ]

    plain_letters = [ch for ch, _ in plain_sorted]
    plain_freq = [freq for _, freq in plain_sorted]
    cipher_freq = [freq for freq, _ in cipher_mapped]
    cipher_letters = [c for _, c in cipher_mapped]

    x = np.arange(len(plain_letters))
    width = 0.4

    plt.figure(figsize=(12, 6))
    plt.bar(
        x - width / 2,
        plain_freq,
        width,
        label="Plain Text (" + "".join(plain_letters) + ")",
        color="skyblue",
    )
    plt.bar(
        x + width / 2,
        cipher_freq,
        width,
        label="Cipher Text (" + "".join(cipher_letters) + ")",
        color="orange",
    )

    plt.xticks(x, plain_letters)
    plt.xlabel("Huruf Plaintext (Cipher di legenda)")
    plt.ylabel("Frekuensi")
    plt.title("Perbandingan Frekuensi (Sorted by Plaintext Frequency)")
    plt.legend()
    plt.show()


# --- Plot terpisah (dual plot) ---
def plot_dual(plain_text, cipher_text):
    alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    plain_counter = Counter([c for c in plain_text.upper() if c in alphabet])
    cipher_counter = Counter([c for c in cipher_text.upper() if c in alphabet])

    # Plaintext
    plt.figure(figsize=(12, 5))
    p_sorted = sorted(plain_counter.items(), key=lambda x: x[1], reverse=True)
    plt.bar([ch for ch, _ in p_sorted], [freq for _, freq in p_sorted], color="blue")
    plt.title("Frekuensi Huruf Plaintext (Descending)")
    plt.xlabel("Huruf")
    plt.ylabel("Frekuensi")

    # Ciphertext
    plt.figure(figsize=(12, 5))
    c_sorted = sorted(cipher_counter.items(), key=lambda x: x[1], reverse=True)
    plt.bar([ch for ch, _ in c_sorted], [freq for _, freq in c_sorted], color="gold")
    plt.title("Frekuensi Huruf Ciphertext (Descending)")
    plt.xlabel("Huruf")
    plt.ylabel("Frekuensi")

    plt.show()


# --- Fungsi tombol ---
def run_single():
    text = entry.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Input Kosong", "Masukkan teks terlebih dahulu!")
        return
    key_map = generate_key()
    cipher = encrypt(text, key_map)

    result_text.config(state="normal")
    result_text.delete("1.0", tk.END)
    result_text.insert("1.0", cipher)
    result_text.config(state="disabled")

    plot_single(text, cipher)


def run_dual():
    text = entry.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Input Kosong", "Masukkan teks terlebih dahulu!")
        return
    key_map = generate_key()
    cipher = encrypt(text, key_map)

    result_text.config(state="normal")
    result_text.delete("1.0", tk.END)
    result_text.insert("1.0", cipher)
    result_text.config(state="disabled")

    plot_dual(text, cipher)


def copy_cipher():
    cipher = result_text.get("1.0", tk.END).strip()
    if cipher:
        root.clipboard_clear()
        root.clipboard_append(cipher)
        root.update()  # supaya clipboard langsung terisi
        messagebox.showinfo("Disalin", "Ciphertext berhasil disalin ke clipboard!")
    else:
        messagebox.showwarning("Kosong", "Tidak ada ciphertext untuk disalin.")


# --- Main Window ---
root = tk.Tk()
root.title("🔒 Substitution Cipher")
root.geometry("700x550")
root.configure(bg="#f5f7fa")

frame = tk.Frame(root, padx=10, pady=10, bg="#f5f7fa")
frame.pack(fill="both", expand=True)

label = tk.Label(
    frame, text="Masukkan Plain Text:", font=("Segoe UI", 11, "bold"), bg="#f5f7fa"
)
label.pack(anchor="w")

# --- Input multi-line ---
entry = tk.Text(frame, width=80, height=6, font=("Consolas", 12), wrap="word")
entry.pack(pady=5)

# --- Tombol dengan warna ---
button_frame = tk.Frame(frame, bg="#f5f7fa")
button_frame.pack(pady=10)

button_single = tk.Button(
    button_frame,
    text="🔒 Encrypt & Single Plot",
    command=run_single,
    bg="#4CAF50",
    fg="white",
    font=("Segoe UI", 10, "bold"),
    padx=10,
    pady=5,
)
button_single.grid(row=0, column=0, padx=10)

button_dual = tk.Button(
    button_frame,
    text="📊 Encrypt & Dual Plot",
    command=run_dual,
    bg="#2196F3",
    fg="white",
    font=("Segoe UI", 10, "bold"),
    padx=10,
    pady=5,
)
button_dual.grid(row=0, column=1, padx=10)

button_copy = tk.Button(
    button_frame,
    text="📋 Copy Ciphertext",
    command=copy_cipher,
    bg="#FF9800",
    fg="white",
    font=("Segoe UI", 10, "bold"),
    padx=10,
    pady=5,
)
button_copy.grid(row=0, column=2, padx=10)

# --- Output multi-line ---
label_result = tk.Label(
    frame, text="Ciphertext:", font=("Segoe UI", 11, "bold"), bg="#f5f7fa"
)
label_result.pack(anchor="w", pady=(15, 0))

result_text = tk.Text(
    frame,
    width=80,
    height=6,
    font=("Consolas", 12),
    fg="blue",
    wrap="word",
    state="disabled",
)
result_text.pack(pady=5)

# --- Status Bar ---
status = tk.Label(root, text="Ready", bd=1, relief="sunken", anchor="w", bg="#e9ecef")
status.pack(side="bottom", fill="x")

root.mainloop()
