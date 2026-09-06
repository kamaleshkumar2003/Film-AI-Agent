# AI Film Production Breakdown & Planning System (V1)

A production-grade web application that converts screenplays (PDF, DOCX, TXT) into a structured, editable, production-ready scene breakdown.

Built with **FastAPI**, **SQLAlchemy**, **Pydantic v2**, and **React 18 + TypeScript + Tailwind CSS**.

---

## 1. Key Architectural Principles

1. **Document-to-Scene Pipeline**:
   ```
   Screenplay (PDF/DOCX/TXT)
          ↓
   Text & Page Extraction (pypdf, python-docx)
          ↓
   Scene Detection (Flexible slugline parser)
          ↓
   Scene-by-Scene Chunking & Analysis (Resumable)
          ↓
   Pydantic Schema Validation & Repair
          ↓
   Relational Database (PostgreSQL / SQLite)
          ↓
   Film Production Breakdown UI (React + TypeScript)
   ```

2. **Strict Evidence vs. Inference Tracking**:
   - For every extracted fact (cast, props, vehicles, special costumes, makeup, equipment, crew), the AI records verbatim screenplay text as `evidence` with a confidence score.
   - For inferred requirements (e.g., rain gear because scene has heavy rain), it explicitly sets `inferred: true` and records the reasoning.
   - AI inferences are never disguised as explicit screenplay facts.

3. **Human Review & Provenance**:
   - Every entity and scene tracks its provenance: `AI_GENERATED`, `HUMAN_EDITED`, or `HUMAN_CONFIRMED`.
   - Production managers can edit headings, times, weather sensitivity, estimated durations, and add/remove props, cast, vehicles, and notes.

4. **Multi-Provider AI Architecture**:
   - **OpenAI Provider** (`gpt-4o-mini` / `gpt-4o`) with structured JSON schema output.
   - **Google Gemini Provider** (`gemini-1.5-pro`) with JSON output.
   - **High-Fidelity Heuristic Provider**: Built-in rule-based NLP analyzer that extracts real facts and evidence without needing an external API key, enabling zero-friction local testing right out of the box.

5. **Extensibility for V2**:
   - Relational database schema designed so that V2 (cast availability, shooting day scheduling, location scouting, weather forecast APIs, OR-Tools optimization) can be plugged in without restructuring.

---

## 2. Quick Start Guide

### Prerequisites
- Python 3.10+
- Node.js v18+ and npm

### Backend Setup

1. Open a terminal in `backend/`:
   ```bash
   cd backend
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate # Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   *By default, `AI_PROVIDER=mock` and `DATABASE_URL=sqlite+aiosqlite:///./production_plan.db`, so the app runs immediately with zero setup.*
   *To use OpenAI or Gemini, set `AI_PROVIDER=openai` and provide `OPENAI_API_KEY` in `.env`.*

5. Start the FastAPI server:
   ```bash
   python run_server.py
   # Or: uvicorn app.main:app --port 8000 --reload
   ```
   API Docs available at: `http://127.0.0.1:8000/docs`

### Frontend Setup

1. Open a terminal in `frontend/`:
   ```bash
   cd frontend
   ```

2. Install npm packages:
   ```bash
   npm install
   ```

3. Start Vite development server:
   ```bash
   npm run dev
   ```
   Open `http://localhost:5173` in your browser.

---

## 3. Testing with the Sample Screenplay

We have included a dedicated 6-scene test screenplay:
`backend/sample_screenplays/neon_harbor.txt`

It tests all screenplay formatting edge cases:
- Scene 1: `EXT. DOCKS - SUNSET` (Heavy rain, CRITICAL weather sensitivity, moving motorcycle, Meera & Arjun, wet clothes, stunts)
- Scene 2: `INT. ABANDONED WAREHOUSE - NIGHT` (Interior, armed henchmen, gun props, laptop, blood makeup, VFX muzzle flash, armorer crew requirement)
- Scene 3: `EXT. CITY STREET - NIGHT - CONTINUOUS` (High-speed car chase, stunts, drone operator, background crowd)
- Scene 4: `INT. DETECTIVE OFFICE - MORNING` (Dialogue scene, coffee cups, case files, character on speakerphone V.O.)
- Scene 5: `INT./EXT. POLICE TRANSPORT VAN - DAY` (Moving vehicle, interior/exterior combo, radio equipment)
- Scene 6: `EXT. SKYSCRAPER ROOFTOP - DAWN` (Golden hour lighting, helicopter VFX)

### In the UI:
1. Click **New Project** -> Create "Project X".
2. Click **Upload Script** -> Select `backend/sample_screenplays/neon_harbor.txt`.
3. Click **Analyze Screenplay** -> Watch live background progress bar.
4. Click any scene to review cast, props, vehicles, weather, and verbatim screenplay evidence.
5. Click **Confirm Breakdown** or edit fields and save.
6. Click **JSON** or **CSV** in the header to download production reports.

---

## 4. Running Automated Tests

Run the complete backend test suite:
```bash
python -m pytest -v backend/tests
```

Run the frontend TypeScript & Vite build:
```bash
cd frontend && npm run build
```
