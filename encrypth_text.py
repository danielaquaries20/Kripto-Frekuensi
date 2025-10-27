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
    cipher_text = ""
    for char in plain_text:
        if char in key_map:
            cipher_text += key_map[char]
        else:
            cipher_text += char
    return cipher_text


# --- Plot gabungan (single plot) ---


def plot_single(plain_text, cipher_text):
    alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    plain_counter = Counter([c for c in plain_text.upper() if c in alphabet])
    cipher_counter = Counter([c for c in cipher_text.upper() if c in alphabet])

    # Urutkan berdasarkan frekuensi plaintext
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
    )
    plt.bar(
        x + width / 2,
        cipher_freq,
        width,
        label="Cipher Text (" + "".join(cipher_letters) + ")",
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


# --- GUI dengan Tkinter ---


def run_single():
    text = entry.get()
    if not text:
        messagebox.showwarning("Input Kosong", "Masukkan teks terlebih dahulu!")
        return
    key_map = generate_key()
    cipher = encrypt(text, key_map)

    # Baris yang dihapus/dimodifikasi:
    # result_var.set(cipher) <-- HAPUS INI

    # Atur hasil ke widget Entry (result_entry)
    result_entry.config(state="normal")  # Buka mode normal untuk penulisan
    result_entry.delete(0, tk.END)  # Hapus teks lama
    result_entry.insert(0, cipher)  # Masukkan teks baru
    result_entry.config(state="readonly")  # Kembalikan ke mode readonly

    plot_single(text, cipher)


def run_dual():
    text = entry.get()
    if not text:
        messagebox.showwarning("Input Kosong", "Masukkan teks terlebih dahulu!")
        return
    key_map = generate_key()
    cipher = encrypt(text, key_map)

    # Baris yang dihapus/dimodifikasi:
    # result_var.set(cipher) <-- HAPUS INI

    # Atur hasil ke widget Entry (result_entry)
    result_entry.config(state="normal")  # Buka mode normal untuk penulisan
    result_entry.delete(0, tk.END)  # Hapus teks lama
    result_entry.insert(0, cipher)  # Masukkan teks baru
    result_entry.config(state="readonly")  # Kembalikan ke mode readonly

    plot_dual(text, cipher)


# --- Main Window ---
root = tk.Tk()
root.title("Substitution Cipher dengan Visualisasi")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

label = tk.Label(frame, text="Masukkan Plain Text:")
label.pack()

entry = tk.Entry(frame, width=50)
entry.pack()

button_single = tk.Button(
    frame, text="Encrypt & Tampilkan Single Plot", command=run_single
)
button_single.pack(pady=5)

button_dual = tk.Button(frame, text="Encrypt & Tampilkan Dual Plot", command=run_dual)
button_dual.pack(pady=5)

label_result = tk.Label(frame, text="Ciphertext:")
label_result.pack()

result_entry = tk.Entry(frame, width=50, fg="blue", state="readonly", justify="center")
result_entry.pack()

# result_var = tk.StringVar()
# result_label = tk.Label(frame, textvariable=result_var,
#                         fg="blue", wraplength=400)
# result_label.pack()

root.mainloop()
