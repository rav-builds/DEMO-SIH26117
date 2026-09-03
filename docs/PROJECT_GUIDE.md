# PROJECT GUIDE — Sovereign AI Workbench
## Master Team Reference · PS 26117 · SIH

> **READ THIS DOCUMENT BEFORE WRITING A SINGLE LINE OF CODE.**
> It is the single source of truth for what we are building, how we are building it, who owns what, and what counts as "done."

---

## Table of Contents

1. [Scope Lock — PS 26117](#1-scope-lock--ps-26117)
2. [Project Overview](#2-project-overview)
3. [What the System Is](#3-what-the-system-is)
4. [Required PS Capabilities](#4-required-ps-capabilities)
5. [Primary Prototype Workflows](#5-primary-prototype-workflows)
6. [System Architecture](#6-system-architecture)
7. [Repository Structure](#7-repository-structure)
8. [Approved Technical Direction](#8-approved-technical-direction)
9. [Hardware Strategy](#9-hardware-strategy)
10. [Development Environment vs Final Runtime](#10-development-environment-vs-final-runtime)
11. [Team Responsibilities](#11-team-responsibilities)
12. [Parallel Development](#12-parallel-development)
13. [API Contract Discipline](#13-api-contract-discipline)
14. [Shared Schema Ownership](#14-shared-schema-ownership)
15. [Agent Event Contract](#15-agent-event-contract)
16. [Git Workflow](#16-git-workflow)
17. [Integration Checkpoints](#17-integration-checkpoints)
18. [Feature Status System](#18-feature-status-system)
19. [Development Sequence](#19-development-sequence)
20. [Testing Rule](#20-testing-rule)
21. [Failure Handling](#21-failure-handling)
22. [Security Rules](#22-security-rules)
23. [Network / Sovereignty Proof](#23-network--sovereignty-proof)
24. [Data Rules](#24-data-rules)
25. [What NOT to Build](#25-what-not-to-build)
26. [Claims Discipline](#26-claims-discipline)
27. [Frontend Development Rule](#27-frontend-development-rule)
28. [Backend Development Rule](#28-backend-development-rule)
29. [AI / Model Development Rule](#29-ai--model-development-rule)
30. [RAG Development Rule](#30-rag-development-rule)
31. [Sandbox Development Rule](#31-sandbox-development-rule)
32. [Document Generation Rule](#32-document-generation-rule)
33. [Definition of Done](#33-definition-of-done)
34. [Demo Readiness Checklist](#34-demo-readiness-checklist)
35. [Demo Failure Plan](#35-demo-failure-plan)
36. [Beginner Glossary](#36-beginner-glossary)
37. [Quick Start for a New Team Member](#37-quick-start-for-a-new-team-member)
38. [Team Communication Rule](#38-team-communication-rule)
39. [Final Project Principle](#39-final-project-principle)

---

## 1. Scope Lock — PS 26117

> [!IMPORTANT]
> This is the most important section. Read it first. Refer back to it every time you want to add something new.

### What We Are Building

This repository implements **SIH Problem Statement PS 26117**:

> **"Sovereign On-Premise Agentic AI Workbench using Open-Weight Multimodal LLMs for Confidential Industrial Work."**

| Field | Value |
|---|---|
| **Problem Statement** | PS 26117 |
| **Target Organization** | Mangalore Refinery and Petrochemicals Limited (MRPL) |
| **Category** | Software |
| **Theme** | Smart Automation |
| **Event** | Smart India Hackathon (SIH) |

### The Non-Negotiable Rule

> [!CAUTION]
> **No team member should add a feature, technology, service, integration, workflow, or product claim simply because it seems useful, impressive, modern, or technically interesting.**

If something is **not required or explicitly supported** by the PS or the approved project briefing, it must **not** be added without full team discussion.

### Priority Order

```
1. Official PS requirements
2. Approved project briefing
3. Implementation decisions necessary to satisfy those requirements
4. NOTHING ELSE unless explicitly approved by the team
```

### What We Prioritize

The prototype must prioritize:

- Working functionality
- Correctness
- Local execution
- Demonstrable sovereignty
- Reliable end-to-end workflows
- Clear evidence

...over unnecessary feature count, impressive-sounding technology lists, or anything not required by the PS.

---

## 2. Project Overview

### The Problem (Beginner-Friendly)

Organizations like MRPL deal with highly sensitive, confidential work every day. This includes:

- Approval notes and board presentations
- Engineering calculations and internal code
- Scanned drawings and inspection reports
- Financial evaluations and vendor negotiations
- Tenders and unreleased designs
- Internal correspondence and confidential business strategy

This creates a painful conflict:

| Path | Problem |
|---|---|
| **Path A — Manual** | Work remains slow, dependent on availability of experts, error-prone |
| **Path B — Cloud AI** | Employees use public AI tools (ChatGPT, Claude, Gemini) and potentially expose confidential data to external servers |

Neither path is acceptable for genuinely confidential industrial work.

### Our Solution

A **self-hosted, on-premise, air-gapped, multi-model, agentic AI workbench** using open-weight multimodal models.

```
CORE PRINCIPLE:

  BRING THE AI TO THE DATA.
  DO NOT SEND CONFIDENTIAL DATA TO PUBLIC AI.
```

Everything runs inside the organization's own controlled infrastructure. No confidential document ever leaves the local network.

---

## 3. What the System Is

### It Is NOT

```
User → chatbot → answer
```

That is a simple chatbot. We are not building that.

### It IS

A **local AI workbench** that can:

- Understand different types of tasks (document, code, vision, reasoning)
- Select the appropriate local model for each task type
- Plan multi-step work automatically
- Use local tools (file I/O, document generation, code execution)
- Retrieve relevant local knowledge (SOPs, manuals, past documents)
- Process scanned and image-based content locally
- Generate real, downloadable output files
- Execute code safely in an isolated sandbox
- Provide a visible trace of what the agent actually did
- Provide evidence that no external network calls were made during the workflow

The system demonstrates **confidential AI processing inside controlled infrastructure**.

---

## 4. Required PS Capabilities

### 4.1 Multi-Model Backend

The system must support **multiple open-weight models** for different task types.

**Conceptual model pool:**

| Role | Purpose |
|---|---|
| Reasoning Model | Document analysis, summarization, approval note drafting |
| Coding Model | Code generation, code reasoning |
| Vision / OCR Model | Scanned PDFs, handwritten notes, images |

The architecture must allow additional models to be added later without restructuring.

---

### 4.2 Automatic Model Selection

> [!IMPORTANT]
> The router must **actually select and use** the corresponding model. Do NOT build a keyword-based UI demonstration. Do NOT show routing events for models that were not actually used.

The system must demonstrate task-based model selection across **at least two different task types**.

**Example:**
```
Document / vision task  →  Vision-capable workflow / model
Coding task             →  Coding model
```

---

### 4.3 Agentic Behaviour

The system must perform **multi-step work**, not just a single prompt → response.

**Conceptual flow:**
```
Task received
  → Plan created
  → Model selected
  → Information retrieved
  → Tools used
  → Result processed
  → Continue / iterate if needed
  → Final output produced
```

The system must demonstrate actual planning, tool use, and iteration. It must **not** simply display a scripted or hardcoded trace.

---

### 4.4 Local Tools

The system should support local tool execution:

- File read / write
- Sandboxed code execution
- Spreadsheet work
- Internal document search
- Document generation (Word, Excel, PowerPoint)

---

### 4.5 Multimodal Understanding

The system should support local processing of:

- Scanned PDFs
- Handwritten notes
- Engineering drawings
- Photographs and images

...through **local** OCR / vision capabilities.

> [!WARNING]
> Do not overclaim P&ID or complex engineering drawing understanding. For the prototype, prioritize **achievable** scanned-document and inspection-report understanding.

---

### 4.6 Real Outputs

The system should produce **actual output files**, not simulated UI cards.

| Output Type | Example |
|---|---|
| Word document | `Approval_Note.docx` |
| Excel spreadsheet | `Calculation.xlsx` |
| PowerPoint | `Report.pptx` |
| Working code | `solution.py` |
| Calculation with steps | Inline text result |

---

### 4.7 Local Knowledge Base

The system should use a **local knowledge base** containing appropriate sample/public documents:

- Standard Operating Procedures (SOPs)
- Equipment manuals
- Past correspondence (sample/synthetic)

Retrieval must happen **locally**. No external database or search API.

---

## 5. Primary Prototype Workflows

These are the workflows that define the prototype. Everything else is secondary.

---

### Workflow 1 — Inspection Report → Approval Note (Hero Workflow)

```
Scanned inspection report (PDF/image)
          ↓
   Local OCR / Vision
          ↓
   Extract findings
          ↓
   Search local knowledge base
          ↓
   Retrieve relevant SOP / manual
          ↓
   Local reasoning model
          ↓
   Draft approval note
          ↓
   Generate Word document
          ↓
   Return  Approval_Note.docx
```

This is the **primary demonstration workflow**. It should run as one continuous, real pipeline.

---

### Workflow 2 — Coding Agent

```
Coding request
      ↓
Task classification / routing
      ↓
Coding model selected
      ↓
Code generated
      ↓
Code sent to Docker sandbox
      ↓
Code executed inside sandbox
      ↓
Result verified
      ↓
Result returned to user
```

> [!CAUTION]
> Generated code must **NOT** execute directly on the host system. Use the Docker sandbox exclusively.

---

### Workflow 3 — Multimodal Task

```
Input: image / scanned document
          ↓
Local vision / OCR processing
          ↓
Extract / understand relevant information
          ↓
Return useful result
```

---

### Workflow 4 — Model Routing Demonstration

Demonstrate at least **two** task types using **actually different** models or workflows, proving that the router makes real decisions based on task type.

---

### Workflow 5 — Sovereignty Proof

Show **visible evidence** that the system is not making external network calls during a demonstrated workflow.

> [!CAUTION]
> Do not merely display `"0 external calls"` unless the system actually measures and proves it. The evidence must be real.

---

## 6. System Architecture

```
+----------------------------------------------------------+
|                          USER                            |
+------------------------+---------------------------------+
                         |
+------------------------v---------------------------------+
|            UI / CHAT / TASK DASHBOARD                   |
|                  (apps/frontend/)                        |
+------------------------+---------------------------------+
                         |  HTTP / REST / SSE
+------------------------v---------------------------------+
|                    BACKEND API                           |
|               (FastAPI -- apps/backend/)                 |
+------------------------+---------------------------------+
                         |
+------------------------v---------------------------------+
|           ORCHESTRATOR / AGENT LAYER                    |
|  +--------------------------------------------------+   |
|  | Task Planner  |  Model Router  |  Tool Executor  |   |
|  +--------------------------------------------------+   |
+--------+---------------------+-------------+------------+
         |                     |             |
+--------v-------+ +-----------v----+ +------v------------------+
|   MODEL POOL   | | LOCAL TOOL     | | LOCAL KNOWLEDGE BASE    |
|                | | LAYER          | |                         |
| Reasoning      | |                | | Vector DB / RAG         |
| Model          | | File Read/Write| | SOPs                    |
|                | | Doc Generation | | Manuals                 |
| Coding         | | Spreadsheet    | | Past Correspondence     |
| Model          | | Docker Code    | |                         |
|                | | Sandbox        | |                         |
| Vision / OCR   | |                | |                         |
| Model          | +----------------+ +-------------------------+
+----------------+

All processing remains inside the controlled local environment.
No confidential data leaves this boundary.
```

### Layer Responsibilities

| Layer | Responsibility |
|---|---|
| **UI / Task Dashboard** | Accept user input (text, file upload), display task status, agent trace, model routing events, results, output downloads, network evidence |
| **Backend API** | Expose REST endpoints; receive tasks; return status, events, and results; coordinate all backend modules |
| **Orchestrator / Agent** | Receive task; create plan; select model; invoke tools; iterate; produce final output |
| **Task Planner** | Break task into steps; determine what tools/models are needed |
| **Model Router** | Map task type to the correct local model |
| **Tool Executor** | Run individual local tools in a controlled way; return results to agent |
| **Model Pool** | Serve local open-weight models; receive prompts; return completions |
| **Local Tool Layer** | Implement concrete tool actions (file I/O, doc generation, sandbox communication) |
| **Local Knowledge Base** | Index and retrieve relevant local documents using vector similarity |

---

## 7. Repository Structure

```
sovereign-ai-workbench/
|
+-- apps/
|   +-- backend/
|   |   +-- Dockerfile
|   |   +-- requirements.txt
|   |   +-- app/
|   |   |   +-- main.py           <- FastAPI application entry point
|   |   |   +-- config.py         <- Settings / environment config
|   |   |   +-- api/              <- API routes and backend communication
|   |   |   |   +-- router.py
|   |   |   |   +-- routes/
|   |   |   |       +-- health.py
|   |   |   +-- agent/            <- Agent orchestration, state, planning, routing, events
|   |   |   +-- models/           <- Local model interfaces, registry, model providers
|   |   |   +-- rag/              <- Knowledge ingestion, embeddings, vector storage, retrieval
|   |   |   +-- vision/           <- PDF/image/OCR/vision processing
|   |   |   +-- tools/            <- File tools, document generation, calculations
|   |   |   +-- sandbox/          <- Isolated code execution interface
|   |   |   +-- security/         <- Network monitoring, sovereignty evidence, policy
|   |   |   +-- schemas/          <- SHARED request/response/event data structures
|   |   +-- tests/
|   |
|   +-- frontend/
|       +-- Dockerfile
|       +-- package.json
|       +-- src/
|           +-- App.tsx           <- Root component (React/TypeScript)
|           +-- components/       <- UI components
|           +-- hooks/            <- Custom React hooks
|           +-- pages/            <- Page-level components
|           +-- services/         <- API communication layer
|           +-- types/            <- Shared TypeScript types
|
+-- configs/                      <- Application configuration files
+-- data/
|   +-- raw/                      <- Raw / public demo material
|   +-- knowledge/                <- Local knowledge-base documents (SOPs, manuals)
|   +-- uploads/                  <- User-uploaded files (runtime)
|   +-- processed/                <- Intermediate processing data
|   +-- outputs/                  <- Generated files (DOCX, XLSX, etc.)
|
+-- docker/                       <- Sandbox Docker configuration
+-- docs/                         <- Project documentation
|   +-- PROJECT_GUIDE.md          <- THIS FILE -- master team guide
|   +-- architecture.md
|   +-- demo.md
|   +-- security.md
+-- models/                       <- Local model config/reference (weights NOT committed)
+-- scripts/                      <- Setup, health-check, network-check utilities
+-- docker-compose.yml
+-- .env.example
+-- .gitignore
+-- README.md
```

### Key Rule on Model Weights

> [!CAUTION]
> Model weight files must **never** be committed to Git. The `models/` directory holds configuration and reference files only. Actual model weights are downloaded separately on the designated model machine.

---

## 8. Approved Technical Direction

> [!NOTE]
> Items marked **IMPLEMENTATION CHOICE** are approved directions from the project briefing. They are not mandated by the PS itself. The PS requires the capability; the team selects the implementation. Do not use both options of an alternative — pick one.

| Layer | Technology / Direction | Purpose | Status |
|---|---|---|---|
| **Backend framework** | Python + FastAPI | REST API server | ESTABLISHED |
| **ASGI server** | Uvicorn | Runs FastAPI in production/dev | ESTABLISHED |
| **Data validation** | Pydantic v2 | Request/response validation and schemas | ESTABLISHED |
| **Model serving** | Ollama **OR** vLLM | Serve local open-weight models — IMPLEMENTATION CHOICE, pick one | PENDING |
| **Agent orchestration** | LangGraph **OR** custom async loop | Coordinate multi-step agent work — IMPLEMENTATION CHOICE, pick one | PENDING |
| **Knowledge base / vector DB** | ChromaDB **OR** Qdrant | Local embedding storage and retrieval — IMPLEMENTATION CHOICE, pick one | PENDING |
| **Code sandbox** | Docker (isolated container) | Safe execution of generated code | PENDING |
| **Document generation** | python-docx, openpyxl, python-pptx | Generate DOCX, XLSX, PPTX outputs | PENDING |
| **Vision / OCR** | Local OCR/vision implementation | Process scanned docs and images locally | PENDING |
| **Network / sovereignty proof** | Wireshark and/or local egress monitoring script | Demonstrate no external calls — IMPLEMENTATION CHOICE | PENDING |
| **Frontend** | React + TypeScript (Vite-based, established in repo) | User interface | ESTABLISHED |

### Important Rules for Technology Selection

1. **Do not use both Ollama and vLLM.** Choose one based on available hardware and time.
2. **Do not use both ChromaDB and Qdrant** unless there is a clear technical reason.
3. **Do not use both LangGraph and another agent framework** unnecessarily.
4. **Keep the stack small and reliable.** A smaller reliable stack beats a large unreliable one.
5. **If a technology is not in this table**, discuss with the team before adding it.

---

## 9. Hardware Strategy

The team works on **one repository** across different development machines.

### Machine Assignments

| Machine | Primary Role |
|---|---|
| **RTX 4050 (6 GB VRAM)** | Primary AI/model machine — runs local model inference |
| **RTX 3050 (4 GB VRAM)** | Backend / integration / development |
| **Apple M5 Mac (16 GB unified)** | Frontend / product development and supporting development |

### Rules

- The **model machine** does not mean everyone needs every model installed locally.
- **Large model weight files remain local to the designated model machine.**
- Model weights must **never** be committed to Git.
- The final architecture should allow other components to communicate with the local model service **over the team's controlled local network**.
- Do **not** expose model services publicly.

### How Components Communicate Across Machines (Development)

```
Mac (Frontend)
    | HTTP request
    v
Backend machine
    | HTTP request to model service
    v
Model machine (Ollama/vLLM running locally)
    | response
    v
Backend machine
    | response
    v
Mac (Frontend)
```

All traffic stays within the team's local network. Nothing reaches the public internet during operation.

---

## 10. Development Environment vs Final Runtime

> [!IMPORTANT]
> This distinction is critical. Read carefully.

### Development Tools (Used to Build the Software)

These tools may be used by developers to write, test, and iterate on the code:

- Cursor, VS Code, or any IDE
- Claude, Gemini, or any AI assistant for writing code
- GitHub (for version control)
- Postman, curl, or any API testing tool

These are **developer productivity tools**. They are **not part of the final confidential AI workflow**.

### Sovereign Runtime (The Final System)

The final system that processes confidential industrial work must:

- Use **local / open-weight models only**
- Use **local processing only**
- Make **no external API calls** during core task execution
- Run entirely **on-premise**

> [!CAUTION]
> Do not accidentally make an external API (e.g., OpenAI, Anthropic, Google) a **runtime dependency**. If the system needs internet to run, it is not sovereign.

---

## 11. Team Responsibilities

Ownership means there is **one clearly responsible person** for each area. It does **not** prevent collaboration. If you need help, ask. But every area has one person who is accountable.

---

### Member 1 — AI / Models / Vision

**Responsible for:**
- Local model runtime (Ollama or vLLM setup)
- Reasoning model integration and testing
- Coding model integration and testing
- Vision / OCR model integration and testing
- Model registry (which model handles which task type)
- Model testing (verify each model returns real responses)
- Vision / OCR pipeline integration

**Primary directories:**
```
apps/backend/app/models/
apps/backend/app/vision/
models/
```

---

### Member 2 — Backend / Agent

**Responsible for:**
- FastAPI application structure
- API route implementation
- Task management (receive, track, complete tasks)
- Agent orchestration logic
- Task state management
- Model router integration
- Tool orchestration within the agent loop
- Backend integration (connecting agent to models, tools, RAG)

**Primary directories:**
```
apps/backend/app/api/
apps/backend/app/agent/
apps/backend/app/schemas/
```

---

### Member 3 — Sandbox / Security

**Responsible for:**
- Docker sandbox setup and management
- Code execution isolation (generated code runs only in sandbox)
- Network isolation configuration
- Security checks and policy enforcement
- Network monitoring / egress evidence collection
- Audit and security information for demo

**Primary directories:**
```
apps/backend/app/sandbox/
apps/backend/app/security/
docker/
```

---

### Member 4 — Frontend

**Responsible for:**
- Overall UI design and implementation
- File upload interface
- Task submission flow
- Task status display (polling or SSE)
- Agent trace / step visualization
- Model routing visibility (which model was selected, why)
- Results display
- Output file download
- Security / network evidence display panel

**Primary directory:**
```
apps/frontend/
```

---

### Member 5 — RAG / Documents

**Responsible for:**
- Local knowledge ingestion pipeline
- Text embedding generation (local)
- Vector database setup and population
- Retrieval implementation (similarity search)
- SOP / manual retrieval integration with agent
- Document generation (python-docx, openpyxl, python-pptx)
- Spreadsheet and calculation tools

**Primary directories:**
```
apps/backend/app/rag/
apps/backend/app/tools/
data/knowledge/
```

---

### Member 6 — QA / UX / Demo

**Responsible for:**
- End-to-end testing across all integrated components
- Sourcing and preparing public / sample datasets for demo
- UX validation (does the UI tell a coherent story?)
- Failure testing (what happens when something goes wrong?)
- Demo flow preparation and rehearsal
- All project documentation
- Presentation readiness

**Primary areas:**
```
tests/
docs/
data/raw/
data/knowledge/
```

---

## 12. Parallel Development

One repository. Everyone works simultaneously on their module.

```
GitHub Repository (sovereign-ai-workbench)
+-- Member 1  -->  models/, vision/
+-- Member 2  -->  api/, agent/, schemas/
+-- Member 3  -->  sandbox/, security/, docker/
+-- Member 4  -->  apps/frontend/
+-- Member 5  -->  rag/, tools/, data/knowledge/
+-- Member 6  -->  tests/, docs/, data/raw/
```

### The Interface Rule

A developer should **not** wait for every other module to be finished. Use **stable interfaces**.

```
Frontend
  | (API contract -- agreed schema)
  v
Backend
  | (agent interface)
  v
Agent
  | (model interface)
  v
Model
```

If the backend is unfinished, the frontend may **temporarily** use mock responses that **exactly match** the agreed API contract.

### Mock Rules

> [!WARNING]
> Mocks are for **development only**. They must never be present in the final demo path.

| Phase | Allowed |
|---|---|
| Development | Mock responses that match agreed contract format |
| Integration checkpoint | Mock must be replaced with real implementation |
| Final demo | Zero mocks — all real components |

**Before final integration, for every mock:**

```
Mock response
    --> REMOVE

Real backend
    --> CONNECT

Real agent
    --> CONNECT

Real local model
    --> CONNECT

Real output
    --> VERIFY
```

---

## 13. API Contract Discipline

### What Is an API Contract?

An API contract defines:

- **Endpoint** — the URL path
- **Request format** — what the caller sends (JSON body, query params, headers)
- **Response format** — what the server returns on success
- **Error format** — what the server returns on failure
- **Status values** — allowed task/operation states
- **Event format** — structure of streaming/event data

### Initial API Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/health` | Backend health check |
| `POST` | `/api/tasks` | Submit a new task |
| `GET` | `/api/tasks/{id}` | Get task status |
| `GET` | `/api/tasks/{id}/events` | Stream agent events (SSE) |
| `GET` | `/api/tasks/{id}/result` | Get completed task result and output |
| `POST` | `/api/knowledge/ingest` | Ingest a document into the local knowledge base |
| `GET` | `/api/security/status` | Get current network/sovereignty status |

> [!IMPORTANT]
> These are interface definitions. They define the **contract** that frontend and backend must honor. They are **not** permission to implement fake functionality behind them.

### Schema Location

All shared request/response/event schemas live here:

```
apps/backend/app/schemas/
```

Both frontend TypeScript types and backend Pydantic models must align with these definitions.

**Do not independently change response structures without communicating with affected teammates.**

---

## 14. Shared Schema Ownership

`apps/backend/app/schemas/` is a **shared contract area**. Any change to a shared structure can break multiple modules.

### Before Changing a Schema

1. Identify every teammate whose module uses that schema.
2. Inform them of the proposed change and why.
3. Agree on the new structure.
4. Update the schema file.
5. Update all affected backend code.
6. Update all affected frontend TypeScript types.
7. Test the affected workflow end-to-end.

> [!CAUTION]
> Do **not** silently change API response structures. This breaks other people's work without warning.

---

## 15. Agent Event Contract

The frontend should display **actual events** generated by backend execution — not hardcoded text.

### Possible Event Types

| Event | Meaning |
|---|---|
| `TASK_RECEIVED` | Task has been accepted and queued |
| `PLAN_CREATED` | Agent has created a step-by-step plan |
| `MODEL_SELECTED` | Model router has selected a specific model |
| `DOCUMENT_PROCESSED` | A document has been OCR/vision processed |
| `KNOWLEDGE_RETRIEVED` | Relevant chunks retrieved from local KB |
| `TOOL_STARTED` | A tool invocation has begun |
| `TOOL_COMPLETED` | A tool invocation has finished |
| `OUTPUT_GENERATED` | A real output file has been created |
| `TASK_COMPLETED` | Task finished successfully |
| `TASK_FAILED` | Task failed (with reason) |

These are **event concepts**. The exact JSON schema must be implemented centrally in `schemas/` and agreed on before frontend and backend implement against it.

> [!CAUTION]
> Do **not** hardcode fake success events in the final product.

---

## 16. Git Workflow

**One repository. Everyone uses it.**

Do not create six independent project repositories.

### Branch Model

```
main                     <- stable, always working
+-- feature/backend      <- backend / agent work
+-- feature/frontend     <- frontend work
+-- feature/models       <- model / vision work
+-- feature/rag          <- RAG / document tools
+-- feature/security     <- sandbox / security work
```

Adapt branch names to match actual team workflow. The principle is: **don't work directly on main**.

### Daily Workflow

**Before starting work:**
```bash
git pull origin main        # get latest changes
git checkout feature/<your-branch>
git merge main              # sync with main if needed
```

**Before committing:**
- Run relevant tests
- Review changed files (`git diff`)
- Remove accidental debug code or `print()` statements
- Confirm no secrets, API keys, or credentials
- Confirm no model weight files
- Confirm no confidential/proprietary data

**Commit message format:**
```
feat: add local model provider
feat: add document ingestion pipeline
feat: add model router
feat: add local RAG retrieval
feat: add docker sandbox
feat: add network egress monitor
fix: handle failed document extraction
fix: model router fallback on unknown task type
docs: update PROJECT_GUIDE integration checkpoints
```

### What to NEVER Commit

```
NO  API keys
NO  Passwords or credentials
NO  .env files with real secrets (use .env.example only)
NO  Model weight files (.bin, .gguf, .safetensors, etc.)
NO  Proprietary or confidential documents
NO  Unnecessary large generated artifacts
```

---

## 17. Integration Checkpoints

> [!IMPORTANT]
> Do **not** wait until the final day to integrate everything. Use these checkpoints to validate integration progressively.

---

**CHECKPOINT 1 — Backend + Local Model**

```
Expected: Backend can send a prompt to a real local model and receive a real response.
Owner: Member 1 + Member 2
```

---

**CHECKPOINT 2 — Local Model + Agent**

```
Expected: A real task can enter an agent workflow and the agent uses the local model.
Owner: Member 2 (agent) + Member 1 (model)
```

---

**CHECKPOINT 3 — Agent + Vision / OCR**

```
Expected: A real scanned document (PDF/image) is processed by the vision module
          and the result is available to the agent.
Owner: Member 1 (vision) + Member 2 (agent)
```

---

**CHECKPOINT 4 — Agent + RAG**

```
Expected: A real local knowledge document (SOP/manual) is indexed and retrieved
          by the RAG module, and the agent receives the retrieved context.
Owner: Member 5 (RAG) + Member 2 (agent)
```

---

**CHECKPOINT 5 — Agent + Document Generation**

```
Expected: A real output file (e.g., Approval_Note.docx) is generated by the tools module
          and can be downloaded.
Owner: Member 5 (tools) + Member 2 (agent)
```

---

**CHECKPOINT 6 — Coding Model + Docker Sandbox**

```
Expected: Real generated code is sent to the Docker sandbox, executed safely,
          and the result (or error) is returned to the agent.
Owner: Member 1 (coding model) + Member 3 (sandbox)
```

---

**CHECKPOINT 7 — Security / Network Proof**

```
Expected: Real evidence of network behavior (egress) is available
          and can be shown during the demo.
Owner: Member 3 (security)
```

---

**CHECKPOINT 8 — Frontend + Backend**

```
Expected: Frontend makes real API calls to the backend. No development mocks remain
          in the user-facing path.
Owner: Member 4 (frontend) + Member 2 (backend)
```

---

**CHECKPOINT 9 — Full End-to-End**

```
Expected:
  Workflow A: Scanned report -> Vision/OCR -> Agent -> RAG -> Reasoning -> Approval_Note.docx
  Workflow B: Coding task -> Coding model -> Docker sandbox -> Verified result returned

Both run with real local components. No mocks. No cloud APIs.
Owner: Member 6 (QA) coordinates. All members participate.
```

---

## 18. Feature Status System

Use this notation consistently in project discussions, issue tracking, and internal documentation:

| Symbol | Meaning |
|---|---|
| `[ ] PLANNED` | Planned but not started |
| `[~] IN DEVELOPMENT` | Currently being worked on |
| `[x] TESTED` | Implemented, run, verified with real inputs |
| `[!] BLOCKED` | Cannot proceed — dependency or issue blocking |
| `[-] DE-SCOPED` | Intentionally removed from scope |

> [!IMPORTANT]
> `[x] TESTED` means the feature has been **actually tested with real inputs producing real outputs**. Do NOT mark something `[x]` merely because the code has been written.

---

## 19. Development Sequence

The recommended implementation order. Do not skip ahead without completing earlier steps.

| Step | Component | Status |
|---|---|---|
| 01 | Repository / file structure | `[x] COMPLETE` |
| 02 | Backend foundation (FastAPI, routes, config) | `[x] COMPLETE` |
| 03 | `GET /api/health` working | `[x] COMPLETE` |
| 04 | Local model connection (Ollama or vLLM) | `[ ] NEXT / IN PROGRESS` |
| 05 | Model abstraction / registry | `[ ] PLANNED` |
| 06 | Model routing (task type -> model) | `[ ] PLANNED` |
| 07 | Agent orchestration loop | `[ ] PLANNED` |
| 08 | Vision / OCR pipeline | `[ ] PLANNED` |
| 09 | Local RAG (ingestion + retrieval) | `[ ] PLANNED` |
| 10 | Document generation tools | `[ ] PLANNED` |
| 11 | Coding sandbox (Docker) | `[ ] PLANNED` |
| 12 | Security / network proof | `[ ] PLANNED` |
| 13 | Frontend integration (real API) | `[ ] PLANNED` |
| 14 | Full end-to-end integration | `[ ] PLANNED` |
| 15 | Demo testing and reliability | `[ ] PLANNED` |

> [!CAUTION]
> Current project status reflects **verified** work only. Do not update this table to claim completion without actually testing.

---

## 20. Testing Rule

Every component follows this exact cycle — no exceptions:

```
IMPLEMENT
    |
    v
RUN
    |
    v
TEST (with real inputs)
    |
    v
VERIFY (real outputs)
    |
    v
COMMIT
    |
    v
INTEGRATE
```

Generated code is **not** automatically working code.

### What "Tested" Means for Each Component

| Component | Evidence of "Tested" |
|---|---|
| Backend | `GET /api/health` returns expected JSON response |
| Local model | Actual local model returns a real completion |
| Vision | Actual sample scanned document is processed and text extracted |
| RAG | Known document indexed -> query performed -> relevant chunk retrieved |
| DOCX generation | Actual `.docx` file created, exists on disk, opens correctly in Word |
| Sandbox | Generated code executes inside Docker -> result returned |
| Security | Actual network traffic measurement collected |
| Frontend | Actual API responses from real backend displayed correctly |

---

## 21. Failure Handling

> [!IMPORTANT]
> The system must **not** hide failures or replace them with fake success responses.

| Failure Type | Required Behavior |
|---|---|
| Model fails | Return and report model failure with reason |
| OCR fails | Report document-processing failure clearly |
| RAG finds nothing | Clearly indicate "no relevant local knowledge found" |
| Sandbox fails | Return execution failure status with error detail |
| Document generation fails | Return output-generation failure |
| Network measurement fails | Do NOT fabricate sovereignty evidence |

> [!CAUTION]
> **Never replace a failed real operation with a fake successful result.** A visible, honest failure is always better than a hidden fake success.

---

## 22. Security Rules

### Core Principle

```
The confidential workflow must remain entirely local.
```

### Do NOT Make the Final Workflow Dependent On:

- Public cloud LLM APIs (OpenAI, Anthropic, Gemini, etc.)
- External OCR services (Google Vision, AWS Textract, etc.)
- Hosted vector databases (Pinecone, Weaviate Cloud, etc.)
- External web search inside the confidential workflow
- Cloud agent frameworks with external dependencies
- External document-processing APIs
- Any external service required for core execution

### Code Execution

Generated code must **not** execute directly on the host system.
All generated code must run inside the Docker sandbox.

### Network Evidence

Network restrictions and evidence must be **real** — not simulated.

### Claims to Avoid

```
"Unhackable"
"Perfectly secure"
"100% secure"
"Zero risk"
"Zero external traffic" (unless actually measured)
```

### Claims to Make (When True)

```
Local execution demonstrated
Controlled components
Network behavior measured
Code sandboxed
Evidence shown
```

---

## 23. Network / Sovereignty Proof

### Why This Matters

The central claim of the project is **sovereignty** — the system processes confidential work without sending data externally. That claim must be **demonstrated**, not merely stated.

Simply showing `"0.00 KB/s outbound"` hardcoded in the UI is meaningless and dishonest.

### What Must Be Demonstrated

During the demo, show **visible, real evidence** that:

1. A workflow was executed using local models.
2. No confidential data left the local network.

### Implementation Direction (Choose One)

| Option | Description |
|---|---|
| **Wireshark capture** | Record network traffic during workflow execution; show in demo |
| **Local egress monitoring script** | Custom script measuring outbound connections in real time |

Use whichever is implemented and **actually working**.

> [!CAUTION]
> The UI may display security status, but the status **must** be backed by actual measurement. Do NOT hardcode `"0.00 KB/s outbound"` to make the demo look good.

---

## 24. Data Rules

### What to Use

- Open-source / open-weight models
- Public domain industrial documents
- Public sample inspection reports
- Synthetic / sample SOPs created for demonstration
- Publicly available technical manuals

### What NOT to Use

- Actual confidential MRPL data
- Proprietary documents
- Any data that cannot be freely used in a public competition

The briefing explicitly supports using public/open sample data for the prototype. A sample public inspection report combined with a sample SOP can demonstrate exactly the same workflow safely.

---

## 25. What NOT to Build

> [!CAUTION]
> This section is as important as the requirements list. Scope creep is the most common reason prototypes fail.

Do **not** add any of the following unless explicitly approved by the team after checking PS scope:

```
Public cloud AI APIs as a runtime dependency
Cloud OCR services
Hosted / external vector databases
External web search in the confidential workflow
Kubernetes deployment (unless specifically required)
Unnecessary microservices
Production enterprise IAM / RBAC systems
Payment systems
Social features
Analytics dashboards unrelated to the PS
Autonomous internet browsing agent
Huge model zoo (dozens of models)
Fine-tuning or training pipeline (unless specifically required)
Full CAD / P&ID intelligence beyond what can realistically be demonstrated
Random AI features unrelated to PS 26117
```

> **Do not sacrifice reliability to increase feature count.**
> A smaller system that works reliably beats a large system that fails during the demo.

---

## 26. Claims Discipline

### Claims We Can Make (When Actually Demonstrated)

| Claim | Condition |
|---|---|
| Runs locally / on-premise | System actually runs on local hardware |
| Uses open-weight local models | Models confirmed running locally |
| Supports multiple task-specific models | Router actually invokes different models |
| Uses local knowledge retrieval | RAG actually retrieves from local KB |
| Performs agentic multi-step work | Agent actually executes multiple real steps |
| Executes code in a sandbox | Docker sandbox actually runs code |
| Produces real deliverables | Actual file written and downloadable |
| Provides visible network evidence | Actual network measurement shown |

### Claims We Must NOT Make

```
Perfect P&ID understanding
Better than ChatGPT / Claude / Gemini
Unhackable
100% secure
Zero risk
Production-ready enterprise platform
Complete MRPL deployment
Perfect reasoning
Supports every industrial document type
Zero external traffic (without actual measurement)
```

---

## 27. Frontend Development Rule

Frontend can and should develop **before** backend is complete.

### Development Phase (Mocks Allowed)

```
User presses "Run Agent"
    |
    v
Frontend calls mock API service
    |
    v
Mock returns sample task status
    |
    v
Mock streams sample events
    |
    v
Mock returns sample output
    |
    v
UI renders correctly using agreed schema format
```

### Integration Phase (Mocks Removed)

```
User presses "Run Agent"
    |
    v
Frontend calls real backend API
    |
    v
Real backend runs real agent
    |
    v
Real agent uses real local model
    |
    v
Real events streamed back
    |
    v
Real output returned
    |
    v
UI renders real result
```

### Rules

- Design the UI around **agreed API contracts**, not around what the backend currently returns.
- Do **not** hardcode final demo behavior into the UI.
- The final UI must display **actual backend state and events**.
- Before integration checkpoint 8, remove all mocks from the live user path.

---

## 28. Backend Development Rule

Backend should not depend on frontend being complete.

Test endpoints directly using API tools:

```bash
# Health check
curl http://localhost:8000/api/health

# Submit a task
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"task_type": "document", "content": "..."}'

# Get task status
curl http://localhost:8000/api/tasks/{id}
```

The full agent pipeline should be testable end-to-end **without any frontend involvement**:

```
API request (curl / Postman / pytest)
    |
    v
FastAPI receives task
    |
    v
Agent runs
    |
    v
Model / tools invoked
    |
    v
API response returned
    |
    v
Verified by test
```

---

## 29. AI / Model Development Rule

### Test Models Independently

Before integrating with the agent layer, verify each model independently:

```python
# Example: test reasoning model directly
response = model_client.generate("Summarize this inspection finding: ...")
assert response is not None
assert len(response.text) > 0
```

### Each Model Has a Clear Purpose

| Model Role | Task Types |
|---|---|
| Reasoning model | Document summarization, drafting, approval notes, reasoning |
| Coding model | Code generation, code review, code reasoning |
| Vision model | Scanned documents, images, handwritten notes |

### Hardware-First Selection

> [!IMPORTANT]
> Do **not** use a large model merely because it is available if it cannot reliably run on available hardware.
>
> **A smaller model that works reliably is better than a large model that fails during the demo.**

Test each model at full load conditions similar to the demo environment before committing to it.

---

## 30. RAG Development Rule

### What RAG Actually Is

```
RAG = Retrieve relevant local information first
    -> give it to the local model as context
    -> model generates a grounded response
```

RAG must use **local data only**. No external search. No external embedding APIs.

### What "RAG is Working" Means

The team must be able to verify this full chain:

```
1. Document exists in data/knowledge/
2. Document is indexed (embedding stored in local vector DB)
3. Query is performed
4. Relevant chunk is retrieved
5. Agent receives the retrieved context
6. Model generates an answer grounded in the retrieved content
```

> [!CAUTION]
> Do NOT claim RAG is working simply because a vector database container is running. The full chain above must be verified with a known test document.

---

## 31. Sandbox Development Rule

### What the Sandbox Must Do

Generated code runs **inside** the Docker sandbox. Never on the host.

### Test Sequence

**Step 1 — Basic execution:**
```
Simple valid code -> sandbox -> execution -> correct result
```

**Step 2 — Error handling:**
```
Invalid / broken code -> sandbox -> controlled error returned
```

**Step 3 — Restriction enforcement:**
```
Code attempting network access or file system escape
    -> sandbox restriction triggered
    -> blocked / controlled behavior
    -> appropriate error returned
```

All three steps must pass before the sandbox is considered `[x] TESTED`.

---

## 32. Document Generation Rule

Generated outputs must be **actual files** — not UI placeholders or simulated cards.

### Minimum Verification for DOCX

```
1. Content generated by model
2. python-docx writes the file
3. File exists at data/outputs/Approval_Note.docx
4. File can be opened in Microsoft Word / LibreOffice
5. Content is correct and meaningful
```

> [!CAUTION]
> Do NOT merely display `"Approval Note Generated"` in the UI without actually producing the `.docx` file.

---

## 33. Definition of Done

### A Module Is DONE Only When:

1. Code exists and is committed.
2. It **runs** (no startup errors).
3. It has been **tested** with real inputs.
4. Expected inputs produce expected outputs.
5. Failure behavior is understood and handled.
6. It follows the agreed interface (API contract / schema).
7. It does **not** introduce unauthorized external dependencies.
8. It is ready for integration with connected modules.
9. All relevant changes are committed to the feature branch.

### The Complete Prototype Is DONE Only When:

The required PS workflows run **end-to-end** with:
- Real local components
- No development mocks
- No cloud APIs
- Real outputs produced
- Sovereignty claim supported by visible evidence

---

## 34. Demo Readiness Checklist

Run through this checklist before the final demonstration. Every item must be verified by actually running it — not by assuming.

```
Infrastructure
[ ] Backend starts without errors
[ ] Health endpoint returns correct response
[ ] Frontend starts and connects to backend

Models
[ ] Reasoning model responds to a real prompt
[ ] Coding model responds to a real coding prompt
[ ] Vision / OCR model processes a real scanned document
[ ] Model routing correctly selects appropriate model for each task type

Agent
[ ] Agent workflow runs end-to-end for a document task
[ ] Agent workflow runs end-to-end for a coding task
[ ] Agent events are visible in the UI
[ ] Model selection events are visible and correct

RAG
[ ] Sample SOP / manual exists in data/knowledge/
[ ] Document is indexed in local vector database
[ ] Retrieval returns relevant content for a known query

Vision / OCR
[ ] Sample scanned document is available
[ ] OCR pipeline extracts text successfully
[ ] Result is usable by the agent

Document Generation
[ ] Approval note workflow produces Approval_Note.docx
[ ] DOCX file exists on disk
[ ] DOCX opens correctly in Word / LibreOffice
[ ] Content is meaningful and correct

Coding Sandbox
[ ] Coding model generates working code for a sample task
[ ] Docker sandbox executes the generated code
[ ] Execution result is returned correctly
[ ] Invalid code produces controlled error (not host crash)

Security / Sovereignty
[ ] Network monitoring is active and measuring real traffic
[ ] Evidence is visible during the demo
[ ] No hardcoded network status values

Integration
[ ] Frontend uses real backend APIs (no development mocks)
[ ] No cloud LLM API is required or called
[ ] No cloud service is required or called

Data / Repository
[ ] No model weights committed to Git
[ ] No confidential or proprietary data in repository
[ ] No API keys or credentials committed
[ ] .env.example is up to date

End-to-End
[ ] Full Workflow 1 (Inspection -> Approval Note) tested multiple times
[ ] Full Workflow 2 (Coding -> Sandbox -> Result) tested multiple times
[ ] Both workflows produce correct real outputs reliably
[ ] Failure paths handled gracefully (no crashes, honest error messages)
```

---

## 35. Demo Failure Plan

> [!IMPORTANT]
> Prepare a fallback path. Every demo should have a smaller, verified alternative ready.

| Primary Failure | Fallback |
|---|---|
| Preferred large model fails to load | Use smaller verified local model (pre-tested on demo hardware) |
| Complex multi-page document fails processing | Use a known-tested simple public sample document |
| Complex multimodal demo case fails | Use the simpler scanned-document demo that is already verified |
| Full end-to-end pipeline is slow | Use a shorter document that completes faster |

> [!CAUTION]
> **Never switch to a fake result.** The fallback must still demonstrate **real local functionality**. A working small demo is infinitely better than a faked large demo.

---

## 36. Beginner Glossary

Definitions for team members who are new to some of these concepts.

| Term | Explanation |
|---|---|
| **Frontend** | The part of the application users see and interact with — the web interface running in the browser. |
| **Backend** | The server-side logic that runs on a machine, handles requests, coordinates processing, and stores data. |
| **API** | Application Programming Interface — a defined way for two programs to communicate, usually by sending and receiving structured messages over the network. |
| **API endpoint** | A specific URL on a server that accepts a specific type of request. For example, `GET /api/health` is an endpoint that returns the backend health status. |
| **FastAPI** | A Python framework for building APIs quickly. It automatically validates request/response data and generates interactive documentation. |
| **Uvicorn** | A fast Python web server that runs FastAPI applications. |
| **localhost** | A name that refers to the current machine — used when a service is running on the same computer as the requester. Address: `127.0.0.1`. |
| **Port** | A numbered communication channel on a machine. For example, the backend runs on port `8000`, so its URL is `http://localhost:8000`. |
| **JSON** | JavaScript Object Notation — a simple text format for structured data, used as the primary data format in our APIs. |
| **Dependency** | A library or package that your code requires to function. Listed in `requirements.txt` (Python) or `package.json` (Node). |
| **LLM** | Large Language Model — an AI model trained on large amounts of text that can understand and generate human language. |
| **Open-weight model** | An LLM whose weights (learned parameters) are publicly released and can be downloaded and run locally without paying an API fee. Examples: Llama, Mistral, Qwen. |
| **Local model** | A model running entirely on a local machine, not accessed via an external API. |
| **Model runtime** | Software that loads and serves a local model so that other programs can send it prompts. Examples: Ollama, vLLM. |
| **Multimodal model** | A model that can process more than one type of input — for example, both text and images. |
| **OCR** | Optical Character Recognition — technology that reads and extracts text from images or scanned documents. |
| **RAG** | Retrieval-Augmented Generation — a technique where relevant documents are retrieved from a local knowledge base and given to the model as context before generating a response, making the answer more accurate and grounded. |
| **Embedding** | A numerical representation of text (or other content) that captures its meaning as a vector of numbers. Similar texts have similar embeddings. |
| **Vector database** | A database that stores embeddings and can quickly find the most similar ones to a query. Used in RAG to find relevant documents. Examples: ChromaDB, Qdrant. |
| **Agent** | An AI system that doesn't just answer one question — it plans, uses tools, observes results, and continues until a goal is achieved. |
| **Orchestrator** | The component that coordinates the agent — managing the sequence of planning, model calls, tool uses, and result handling. |
| **Model router** | A component that decides which local model is best suited for a given task type. |
| **Tool** | A function the agent can invoke to do something concrete — read a file, write a document, run code, search the knowledge base. |
| **Sandbox** | An isolated execution environment where generated code can run safely without affecting the host system. Our sandbox uses Docker. |
| **Docker** | A platform for running software in isolated containers — lightweight virtual machines that share the host OS but are otherwise isolated. |
| **Air-gapped** | A system that is physically or logically disconnected from external networks (particularly the public internet) to protect confidential data. |
| **On-premise** | Software or hardware that operates within an organization's own facilities rather than in an external cloud. |
| **Network egress** | Data flowing outward from the local system to external destinations. Measuring egress proves (or disproves) the sovereignty claim. |
| **Mock** | A fake implementation that simulates real behavior for development purposes. Used so frontend can develop without waiting for backend, and vice versa. Must be removed before the final demo. |
| **API contract** | The agreed definition of an endpoint: what request it accepts, what response it returns, and what errors it can produce. Both sides (frontend and backend) must honor the same contract. |
| **Git** | A version control system that tracks changes to files and allows multiple developers to collaborate on the same codebase. |
| **Repository (repo)** | The central collection of all project files and their full change history, managed by Git. |
| **Branch** | A parallel version of the repository where changes can be made without affecting the main version until merged. |
| **Commit** | A saved snapshot of changes to one or more files. Each commit has a message describing what changed and why. |
| **Merge** | The process of integrating changes from one branch into another. |

---

## 37. Quick Start for a New Team Member

Before writing a single line of code:

1. **Read `docs/PROJECT_GUIDE.md`** (this document) in full.
2. **Understand the PS scope** — what we are building and what we are not.
3. **Identify your assigned module** from Section 11.
4. **Pull the latest repository:**
   ```bash
   git clone <repo-url>
   cd sovereign-ai-workbench
   git pull
   ```
5. **Check the API / schema contract** relevant to your module (`apps/backend/app/schemas/`).
6. **Check dependencies on other modules** — what do you need from others? What does someone need from you?
7. **Do not introduce unrelated technology** — if it's not in Section 8, discuss first.
8. **Build the smallest working version first** — get one thing working end-to-end before adding complexity.
9. **Test it locally** with real inputs. Verify real outputs.
10. **Commit clearly:**
    ```bash
    git add .
    git commit -m "feat: add <description of what you built>"
    git push origin feature/<your-branch>
    ```
11. **Inform the relevant teammate** when you change a shared interface or schema.
12. **Integrate at the next checkpoint** — don't hold your work isolated for too long.

---

## 38. Team Communication Rule

Simple rules that prevent silent breakage:

| Event | Action Required |
|---|---|
| You change an API endpoint | Inform Member 4 (Frontend) AND Member 2 (Backend) |
| You change a schema | Inform every module owner affected by that schema |
| You change model behavior (input/output format) | Inform Member 2 (Agent/Backend) |
| You change security / network behavior | Inform Member 6 (QA/Demo) |
| Your feature is blocked | Mark `[!] BLOCKED` — do not silently wait |
| Your feature is unfinished | Do not mark `[x]` — mark `[~] IN DEVELOPMENT` |
| You discover a new feature idea | Do NOT immediately implement — check PS scope first, then discuss with team |
| You are about to modify a shared schema | Notify all affected teammates BEFORE making the change |

---

## 39. Final Project Principle

> **"We are not building another chatbot.**
>
> **We are building a way for organizations to use agentic AI on confidential work while keeping the processing inside their own infrastructure — and demonstrating that sovereignty claim with real evidence."**

This statement comes directly from the spirit of PS 26117.

Every decision — which model to use, which tool to build, which feature to add — should be evaluated against this principle.

If a decision makes the system more reliable, more local, more demonstrably sovereign, and better at the defined workflows: it belongs.

If it adds complexity, external dependencies, or features unrelated to the PS: it does not belong, regardless of how impressive it sounds.

---

*Document version: 1.0 · Created: 2026-09-03 · Project: PS 26117 · Sovereign AI Workbench*
