"""Lab 05 — pertanyaan sama, jawaban beda? Konsisten vs tangguh vs benar."""
import os, re, sqlite3, sys
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lab import chat, models

N = int(os.environ.get("N", "10"))
SUFFIX = " Apakah layak? Jawab diawali LAYAK atau TIDAK LAYAK, lalu satu kalimat alasan."
DATA = ("Data nasabah (FIKTIF): skor kredit 600, penghasilan Rp 8 juta/bulan, cicilan berjalan Rp 3,5 juta/bulan, "
        "mengajukan pinjaman tambahan Rp 50 juta tenor 36 bulan.")
VARIANTS = {  # isi sama, cara bertanya berbeda
    "asli": DATA + SUFFIX,
    "urutan dibalik": "Nasabah (FIKTIF) mengajukan pinjaman tambahan Rp 50 juta tenor 36 bulan. Cicilan berjalan Rp 3,5 juta/bulan, "
                      "penghasilan Rp 8 juta/bulan, skor kredit 600." + SUFFIX,
    "pakai 'tolong'": "Tolong bantu analisa. " + DATA + SUFFIX,
    "sebut 'analis risiko'": "Kamu analis risiko kredit. " + DATA + SUFFIX,
}
SQL_Q = ("Tulis satu query SQL (SQLite) untuk 3 customer_id dengan total amount terbesar dari tabel "
         "orders(customer_id, amount, status), hanya status 'paid'. Hanya query.")
db = sqlite3.connect(":memory:")
db.execute("create table orders(customer_id int, amount real, status text)")
db.executemany("insert into orders values(?,?,?)", [(1, 100, "paid"), (1, 50, "refund"), (2, 120, "paid"), (3, 90, "paid"),
                                                    (3, 40, "paid"), (4, 200, "refund"), (5, 60, "paid")])
EXPECTED = [r[0] for r in db.execute("select customer_id from orders where status='paid' group by customer_id "
                                     "order by sum(amount) desc limit 3")]


def verdict(a):
    a = a.upper().lstrip("* ")
    return "TIDAK LAYAK" if a.startswith("TIDAK") else "LAYAK" if a.startswith("LAYAK") else "lain"


def sql_correct(a):
    m = re.search(r"(SELECT[\s\S]*?)(;|```|$)", a, re.I)
    try:
        return [r[0] for r in db.execute(m.group(1))] == EXPECTED
    except Exception:
        return False


for model, think in models("qwen3.5:2b,qwen3:4b-instruct-2507-q4_K_M"):
    print(f"\n######## {model}")
    hot = [chat(model, [{"role": "user", "content": VARIANTS["asli"]}], temp=0.8, think=think)["message"]["content"] for _ in range(N)]
    print(f"1) temperature 0.8, pertanyaan sama {N}x → {dict(Counter(verdict(a) for a in hot))}")
    print("2) temperature 0, variasi kalimat (isi sama):")
    for name, q in VARIANTS.items():
        a = chat(model, [{"role": "user", "content": q}], temp=0, think=think)["message"]["content"].strip()
        print(f"   {name:22} → {verdict(a):12} | {a.splitlines()[0][:100]}")
    sqls = [chat(model, [{"role": "user", "content": SQL_Q}], temp=t, think=think)["message"]["content"].strip()
            for t in (0, 0.8) for _ in range(N)]
    print(f"3) SQL {len(sqls)}x (temperature 0 & 0.8): {len(set(sqls))} versi berbeda, "
          f"benar saat dieksekusi {sum(map(sql_correct, sqls))}/{len(sqls)}")
    print("   contoh:", sqls[0].replace("\n", " ")[:160])
