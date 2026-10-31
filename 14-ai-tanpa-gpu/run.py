"""Lab 14 — AI tanpa GPU: model yang sama di GPU vs dipaksa CPU saja (opsi Ollama num_gpu=0)."""
import os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lab import chat

MODELS = os.environ.get("MODELS", "qwen3:0.6b,qwen3:1.7b,qwen3.5:2b,qwen3:4b-instruct-2507-q4_K_M").split(",")
LONG_MODELS = os.environ.get("LONG_MODELS", "qwen3:1.7b,qwen3:4b-instruct-2507-q4_K_M").split(",")
DEVICES = [("GPU", {}), ("CPU", {"num_gpu": 0})]

EMAIL = ("Dari: Budi (Finance)\nKepada: Tim Pengadaan\nPerihal: Keterlambatan pembayaran vendor Q3\n\n"
 "Halo tim, berikut update pembayaran vendor kuartal 3. Dari 42 invoice yang jatuh tempo, 35 sudah dibayar tepat waktu. "
 "Tujuh invoice terlambat: lima karena dokumen PO tidak lengkap (tanda tangan manajer belum ada), dua karena nomor rekening vendor berubah "
 "dan belum diverifikasi. Total nilai yang tertunda Rp 418 juta. Vendor PT Sumber Makmur (Rp 210 juta) sudah mengirim surat teguran kedua "
 "dan mengancam menghentikan pengiriman bahan baku mulai 15 November. Mohon tim pengadaan melengkapi tanda tangan PO paling lambat Jumat, "
 "dan tim treasury memverifikasi rekening baru melalui telepon ke nomor yang terdaftar, bukan nomor di email vendor. "
 "Setelah itu Finance bisa membayar dalam 2 hari kerja. Terima kasih, Budi. (FIKTIF)")
TASK = "Ringkas email ini dalam 3 poin, lalu sebutkan 1 tindakan paling mendesak."

# Dokumen panjang fiktif (±5.200 token): 120 butir kebijakan retensi
random.seed(7)
units = ["Keuangan", "Pengadaan", "SDM", "TI", "Operasional", "Pemasaran", "Legal", "Audit Internal"]
lines = [f"Butir {i}. Unit {random.choice(units)} wajib menyimpan dokumen kategori {random.choice('ABCD')} selama "
         f"{random.randint(2, 10)} tahun; akses hanya untuk {random.choice(['manajer', 'staf terkait', 'auditor', 'direksi'])} "
         f"dan setiap perubahan dicatat di log." for i in range(1, 121)]
DOC = "Kebijakan Retensi Dokumen PT Contoh Sejahtera (FIKTIF)\n" + "\n".join(lines)
Q = "Berdasarkan kebijakan di atas, berapa lama butir 77 mewajibkan dokumen disimpan, dan unit mana?"


def measure(model, prompt, num_ctx, opts):
    chat(model, [{"role": "user", "content": "Halo"}], num_predict=1, num_ctx=num_ctx, **opts)  # muat model dulu
    d = chat(model, [{"role": "user", "content": prompt}], num_predict=300, num_ctx=num_ctx, **opts)
    return d, d["eval_count"] / (d["eval_duration"] / 1e9), d["prompt_eval_duration"] / 1e9


print("Tugas 1: ringkas email")
print(f"{'model':32} {'alat':4} {'tok/s':>7} {'baca prompt':>12} {'total':>8}")
for m in MODELS:
    for dev, opts in DEVICES:
        d, tps, ps = measure(m, EMAIL + "\n\n" + TASK, 4096, opts)
        print(f"{m:32} {dev:4} {tps:7.1f} {ps:10.1f} s {d['secs']:6.1f} s")

print(f"\nTugas 2: dokumen panjang. Jawaban benar: {lines[76]}")
for m in LONG_MODELS:
    for dev, opts in DEVICES:
        d, tps, ps = measure(m, DOC + "\n\n" + Q, 8192, opts)
        ans = d["message"]["content"].split("</think>")[-1].strip().replace("\n", " ")
        print(f"{m:32} {dev:4} prompt {d['prompt_eval_count']} token, baca {ps:.1f} s, total {d['secs']:.1f} s\n     → …{ans[-120:]}")
