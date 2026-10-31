"""Lab 15 — pencarian kata kunci vs pencarian semantik (embedding) di potongan kebijakan fiktif."""
import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lab import embed

# 12 potongan kebijakan FIKTIF, campuran Bahasa Indonesia & Inggris
DOCS = [
 "Karyawati yang bersalin berhak istirahat 3 bulan dengan upah penuh.",
 "Maternity leave: female employees receive 3 months of fully paid leave after giving birth.",
 "Cuti sakit lebih dari 2 hari wajib melampirkan surat dokter.",
 "Cuti tahunan 14 hari kerja; sisa maksimal 5 hari dapat dibawa ke tahun berikutnya.",
 "Paternity leave: 5 working days for employees whose wife gives birth.",
 "Work from home (WFH) maksimal 2 hari per minggu dengan persetujuan atasan.",
 "Kehilangan perangkat kantor wajib dilaporkan ke tim IT paling lambat 1x24 jam.",
 "Password minimal 12 karakter dan dilarang dibagikan kepada siapa pun, termasuk tim IT.",
 "Penggantian kacamata maksimal Rp 750.000 per 2 tahun dengan resep dokter mata.",
 "Uang harian perjalanan dinas Rp 500.000 untuk luar Jawa.",
 "SOP-TI-017: prosedur pemulihan akun email yang terkunci.",
 "Kantor tutup pada hari libur nasional dan cuti bersama.",
]
QS = [("cuti melahirkan", [0, 1]), ("laptop saya dicuri", [6]), ("berapa hari boleh kerja dari rumah", [5]),
      ("bolehkah saya kasih kata sandi ke orang IT?", [7]), ("berapa lama cuti untuk suami saat istri melahirkan", [4]),
      ("SOP-TI-017", [10]), ("tunjangan dinas ke Makassar", [9])]
STOP = {"saya", "ke", "di", "dan", "yang", "untuk", "berapa", "boleh", "bolehkah", "saat", "lama", "the", "for", "of"}
tok = lambda s: [w for w in re.findall(r"[a-z0-9-]+", s.lower()) if w not in STOP]
def kw(q):
    qs = set(tok(q)); sc = [len(qs & set(tok(d))) for d in DOCS]
    return sorted(range(len(DOCS)), key=lambda i: -sc[i]), sc
MODEL = os.environ.get("EMBED_MODEL", "bge-m3:567m")
E = embed(MODEL, DOCS)
cos = lambda a, b: sum(x * y for x, y in zip(a, b)) / math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))

for q, rel in QS:
    order, sc = kw(q)
    qe = embed(MODEL, [q])[0]
    ss = [cos(qe, e) for e in E]
    sorder = sorted(range(len(DOCS)), key=lambda i: -ss[i])
    mark = lambda i: "✓" if i in rel else "✗"
    print(f"\n>>> {q}")
    print(f"  kata kunci: {mark(order[0]) if sc[order[0]] else '✗'} " + (DOCS[order[0]] if sc[order[0]] else "(tidak ada kata yang sama)"))
    for i in sorder[:3]:
        print(f"  semantik  : {mark(i)} [{ss[i]:.3f}] {DOCS[i]}")
