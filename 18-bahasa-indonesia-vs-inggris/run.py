"""Lab 18 — Bahasa Indonesia vs Inggris: 12 soal identik dua bahasa, dinilai otomatis."""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lab import chat

MODELS = os.environ.get("MODELS", "qwen3:4b-instruct-2507-q4_K_M,qwen3.5:2b,qwen3:1.7b,qwen3:0.6b").split(",")
num = lambda a: re.sub(r"[.,\s]", "", a)
# (kunci, soal ID, soal EN, cek)
Q = [
 ("hitung", "Sebuah toko menjual 3 buku seharga 12.500 per buku dan 2 pulpen seharga 8.750 per pulpen. Berapa totalnya? Jawab angkanya saja.",
  "A shop sells 3 books at 12,500 each and 2 pens at 8,750 each. What is the total? Answer with the number only.", lambda a: "55000" in num(a)),
 ("persen", "Harga 240.000 didiskon 15%. Berapa harga setelah diskon? Jawab angkanya saja.",
  "A price of 240,000 gets a 15% discount. What is the price after the discount? Answer with the number only.", lambda a: "204000" in num(a)),
 ("logika", "Andi lebih tua dari Budi. Budi lebih tua dari Citra. Siapa yang paling muda? Jawab satu nama.",
  "Andi is older than Budi. Budi is older than Citra. Who is the youngest? Answer with one name.", lambda a: "citra" in a.lower() and "andi" not in a.lower()),
 ("hari", "Jika hari ini Jumat, 4 hari lagi hari apa? Jawab satu kata.", "If today is Friday, what day is it in 4 days? Answer with one word.",
  lambda a: "selasa" in a.lower() or "tuesday" in a.lower()),
 ("negasi", "Semua manajer wajib ikut rapat, kecuali yang sedang cuti. Rina manajer dan sedang cuti. Apakah Rina wajib ikut rapat? Jawab ya atau tidak.",
  "All managers must attend the meeting, except those on leave. Rina is a manager and is on leave. Must Rina attend? Answer yes or no.",
  lambda a: a.lower().strip(" .*").startswith(("tidak", "no"))),
 ("sentimen", "Klasifikasikan sentimen: 'Aplikasinya sih bagus, tapi CS-nya lelet banget, bikin kesel.' Jawab satu kata: positif/negatif/netral.",
  "Classify the sentiment: 'The app is fine, but customer service is painfully slow, so annoying.' Answer one word: positive/negative/neutral.",
  lambda a: "negatif" in a.lower() or "negative" in a.lower()),
 ("ekstraksi", "Dari teks: 'Rapat dipindah ke Kamis, 6 November 2026 pukul 14.00 di ruang Melati.' Jam berapa rapatnya? Jawab jamnya saja.",
  "From the text: 'The meeting moved to Thursday, 6 November 2026 at 14:00 in the Melati room.' What time is the meeting? Answer the time only.",
  lambda a: "14" in a or "2 pm" in a.lower() or "2:00" in a),
 ("geografi", "Apa ibu kota provinsi Sulawesi Selatan? Jawab satu kata.", "What is the capital of South Sulawesi province? Answer one word.",
  lambda a: "makassar" in a.lower()),
 ("idiom", "Apa arti ungkapan 'buah bibir'? Jawab singkat.", "What does the Indonesian idiom 'buah bibir' mean? Answer briefly.",
  lambda a: any(k in a.lower() for k in ["dibicarakan", "perbincangan", "pembicaraan", "talked about", "talk of", "gossip", "topic of conversation", "omongan", "gunjing"])),
 ("satuan", "1,5 jam ditambah 45 menit sama dengan berapa menit? Jawab angkanya saja.", "1.5 hours plus 45 minutes equals how many minutes? Answer with the number only.",
  lambda a: "135" in a),
 ("format", "Sebutkan 3 warna bendera Prancis, dipisah koma, huruf kecil semua.", "List the 3 colors of the French flag, comma separated, all lowercase.",
  lambda a: all(c in a.lower() for c in ["biru", "putih", "merah"]) or all(c in a.lower() for c in ["blue", "white", "red"])),
 ("kalimat", "Berapa jumlah kata dalam kalimat 'saya sedang belajar memasak nasi goreng'? Jawab angkanya saja.",
  "How many words are in the sentence 'I am learning to cook rice'? Answer with the number only.", lambda a: "6" in a and "7" not in a and "5" not in a),
]

for m in MODELS:
    score = {"ID": 0, "EN": 0}
    print(f"\n######## {m}")
    for key, qid, qen, check in Q:
        for lang, q in [("ID", qid), ("EN", qen)]:
            a = chat(m, [{"role": "user", "content": q}])["message"]["content"].split("</think>")[-1].strip()
            ok = bool(check(a))
            score[lang] += ok
            if not ok or os.environ.get("VERBOSE"):
                print(f"  [{key} {lang}] {'benar' if ok else 'SALAH'} → {a.replace(chr(10), ' ')[:120]}")
    print(f"  Indonesia {score['ID']}/{len(Q)} · Inggris {score['EN']}/{len(Q)}")
