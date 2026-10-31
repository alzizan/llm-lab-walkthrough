"""Lab 17 — kuantisasi 4-bit vs 8-bit: model yang sama, 45 soal berjawaban pasti (memakai ulang soal Lab 04 & Lab 09)."""
import json, os, re, sqlite3, sys, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from lab import chat, ask, OLLAMA

MODELS = os.environ.get("MODELS", "qwen3:4b-instruct-2507-q4_K_M,qwen3:4b-instruct-2507-q8_0,qwen3:1.7b,qwen3:1.7b-q8_0").split(",")

# Ambil daftar soal & penilai dari Lab 04 (10 soal dasar) dan Lab 09 (20 pertanyaan buku saku), tanpa menjalankannya
src4 = open(os.path.join(HERE, "..", "04-ukuran-model", "run.py")).read()
src9 = open(os.path.join(HERE, "..", "09-pertanyaan-emas", "run.py")).read()
g4, g9 = {}, {}
exec("import re, json, sqlite3\nOLLAMA = " + repr(OLLAMA) + "\n" + src4[src4.index("def ps():"):src4.index("DEFAULT =")], g4)
exec("import re\n" + src9[src9.index("KB = "):src9.index("P2 =")], g9)
num = lambda a: re.sub(r"[.\s]", "", a)

# 15 soal hitungan bisnis (jawaban benar di elemen kedua)
MATH = [("Harga barang Rp 240.000 didiskon 15%, lalu dikenai PPN 11% dari harga setelah diskon. Berapa yang dibayar?", "226440"),
 ("Gaji Rp 7.500.000, dipotong BPJS 4% dari gaji dan pajak Rp 187.500. Berapa gaji bersih?", "7012500"),
 ("Lembur 3 jam di hari kerja: jam pertama 1,5x upah per jam, jam berikutnya 2x. Upah per jam Rp 40.000. Berapa total upah lembur?", "220000"),
 ("Mobil menempuh 180 km dalam 2 jam 15 menit. Berapa kecepatan rata-ratanya dalam km/jam?", "80"),
 ("Tabungan Rp 10.000.000 dengan bunga majemuk 6% per tahun selama 2 tahun. Berapa saldo akhir?", "11236000"),
 ("Dari 1.250 nasabah, 18% menunggak. Berapa nasabah yang tidak menunggak?", "1025"),
 ("Penjualan Januari Rp 120 juta, Februari Rp 150 juta. Berapa persen pertumbuhannya?", "25"),
 ("Proyek selesai oleh 6 orang dalam 10 hari. Jika dikerjakan 4 orang dengan kecepatan sama, berapa hari?", "15"),
 ("Rata-rata 4 nilai ujian adalah 78. Berapa nilai ujian ke-5 agar rata-rata menjadi 80?", "88"),
 ("Stok awal 500 unit, terjual 35 unit per hari, dan ada restock 100 unit di akhir hari ke-5 dan hari ke-10. Berapa stok di akhir hari ke-10?", "350"),
 ("Invoice Rp 12.000.000 jatuh tempo hari ke-30, denda 0,1% dari nilai invoice per hari terlambat. Dibayar hari ke-45. Berapa dendanya?", "180000"),
 ("Kurs 1 USD = Rp 16.250. Laptop seharga USD 1.200 dikenai bea masuk 7,5% dari harga dalam rupiah. Berapa total dalam rupiah?", "20962500"),
 ("Shift malam pukul 23.00 sampai 07.00. Karyawan masuk shift malam 4 kali seminggu. Berapa jam kerja per minggu?", "32"),
 ("Diskon bertingkat 20% lalu 10%. Diskon totalnya setara berapa persen?", "28"),
 ("Perbandingan karyawan laki-laki dan perempuan 3:5, total 240 orang. Berapa karyawan perempuan?", "150")]
SUF = " Tulis jawaban akhir (angka saja) di baris terakhir."
def last_num_ok(a, key):
    last = [l for l in a.strip().split("\n") if l.strip()][-1]
    return key in num(last).replace(",", "")

print(f"{'model':34}{'file GB':>8}{'VRAM GB':>8}{'tok/s':>7}{'dasar':>7}{'hitung':>8}{'saku':>6}{'total':>7}")
for m in MODELS:
    chat(m, [{"role": "user", "content": "hai"}], num_predict=1)
    vram = next(x["size_vram"] for x in json.load(urllib.request.urlopen(OLLAMA + "/api/ps"))["models"] if x["name"] == m)
    size = next(x["size"] for x in json.load(urllib.request.urlopen(OLLAMA + "/api/tags"))["models"] if x["name"] == m)
    score, tok, dur = {"dasar": 0, "hitung": 0, "saku": 0}, 0, 0.0
    for name, q, check in g4["TASKS"]:
        d = chat(m, [{"role": "user", "content": q}])
        score["dasar"] += bool(check(d["message"]["content"].split("</think>")[-1].strip()))
        tok += d["eval_count"]; dur += d["eval_duration"] / 1e9
    for q, key in MATH:
        d = chat(m, [{"role": "user", "content": q + SUF}])
        score["hitung"] += last_num_ok(d["message"]["content"].split("</think>")[-1].strip(), key)
        tok += d["eval_count"]; dur += d["eval_duration"] / 1e9
    for q, keys in g9["GOLD"]:
        a, d = ask(m, g9["P1"], q)
        score["saku"] += g9["correct"](a, keys)
        tok += d["eval_count"]; dur += d["eval_duration"] / 1e9
    print(f"{m:34}{size / 1e9:>8.1f}{vram / 1e9:>8.1f}{tok / dur:>7.1f}{score['dasar']:>5}/10{score['hitung']:>5}/15"
          f"{score['saku']:>3}/20{sum(score.values()):>4}/45")
