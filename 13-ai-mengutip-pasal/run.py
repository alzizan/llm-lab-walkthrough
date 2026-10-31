"""Lab 13 — AI mengutip pasal UU PDP: tanpa dokumen vs dengan kutipan teks resmi."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lab import ask, models

# Kutipan pasal UU 27/2022 (dicek ke pasal.id, 31 Okt 2026). Untuk pemakaian nyata, ambil teks resmi.
DOC = """[UU 27/2022 tentang Pelindungan Data Pribadi — kutipan]
Pasal 4 (1) Data Pribadi terdiri atas Data Pribadi yang bersifat spesifik dan Data Pribadi yang bersifat umum. (2) Data Pribadi yang bersifat spesifik meliputi: a. data dan informasi kesehatan; b. data biometrik; c. data genetika; d. catatan kejahatan; e. data anak; f. data keuangan pribadi; dan/atau g. data lainnya sesuai dengan ketentuan peraturan perundang-undangan.
Pasal 46 (1) Dalam hal terjadi kegagalan Pelindungan Data Pribadi, Pengendali Data Pribadi wajib menyampaikan pemberitahuan secara tertulis paling lambat 3 x 24 (tiga kali dua puluh empat) jam kepada: a. Subjek Data Pribadi; dan b. lembaga.
Pasal 53 (1) Pengendali Data Pribadi dan Prosesor Data Pribadi wajib menunjuk pejabat atau petugas yang melaksanakan fungsi Pelindungan Data Pribadi dalam hal: a. pemrosesan Data Pribadi untuk kepentingan pelayanan publik; b. kegiatan inti Pengendali Data Pribadi memiliki sifat, ruang lingkup, dan/atau tujuan yang memerlukan pemantauan secara teratur dan sistematis atas Data Pribadi dengan skala besar; dan c. kegiatan inti Pengendali Data Pribadi terdiri dari pemrosesan Data Pribadi dalam skala besar untuk Data Pribadi yang bersifat spesifik dan/atau Data Pribadi yang berkaitan dengan tindak pidana.
Pasal 57 (3) Sanksi administratif berupa denda administratif paling tinggi 2 (dua) persen dari pendapatan tahunan atau penerimaan tahunan terhadap variabel pelanggaran.
Pasal 67 (1) Setiap Orang yang dengan sengaja dan melawan hukum memperoleh atau mengumpulkan Data Pribadi yang bukan miliknya ... dipidana dengan pidana penjara paling lama 5 (lima) tahun dan/atau pidana denda paling banyak Rp5.000.000.000,00. (2) Setiap Orang yang dengan sengaja dan melawan hukum mengungkapkan Data Pribadi yang bukan miliknya dipidana dengan pidana penjara paling lama 4 (empat) tahun dan/atau pidana denda paling banyak Rp4.000.000.000,00. (3) ... menggunakan Data Pribadi yang bukan miliknya dipidana dengan pidana penjara paling lama 5 (lima) tahun dan/atau pidana denda paling banyak Rp5.000.000.000,00."""
QS = [
 ("notif", "Menurut UU PDP (UU 27/2022), berapa batas waktu pengendali data memberi tahu kegagalan pelindungan data pribadi? Sebutkan pasalnya."),
 ("pidana", "Menurut UU PDP, apa ancaman pidana maksimal bagi orang yang dengan sengaja dan melawan hukum mengungkapkan data pribadi milik orang lain? Sebutkan pasal dan ayatnya."),
 ("spesifik", "Pasal berapa di UU PDP yang mengatur data pribadi bersifat spesifik, dan apa saja jenisnya?"),
 ("denda", "Berapa denda administratif paling tinggi di UU PDP? Sebutkan pasalnya."),
 ("dpo", "Pasal berapa di UU PDP yang mewajibkan penunjukan pejabat pelindungan data pribadi (DPO)?"),
 ("isi46", "Apa isi Pasal 46 UU PDP?"),
]
SYS_DOC = ("Jawab HANYA berdasarkan kutipan undang-undang berikut. Sebutkan nomor pasal dan ayat. "
           "Jika tidak ada di kutipan, jawab: \"Tidak ada di kutipan.\" Bahasa Indonesia, singkat.\n\n" + DOC)

for model, think in models():
    print(f"\n######## {model}{' (thinking)' if think else ''}")
    for mode, system in [("tanpa dokumen", "Jawab singkat dalam Bahasa Indonesia."), ("dengan kutipan", SYS_DOC)]:
        print(f"--- {mode}")
        for key, q in QS:
            answer, _ = ask(model, system, q, think=think)
            print(f"  [{key}] {q}\n     → {answer.replace(chr(10), ' ')[:300]}")
