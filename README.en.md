# LLM Lab — Hands-On Tests of Local AI, with Fictional Data

**Language:** [Bahasa Indonesia](README.md) · English

A series of small experiments you can run yourself to understand how AI models (LLMs) behave before
using them at work: prompt injection, prompt leakage, AI agents, model size, answer consistency, and
more.

Every result in this repo comes from a real run, not a made-up example. All data (companies,
documents, names, numbers, email addresses) is **fictional**. The images are renderings of the real
text output from the API, not application screenshots.

> The prompts, documents, and model answers inside the scripts are in Indonesian — that is part of
> what is being tested. Each lab's English README translates the key prompts and answers.

Created by [PT Alzizan Digital Solutions](https://alzizan.co.id).

## Setup (once)

1. Install [Ollama](https://ollama.com/download) (we used version 0.40.11).
2. Download the models used by the labs (all fit on a 6 GB GPU; without a GPU they still run, just slower):

   ```bash
   ollama pull qwen3:4b-instruct-2507-q4_K_M   # 2.5 GB
   ollama pull qwen3:4b                        # 2.5 GB
   ollama pull qwen3.5:2b                      # 2.7 GB
   ```

   Some labs need extra models; those are listed in the lab's README.
3. Python 3.10+. No `pip install` needed: the scripts use only the standard library.
4. Clone this repo and run from the root folder:

   ```bash
   git clone https://github.com/alzizan/llm-lab-walkthrough.git
   cd llm-lab-walkthrough
   python 01-prompt-injection-dokumen/run.py
   ```

Ollama on another machine? `OLLAMA_URL=http://server-address:11434 python ...`.
Change models: `MODELS="llama3.2:3b,qwen3:4b:think" python ...` (the `:think` suffix = thinking mode).

## Labs

| Lab | What is tested |
|---|---|
| [01 — Prompt injection through a document](01-prompt-injection-dokumen/README.en.md) | Can hidden text in a knowledge-base PDF make a chatbot ask for national ID numbers & passwords? |
| [02 — Extracting the system prompt](02-bongkar-prompt-sistem/README.en.md) | How safe are "secrets" stored in a chatbot's system prompt? |
| [03 — An AI agent fooled by a web page](03-agent-tertipu-halaman-web/README.en.md) | Can a web search result make an agent send confidential data out? |
| [04 — Model size](04-ukuran-model/README.en.md) | 0.6B to 4B: accuracy, speed, and GPU memory on 10 questions with exact answers |
| [05 — Answer consistency](05-konsistensi-jawaban/README.en.md) | Same question, different answers? Temperature, rephrasing, and "consistent but wrong" |
| [06 — AI doing arithmetic](06-ai-berhitung/README.en.md) | Summing 30 transactions itself vs writing SQL and letting the database compute |
| [07 — RAG retrieves the wrong document](07-rag-salah-ambil/README.en.md) | The document exists, the answer is still wrong: chunking, similarity ranking, and revoked documents |
| [08 — Daring to say "I don't know"](08-berani-tidak-tahu/README.en.md) | Questions that are "almost" in the document, strict prompts, and assumptions that still slip through |
| [09 — 20 golden questions](09-pertanyaan-emas/README.en.md) | Automatic evaluation before changing a model/prompt: same score, different kinds of mistakes |
| [10 — Inside a model file](10-isi-file-model/README.en.md) | Taking a model file apart (GGUF, template, license, sha256) and why pickle is dangerous |
| [11 — Token cost vs GPU](11-biaya-token-vs-gpu/README.en.md) | Measure tokens, time, and GPU power, then compare with a cloud API bill |
| [12 — Personal data in prompts](12-data-pribadi-di-prompt/README.en.md) | Regex + local-model filters before a prompt leaves, and what still gets through (UU PDP Article 56) |
| [13 — AI citing legal articles](13-ai-mengutip-pasal/README.en.md) | UU PDP questions without documents vs with the official article text: made-up article numbers that sound convincing |
| [14 — AI without a GPU](14-ai-tanpa-gpu/README.en.md) | The same model on GPU vs CPU only: writing speed, time to read a long document |
| [15 — Semantic search](15-pencarian-makna/README.en.md) | Keywords vs embeddings: "cuti melahirkan" finds "bersalin" and "maternity leave", plus the weaknesses |
| [16 — AI forgets page 50](16-ai-lupa-halaman-50/README.en.md) | An 80-page document: default context, truncated document, larger context, and RAG |
| [17 — 4-bit quantization](17-kuantisasi-4bit/README.en.md) | The same model in 4-bit vs 8-bit: 45 questions, GPU memory, and small models' arithmetic |
| [18 — Indonesian vs English](18-bahasa-indonesia-vs-inggris/README.en.md) | 12 identical questions in two languages to 4 local models |
| [19 — Invoice to JSON](19-invoice-ke-json/README.en.md) | Extracting invoice text to schema-bound JSON, then business-rule validation catches a miscalculated invoice |
| [20 — Shadow AI](20-shadow-ai/README.en.md) | Reading office proxy/DNS logs: who uses public chatbots, where, and large uploads (no AI model) |

## Notes

- Results may differ on your machine (model version, GPU, Ollama version). Even at temperature 0,
  answers can differ between runs. Run several times.
- The security labs here are for testing systems **you own**.

## About

We build Enterprise Data Platform: catalog, governance, lakehouse, and AI that runs 100% on-premise,
with AI context filtered by access rights & masking.

- Free trial: https://alzizan.co.id/register
- Demo videos: https://www.youtube.com/@AlzizanDigitalSolutions

Content licensed under [CC BY 4.0](LICENSE).
