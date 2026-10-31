"""Lab 20 — deteksi shadow AI dari log proxy/firewall/DNS yang sudah dimiliki kantor (stdlib saja, tanpa model AI).

Pemakaian:
  python 20-shadow-ai/run.py                 # bangkitkan log SIMULASI lalu analisis
  python 20-shadow-ai/run.py log-anda.csv    # analisis log Anda sendiri

Format CSV: waktu,user,unit,domain,bytes_keluar (sesuaikan nama kolom di COLS bila berbeda).
"""
import collections, csv, os, random, sys

COLS = {"user": "user", "unit": "unit", "domain": "domain", "bytes": "bytes_keluar", "time": "waktu"}
# Daftar domain layanan AI publik. Lengkapi sendiri; tandai yang SUDAH disetujui perusahaan di APPROVED.
AI = ["chatgpt.com", "chat.openai.com", "gemini.google.com", "claude.ai", "copilot.microsoft.com",
      "chat.deepseek.com", "www.perplexity.ai", "poe.com", "chat.mistral.ai", "huggingface.co"]
APPROVED = set(os.environ.get("APPROVED", "").split(",")) - {""}
BIG = int(os.environ.get("BIG_BYTES", "100000"))  # unggahan di atas ini = indikasi dokumen/file


def simulate(path):
    """Log proxy FIKTIF 1 minggu, 40 karyawan. Angkanya karangan generator, bukan data perusahaan nyata."""
    random.seed(19)
    depts = {"Keuangan": 8, "Pemasaran": 7, "SDM": 5, "Legal": 4, "TI": 6, "Operasional": 10}
    rate = {"Keuangan": .35, "Pemasaran": .6, "SDM": .3, "Legal": .25, "TI": .7, "Operasional": .1}
    ai = ["chatgpt.com", "gemini.google.com", "claude.ai", "copilot.microsoft.com", "chat.deepseek.com", "www.perplexity.ai", "poe.com"]
    normal = ["mail.contoh.co.id", "erp.contoh.co.id", "www.google.com", "www.youtube.com", "drive.google.com", "web.whatsapp.com", "news.detik.com"]
    rows = []
    for dept, n in depts.items():
        for u in range(1, n + 1):
            user, uses_ai = f"{dept[:3].lower()}{u:02d}", random.random() < rate[dept] * 1.4
            for day in range(1, 6):
                for _ in range(random.randint(25, 45)):
                    if uses_ai and random.random() < .12:
                        dom = random.choice(ai)
                        up = random.choice([800, 1500, 3000, 6000]) if random.random() < .85 else random.choice([120_000, 350_000, 900_000])
                    else:
                        dom, up = random.choice(normal), random.randint(300, 5000)
                    rows.append((f"2026-10-{20 + day:02d} {random.randint(8, 17):02d}:{random.randint(0, 59):02d}", user, dept, dom, up))
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["waktu", "user", "unit", "domain", "bytes_keluar"])
        w.writerows(sorted(rows))


path = sys.argv[1] if len(sys.argv) > 1 else "proxy-log-simulasi.csv"
if len(sys.argv) == 1:
    simulate(path)
    print(f"(log SIMULASI ditulis ke {path})")

log = list(csv.DictReader(open(path)))
hit = lambda d: any(d == a or d.endswith("." + a) for a in AI)
ai = [r for r in log if hit(r[COLS["domain"]])]
users = {r[COLS["user"]]: r[COLS["unit"]] for r in log}
ai_users = {r[COLS["user"]] for r in ai}
print(f"\nBaris log: {len(log)} · karyawan: {len(users)} · memakai layanan AI publik: {len(ai_users)} ({len(ai_users) / max(len(users), 1):.0%})")

print("\nPer unit (user AI / total user, jumlah permintaan):")
total = collections.Counter(users.values())
per = collections.defaultdict(lambda: [set(), 0])
for r in ai:
    per[r[COLS["unit"]]][0].add(r[COLS["user"]])
    per[r[COLS["unit"]]][1] += 1
for unit in total:
    print(f"  {unit:14} {len(per[unit][0]):>3}/{total[unit]:<3} user · {per[unit][1]:>5} permintaan")

print("\nPer layanan:")
for dom, n in collections.Counter(r[COLS["domain"]] for r in ai).most_common():
    print(f"  {dom:26} {n:>5}  {'(disetujui)' if dom in APPROVED else '(belum disetujui)'}")

big = [r for r in ai if int(r[COLS["bytes"]]) > BIG and r[COLS["domain"]] not in APPROVED]
print(f"\nUnggahan > {BIG // 1000} KB ke layanan yang belum disetujui: {len(big)} kali")
for unit, n in collections.Counter(r[COLS["unit"]] for r in big).most_common():
    print(f"  {unit:14} {n}")
for r in big[:10]:
    print(f"  {r[COLS['time']]}  {r[COLS['user']]:8} {r[COLS['unit']]:12} {r[COLS['domain']]:24} {int(r[COLS['bytes']]) // 1000} KB")
print("\nCatatan: log hanya menunjukkan siapa, kapan, ke mana, dan ukuran. Isi prompt tidak terlihat (HTTPS).")
