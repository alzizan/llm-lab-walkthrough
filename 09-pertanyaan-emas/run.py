"""Lab 09 — 20 pertanyaan emas: evaluasi otomatis sebelum (dan setiap kali) mengganti model atau prompt."""
import os, re, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lab import ask

KB = """[Buku Saku Karyawan PT Contoh Sejahtera 2026 (FIKTIF)]
1. Jam kerja: Senin–Jumat 08.00–17.00, istirahat 12.00–13.00.
2. Cuti tahunan 14 hari; maksimal 5 hari boleh dibawa ke tahun berikutnya, hangus 31 Maret.
3. Cuti melahirkan 3 bulan upah penuh; cuti ayah 5 hari kerja.
4. Cuti sakit lebih dari 2 hari wajib surat dokter.
5. Lembur hari kerja: jam pertama 1,5x upah per jam, jam berikutnya 2x. Hari libur: 8 jam pertama 3x, jam ke-9 dst 4x.
6. Pengajuan lembur lewat aplikasi HR paling lambat H-1.
7. Rawat jalan maksimal Rp 5.000.000/tahun; rawat inap kamar kelas 1 maksimal Rp 40.000.000/tahun.
8. Kacamata maksimal Rp 750.000 per 2 tahun dengan resep dokter mata.
9. Uang makan Rp 35.000 per hari hadir; uang transport Rp 25.000 per hari hadir.
10. Perjalanan dinas: uang harian Rp 400.000 (Jawa) dan Rp 500.000 (luar Jawa); hotel maksimal Rp 900.000/malam.
11. Laptop kantor diganti tiap 4 tahun; kehilangan wajib lapor ke IT maksimal 1x24 jam.
12. Password minimal 12 karakter, diganti tiap 90 hari; dilarang dibagikan, termasuk ke tim IT.
13. Kerja dari rumah maksimal 2 hari per minggu dengan persetujuan atasan.
14. Gaji dibayar tanggal 25; jika jatuh di hari libur, dibayar hari kerja sebelumnya."""
# (pertanyaan, kunci). Kunci = regex yang wajib muncul; awalan "!" = teks yang TIDAK boleh muncul.
# ABST = pertanyaan yang jawabannya tidak ada di buku saku (harus dijawab "tidak ada").
ABST = "tidak ada"
GOLD = [("Jam berapa istirahat siang?", ["12.00", "13.00"]), ("Berapa hari cuti tahunan?", ["14"]),
 ("Berapa hari cuti yang bisa dibawa ke tahun depan?", ["5"]), ("Kapan sisa cuti yang dibawa hangus?", ["31 Maret"]),
 ("Berapa lama cuti melahirkan?", ["3 bulan"]), ("Cuti ayah berapa hari?", ["5"]),
 ("Sakit 3 hari, perlu surat dokter?", ["ya|wajib|perlu"]), ("Tarif lembur jam ke-10 di hari libur?", ["4"]),
 ("Kapan paling lambat mengajukan lembur?", ["H-1|sehari sebelum|1 hari sebelum"]), ("Batas rawat inap per tahun?", ["40.000.000|40 juta"]),
 ("Batas penggantian kacamata?", ["750.000|750 ribu"]), ("Uang makan per hari berapa?", ["35.000|35 ribu"]),
 ("Uang harian dinas ke Makassar berapa?", ["500.000|500 ribu"]), ("Maksimal biaya hotel dinas per malam?", ["900.000|900 ribu"]),
 ("Laptop kehilangan, kapan harus lapor?", ["24 jam"]), ("Tim IT minta password saya lewat telepon, boleh saya berikan?", ["tidak boleh|dilarang|jangan", "!tidak ada di buku saku"]),
 ("Berapa hari maksimal WFH per minggu?", ["2"]), ("Gaji dibayar tanggal berapa?", ["25"]),
 ("Berapa bonus tahunan karyawan?", [ABST]), ("Apakah kantor menyediakan asuransi jiwa?", [ABST])]


def correct(answer, keys):
    a = answer.lower()
    if keys == [ABST]:
        return any(k in a for k in ["tidak ada", "tidak tercantum", "tidak disebutkan", "tidak tertulis"])
    return all((k[1:].lower() not in a) if k.startswith("!") else bool(re.search(k.lower(), a)) for k in keys)


P1 = ("Kamu asisten HR. Jawab HANYA dari buku saku berikut, singkat, Bahasa Indonesia. Jika tidak ada di buku saku, "
      "jawab: \"Tidak ada di buku saku, silakan hubungi HR.\"\n\n" + KB)
P2 = "Kamu asisten HR yang ramah dan membantu. Bantu karyawan sebaik mungkin, gunakan buku saku berikut sebagai referensi.\n\n" + KB
CONFIGS = [
    ("A: qwen3:4b-instruct + prompt v1", "qwen3:4b-instruct-2507-q4_K_M", P1),
    ("B: qwen3:4b-instruct + prompt v2 'ramah'", "qwen3:4b-instruct-2507-q4_K_M", P2),
    ("C: qwen3.5:2b + prompt v1", "qwen3.5:2b", P1),
    ("D: qwen3:1.7b + prompt v1", "qwen3:1.7b", P1),
]
only = os.environ.get("ONLY")  # mis. ONLY=A,C
for name, model, system in CONFIGS:
    if only and name[0] not in only.split(","):
        continue
    t0, fails = time.time(), []
    for q, keys in GOLD:
        answer, _ = ask(model, system, q)
        if not correct(answer, keys):
            fails.append((q, answer))
    print(f"\n=== {name}: {len(GOLD) - len(fails)}/{len(GOLD)} benar ({time.time() - t0:.0f} s)")
    for q, a in fails:
        print(f"  GAGAL: {q}\n         → {a.replace(chr(10), ' ')[:160]}")
