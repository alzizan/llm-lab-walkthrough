"""Lab 06 — AI menjumlah 30 transaksi vs AI menulis SQL dan database yang menghitung."""
import os, random, re, sqlite3, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lab import chat, models

SEEDS = [int(s) for s in os.environ.get("SEEDS", "1,2,3,4,5").split(",")]
SQL_Q = "Tabel SQLite trx(id text, amount integer) berisi transaksi hari ini. Tulis satu query SQL yang menghasilkan total dan rata-rata amount. Hanya query."
rp = lambda n: f"Rp {n:,}".replace(",", ".")


def dataset(seed):  # 30 transaksi fiktif, sama persis untuk seed yang sama
    random.seed(seed)
    return [random.randrange(150, 9800) * 1000 + random.choice([0, 250, 500, 750]) for _ in range(30)]


def parse_total(answer):
    answer = answer[answer.upper().rfind("TOTAL"):]
    m = re.search(r"TOTAL[^\d]*([\d.,]+)", answer, re.I)
    return int(re.sub(r",\d+$", "", m.group(1)).replace(".", "")) if m else None


for model, think in models("qwen3.5:2b,qwen3:4b-instruct-2507-q4_K_M"):
    print(f"\n######## {model}{' (thinking)' if think else ''}")
    ok = 0
    for seed in SEEDS:
        amounts = dataset(seed)
        rows = "\n".join(f"TRX-{i + 1:03d}  {rp(a)}" for i, a in enumerate(amounts))
        q = f"Berikut 30 transaksi hari ini (FIKTIF):\n{rows}\n\nBerapa TOTAL nilai transaksi? Akhiri jawaban dengan format:\nTOTAL: Rp ..."
        d = chat(model, [{"role": "user", "content": q}], think=think)
        got, true = parse_total(d["message"]["content"]), sum(amounts)
        ok += got == true
        status = "benar" if got == true else ("tidak terbaca" if got is None else f"SALAH, selisih {rp(abs(got - true))}")
        print(f"  data #{seed}: benar {rp(true)} · model {rp(got) if got else '-'} · {status} · {d['secs']} s")
    print(f"  → menjumlah sendiri: {ok}/{len(SEEDS)} benar")

    sql = chat(model, [{"role": "user", "content": SQL_Q}], think=think)["message"]["content"]
    m = re.search(r"(SELECT[\s\S]*?)(;|```|$)", sql, re.I)
    db = sqlite3.connect(":memory:")
    db.execute("create table trx(id text, amount integer)")
    db.executemany("insert into trx values(?,?)", [(f"TRX-{i}", a) for i, a in enumerate(dataset(SEEDS[0]))])
    try:
        total = db.execute(m.group(1)).fetchone()[0]
        print(f"  → jalur SQL: {m.group(1).strip()} → {rp(total)} ({'tepat' if total == sum(dataset(SEEDS[0])) else 'SALAH'})")
    except Exception as e:
        print(f"  → jalur SQL: {sql.strip()[:120]!r} → error: {e} (ketahuan saat dieksekusi)")
