"""Lab 11 — ukur token, waktu, dan daya GPU dari permintaan nyata, lalu hitung biaya per bulan.

Daya GPU dibaca dari `nvidia-smi` tiap detik (jalankan di mesin yang sama dengan GPU-nya).
Tanpa nvidia-smi, script tetap jalan dan hanya menghitung token & waktu.
"""
import os, subprocess, sys, threading, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lab import chat

MODEL = os.environ.get("MODEL", "qwen3:4b-instruct-2507-q4_K_M")
TARIF = float(os.environ.get("TARIF_KWH", "1444.70"))      # Rp/kWh, sesuaikan golongan listrik Anda
USERS, Q_PER_DAY = int(os.environ.get("USERS", "200")), int(os.environ.get("Q_PER_DAY", "20"))
PRICES = [(0.15, 0.60), (0.25, 2.00)]  # contoh harga API cloud US$/1 juta token (masuk, keluar) — CEK HARGA TERKINI

DOC = """Buku saku karyawan (FIKTIF): jam kerja 08.00–17.00; cuti tahunan 14 hari, maks 5 hari dibawa, hangus 31 Maret;
lembur hari kerja 1,5x jam pertama lalu 2x; hari libur 3x untuk 8 jam pertama, 4x setelahnya; rawat jalan Rp 5 juta/tahun;
rawat inap kelas 1 Rp 40 juta/tahun; kacamata Rp 750 ribu/2 tahun; uang makan Rp 35 ribu/hari; dinas Jawa Rp 400 ribu/hari,
luar Jawa Rp 500 ribu/hari, hotel maks Rp 900 ribu/malam; WFH maks 2 hari/minggu; gaji tanggal 25."""
TASKS = ["Ringkas buku saku ini dalam 5 poin.", "Jelaskan aturan lembur hari libur dengan contoh untuk upah Rp 50.000/jam, 10 jam.",
         "Buat FAQ 5 pertanyaan dari buku saku ini.", "Tulis email pengumuman aturan WFH untuk karyawan.",
         "Hitung total biaya dinas ke luar Jawa 3 malam."] * 4

samples, stop = [], threading.Event()


def sample_power():
    while not stop.is_set():
        try:
            out = subprocess.run(["nvidia-smi", "--query-gpu=power.draw,utilization.gpu", "--format=csv,noheader,nounits"],
                                 capture_output=True, text=True, timeout=5).stdout.split(",")
            samples.append((float(out[0]), float(out[1])))
        except Exception:
            return
        time.sleep(1)


chat(MODEL, [{"role": "user", "content": "hai"}], num_predict=1)  # muat model dulu
threading.Thread(target=sample_power, daemon=True).start()
tin = tout = 0
t0 = time.time()
for task in TASKS:
    d = chat(MODEL, [{"role": "system", "content": "Kamu asisten HR. Gunakan buku saku berikut.\n\n" + DOC},
                     {"role": "user", "content": task}])
    tin += d["prompt_eval_count"]; tout += d["eval_count"]
wall = time.time() - t0; stop.set()
n = len(TASKS)
print(f"{n} permintaan · {tin / n:.0f} token masuk & {tout / n:.0f} token keluar per permintaan · {wall / n:.1f} s/permintaan")

busy = [w for w, u in samples if u > 50]
if busy:
    watt = sum(busy) / len(busy)
    kwh_per_m = watt * wall / 3600 / 1000 / tout * 1e6
    print(f"daya GPU saat bekerja ±{watt:.1f} W → {kwh_per_m:.2f} kWh per 1 juta token keluaran ≈ Rp {kwh_per_m * TARIF:,.0f}")
else:
    kwh_per_m = None
    print("(nvidia-smi tidak tersedia: daya tidak diukur)")

req_day = USERS * Q_PER_DAY
m_in, m_out = req_day * 30 * tin / n / 1e6, req_day * 30 * tout / n / 1e6
print(f"\nSkenario {USERS} user × {Q_PER_DAY} pertanyaan/hari = {req_day:,} permintaan/hari")
print(f"  token/bulan: {m_in:.1f} juta masuk + {m_out:.1f} juta keluar")
print(f"  waktu proses berurutan di GPU ini: {req_day * wall / n / 3600:.1f} jam/hari")
if kwh_per_m:
    print(f"  listrik GPU/bulan: ±Rp {m_out * kwh_per_m * TARIF:,.0f}")
for p_in, p_out in PRICES:
    print(f"  API cloud US${p_in}/US${p_out} per 1 juta token: ±US${m_in * p_in + m_out * p_out:,.0f}/bulan")
