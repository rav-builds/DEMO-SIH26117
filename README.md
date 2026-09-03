# Sovereign AI Workbench (SIH 2026 - Problem Statement SIH26117)

A modular, sovereign, and model-agnostic AI execution platform developed for the **Smart India Hackathon 2026 (SIH26117)**. Designed for defense, government, and high-security enterprise environments, the workbench operates completely air-gapped with zero external telemetry and zero data leakage.

The platform provides autonomous multi-step agents, Reciprocal Rank Fusion Hybrid RAG, multimodal computer vision with automated image compression, isolated Docker sandbox code execution, tamper-evident cryptographic audit trails, and a tactical command center frontend with native Server-Sent Events (SSE) streaming.

---

## Key Platform Capabilities

- **Local & Sovereign Intelligence:** 100% air-gapped execution on local hardware (consumer CPUs, Apple Silicon MacBooks, or dedicated GPU servers).
- **Model-Agnostic Serving Contract:** Zero vendor lock-in. Powered by **Ornith-1.5-9B** (`ornith-ai/Ornith-1.5-9B`) with runtime switching across **Ollama (GGUF)**, **MLX (Apple Silicon)**, and **vLLM (NVIDIA GPU)** without application code changes.
- **Autonomous Agent Graph:** Dynamic multi-step reasoning loop with deterministic tool dispatch (`calculator`, `document_tool`, `file_tool`, `sandbox`), native XML tool-calling parser, and `<think>` reasoning trace extraction.
- **Hybrid RAG Pipeline:** Semantic vector search (Qdrant) fused with BM25 keyword matching via Reciprocal Rank Fusion (RRF, $k=60$) and batched embedding generation (batch size 32).
- **Optimized Multimodal Vision & OCR:** Pillow-powered pre-encoding pipeline resizing images to max 1024px and compressing to JPEG (quality 75) for 60–80% payload reduction. Non-blocking Tesseract OCR and PyMuPDF text/image extraction.
- **Isolated Docker Code Sandbox:** Hardened container execution with strict boundaries: `--memory=256m`, `--network=none`, `--rm`, `--read-only`, and `--pids-limit=64`.
- **Tamper-Evident Audit Logging:** Append-only JSONL cryptographic trail (`data/audit.jsonl`) recording SHA-256 prompt hashes, tool executions, and outbound egress firewall compliance.
- **Reactive Command Center UI:** React 19 + TypeScript frontend with native SSE `ReadableStream` token parsing, collapsible reasoning drawers, live Docker execution console, and air-gap telemetry ribbons.

---

## Foundation Model: Ornith-1.5-9B

- **Architecture:** Dense ~9B parameter hybrid model (~8.95B language + ~0.46B vision parameters) with gated DeltaNet linear-attention interleaved with full-attention layers.
- **Native Multimodal Support:** Includes a vision tower accessible via `mmproj` (`mmproj-Ornith-1.5-9B-f16.gguf`) for visual reasoning, diagram QA, and document layout analysis.
- **Reasoning & Tool Calling:** Built-in XML tool-calling parser (`qwen3_xml`) and thinking trace reasoning parser (`qwen3`).
- **Context Window:** Up to 262,144 tokens.
- **Hardware Profiles:** Deployable quantized on CPU laptops (`Q4_K_M`, `Q5_K_M`, `Q8_0`), unified memory on Apple Silicon (MLX), or unquantized on GPU servers (vLLM).

---

## Project Architecture

```text
SIH 2026 (DEMO-SIH26117)/
├── apps/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── agent/                 # Autonomous agent orchestration
│   │   │   │   ├── events.py          # Agent streaming event models
│   │   │   │   ├── graph.py           # Multi-step reasoning & tool execution graph
│   │   │   │   ├── router.py          # Intent & pipeline router
│   │   │   │   └── state.py           # Agent memory & step state
│   │   │   ├── api/                   # REST & SSE API layer
│   │   │   │   ├── routes/
│   │   │   │   │   ├── health.py      # Health check endpoint (/api/health)
│   │   │   │   │   ├── knowledge.py   # RAG upload, query & collection stats
│   │   │   │   │   ├── security.py    # Audit trail & egress status
│   │   │   │   │   └── tasks.py       # Task dispatch, polling & SSE stream
│   │   │   │   └── router.py          # Central route registry
│   │   │   ├── config.py              # Dynamic settings & endpoint resolver
│   │   │   ├── main.py                # FastAPI entrypoint, CORS & lifespan
│   │   │   ├── models/                # Model-agnostic client layer
│   │   │   │   ├── base.py            # BaseModelClient, ChatMessage, GenerationRequest
│   │   │   │   ├── local_client.py    # Universal OpenAI-compatible pooling client
│   │   │   │   ├── ollama.py          # Persistent socket-safe Ollama lifecycle client
│   │   │   │   ├── registry.py        # Role-based model registry & client factory
│   │   │   │   └── vision.py          # Pillow-optimized multimodal serializer
│   │   │   ├── rag/                   # Hybrid RAG pipeline
│   │   │   │   ├── embeddings.py      # Batched embedding generator (batch size 32)
│   │   │   │   ├── ingest.py          # Async document chunking & Qdrant ingestion
│   │   │   │   ├── retriever.py       # Hybrid Vector + BM25 Reciprocal Rank Fusion
│   │   │   │   └── vector_store.py    # Qdrant client & collection manager
│   │   │   ├── sandbox/               # Isolated code execution
│   │   │   │   ├── docker_runner.py   # Async subprocess Docker container runner
│   │   │   │   └── limits.py          # Strict resource limits (--memory=256m, --network=none)
│   │   │   ├── schemas/               # Pydantic v2 DTOs with memory safety constraints
│   │   │   │   ├── events.py          # SSE streaming event schemas (Token, Reasoning, Tool)
│   │   │   │   ├── response.py        # Standardized APIResponse envelope
│   │   │   │   └── tasks.py           # TaskRequest, TaskResponse, TaskStatus, TaskType
│   │   │   ├── security/              # Zero-Trust security & auditability
│   │   │   │   ├── audit.py           # Append-only cryptographic JSONL logger
│   │   │   │   ├── network.py         # Outbound egress firewall guard
│   │   │   │   └── policy.py          # Role-based action & tool authorization
│   │   │   ├── tools/                 # Agent tools
│   │   │   │   ├── calculator.py      # Deterministic math tool (ast + Decimal, no eval)
│   │   │   │   ├── document_tool.py   # PDF / DOCX / TXT excerpt search
│   │   │   │   └── file_tool.py       # Sandboxed file reader and writer
│   │   │   └── vision/                # Computer vision & OCR
│   │   │       ├── image.py           # Async image resizing & contrast enhancement
│   │   │       ├── ocr.py             # Tesseract OCR engine with PyMuPDF fallback
│   │   │       └── pdf.py             # Async PyMuPDF renderer and metadata parser
│   │   ├── Dockerfile
│   │   └── requirements.txt           # Pinned backend dependencies
│   └── frontend/                      # React 19 + TypeScript + Vite UI
│       ├── src/
│       │   ├── App.tsx                # Tactical workbench with native SSE stream reader
│       │   ├── index.css              # Dark sovereign command center design system
│       │   └── main.tsx               # Root entrypoint
│       ├── index.html
│       ├── package.json
│       ├── tsconfig.json
│       └── vite.config.ts             # Dev server with backend proxy to :8000
├── configs/
│   └── models.yaml                    # Serving backends, model catalog & hardware specs
├── data/                              # Local persistence (tasks.jsonl, audit.jsonl)
├── docs/                              # Architecture, security, and demo specs
├── .env.example                       # Centralized environment template with MODEL_BACKEND switch
├── brain.md                           # System blueprint and architectural log
├── docker-compose.yml                 # Multi-service container orchestration
└── README.md                          # Project documentation
```

---

## Local Serving Setup: Choose Your Engine

Teammates can run on different hardware without modifying application code. Set `MODEL_BACKEND` in your `.env` file to match your machine:

```env
# Choose: 'ollama' (CPU/GGUF) | 'mlx' (Apple Silicon) | 'vllm' (GPU Server)
MODEL_BACKEND="ollama"
```

---

### Path 1: GGUF / Ollama (Universal CPU & Low-VRAM Laptops)

Recommended for team members running on Windows, Linux, or CPU-only laptops without a dedicated GPU.

#### 1. Launch with Ollama
```bash
# Pull and start the quantized Ornith-1.5-9B GGUF model
ollama run ornith-1.5:9b-q4_k_m
```

#### 2. (Optional) Enable Vision with `mmproj`
To enable multimodal vision in Ollama:
1. Download `Ornith-1.5-9B-Q4_K_M.gguf` and `mmproj-Ornith-1.5-9B-f16.gguf`.
2. Create a `Modelfile`:
   ```dockerfile
   FROM ./Ornith-1.5-9B-Q4_K_M.gguf
   ADAPTER ./mmproj-Ornith-1.5-9B-f16.gguf
   ```
3. Build the model:
   ```bash
   ollama create ornith-1.5:9b-q4_k_m -f Modelfile
   ```

#### 3. Verify Ollama Endpoint
```bash
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ornith-1.5:9b-q4_k_m",
    "messages": [
      {"role": "user", "content": "Hello! Explain what 14 * 16 is."}
    ]
  }'
```

---

### Path 2: MLX (Apple Silicon MacBooks)

Recommended for team members running on Apple Silicon (M1/M2/M3/M4) for unified memory acceleration.

#### Option A: Via LM Studio
1. Open **LM Studio** on macOS.
2. Search and download `ornith-ai/Ornith-1.5-9B-MLX`.
3. Navigate to the **Local Server** tab and click **Start Server** on port `1234`.

#### Option B: Via `mlx-lm` CLI
```bash
pip install mlx-lm
python -m mlx_lm.server --model "ornith-ai/Ornith-1.5-9B-MLX" --port 8080
```

#### Verify MLX Endpoint
```bash
curl http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ornith-ai/Ornith-1.5-9B-MLX",
    "messages": [
      {"role": "user", "content": "Hello! Explain what 14 * 16 is."}
    ]
  }'
```

---

### Path 3: vLLM (Dedicated GPU Server)

For high-throughput serving on an NVIDIA GPU server with concurrency optimizations:
```bash
vllm serve "ornith-ai/Ornith-1.5-9B" \
  --port 8000 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_xml \
  --reasoning-parser qwen3 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.90 \
  --enable-chunked-prefill
```

---

## Quickstart Guide

### 1. Configure Environment
```bash
cp .env.example .env
```
Edit `.env` to select your backend (`MODEL_BACKEND="ollama"`, `"mlx"`, or `"vllm"`).

### 2. Set Up & Run the Backend
```bash
cd apps/backend
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- **Interactive API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Root Status Endpoint:** `GET http://localhost:8000/`
- **Health Check Endpoint:** `GET http://localhost:8000/api/health`

### 3. Set Up & Run the Frontend
In a separate terminal:
```bash
cd apps/frontend
npm install
npm run dev
```

- **Command Center UI:** [http://localhost:5173](http://localhost:5173)

---

## Primary API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Root status, app version, active backend, and active model |
| `GET` | `/api/health` | Service health status check |
| `POST` | `/api/tasks` | Submit task for background execution (`general`, `rag`, `agent`, `vision`, `sandbox`) |
| `GET` | `/api/tasks` | List recent tasks with optional status filter |
| `GET` | `/api/tasks/{task_id}` | Fetch task status, execution duration, and structured output |
| `DELETE` | `/api/tasks/{task_id}` | Cancel pending or running task |
| `GET` | `/api/tasks/{task_id}/stream` | Server-Sent Events (SSE) stream for real-time tokens and reasoning traces |
| `POST` | `/api/knowledge/ingest` | Upload and ingest document (`.pdf`, `.docx`, `.txt`) into Qdrant |
| `POST` | `/api/knowledge/query` | Perform hybrid vector + BM25 search over ingested documents |
| `GET` | `/api/knowledge/status` | Vector collection statistics and points count |
| `GET` | `/api/security/audit` | Query cryptographic append-only audit trail (`data/audit.jsonl`) |
| `GET` | `/api/security/status` | Air-gap verification and outbound network egress compliance status |

---

## Tech Stack Summary

| Layer | Technologies |
| :--- | :--- |
| **Backend Framework** | Python 3.10+, FastAPI, Uvicorn, Pydantic v2, Pydantic-Settings |
| **Model Inference** | HTTP connection pooling, SSE streaming, `<think>` parser, `httpx` |
| **Local Foundation Model** | `ornith-ai/Ornith-1.5-9B` (Ollama GGUF / MLX / vLLM) |
| **Vector Store & Retrieval** | Qdrant, `rank-bm25` (BM25Okapi), Reciprocal Rank Fusion |
| **Document & Vision** | Pillow, PyMuPDF (`fitz`), `python-docx`, Tesseract OCR |
| **Security & Auditing** | `aiofiles`, SHA-256 cryptographic hashing, egress firewall guard |
| **Sandbox Execution** | Docker CLI subprocess runner with memory & network isolation limits |
| **Frontend UI** | React 19, TypeScript, Vite, Vanilla CSS design system, Lucide Icons |
