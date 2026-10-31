"""Lab 19 — teks invoice ke JSON terstruktur (format JSON schema Ollama), lalu validasi aturan bisnis di kode."""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lab import chat

MODELS = os.environ.get("MODELS", "qwen3:4b-instruct-2507-q4_K_M,qwen3.5:2b,qwen3:1.7b").split(",")

# 5 invoice FIKTIF dalam bentuk teks, beserta jawaban benar
INV = [
 ("""PT SINAR ABADI LOGISTIK
INVOICE No. INV/2026/03/0142
Tanggal: 12 Maret 2026
Kepada: PT Contoh Sejahtera
1. Jasa pengiriman Jakarta–Surabaya (3 truk) Rp 13.500.000
2. Asuransi barang Rp 450.000
Subtotal Rp 13.950.000
PPN 11% Rp 1.534.500
TOTAL Rp 15.484.500
(FIKTIF)""", {"nomor": "INV/2026/03/0142", "tanggal": "2026-03-12", "subtotal": 13950000, "ppn": 1534500, "total": 15484500}),
 ("""CV Maju Jaya Komputer — Faktur #MJK-0091   tgl 03/04/2026
Laptop 14" x2 @ 9.750.000 = 19.500.000
Mouse wireless x2 @ 175.000 = 350.000
Diskon -500.000
DPP 19.350.000 | PPN 11% 2.128.500 | Grand Total 21.478.500
Uang muka yang sudah dibayar: 10.000.000. Sisa tagihan: 11.478.500 (FIKTIF)""",
  {"nomor": "MJK-0091", "tanggal": "2026-04-03", "subtotal": 19350000, "ppn": 2128500, "total": 21478500}),
 ("""Tagihan dari: Katering Ibu Sari
Nomor: KIS-26-077, tanggal 2026-05-20
Nasi kotak rapat 120 porsi x Rp 35.000 = Rp 4.200.000
(tidak dikenakan PPN)
Jumlah dibayar: Rp 4.200.000 (FIKTIF)""", {"nomor": "KIS-26-077", "tanggal": "2026-05-20", "subtotal": 4200000, "ppn": 0, "total": 4200000}),
 ("""PT DATA PRIMA NUSANTARA
Invoice: DPN-INV-5531 / Date: 30 June 2026
Annual software subscription ........ IDR 48,000,000.00
VAT 11% ............................. IDR 5,280,000.00
Amount due .......................... IDR 53,280,000.00 (FICTIONAL)""",
  {"nomor": "DPN-INV-5531", "tanggal": "2026-06-30", "subtotal": 48000000, "ppn": 5280000, "total": 53280000}),
 ("""UD Berkah Cetak, Nota No. 0815, tanggal 7 Juli 2026
Cetak brosur 2.000 lembar Rp 3.000.000
Cetak spanduk 4 buah Rp 1.200.000
Subtotal Rp 4.200.000
PPN 11% Rp 462.000
Total Rp 4.762.000 (FIKTIF)""", {"nomor": "0815", "tanggal": "2026-07-07", "subtotal": 4200000, "ppn": 462000, "total": 4762000}),
]
# Nota terakhir sengaja SALAH HITUNG di sumbernya: 4.200.000 + 462.000 = 4.662.000, bukan 4.762.000.
SCHEMA = {"type": "object", "properties": {"nomor": {"type": "string"}, "tanggal": {"type": "string", "description": "YYYY-MM-DD"},
          "subtotal": {"type": "integer"}, "ppn": {"type": "integer"}, "total": {"type": "integer"}},
          "required": ["nomor", "tanggal", "subtotal", "ppn", "total"]}
SYS = ("Ekstrak data invoice ke JSON dengan key: nomor, tanggal (format YYYY-MM-DD), subtotal, ppn, total. "
       "Semua angka dalam rupiah sebagai bilangan bulat tanpa titik/koma. subtotal = sebelum PPN. total = total tagihan termasuk PPN. "
       "Salin angka persis dari dokumen, jangan menghitung ulang. Hanya JSON.")
def parse(a):
    m = re.search(r"\{[\s\S]*\}", a)
    try: return json.loads(m.group(0))
    except Exception: return None


def validate(j):
    """Aturan bisnis sederhana. Yang gagal → antrean review manusia."""
    issues = []
    if not all(isinstance(j.get(k), int) for k in ("subtotal", "ppn", "total")):
        return ["angka bukan bilangan bulat"]
    if j["subtotal"] + j["ppn"] != j["total"]:
        issues.append(f"subtotal + ppn = {j['subtotal'] + j['ppn']:,} ≠ total {j['total']:,}")
    if j["ppn"] and abs(j["ppn"] - round(j["subtotal"] * 0.11)) > 1:
        issues.append("PPN bukan 11% dari subtotal")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(j.get("tanggal", ""))):
        issues.append("format tanggal")
    return issues


for m in MODELS:
    print(f"\n######## {m}")
    for mode in ["prompt saja", "format schema"]:
        ok = 0
        for i, (txt, truth) in enumerate(INV):
            extra = {"format": SCHEMA} if mode == "format schema" else {}
            d = chat(m, [{"role": "system", "content": SYS}, {"role": "user", "content": txt}], **extra)
            a = d["message"]["content"].split("</think>")[-1].strip()
            j = parse(a)
            if not isinstance(j, dict):
                print(f"  [{mode}] invoice {i + 1}: BUKAN JSON objek valid ({len(a)} karakter) → {a[:100]!r}")
                continue
            wrong = [k for k in truth if str(j.get(k)) != str(truth[k])]
            ok += not wrong
            issues = validate(j)
            print(f"  [{mode}] invoice {i + 1}: {'benar' if not wrong else 'SALAH ' + str(wrong)}"
                  f"{' · VALIDASI: ' + '; '.join(issues) if issues else ''}")
        print(f"  [{mode}] {ok}/{len(INV)} benar semua field")
