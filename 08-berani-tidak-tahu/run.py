"""Lab 08 — melatih AI berani bilang "tidak ada di dokumen"."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lab import ask, models

DOC = ("[kebijakan-benefit-2025.pdf — PT Contoh Sejahtera (FIKTIF)]\n"
       "Rawat jalan: maksimal Rp 5.000.000 per tahun. Rawat inap: kamar kelas 1, maksimal Rp 40.000.000 per tahun. "
       "Kacamata: maksimal Rp 750.000 per 2 tahun dengan resep dokter mata. Melahirkan normal: maksimal Rp 8.000.000.")
QUESTIONS = [  # (jenis, pertanyaan)
    ("ada di dokumen", "Berapa batas penggantian kacamata?"),
    ("jelas di luar dokumen", "Berapa batas reimburse perawatan gigi?"),
    ("dekat: tanggungan istri", "Istri saya mau rawat inap, plafonnya berapa?"),
    ("dekat: lensa kontak", "Saya mau beli lensa kontak, ditanggung berapa?"),
    ("dekat: caesar", "Saya melahirkan caesar bulan depan, dapat berapa?"),
    ("dekat: pensiun", "Kalau saya sudah pensiun, rawat jalan masih ditanggung?"),
]
PROMPTS = {
    "biasa": "Kamu asisten HR. Jawab pertanyaan karyawan berdasarkan dokumen berikut. Jawab singkat dalam Bahasa Indonesia.\n\n" + DOC,
    "ketat": ("Kamu asisten HR. Jawab HANYA dari dokumen berikut. Jika jawabannya tidak tertulis eksplisit di dokumen, "
              "jawab persis: \"Tidak ada di dokumen kebijakan. Silakan hubungi HR.\" Jangan menebak, jangan memakai pengetahuan umum. "
              "Jika ada, sebutkan kalimat dokumen yang menjadi dasar jawaban. Bahasa Indonesia, singkat.\n\n" + DOC),
}

for model, think in models():
    print(f"\n######## {model}{' (thinking)' if think else ''}")
    for pname, system in PROMPTS.items():
        print(f"--- prompt {pname}")
        for kind, q in QUESTIONS:
            answer, _ = ask(model, system, q, think=think)
            print(f"  [{kind}] {q}\n     → {answer.replace(chr(10), ' ')[:200]}")
    answer, _ = ask(model, None, "Berapa plafon rawat inap karyawan di PT Contoh Sejahtera?", think=think)
    print(f"--- tanpa dokumen sama sekali\n     → {answer.replace(chr(10), ' ')[:200]}")
