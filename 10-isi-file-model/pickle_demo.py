"""Demo TIDAK berbahaya: file pickle yang menjalankan print() saat dibuka. Jangan pernah pickle.load file dari sumber tak dikenal."""
import pickle, io
class Model:  # file "model" palsu: isinya pickle, bukan sekadar angka
    def __reduce__(self):
        return (print, ("!!! KODE INI JALAN SAAT FILE MODEL DIBUKA (bisa saja: curl … | sh) !!!",))
data = pickle.dumps(Model())
print("ukuran file:", len(data), "byte")
print(">>> pickle.load(file_model)")
pickle.loads(data)
