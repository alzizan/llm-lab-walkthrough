"""Lab 12 — penyaring data pribadi sebelum prompt dikirim ke layanan AI eksternal.

Lapis 1: regex (NIK, HP, email, NPWP). Lapis 2: model LOKAL mendaftar data pribadi yang tersisa.
Penyaring lapis 2 harus lokal: kalau memakai AI eksternal, datanya sudah keluar sebelum disaring.
"""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lab import ask

MODEL = os.environ.get("MODEL", "qwen3:4b-instruct-2507-q4_K_M")
PROMPT = os.environ.get("PROMPT") or (
    "Tolong buatkan surat penagihan yang sopan untuk nasabah ini (FIKTIF): Ibu Ratna Kusumawardani, NIK 3275014507880012, "
    "HP 0812-3456-7890, email ratna.kw@contohmail.id, alamat Jl. Melati Raya No. 17, Bekasi Utara. "
    "Tunggakan kartu kredit Rp 12.450.000, sudah 62 hari. Dia sedang dirawat karena kanker payudara, jadi minta keringanan.")
RULES = {
    "NIK": r"\b\d{16}\b",
    "HP": r"(?:\+62|0)8\d{1,3}[-\s]?\d{3,4}[-\s]?\d{3,5}",
    "EMAIL": r"[\w.+-]+@[\w-]+\.[\w.-]+",
    "NPWP": r"\b\d{2}\.\d{3}\.\d{3}\.\d-\d{3}\.\d{3}\b",
}
DETECTOR = ("Kamu pendeteksi data pribadi (UU PDP). Dari teks berikut, daftar SEMUA data pribadi yang tersisa, satu per baris "
            "dengan format 'jenis: nilai'. Tandai data pribadi yang bersifat spesifik (kesehatan, keuangan, dll.) dengan [SPESIFIK]. Hanya daftar.")

masked = PROMPT
print("== Lapis 1 — regex")
for kind, rx in RULES.items():
    for value in re.findall(rx, masked):
        print(f"  tertangkap {kind}: {value}")
    masked = re.sub(rx, f"[{kind}]", masked)
print("  hasil: " + masked)

print(f"\n== Lapis 2 — {MODEL} (lokal) mendaftar data pribadi yang tersisa")
found, _ = ask(MODEL, DETECTOR, masked)
print("  " + found.strip().replace("\n", "\n  "))

print("\nPeriksa manual: adakah yang lolos? (di uji kami: nama nasabah lolos dari kedua lapis)")
