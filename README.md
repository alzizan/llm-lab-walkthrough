# LLM Lab — Uji Langsung AI Lokal, dengan Data Fiktif

Serangkaian eksperimen kecil yang bisa Anda jalankan sendiri untuk memahami perilaku model AI
(LLM) sebelum dipakai di perusahaan: prompt injection, kebocoran prompt, AI agent, ukuran model,
konsistensi jawaban, dan lainnya.

Semua hasil di repo ini dari run nyata, bukan contoh karangan. Semua data (perusahaan, dokumen,
nama, angka, alamat email) **fiktif**. Gambar adalah render teks output asli dari API, bukan
screenshot aplikasi.

Disusun oleh [PT Alzizan Digital Solutions](https://alzizan.co.id).

## Persiapan (sekali saja)

1. Pasang [Ollama](https://ollama.com/download) (kami memakai versi 0.40.11).
2. Unduh model yang dipakai lab (semua muat di GPU 6 GB; tanpa GPU tetap jalan, hanya lebih lambat):

   ```bash
   ollama pull qwen3:4b-instruct-2507-q4_K_M   # 2,5 GB
   ollama pull qwen3:4b                        # 2,5 GB
   ollama pull qwen3.5:2b                      # 2,7 GB
   ```

   Lab tertentu butuh model tambahan; disebutkan di README lab tersebut.
3. Python 3.10+. Tidak perlu `pip install`: script hanya memakai standard library.
4. Clone repo ini dan jalankan dari folder root:

   ```bash
   git clone https://github.com/alzizan/llm-lab-walkthrough.git
   cd llm-lab-walkthrough
   python 01-prompt-injection-dokumen/run.py
   ```

Ollama di mesin lain? `OLLAMA_URL=http://alamat-server:11434 python ...`.
Ganti model: `MODELS="llama3.2:3b,qwen3:4b:think" python ...` (akhiran `:think` = mode thinking).

## Daftar Lab

| Lab | Pertanyaan yang diuji |
|---|---|
| [01 — Prompt injection lewat dokumen](01-prompt-injection-dokumen/README.md) | Bisakah teks tersembunyi di PDF knowledge base membuat chatbot meminta NIK & password? |
| [02 — Membongkar prompt sistem](02-bongkar-prompt-sistem/README.md) | Seberapa aman "rahasia" yang disimpan di prompt sistem chatbot? |
| [03 — AI agent tertipu halaman web](03-agent-tertipu-halaman-web/README.md) | Bisakah hasil web search membuat agent mengirim data rahasia keluar? |
| [04 — Ukuran model](04-ukuran-model/README.md) | 0,6B sampai 4B: akurasi, kecepatan, dan memori GPU pada 10 soal berjawaban pasti |
| [05 — Konsistensi jawaban](05-konsistensi-jawaban/README.md) | Pertanyaan sama, jawaban beda? Temperature, variasi kalimat, dan "konsisten tapi salah" |
| [06 — AI berhitung](06-ai-berhitung/README.md) | Menjumlah 30 transaksi sendiri vs menulis SQL dan biarkan database yang menghitung |
| [07 — RAG salah ambil dokumen](07-rag-salah-ambil/README.md) | Dokumennya ada, jawabannya tetap salah: chunking, peringkat kemiripan, dan dokumen yang sudah dicabut |
| [08 — Berani bilang tidak tahu](08-berani-tidak-tahu/README.md) | Pertanyaan yang "hampir" ada di dokumen, prompt ketat, dan asumsi yang tetap lolos |
| [09 — 20 pertanyaan emas](09-pertanyaan-emas/README.md) | Evaluasi otomatis sebelum ganti model/prompt: skor sama, jenis kesalahan berbeda |
| [10 — Isi file model](10-isi-file-model/README.md) | Membongkar file model (GGUF, template, lisensi, sha256) dan kenapa pickle berbahaya |
| [11 — Biaya token vs GPU](11-biaya-token-vs-gpu/README.md) | Ukur token, waktu, dan daya GPU, lalu bandingkan dengan tagihan API cloud |
| [12 — Data pribadi di prompt](12-data-pribadi-di-prompt/README.md) | Penyaring regex + model lokal sebelum prompt keluar, dan apa yang tetap lolos (UU PDP Pasal 56) |
| [13 — AI mengutip pasal](13-ai-mengutip-pasal/README.md) | Pertanyaan UU PDP tanpa dokumen vs dengan kutipan teks pasal resmi: nomor pasal karangan yang terdengar meyakinkan |

## Catatan

- Hasil bisa berbeda di mesin Anda (versi model, GPU, versi Ollama). Bahkan di temperature 0,
  jawaban bisa berbeda antar-run. Jalankan beberapa kali.
- Lab keamanan di sini untuk menguji sistem **milik Anda sendiri**.

## Tentang

Kami membangun Enterprise Data Platform: catalog, governance, lakehouse, dan AI yang berjalan 100%
on-premise, dengan konteks AI yang disaring hak akses & masking.

- Coba gratis: https://alzizan.co.id/register
- Video demo: https://www.youtube.com/@AlzizanDigitalSolutions

Konten dilisensikan [CC BY 4.0](LICENSE).
