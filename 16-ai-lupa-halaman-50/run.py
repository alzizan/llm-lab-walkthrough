"""Lab 16 — AI "lupa" halaman 50: konteks default, dokumen dipotong, konteks diperbesar, dan RAG."""
import json, math, os, random, sys, urllib.error, urllib.request
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lab import chat, embed, OLLAMA

M = os.environ.get("MODEL", "qwen3:4b-instruct-2507-q4_K_M")
EMBED = os.environ.get("EMBED_MODEL", "bge-m3:567m")
BIG_CTX = int(os.environ.get("BIG_CTX", "32768"))

# Dokumen pedoman FIKTIF 80 halaman (±18.900 token), satu kalimat unik disisipkan di halaman tertentu
random.seed(11)
topics = ["pengadaan barang", "perjalanan dinas", "pengelolaan arsip", "keamanan gedung", "rapat direksi", "pelatihan karyawan",
          "pemeliharaan kendaraan", "pengelolaan aset TI", "layanan pelanggan", "pelaporan keuangan"]
roles = ["kepala divisi", "manajer unit", "staf administrasi", "tim audit", "sekretaris perusahaan", "petugas K3"]
def page(n):
    t = random.choice(topics); s = []
    for k in range(5):
        s.append(f"{n}.{k+1} Dalam {t}, {random.choice(roles)} wajib {random.choice(['memeriksa', 'menyetujui', 'mencatat', 'meninjau', 'mengarsipkan'])} "
                 f"dokumen {random.choice(['formulir', 'laporan', 'berita acara', 'memo', 'daftar periksa'])} paling lambat {random.randint(1, 14)} hari kerja "
                 f"setelah {random.choice(['permintaan diterima', 'kegiatan selesai', 'akhir bulan', 'rapat koordinasi'])}.")
    return f"--- Halaman {n} ---\n" + " ".join(s)
NEEDLE = "Kode darurat untuk membuka ruang server lantai 7 adalah MERPATI-4471, hanya boleh dipakai saat kebakaran."
Q = "Apa kode darurat untuk membuka ruang server lantai 7?"
pages = [page(i) for i in range(1, 81)]
def doc_with(pos):
    p = list(pages); p[pos - 1] = p[pos - 1] + " " + NEEDLE
    return "Pedoman Operasional PT Contoh Sejahtera (FIKTIF), 80 halaman\n\n" + "\n".join(p)


def run(label, prompt, **opts):
    try:
        d = chat(M, [{"role": "user", "content": prompt + "\n\n" + Q}], num_predict=120, **opts)
    except urllib.error.HTTPError as e:
        print(f"{label}\n   ERROR: {json.load(e)['error']}")
        return
    loaded = next((x for x in json.load(urllib.request.urlopen(OLLAMA + "/api/ps"))["models"] if x["name"] == M), {})
    a = d["message"]["content"].strip().replace("\n", " ")
    print(f"{label}\n   {'BENAR' if 'MERPATI-4471' in a else 'SALAH'} · {d['prompt_eval_count']} token · {d['secs']} s · "
          f"memori {loaded.get('size', 0) / 1e9:.2f} GB (GPU {loaded.get('size_vram', 0) / 1e9:.2f} GB)\n   → {a[:160]}")


run("1. Pengaturan default", doc_with(50))
run("2. Dokumen dipotong 20.000 karakter (halaman 1–30), num_ctx 8192", doc_with(50)[:20000], num_ctx=8192)
for pos in [5, 50, 75]:
    run(f"3. num_ctx {BIG_CTX}, kalimat di halaman {pos}", doc_with(pos), num_ctx=BIG_CTX)

chunks = doc_with(50).split("\n")[2:]  # satu baris = satu potongan
E = embed(EMBED, chunks)
qe = embed(EMBED, [Q])[0]
cos = lambda a, b: sum(x * y for x, y in zip(a, b)) / math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))
top = sorted(range(len(chunks)), key=lambda i: -cos(qe, E[i]))[:3]
run("4. RAG: 3 potongan paling relevan (" + ", ".join(chunks[i][:12] for i in top) + ")", "\n".join(chunks[i] for i in top))
