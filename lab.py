"""Helper kecil untuk semua lab: memanggil Ollama lewat HTTP (stdlib saja, tanpa pip install)."""
import json, os, time, urllib.request

OLLAMA = os.environ.get("OLLAMA_URL", "http://localhost:11434")


def chat(model, messages, temp=0, think=False, tools=None, **opts):
    body = {"model": model, "messages": messages, "stream": False, "think": think,
            "options": {"temperature": temp, **opts}}
    if tools:
        body["tools"] = tools
    t = time.time()
    req = urllib.request.Request(OLLAMA + "/api/chat", json.dumps(body).encode(), {"Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req, timeout=900))
    d["secs"] = round(time.time() - t, 1)
    return d


def ask(model, system, user, **kw):
    """Satu pertanyaan, satu jawaban. Mengembalikan (teks jawaban, respons mentah)."""
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
    d = chat(model, msgs, **kw)
    return d["message"]["content"].split("</think>")[-1].strip(), d


def embed(model, texts):
    req = urllib.request.Request(OLLAMA + "/api/embed", json.dumps({"model": model, "input": texts}).encode(),
                                 {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=300))["embeddings"]


# Model default semua lab. Ganti lewat env MODELS="model1,model2:think,..." (":think" = thinking mode ON).
def models(default="qwen3:4b-instruct-2507-q4_K_M,qwen3:4b:think,qwen3.5:2b"):
    out = []
    for m in os.environ.get("MODELS", default).split(","):
        think = m.endswith(":think")
        out.append((m[: -len(":think")] if think else m, think))
    return out
