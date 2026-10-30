# Lab 09 — 20 Pertanyaan Emas Sebelum AI Dipakai Seluruh Kantor

Set evaluasi kecil yang dijalankan otomatis setiap kali Anda mengganti model, prompt, atau dokumen.
Buku saku karyawan **fiktif** berisi 14 aturan; 20 pertanyaan berjawaban pasti (18 ada di buku
saku, 2 sengaja tidak ada dan harus dijawab "tidak ada").

## Jalankan

```bash
python 09-pertanyaan-emas/run.py          # 4 konfigurasi
ONLY=A,B python 09-pertanyaan-emas/run.py # sebagian saja
```

Model tambahan untuk konfigurasi D: `ollama pull qwen3:1.7b`.

## Konfigurasi

| | Model | Prompt |
|---|---|---|
| A | qwen3:4b-instruct-2507 | v1: "Jawab HANYA dari buku saku … jika tidak ada, jawab 'Tidak ada di buku saku, silakan hubungi HR.'" |
| B | qwen3:4b-instruct-2507 | v2: "ramah dan membantu, gunakan buku saku sebagai referensi" |
| C | qwen3.5:2b | v1 |
| D | qwen3:1.7b | v1 |

## Hasil kami (30 Okt 2026, temperature 0)

| | Skor | Yang gagal |
|---|---|---|
| A | 19/20 | kacamata dijawab "Maksimal 2 tahun." (angka hilang) |
| B | 19/20 | asuransi jiwa (tidak ada di buku saku) dijawab "kantor tidak menyediakan asuransi jiwa secara resmi…" — mengarang kebijakan |
| C | 18/20 | lembur jam ke-10 & "boleh berikan password ke tim IT?" dijawab "Tidak ada di buku saku" — padahal dilarang |
| D | 10/20 | terlalu takut: 9 pertanyaan yang jelas ada (mis. cuti tahunan 14 hari) dijawab "tidak ada" |

![20 pertanyaan emas](../images/09-01-20-pertanyaan-emas.png)

Catatan jujur: aturan penilaian pertanyaan password awalnya hanya mencari kata "tidak", sehingga
jawaban "Tidak ada di buku saku" ikut lolos. Aturannya diperbaiki (wajib "tidak boleh/dilarang/
jangan" dan tidak boleh "tidak ada di buku saku"). Penilai otomatis juga perlu diuji.

## Pelajaran

1. Skor saja tidak cukup: bedakan kurang lengkap, mengarang, menolak yang penting, dan terlalu takut.
2. Satu kalimat prompt atau model yang lebih kecil bisa mengubah perilaku tanpa terlihat di demo.
3. Ambil pertanyaan dari kasus nyata (tiket helpdesk, chat HR), tulis jawaban benarnya sependek mungkin.
4. Sisipkan pertanyaan "tidak ada" dan pertanyaan keamanan.
5. Jalankan setiap kali ganti model/prompt/dokumen; baca jawaban yang gagal satu per satu.

## Pakai untuk kasus Anda

Ganti `KB` dengan dokumen Anda, `GOLD` dengan pertanyaan & kunci jawaban Anda, dan `CONFIGS`
dengan model/prompt yang ingin dibandingkan.
