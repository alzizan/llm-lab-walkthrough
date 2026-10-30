"""Lab 07 — RAG mengambil potongan dokumen yang salah: cara memotong (chunking) menentukan jawaban."""
import json, math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lab import ask, embed

EMBED = os.environ.get("EMBED_MODEL", "bge-m3:567m")
MODEL = os.environ.get("MODEL", "qwen3:4b-instruct-2507-q4_K_M")
DOCS = {
 "kebijakan-lembur-2022.pdf": ("KEBIJAKAN LEMBUR PT Contoh Sejahtera (FIKTIF). Nomor HR-07/2022. STATUS: DICABUT sejak 1 Januari 2025, diganti HR-02/2025. "
   "Bagian 1 Umum. Lembur wajib disetujui atasan langsung sebelum dikerjakan dan dicatat di sistem absensi. "
   "Bagian 2 Tarif. Uang lembur hari kerja dibayar 1,5 kali upah per jam. Uang lembur hari libur dan hari raya dibayar 2 kali upah per jam untuk seluruh jam lembur."),
 "kebijakan-lembur-2025.pdf": ("KEBIJAKAN LEMBUR PT Contoh Sejahtera (FIKTIF). Nomor HR-02/2025. STATUS: BERLAKU mulai 1 Januari 2025. "
   "Bagian 1 Umum. Pengajuan lembur dilakukan melalui aplikasi HR paling lambat H-1, kecuali keadaan darurat operasional. "
   "Bagian 2 Tarif. Hari kerja: jam pertama 1,5 kali upah per jam, jam berikutnya 2 kali. Hari libur: 8 jam pertama 3 kali upah per jam, jam ke-9 dan seterusnya 4 kali upah per jam."),
 "kebijakan-cuti-2025.pdf": ("KEBIJAKAN CUTI PT Contoh Sejahtera (FIKTIF). Cuti tahunan 14 hari. Cuti sakit lebih dari 2 hari wajib surat dokter. "
   "Cuti melahirkan 3 bulan dengan upah penuh. Cuti ayah 5 hari kerja."),
}
Q = "Berapa tarif uang lembur kalau saya kerja di hari libur?"
def chunks_fixed(size=160):
    out = []
    for src, t in DOCS.items():
        for i in range(0, len(t), size): out.append({"src": src, "text": t[i:i + size]})
    return out
def chunks_section():
    out = []
    for src, t in DOCS.items():
        head = t.split(" Bagian 1")[0] if "Bagian 1" in t else t[:80]
        parts = t.split("Bagian ")
        for p in (parts[1:] if len(parts) > 1 else [t]):
            out.append({"src": src, "text": f"[{head[:140]}] Bagian {p}".strip() if len(parts) > 1 else t, "dicabut": "DICABUT" in head})
    return out
def cos(a, b): return sum(x * y for x, y in zip(a, b)) / math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))
def retrieve(ch, k=2, drop_revoked=False):
    ch = [c for c in ch if not (drop_revoked and c.get("dicabut"))]
    E = embed(EMBED, [c["text"] for c in ch] + [Q]); q = E[-1]
    sc = sorted(((cos(e, q), c) for e, c in zip(E[:-1], ch)), key=lambda x: -x[0])
    return [{"score": round(s, 3), **c} for s, c in sc[:k]]
SYS = "Kamu asisten HR. Jawab HANYA dari potongan dokumen berikut, singkat, Bahasa Indonesia, sebutkan nama file sumbernya.\n\n"

for name, ch, drop in [("A. potong per 160 karakter", chunks_fixed(), False),
                       ("B. potong per bagian + judul & status di tiap potongan", chunks_section(), False),
                       ("C. B + dokumen DICABUT tidak diindeks", chunks_section(), True)]:
    top = retrieve(ch, drop_revoked=drop)
    context = "\n\n".join(f"[{c['src']}] {c['text']}" for c in top)
    answer, _ = ask(MODEL, SYS + context, Q)
    print(f"\n=== {name}")
    for c in top:
        print(f"  {c['score']:.3f} {c['src']:26} {c['text'][:90]!r}")
    print("  →", answer.replace("\n", " "))
