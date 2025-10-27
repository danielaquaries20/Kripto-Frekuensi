import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import string, collections, random, json
import matplotlib.pyplot as plt

# =========================
# Konfigurasi & data bahasa
# =========================

ENGLISH_FREQ_ORDER = "ETAOINSHRDLUCMFYWGPBVKXQJZ"

COMMON_BIGRAMS_EN = [
    "TH",
    "HE",
    "IN",
    "ER",
    "AN",
    "RE",
    "ON",
    "AT",
    "EN",
    "ND",
    "TI",
    "ES",
    "OR",
    "TE",
    "OF",
    "ED",
    "IS",
    "IT",
    "AL",
    "AR",
]
COMMON_TRIGRAMS_EN = [
    "THE",
    "AND",
    "ING",
    "HER",
    "ERE",
    "ENT",
    "THA",
    "NTH",
    "WAS",
    "ETH",
]
COMMON_WORDS_EN = [
    "THE",
    "AND",
    "OF",
    "TO",
    "IN",
    "IS",
    "IT",
    "YOU",
    "THAT",
    "FOR",
    "ON",
    "WITH",
    "AS",
    "I",
    "THIS",
]

# Versi sederhana untuk bahasa Indonesia (opsional, dapat ditambah)
COMMON_BIGRAMS_ID = [
    "AN",
    "NG",
    "ER",
    "DA",
    "KA",
    "YA",
    "LA",
    "TU",
    "DI",
    "KE",
    "SA",
    "TA",
]
COMMON_TRIGRAMS_ID = ["DAN", "YANG", "ING", "KAN", "NGA", "ANG", "BER", "TER"]
COMMON_WORDS_ID = [
    "DAN",
    "YANG",
    "ADA",
    "INI",
    "UNTUK",
    "KEPADA",
    "DALAM",
    "ITU",
    "DARI",
    "KITA",
    "ANDA",
]

# =========================
# Utilitas analisis & skor
# =========================


def normalize_text(text):
    return "".join(ch for ch in text.upper() if ch in string.ascii_uppercase)


def frequency_analysis(text):
    norm = normalize_text(text)
    total = len(norm)
    counter = collections.Counter(norm)
    return counter, total


def proportions(counter, total):
    return {
        k: (counter.get(k, 0) / total * 100 if total > 0 else 0.0)
        for k in string.ascii_uppercase
    }


def suggest_mapping(counter):
    cipher_order = [l for l, _ in sorted(counter.items(), key=lambda x: (-x[1], x[0]))]
    suggestion = {}
    for i, c in enumerate(cipher_order):
        if i < len(ENGLISH_FREQ_ORDER):
            suggestion[c] = ENGLISH_FREQ_ORDER[i]
    return suggestion


def apply_mapping(text, mapping, unknown_char="·"):
    out = []
    for ch in text:
        up = ch.upper()
        if up in string.ascii_uppercase:
            mapped = mapping.get(up)
            if mapped:
                out.append(mapped if ch.isupper() else mapped.lower())
            else:
                out.append(unknown_char)
        else:
            out.append(ch)
    return "".join(out)


def ngram_analysis(text, n=2, top_k=10):
    norm = normalize_text(text)
    ngrams = [norm[i : i + n] for i in range(len(norm) - n + 1)]
    counter = collections.Counter(ngrams)
    return counter.most_common(top_k)


def score_text_rich(text, lang="EN"):
    """Skor bahasa kaya: bigram + trigram + kata umum (berbobot)."""
    text = text.upper()
    if lang.upper() == "ID":
        bigrams, trigrams, words = (
            COMMON_BIGRAMS_ID,
            COMMON_TRIGRAMS_ID,
            COMMON_WORDS_ID,
        )
    else:
        bigrams, trigrams, words = (
            COMMON_BIGRAMS_EN,
            COMMON_TRIGRAMS_EN,
            COMMON_WORDS_EN,
        )
    score = 0
    for bg in bigrams:
        score += text.count(bg)  # bobot 1
    for tg in trigrams:
        score += 2 * text.count(tg)  # bobot 2
    for w in words:
        score += 3 * text.count(w)  # bobot 3
    return score


# =========================
# Caesar cipher attack
# =========================


def caesar_decrypt(ciphertext, shift):
    result = []
    for ch in ciphertext:
        if ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            result.append(chr((ord(ch) - base - shift) % 26 + base))
        else:
            result.append(ch)
    return "".join(result)


def caesar_attack(ciphertext, lang="EN"):
    results = {}
    best_shift, best_text, best_score = 0, "", -1
    for shift in range(26):
        candidate = caesar_decrypt(ciphertext, shift)
        s = score_text_rich(candidate, lang=lang)
        results[shift] = candidate
        if s > best_score:
            best_score, best_shift, best_text = s, shift, candidate
    return best_shift, best_text, best_score, results


# =========================
# Random substitution attack
# =========================


def decrypt_with_map_upper(text, mapping):
    """Dekripsi memakai map huruf uppercase (plaintext uppercase)."""
    out = []
    for ch in text.upper():
        if ch in string.ascii_uppercase:
            out.append(mapping.get(ch, ch))
        else:
            out.append(ch)
    return "".join(out)


def random_substitution_attack(
    ciphertext, iterations=8000, lang="EN", initial_mapping=None
):
    """
    Heuristik hill-climbing:
    - Jika initial_mapping diberikan, digunakan sebagai start; sisanya diisi random.
    - Mengembalikan (best_plaintext, best_score, best_mapping).
    """
    letters = list(string.ascii_uppercase)
    # Inisialisasi mapping
    if initial_mapping:
        used = set(initial_mapping.values())
        unused = [l for l in letters if l not in used]
        mapping = dict(initial_mapping)
        for c in letters:
            if c not in mapping:
                mapping[c] = unused.pop() if unused else random.choice(letters)
    else:
        shuffled = letters[:]
        random.shuffle(shuffled)
        mapping = dict(zip(letters, shuffled))

    best_mapping = mapping
    best_plain = decrypt_with_map_upper(ciphertext, best_mapping)
    best_score = score_text_rich(best_plain, lang=lang)

    for _ in range(iterations):
        # Swap dua cipher key untuk perubahan kecil
        a, b = random.sample(letters, 2)
        new_mapping = best_mapping.copy()
        new_mapping[a], new_mapping[b] = new_mapping[b], new_mapping[a]

        new_plain = decrypt_with_map_upper(ciphertext, new_mapping)
        new_score = score_text_rich(new_plain, lang=lang)

        if new_score > best_score:
            best_mapping, best_plain, best_score = new_mapping, new_plain, new_score

    return best_plain, best_score, best_mapping


def auto_tune_attack(ciphertext, hint_mapping, iterations=8000, lang="EN"):
    """
    Auto-tune: mulai dari hint frekuensi sebagai initial mapping,
    lalu lakukan hill-climbing dengan skor bahasa kaya.
    Mengembalikan (best_plaintext, best_score, best_mapping).
    """
    return random_substitution_attack(
        ciphertext, iterations=iterations, lang=lang, initial_mapping=hint_mapping
    )


# =========================
# GUI aplikasi
# =========================


class SubstitutionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Analisis & Attack Substitusi (Auto-Tune)")

        # State utama
        self.ciphertext = ""
        self.mapping = {}  # mapping manual user (persist sepanjang sesi)
        self.hint_mapping = {}  # mapping hasil saran awal (frekuensi)
        self.attack_preview = (
            ""  # plaintext hasil attack (tidak mengubah mapping manual)
        )
        self.attack_mapping = {}  # mapping hasil attack (bisa di-merge)
        self.lang = tk.StringVar(value="EN")  # Bahasa target skor (EN/ID)

        # Layout utama kiri-kanan
        main = tk.PanedWindow(root, sashrelief="raised", sashwidth=6)
        main.pack(fill="both", expand=True)

        left = tk.Frame(main)
        right = tk.Frame(main)
        main.add(left, minsize=420)
        main.add(right, minsize=380)

        # Pengaturan bahasa skor
        lang_frame = tk.Frame(left)
        lang_frame.pack(fill="x")
        tk.Label(lang_frame, text="Bahasa skor:").pack(side="left")
        ttk.Combobox(
            lang_frame, textvariable=self.lang, values=["EN", "ID"], width=5
        ).pack(side="left")

        # Input ciphertext
        tk.Label(left, text="Ciphertext:").pack(anchor="w")
        self.input_text = tk.Text(left, height=8)
        self.input_text.pack(fill="both", expand=True)

        # Toolbar analisis & attack
        btn_frame = tk.Frame(left)
        btn_frame.pack(fill="x", pady=4)
        tk.Button(btn_frame, text="Analisis", command=self.analyze).pack(side="left")
        tk.Button(
            btn_frame, text="Histogram (cipher)", command=self.show_histogram_cipher
        ).pack(side="left")
        tk.Button(btn_frame, text="Hint Lanjutan", command=self.advanced_hint).pack(
            side="left"
        )
        tk.Button(btn_frame, text="Caesar Attack", command=self.run_caesar_attack).pack(
            side="left"
        )
        tk.Button(btn_frame, text="Random Attack", command=self.run_random_attack).pack(
            side="left"
        )
        tk.Button(btn_frame, text="Auto-Tune Attack", command=self.run_auto_tune).pack(
            side="left"
        )

        # Mapping manual + simpan/muat
        map_frame = tk.Frame(left)
        map_frame.pack(fill="x", pady=6)
        tk.Label(map_frame, text="Mapping manual: Cipher → Plain").grid(
            row=0, column=0, columnspan=8, sticky="w"
        )
        tk.Label(map_frame, text="Cipher").grid(row=1, column=0)
        self.cipher_var = tk.StringVar()
        self.cipher_box = ttk.Combobox(
            map_frame,
            textvariable=self.cipher_var,
            values=list(string.ascii_uppercase),
            width=5,
        )
        self.cipher_box.grid(row=1, column=1)
        tk.Label(map_frame, text="→ Plain").grid(row=1, column=2)
        self.plain_var = tk.StringVar()
        self.plain_box = ttk.Combobox(
            map_frame,
            textvariable=self.plain_var,
            values=list(string.ascii_uppercase),
            width=5,
        )
        self.plain_box.grid(row=1, column=3)
        tk.Button(map_frame, text="Map", command=self.update_mapping).grid(
            row=1, column=4
        )
        tk.Button(map_frame, text="Reset mapping", command=self.reset_mapping).grid(
            row=1, column=5
        )

        tk.Button(map_frame, text="Simpan mapping", command=self.save_mapping).grid(
            row=2, column=4, pady=4
        )
        tk.Button(map_frame, text="Muat mapping", command=self.load_mapping).grid(
            row=2, column=5, pady=4
        )

        # Preview manual (hint + mapping manual)
        tk.Label(left, text="Preview dekripsi (mapping manual):").pack(anchor="w")
        self.output_text = tk.Text(left, height=12, bg="#f0f0f0")
        self.output_text.pack(fill="both", expand=True)

        # Panel kanan: hasil attack & analisisnya
        tk.Label(right, text="Hasil attack (tidak mengubah mapping manual):").pack(
            anchor="w"
        )
        self.attack_text = tk.Text(right, height=12, bg="#fff8e1")
        self.attack_text.pack(fill="both", expand=True)

        ana_frame = tk.Frame(right)
        ana_frame.pack(fill="x", pady=4)
        tk.Button(
            ana_frame,
            text="Analisis frekuensi hasil attack",
            command=self.analyze_attack_preview,
        ).pack(side="left")
        tk.Button(
            ana_frame,
            text="Histogram (attack plaintext)",
            command=self.show_histogram_attack,
        ).pack(side="left")
        tk.Button(
            ana_frame,
            text="Terapkan attack ke preview manual",
            command=self.apply_attack_to_preview,
        ).pack(side="left")
        tk.Button(
            ana_frame,
            text="Gabungkan mapping attack → manual",
            command=self.merge_attack_mapping,
        ).pack(side="left")

        # Status
        self.status = tk.StringVar(value="Status: siap")
        tk.Label(root, textvariable=self.status, anchor="w").pack(fill="x")

    # ====== Utilitas UI ======
    def set_status(self, text):
        self.status.set(f"Status: {text}")

    def update_preview_manual(self):
        # Kombinasi: hint_mapping sebagai baseline, di-override oleh mapping manual user
        mapping_effective = dict(self.hint_mapping)
        mapping_effective.update(self.mapping)
        decrypted = apply_mapping(self.ciphertext, mapping_effective)
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", decrypted)

    # ====== Analisis & hint ======
    def analyze(self):
        self.ciphertext = self.input_text.get("1.0", "end").strip()
        if not self.ciphertext:
            messagebox.showwarning("Peringatan", "Masukkan ciphertext terlebih dahulu.")
            return
        counter, total = frequency_analysis(self.ciphertext)
        self.hint_mapping = suggest_mapping(counter)
        self.update_preview_manual()
        self.set_status(
            f"Analisis selesai. Total huruf: {total}. Hint awal diterapkan (bisa dioverride manual)."
        )

    def show_histogram_cipher(self):
        if not self.ciphertext:
            messagebox.showwarning(
                "Peringatan", "Analisis dulu sebelum menampilkan histogram."
            )
            return
        counter, _ = frequency_analysis(self.ciphertext)
        letters = list(string.ascii_uppercase)
        values = [counter.get(l, 0) for l in letters]
        plt.figure(figsize=(12, 5))
        plt.bar(letters, values, color="#4C78A8")
        plt.title("Histogram Frekuensi Huruf (Ciphertext)")
        plt.xlabel("Huruf")
        plt.ylabel("Jumlah")
        plt.show()

    def advanced_hint(self):
        if not self.ciphertext:
            messagebox.showwarning(
                "Peringatan", "Analisis dulu sebelum menggunakan hint lanjutan."
            )
            return

        # Pilih dataset sesuai bahasa
        if self.lang.get().upper() == "ID":
            bigram_list = COMMON_BIGRAMS_ID
            trigram_list = COMMON_TRIGRAMS_ID
        else:
            bigram_list = COMMON_BIGRAMS_EN
            trigram_list = COMMON_TRIGRAMS_EN

        # Hitung frekuensi n-gram dari ciphertext
        bigrams = ngram_analysis(self.ciphertext, n=2, top_k=10)
        trigrams = ngram_analysis(self.ciphertext, n=3, top_k=10)

        msg = "=== Bigram Ciphertext Teratas ===\n"
        for bg, count in bigrams:
            msg += f"{bg} : {count}\n"

        msg += "\n=== Trigram Ciphertext Teratas ===\n"
        for tg, count in trigrams:
            msg += f"{tg} : {count}\n"

        # Tambahkan saran berdasarkan bahasa
        hint_lines = []
        if trigram_list:
            hint_lines.append(
                f"Trigram umum bahasa {self.lang.get()}: {', '.join(trigram_list[:5])}"
            )
        if bigram_list:
            hint_lines.append(
                f"Bigram umum bahasa {self.lang.get()}: {', '.join(bigram_list[:5])}"
            )

        if hint_lines:
            msg += "\nSaran:\n- " + "\n- ".join(hint_lines)

        messagebox.showinfo("Hint Lanjutan", msg)

    # ====== Mapping manual ======
    def update_mapping(self):
        c = self.cipher_var.get().upper()
        p = self.plain_var.get().upper()
        if c in string.ascii_uppercase and p in string.ascii_uppercase:
            self.mapping[c] = p
            self.update_preview_manual()
            self.set_status(f"Mapping diperbarui: {c} -> {p}")
        else:
            messagebox.showerror("Error", "Pilih huruf A–Z untuk mapping.")

    def reset_mapping(self):
        self.mapping = {}
        self.update_preview_manual()
        self.set_status("Mapping manual dikosongkan (hint awal tetap ada).")

    def save_mapping(self):
        if not self.mapping:
            messagebox.showinfo("Info", "Mapping manual kosong.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON", "*.json")]
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.mapping, f, ensure_ascii=False, indent=2)
        self.set_status(f"Mapping disimpan ke {path}")

    def load_mapping(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Validasi sederhana
            for k, v in data.items():
                if k not in string.ascii_uppercase or v not in string.ascii_uppercase:
                    raise ValueError("Format mapping tidak valid.")
            self.mapping = data
            self.update_preview_manual()
            self.set_status(f"Mapping dimuat dari {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat mapping: {e}")

    # ====== Attack (hasil & mapping terpisah) ======
    def run_caesar_attack(self):
        self.ciphertext = self.input_text.get("1.0", "end").strip()
        if not self.ciphertext:
            messagebox.showwarning("Peringatan", "Masukkan ciphertext terlebih dahulu.")
            return
        best_shift, best_text, best_score, _ = caesar_attack(
            self.ciphertext, lang=self.lang.get()
        )
        self.attack_preview = best_text
        self.attack_mapping = {}  # Caesar tidak menggunakan mapping A-Z penuh
        self.attack_text.delete("1.0", "end")
        self.attack_text.insert(
            "1.0",
            f"[Caesar shift {best_shift}, skor {best_score}]\n\n{self.attack_preview}",
        )
        self.set_status(
            f"Caesar attack selesai. Shift terbaik: {best_shift} (skor {best_score})."
        )

    def run_random_attack(self):
        self.ciphertext = self.input_text.get("1.0", "end").strip()
        if not self.ciphertext:
            messagebox.showwarning("Peringatan", "Masukkan ciphertext terlebih dahulu.")
            return
        try:
            iterations = simpledialog.askinteger(
                "Random Attack",
                "Jumlah iterasi (disarankan 8000–20000):",
                initialvalue=12000,
                minvalue=1000,
                maxvalue=200000,
            )
            if iterations is None:
                return
        except Exception:
            iterations = 12000
        best_plain, best_score, best_mapping = random_substitution_attack(
            self.ciphertext, iterations=iterations, lang=self.lang.get()
        )
        self.attack_preview = best_plain
        self.attack_mapping = best_mapping
        self.attack_text.delete("1.0", "end")
        self.attack_text.insert(
            "1.0",
            f"[Random substitution, skor {best_score}, iterasi {iterations}]\n\n{self.attack_preview}",
        )
        self.set_status(
            f"Random attack selesai. Skor {best_score}. Mapping tersedia untuk merge."
        )

    def run_auto_tune(self):
        self.ciphertext = self.input_text.get("1.0", "end").strip()
        if not self.ciphertext:
            messagebox.showwarning("Peringatan", "Masukkan ciphertext terlebih dahulu.")
            return
        if not self.hint_mapping:
            messagebox.showinfo(
                "Info", "Belum ada hint mapping. Jalankan 'Analisis' terlebih dahulu."
            )
            return
        try:
            iterations = simpledialog.askinteger(
                "Auto-Tune Attack",
                "Jumlah iterasi (disarankan 8000–20000):",
                initialvalue=15000,
                minvalue=1000,
                maxvalue=300000,
            )
            if iterations is None:
                return
        except Exception:
            iterations = 15000
        best_plain, best_score, best_mapping = auto_tune_attack(
            self.ciphertext,
            self.hint_mapping,
            iterations=iterations,
            lang=self.lang.get(),
        )
        self.attack_preview = best_plain
        self.attack_mapping = best_mapping
        self.attack_text.delete("1.0", "end")
        self.attack_text.insert(
            "1.0",
            f"[Auto-Tune, skor {best_score}, iterasi {iterations}]\n\n{self.attack_preview}",
        )
        self.set_status("Auto-Tune selesai. Mapping siap pakai dan bisa di-merge.")

    # ====== Analisis hasil attack ======
    def analyze_attack_preview(self):
        if not self.attack_preview:
            messagebox.showinfo("Info", "Belum ada hasil attack untuk dianalisis.")
            return
        # Cipher stats
        c_counter, c_total = frequency_analysis(self.ciphertext)
        c_prop = proportions(c_counter, c_total)
        # Attack plaintext stats
        a_counter, a_total = frequency_analysis(self.attack_preview)
        a_prop = proportions(a_counter, a_total)

        def top_list(counter, prop, top=10):
            items = sorted(counter.items(), key=lambda x: (-x[1], x[0]))[:top]
            lines = [f"{l}: {counter[l]} ({prop[l]:.2f}%)" for l, _ in items]
            return "\n".join(lines)

        msg = "=== Perbandingan Frekuensi ===\n"
        msg += f"\nCiphertext (total {c_total}):\n{top_list(c_counter, c_prop)}\n"
        msg += f"\nAttack plaintext (total {a_total}):\n{top_list(a_counter, a_prop)}\n"
        messagebox.showinfo("Analisis Attack", msg)

    def show_histogram_attack(self):
        if not self.attack_preview:
            messagebox.showinfo(
                "Info", "Belum ada hasil attack untuk ditampilkan histogramnya."
            )
            return
        counter, _ = frequency_analysis(self.attack_preview)
        letters = list(string.ascii_uppercase)
        values = [counter.get(l, 0) for l in letters]
        plt.figure(figsize=(12, 5))
        plt.bar(letters, values, color="#F28E2B")
        plt.title("Histogram Frekuensi Huruf (Attack plaintext)")
        plt.xlabel("Huruf")
        plt.ylabel("Jumlah")
        plt.show()

    def apply_attack_to_preview(self):
        if not self.attack_preview:
            messagebox.showinfo("Info", "Belum ada hasil attack untuk diterapkan.")
            return
        # Terapkan hasil attack ke panel preview manual (hanya mengganti teks, tidak mengubah mapping)
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", self.attack_preview)
        self.set_status(
            "Hasil attack diterapkan ke preview manual (mapping manual tetap)."
        )

    def merge_attack_mapping(self):
        if not self.attack_mapping:
            messagebox.showinfo(
                "Info", "Tidak ada mapping dari hasil attack untuk digabungkan."
            )
            return
        # Gabungkan mapping attack → manual (manual dapat dioverride lagi)
        self.mapping.update(self.attack_mapping)
        self.update_preview_manual()
        self.set_status("Mapping attack digabungkan ke mapping manual.")


# =========================
# Main
# =========================

if __name__ == "__main__":
    root = tk.Tk()
    app = SubstitutionGUI(root)
    root.mainloop()
