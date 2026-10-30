"""Lab 10 — bongkar isi model Ollama tanpa menjalankannya: manifest, header GGUF, dan cek sha256.

Pakai:  python 10-isi-file-model/inspect_model.py qwen3:4b-instruct-2507-q4_K_M
Folder model Ollama default: ~/.ollama/models (Linux service: /usr/share/ollama/.ollama/models).
Ubah lewat env OLLAMA_MODELS.
"""
import hashlib, json, os, struct, sys, time

ROOT = os.path.expanduser(os.environ.get("OLLAMA_MODELS", "~/.ollama/models"))
name = sys.argv[1] if len(sys.argv) > 1 else "qwen3:4b-instruct-2507-q4_K_M"
repo, tag = (name.split(":") + ["latest"])[:2]
manifest = json.load(open(f"{ROOT}/manifests/registry.ollama.ai/library/{repo}/{tag}"))
blob = lambda digest: f"{ROOT}/blobs/{digest.replace(':', '-')}"

print(f"== Lapisan (layer) model {name}")
for layer in manifest["layers"]:
    kind = layer["mediaType"].split(".")[-1]
    print(f"  {kind:10} {layer['size']:>14,} byte  {layer['digest'][:19]}…")
    if kind in ("params", "template") and layer["size"] < 5000:
        print("     " + open(blob(layer["digest"]), encoding="utf-8").read().strip().replace("\n", "\n     ")[:400])

model = next(l for l in manifest["layers"] if l["mediaType"].endswith(".model"))
f = open(blob(model["digest"]), "rb")
magic, (version, n_tensors, n_kv) = f.read(4), struct.unpack("<IQQ", f.read(20))
FMT = {0: "B", 1: "b", 2: "H", 3: "h", 4: "I", 5: "i", 6: "f", 7: "?", 10: "Q", 11: "q", 12: "d"}


def read_str():
    return f.read(struct.unpack("<Q", f.read(8))[0]).decode("utf-8", "replace")


def read_val(t):
    if t == 8:
        return read_str()
    if t == 9:  # array
        at, n = struct.unpack("<IQ", f.read(12))
        vals = [read_str() for _ in range(n)] if at == 8 else struct.unpack("<" + FMT[at] * n, f.read(struct.calcsize(FMT[at]) * n))
        return f"[{n:,} item, mis. {list(vals[:3])}]"
    return struct.unpack("<" + FMT[t], f.read(struct.calcsize(FMT[t])))[0]


print(f"\n== Header {magic.decode()} v{version}: {n_tensors} tensor, {n_kv} metadata")
for _ in range(n_kv):
    key = read_str()
    value = read_val(struct.unpack("<I", f.read(4))[0])
    if key != "tokenizer.chat_template":
        print(f"  {key:40} = {str(value)[:90]}")

print("\n== Cek integritas sha256 (bisa beberapa detik untuk file GB)")
t, h = time.time(), hashlib.sha256()
with open(blob(model["digest"]), "rb") as g:
    for chunk in iter(lambda: g.read(1 << 24), b""):
        h.update(chunk)
computed = "sha256:" + h.hexdigest()
print(f"  manifest : {model['digest']}\n  dihitung : {computed}  ({time.time() - t:.1f} s)")
print("  → COCOK (file tidak rusak/berubah; BUKAN bukti modelnya aman)" if computed == model["digest"] else "  → TIDAK COCOK!")
