"""Lab 04 — model 0,6B sampai 4B: akurasi, kecepatan, dan memori GPU pada 10 soal berjawaban pasti."""
import json, os, re, sqlite3, sys, time, urllib.request
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lab import chat, models, OLLAMA

def ps():
    return json.load(urllib.request.urlopen(OLLAMA + "/api/ps"))["models"]
def tags():
    return {m["name"]: m["size"] for m in json.load(urllib.request.urlopen(OLLAMA + "/api/tags"))["models"]}
def sql_ok(a):
    m = re.search(r"(SELECT[\s\S]*?)(;|```|$)", a, re.I)
    if not m: return False
    db = sqlite3.connect(":memory:"); db.execute("create table orders(customer_id int, amount real)")
    db.executemany("insert into orders values(?,?)", [(1, 10), (1, 5), (2, 7), (3, 1), (3, 2)])
    try: return sorted(db.execute(m.group(1)).fetchall()) == [(1, 15.0), (2, 7.0), (3, 3.0)]
    except Exception: return False
def json_ok(a):
    m = re.search(r"\{[\s\S]*\}", a)
    try: d = json.loads(m.group(0)); return d.get("nama") == "Rina" and d.get("kota") == "Medan"
    except Exception: return False
num = lambda a: re.sub(r"[.\s]", "", a)
TASKS = [
 ("hitung", "Toko menjual 3 buku @Rp 12.500 dan 2 pulpen @Rp 8.750. Berapa total yang dibayar? Jawab angkanya saja.", lambda a: "55000" in num(a)),
 ("logika", "Andi lebih tua dari Budi. Budi lebih tua dari Citra. Siapa yang paling muda? Jawab satu nama.", lambda a: "citra" in a.strip().split("\n")[-1].lower() and "andi" not in a.strip().split("\n")[-1].lower()),
 ("hari", "Jika hari ini Senin, 3 hari lagi hari apa? Jawab satu kata.", lambda a: "kamis" in a.lower() or "thursday" in a.lower()),
 ("satuan", "2,5 jam sama dengan berapa menit? Jawab angkanya saja.", lambda a: "150" in a),
 ("ekstraksi", "Dari teks: 'Invoice INV-2291 tertanggal 12 Maret 2026, total Rp 4.350.000, jatuh tempo 30 hari.' Berapa total invoice? Jawab angkanya saja.", lambda a: "4350000" in num(a)),
 ("sentimen", "Klasifikasikan sentimen ulasan ini sebagai positif/negatif/netral: 'Pelayanannya lambat banget, kecewa berat.' Jawab satu kata.", lambda a: "negatif" in a.lower()),
 ("pengetahuan", "Apa ibu kota provinsi Jawa Barat? Jawab satu kata.", lambda a: "bandung" in a.lower()),
 ("dokumen", "Dokumen: 'Penggantian kacamata maksimal Rp 750.000 per 2 tahun, wajib resep dokter mata.' Pertanyaan: berapa batas penggantian kacamata? Jawab angkanya saja.", lambda a: "750000" in num(a)),
 ("sql", "Tulis satu query SQL (SQLite) untuk total amount per customer_id dari tabel orders(customer_id, amount). Hanya query, tanpa penjelasan.", sql_ok),
 ("json", "Ubah kalimat 'Rina tinggal di Medan' menjadi JSON dengan key nama dan kota. Hanya JSON.", json_ok),
]

DEFAULT = "qwen3:0.6b,qwen3:1.7b,qwen3.5:2b,qwen3:4b-instruct-2507-q4_K_M,qwen3:4b:think"
size = tags()
print(f"{'model':38}{'file GB':>8}{'VRAM GB':>8}{'benar':>7}{'detik':>8}{'token/s':>9}")
for m, think in models(DEFAULT):
    chat(m, [{"role": "user", "content": "hai"}], num_predict=1)  # muat model dulu
    loaded = next(x for x in ps() if x["name"] == m)
    ok = tok = 0; dur = 0.0; t0 = time.time()
    for name, q, check in TASKS:
        d = chat(m, [{"role": "user", "content": q}], think=think)
        a = d["message"]["content"].split("</think>")[-1].strip()
        tok += d.get("eval_count", 0); dur += d.get("eval_duration", 1) / 1e9
        good = bool(check(a)); ok += good
        if not good or os.environ.get("VERBOSE"):
            print(f"   [{m}] {name}: {'benar' if good else 'SALAH'} → {a[:120]!r}")
    label = m + (" (thinking)" if think else "")
    print(f"{label:38}{size[m] / 1e9:>8.1f}{loaded['size_vram'] / 1e9:>8.1f}{ok:>5}/10{time.time() - t0:>8.1f}{tok / dur:>9.0f}")
