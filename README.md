# Teaching Tools — Code Audit & Bug-Fix Report

> Previous README content archived to [notes.md](notes.md).

---

## 1. Bugs, Errors & Broken Logic Identified

### 14 bugs found across the codebase:

| # | File | Bug | Severity |
| :--- | :--- | :--- | :--- |
| 1 | `utils/saved_results.py` | `DataFrame.map` used — only available in pandas >= 2.1.0; `requirements.txt` allows 2.0.x | High |
| 2 | `pages/02_Question.py`, `03_Question_Combined.py` | `value_counts().reset_index()` column rename mismatched between pandas 1.x and 2.x | High |
| 3 | `utils/storage.py` | Path traversal in `load_dataset()` — unsanitized filename concatenation | High |
| 4 | `pages/04_Test_Question_Parser.py` | Selectbox used `.index()` on label strings — duplicate labels load wrong dataset | High |
| 5 | `app.py` | Preview/Save buttons used stale `validated_data` without checking current text area | High |
| 6 | `pages/01_Student.py` | Lesson sorting defaulted to `999` for all entries (no `week` key in data) | Medium |
| 7 | `pages/01_Student.py` | `len()` and loops crash on `None`/non-list `datasets`/`questions` fields | Medium |
| **8** | `pages/03_Question_Combined.py` | Missing `"calculation_required" in df` guard — `KeyError` if column absent in any dataset | **Medium** |
| **9** | `utils/prompt_loader.py` | `load_prompt()` lacks path sanitization — latent traversal risk | **Low** |
| **10** | `pages/02_Question.py` | Dead function `codes_from_row()` defined but never called | **Low** |
| **11** | `pages/02_Question.py`, `03_Question_Combined.py` | `.explode()` on string values splits characters instead of lists — produces incorrect analytics | **Medium** |
| **12** | `project_directory.md` | Missing `04_Test_Question_Parser.py` from pages listing (outdated) | **Info** |
| **13** | `utils/saved_results.py` | `build_summary()` assumes `"Main Chapter"` column exists — crashes if absent | **Low** |
| **14** | `pages/04_Test_Question_Parser.py` | Chapter summary uses pre-edit `filled_df` while export saves post-edit `edited_df` — stale summary | **Low** |

---

## 2. Fixes Applied

### Bugs 1-7 (pre-existing fixes — verified present in codebase)

| # | Fix |
| :--- | :--- |
| 1 | Version-safe fallback: `hasattr(df_subset, "map")` → `.map`, else `.applymap` |
| 2 | Direct `.columns = ["Syllabus", "Count"]` assignment instead of `.rename()` |
| 3 | `Path(filename).name` strips directory components before joining path |
| 4 | Integer-indexed selectbox with `format_func` display — eliminates `.index()` ambiguity |
| 5 | Re-parse text area on Preview/Save; warn if mismatch with `validated_data` |
| 6 | `get_week_number()` regex helper extracts week from lesson ID (e.g. `week_7_waves` → `7`) |
| 7 | `isinstance(..., list)` guards before all `len()` calls and loops |

### Bugs 8-14 (new fixes applied in this session)

| # | File | Before | After |
| :--- | :--- | :--- | :--- |
| 8 | `pages/03_Question_Combined.py:74` | `int(df["calculation_required"].sum())` | `int(df["calculation_required"].sum()) if "calculation_required" in df else 0` |
| 9 | `utils/prompt_loader.py:14` | `PROMPT_DIR / f"{prompt_name}.txt"` | `Path(prompt_name).name` sanitization before path join |
| 10 | `pages/02_Question.py:23-25` | `codes_from_row()` function defined, never used | Removed entire dead function |
| 11 | `pages/02_Question.py:147-148`, `03_Question_Combined.py:185-186, 209-210` | `df.explode("syllabus_codes")` — explodes strings into chars | `df["syllabus_codes"].apply(as_list).explode()` — guards via `as_list` |
| 12 | `project_directory.md` | Missing `04_Test_Question_Parser.py` | Added to pages listing |
| 13 | `utils/saved_results.py:190` | `df.groupby("Main Chapter")` — unchecked | Returns empty DataFrame if `"Main Chapter" not in df.columns` |
| 14 | `pages/04_Test_Question_Parser.py:112` | `build_summary(filled_df)` — ignores data editor edits | `build_summary(edited_df[edited_df["Question ID"].notna()])` — reflects edits |

---

## 3. Code Cleanups

- **Removed dead code** (`codes_from_row()` in `02_Question.py`) — unused function eliminated
- **Guard-as-list before explode** — applied `df["col"].apply(as_list).explode()` in 4 locations to prevent string-character explosion
- **Column existence checks** — added `if "calculation_required" in df`, `if "Main Chapter" in df.columns` guards to prevent silent `KeyError`
- **Path sanitization** — `Path(prompt_name).name` added in `prompt_loader.py` matching the pattern already in `storage.py`
- **Updated docs** — `project_directory.md` now includes `04_Test_Question_Parser.py`

---

## 4. Inline Comments Added

All non-trivial decision points now have inline comments explaining the rationale:

| Location | Subject |
| :--- | :--- |
| `utils/saved_results.py:171-172` | Pandas `.map`/`.applymap` version-safe fallback |
| `utils/storage.py:77-78` | Path traversal sanitization via `Path(filename).name` |
| `utils/prompt_loader.py:15` | Path traversal sanitization (same pattern) |
| `pages/04_Test_Question_Parser.py:46` | Integer-indexed selectbox to avoid duplicate-label bug |
| `pages/04_Test_Question_Parser.py:143` | Same pattern in preview selectbox |
| `app.py:74, 96` | Stale-content guard before Preview/Save |
| `pages/01_Student.py:79` | Two-step week number extraction (explicit key → regex fallback → 999) |
| `pages/01_Student.py:107, 115, 127, 139, 164` | `isinstance` guards before list operations |
| `pages/02_Question.py:153, 168` | Direct `.columns = [...]` instead of `.rename()` |
| `pages/03_Question_Combined.py:190, 203, 216` | Same column-naming pattern |

---

## 5. Summary of All Changes

| File | Changes |
| :--- | :--- |
| `utils/saved_results.py` | Bug 1 (map/applymap fallback), Bug 13 (Main Chapter guard) |
| `utils/storage.py` | Bug 3 (path traversal fix, verified) |
| `utils/prompt_loader.py` | Bug 9 (path sanitization added) |
| `pages/01_Student.py` | Bug 6 (get_week_number), Bug 7 (isinstance guards, verified) |
| `pages/02_Question.py` | Bug 2 & 10 (column naming fix, dead code removal), Bug 11 (as_list explode guard) |
| `pages/03_Question_Combined.py` | Bug 2 & 8 (column naming, calculation_required guard), Bug 11 (as_list explode guard) |
| `pages/04_Test_Question_Parser.py` | Bug 4 & 14 (index-based selectbox, summary sync) |
| `app.py` | Bug 5 (stale content guard, verified) |
| `project_directory.md` | Bug 12 (added missing page reference) |
| `README.md` & `notes.md` | Archived old README to notes.md; this file replaces README.md |

---

# Teaching Tools — Complete Project Documentation

---

## 1. Project Overview

**Teaching Tools** is a suite of Streamlit-based applications and a FastAPI service for educators and curriculum developers to extract, validate, browse, and manage educational question datasets.

### Problem It Solves

Educators frequently work with unstructured question data from PDFs, OCR outputs, and markdown tables. This toolkit provides:

- **Prompt-driven extraction** — Load week-specific prompt templates and paste OCR/PDF text, then validate and save structured JSON datasets
- **Student & lesson management** — Browse students, their lesson plans, and attached datasets from a registry
- **Question exploration** — Filter and analyze extracted questions by syllabus code, topic, calculation requirement, and keyword across single or multiple datasets
- **Test question parsing** — Paste markdown, CSV, or TSV tables of test questions; parse, edit, and export them as structured CSV/JSON
- **REST API** — HTTP access to all datasets and saved results for integration with external tools

---

## 2. Tech Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **Frontend / UI** | [Streamlit](https://streamlit.io) >= 1.31 |
| **Backend / API** | [FastAPI](https://fastapi.tiangolo.com) >= 0.111 |
| **ASGI Server** | [Uvicorn](https://www.uvicorn.org) >= 0.30 |
| **Data Processing** | [Pandas](https://pandas.pydata.org) >= 2.0 |
| **Data Storage** | Local JSON files (`data/` directory), CSV files |

---

## 3. Architecture Overview

```
User ──→ Streamlit Web UI (app.py + pages/)
            │
            ├── utils/json_validator.py     — JSON schema validation
            ├── utils/prompt_loader.py      — Load .txt prompt templates
            ├── utils/storage.py            — Dataset CRUD + registry
            ├── utils/lesson_registry.py    — Lesson/student registry CRUD
            └── utils/saved_results.py      — Table parse, CSV save, manifest
                    │
                    ▼
            data/                           — Disk-backed storage
              ├── extracted_questions/      — JSON datasets (via app.py)
              ├── saved_results/            — CSV exports (via parser)
              ├── registry.json             — Dataset registry index
              └── registry_lesson.json      — Student/lesson registry

User ──→ FastAPI Server (api/main.py)       — REST endpoints
            │
            ├── utils/storage.py            — Read datasets
            └── utils/saved_results.py      — Read saved results
```

### Module Overview

| Module | Path | Responsibility | Key Exports |
| :--- | :--- | :--- | :--- |
| **Main Entry** | `app.py` | Prompt → validate → preview → save workflow | Streamlit page |
| **Student Dashboard** | `pages/01_Student.py` | Browse students, lessons, attached datasets | Streamlit page |
| **Question Explorer** | `pages/02_Question.py` | Single-dataset filtering & analytics | Streamlit page |
| **Combined Explorer** | `pages/03_Question_Combined.py` | Cross-dataset global filtering & analytics | Streamlit page |
| **Test Parser** | `pages/04_Test_Question_Parser.py` | Markdown/CSV/TSV table parsing & export | Streamlit page |
| **API Server** | `api/main.py` | REST endpoints for datasets & saved results | FastAPI app |
| **Prompt Loader** | `utils/prompt_loader.py` | List & load `.txt` prompt templates | `list_prompts()`, `load_prompt()` |
| **Storage** | `utils/storage.py` | Dataset CRUD with path-sanitized I/O | `save_dataset()`, `load_dataset()`, `load_registry()` |
| **Saved Results** | `utils/saved_results.py` | CSV/JSON table parse, save, manifest, export | `parse_input()`, `save_result()`, `build_summary()` |
| **Lesson Registry** | `utils/lesson_registry.py` | Student/lesson CRUD | `add_lesson()`, `get_student_lessons()` |
| **JSON Validator** | `utils/json_validator.py` | Validate extracted question JSON schema | `validate_schema()` |

### Component Relationships

| Page / Module | Consumes From | Produces |
| :--- | :--- | :--- |
| `app.py` | `prompt_loader.py` (prompts), `json_validator.py` (schema), `storage.py` (registry) | `data/extracted_questions/*.json`, `data/registry.json` |
| `01_Student.py` | `lesson_registry.py`, `storage.py` | (read-only display) |
| `02_Question.py` | `storage.py` | (read-only filtering) |
| `03_Question_Combined.py` | `storage.py` | (read-only filtering) |
| `04_Test_Question_Parser.py` | `saved_results.py` | `data/saved_results/*.csv`, `data/saved_results/manifest.json` |
| `api/main.py` | `storage.py`, `saved_results.py` | HTTP JSON responses |

All pages read/write through `utils/` modules, never accessing the filesystem directly.

---

## 4. Installation & Setup

### Prerequisites

- Python 3.10 or later
- pip

### Steps

```bash
# 1. Clone the repository
git clone <repo-url>
cd teaching_tools

# 2. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify the data directory structure exists
ls data/                   # Should show extracted_questions/, saved_results/, registry.json
```

### Requirements (`requirements.txt`)

```
streamlit>=1.31
pandas>=2.0
fastapi>=0.111
uvicorn>=0.30
```

No other third-party dependencies. All other imports (`json`, `re`, `pathlib`, `datetime`, `io`) are Python standard library.

---

## 5. Usage Guide

### Streamlit Applications

All Streamlit apps are launched from `app.py`. Use the sidebar to navigate between pages.

#### Main Extractor (`app.py`)

```
streamlit run app.py
```

1. **Prompt Selection** — Choose a week prompt from the sidebar dropdown
2. **Source Text** — Paste OCR or PDF text in the right column
3. **JSON Output** — Paste model-generated JSON in the text area
4. **Validate** — Click "Validate" to check JSON against the schema
5. **Preview** — Click "Preview" to see the formatted data (re-validates against current text)
6. **Save** — Click "Save" to persist to `data/extracted_questions/`
7. **Dataset Registry** — Browse and open previously saved datasets at the bottom

#### Student Dashboard (`01_Student.py`)

```
streamlit run app.py   # then navigate to "Student" in sidebar
```

- Select a student from the dropdown
- View student profile metrics (Name, Grade, School, Lessons count)
- Expand any lesson to see metadata (Week, Date Range, Syllabus), objectives, assessments, practice questions, and attached datasets
- Sort order is determined by week number (extracted from lesson IDs like `week_7_waves`)
- Raw JSON viewer at bottom for debugging

#### Question Explorer (`02_Question.py`)

```
streamlit run app.py   # then navigate to "Question" in sidebar
```

- Select a dataset file from the dropdown
- View overview metrics: Topic, Question count, Unique Files, Calculation Questions
- Use filters: source file (multiselect), syllabus code (multiselect), calculation required (radio), keyword search
- Expand any question to see full details (Summary, Physical Concepts, Variables, Reasoning Focus)
- View analytics: Syllabus Coverage table and Physical Concept Frequency table

#### Combined Question Explorer (`03_Question_Combined.py`)

```
streamlit run app.py   # then navigate to "Question_Combined" in sidebar
```

- Automatically loads all datasets from `data/extracted_questions/`, skipping corrupted files
- View global overview metrics: Datasets Loaded, Total Questions, Unique Topics, Calculation Questions
- Global filters: dataset file, topic, syllabus code, calculation required, keyword
- Combined filtered table with expandable question details
- Analytics: Syllabus Coverage, Topic Distribution, Concept Frequency

#### Test Question Parser (`04_Test_Question_Parser.py`)

```
streamlit run app.py   # then navigate to "Test_Question_Parser" in sidebar
```

1. **Input Settings** (sidebar) — Select test type (MEXT, EJU, A-Level, SAT, ACT, Custom), enter source label, choose input format (Auto/Markdown/CSV/TSV), toggle sample table
2. **Question Table** — Paste a markdown, CSV, or TSV table (sample table loaded by default)
3. **Parsed Data tab** — View and edit the parsed rows inline using Streamlit's data editor
4. **Chapter Summary tab** — See aggregated chapter/subchapter breakdown with bar chart
5. **Export tab** — Save to local storage (`data/saved_results/`) or download as CSV/JSON
6. **Saved Results tab** — Browse, preview, and reload previously saved exports from the manifest

### FastAPI Server

```bash
uvicorn api.main:app --reload --port 8000
```

Base URL: `http://127.0.0.1:8000`

---

## 6. API Reference

| Method | Endpoint | Description | Response |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Health check | `{"status": "ok"}` |
| `GET` | `/datasets/registry` | Full dataset registry | `{"datasets": [...]}` |
| `GET` | `/datasets` | List of dataset metadata entries | `{"datasets": [...]}` |
| `GET` | `/datasets/{filename}` | Load one dataset by filename | Full dataset JSON |
| `GET` | `/saved-results` | List saved table-parser results | `{"saved_results": [...]}` |
| `GET` | `/saved-results/{index}` | Get a saved result by manifest index | `{"meta": {...}, "rows": [...], "columns": [...], "row_count": N}` |

### Example

```bash
# Health check
curl http://127.0.0.1:8000/health

# List all datasets
curl http://127.0.0.1:8000/datasets

# Load a specific dataset
curl http://127.0.0.1:8000/datasets/thermal.json

# List saved results from test parser
curl http://127.0.0.1:8000/saved-results

# Get a specific saved result (by manifest index)
curl http://127.0.0.1:8000/saved-results/0
```

---

## 7. Environment Variables

This project currently requires **no environment variables**. All configuration is file-based:

| Configuration | Location |
| :--- | :--- |
| Prompt templates | `prompts/week*.txt` |
| Dataset storage | `data/extracted_questions/` |
| Saved results | `data/saved_results/` |
| Dataset registry | `data/registry.json` |
| Lesson registry | `data/registry_lesson.json` |
| Saved results manifest | `data/saved_results/manifest.json` |

If deploying with environment-specific paths, create a `.env` file and use `python-dotenv` to load variables like `DATASETS_DIR`, `PROMPTS_DIR`, etc.

---

## 8. Contributing Guide

### How to Contribute

1. **Fork** the repository
2. **Create a feature branch** (`git checkout -b feature/my-feature`)
3. **Make your changes** following the existing code style:
   - Keep functions small and focused
   - Use the existing `as_list()` guard pattern for list fields
   - Add inline comments for any non-obvious logic
   - Maintain pandas version compatibility (2.0+)
4. **Run the app** to verify your changes work:
   ```bash
   streamlit run app.py
   ```
5. **Check for regressions** — load existing datasets and confirm all pages render
6. **Commit** with a clear message describing what and why
7. **Push** and open a Pull Request

### Code Style Guidelines

- Use type hints where practical
- Prefer explicit column assignment over `.rename()` (pandas version compatibility)
- Sanitize all user-supplied file paths with `Path(name).name`
- Wrap list fields with `isinstance(value, list) else []` before iteration
- Test with both pandas 2.0.x and 2.1+ if making DataFrame changes
- Do not modify files in `data/` directly — always go through the `utils/` module functions

---

## 9. License

This project is provided for educational and internal use. No license has been specified. Contact the repository owner for usage terms.

---

# Scaling Guide

---

## 1. Current Bottlenecks — What Breaks First Under Load

| Bottleneck | Component | Why It Breaks |
| :--- | :--- | :--- |
| **File-system storage** | `data/` directory | Every dataset read does a synchronous `Path.read_text()` or `pd.read_csv()`. At ~50 concurrent requests the disk I/O becomes the serialization bottleneck. No connection pooling, no caching. |
| **In-memory Pandas** | All pages | Every page load re-reads and re-parses all JSON/CSV files into DataFrames. With 100+ datasets of 10k+ questions each, memory per Streamlit session exceeds 500 MB. Streamlit runs one Python process per session — OOM kills are the first failure mode. |
| **No query layer** | Syllabus filter, keyword search | Filters iterate in Python (`df.apply(lambda row: kw in str(row).lower(), axis=1)`). O(n*m) per request — no indexes, no query planner. At 1k+ questions per dataset, filter latency exceeds 2 s. |
| **Streamlit process model** | Entire UI | Streamlit reruns the entire script on every interaction. Each rerun reloads all data. Beyond ~10 simultaneous users, the single-process GIL-bound rerender cycle causes timeouts. |
| **Resource registry** | `registry.json`, `manifest.json` | Written as atomic `json.dump`. Concurrent writes from multiple sessions cause race conditions and data loss. No transactional guarantees. |
| **No auth / no tenant isolation** | API + UI | All data is shared across all users. No session scoping. At scale this is both a security and data-partitioning problem. |

---

## 2. Database Scaling

### Immediate (MVP → 1k users)

Replace file-based storage with a relational database.

| Change | Technology | Benefit |
| :--- | :--- | :--- |
| Datasets → tables | PostgreSQL + SQLAlchemy | Atomic writes, concurrent reads, transactional integrity |
| Syllabus codes → junction table | `question_syllabus(question_id, code)` | Normalized queries, proper indexing |
| Full-text search | PostgreSQL `tsvector` / GIN index | Replace O(n) Python filter with indexed `@@ to_tsquery()` |
| Registry → DB table | `datasets` + `saved_results` tables | No more JSON file corruption from concurrent writes |

```sql
-- Example index strategy
CREATE INDEX idx_question_syllabus ON question_syllabus(code);
CREATE INDEX idx_question_calculation ON questions(calculation_required);
CREATE INDEX idx_question_topic ON questions(topic);
CREATE INDEX idx_question_search ON questions USING GIN(to_tsvector('english', question_summary));
```

### Growth (1k → 10k users)

| Technique | Implementation |
| :--- | :--- |
| **Connection pooling** | PgBouncer / Pgpool — reduces PostgreSQL connection overhead |
| **Read replicas** | 1 primary (writes) + 2 replicas (reads). Streamlit reads go to replicas; saves go to primary. |
| **Caching layer** | Redis — cache dataset queries, analytics aggregations, registry snapshots. TTL: 5 min for datasets, 1 h for analytics. |
| **Query result cache** | Materialized views for syllabus coverage and concept frequency, refreshed nightly or on save. |

### Scale (10k → 100k users)

| Technique | Implementation |
| :--- | :--- |
| **Sharding** | Shard by `tenant_id` or `dataset_topic` hash across 4+ PostgreSQL instances |
| **TimescaleDB** | If temporal query patterns emerge (question by exam year), hypertables improve range-scan performance |
| **Elasticsearch** | Replace PostgreSQL full-text search with dedicated ES cluster for complex syllabus + keyword + concept queries |

---

## 3. Backend Scaling

### Streamlit Frontend (current)

**Cannot horizontally scale** — Streamlit's session-per-process model ties one user to one Python process.

| Phase | Solution |
| :--- | :--- |
| 1k users | Run 4–8 Streamlit workers behind **nginx reverse proxy** with sticky sessions (`ip_hash`). Each worker handles ~5–10 concurrent sessions. |
| 10k users | **Replace Streamlit** with a decoupled frontend. Keep Streamlit only for internal/admin dashboards. Build a dedicated frontend (see Section 4). |
| 100k users | Streamlit removed entirely or used as a read-only admin panel on isolated infrastructure. |

### FastAPI Backend

| Phase | Scaling |
| :--- | :--- |
| 1k users | Single Uvicorn process behind nginx. Add `--workers 4` for multi-core. |
| 10k users | **Horizontal scaling**: 3–6 Uvicorn instances behind **AWS ALB** / nginx upstream. Containerize with Docker. Health-check endpoints (`/health`) for load balancer targets. |
| 100k users | **Auto-scaling group** (CPU > 70% → spawn new instance). **Async DB driver** (`asyncpg` instead of `psycopg2`) to handle 5k+ concurrent connections per instance. |

### Background Jobs

| Task | Tool | Reason |
| :--- | :--- | :--- |
| Dataset import / reindex | Celery + Redis broker | Prevent 30-second import from blocking the API |
| Analytics aggregation | Celery beat (scheduled) | Pre-compute syllabus coverage hourly instead of on every page load |
| Cache warm | Celery beat | Keep Redis hot for common queries |

---

## 4. Frontend Scaling

### Current: Monolithic Streamlit

**Bottleneck**: Entire page rerenders on every interaction. No code splitting, no lazy loading.

### Recommended Migration Path

| Phase | Architecture |
| :--- | :--- |
| **MVP → 1k users** | Keep Streamlit. Add **nginx caching** for static assets. Enable Streamlit's `runner.fastReruns = true` and `server.enableCORS = false`. |
| **1k → 10k users** | Build a decoupled **React / Next.js** SPA. Streamlit becomes a headless backend for data APIs, or is replaced entirely. |
| **10k → 100k users** | Next.js with **ISR (Incremental Static Regeneration)** for dataset pages. **CDN** (CloudFront / Cloudflare) for static builds. |

### CDN Strategy

| Asset | Cache Strategy |
| :--- | :--- |
| Streamlit static files (JS/CSS) | CloudFront with 1-year cache + versioned hash in URL |
| Dataset JSON responses | CDN with 5-min TTL, purged on save |
| CSV exports | Pre-signed S3 URLs, 15-min expiry |

### Frontend Optimizations

| Technique | When |
| :--- | :--- |
| Lazy load tab content | Always — Streamlit renders all tabs, wasting resources |
| Virtual scrolling (react-window) | 10k+ questions — only render visible rows |
| Debounced search input | Keyword filter — wait 300 ms after keystroke |
| SSR for public pages | Next.js `getStaticProps` for dataset detail pages |
| Skeleton loading | Replace Streamlit spinners with skeleton placeholders |

---

## 5. Infrastructure Recommendations

### Stack: AWS (primary) — equivalent services exist on GCP / Azure

| Service | Purpose | Estimated Cost |
| :--- | :--- | :--- |
| **EC2 / ECS Fargate** | Streamlit + FastAPI containers | $30–150 / mo |
| **RDS PostgreSQL** | Primary database | $15–200 / mo (db.t3.micro → db.r6g.large) |
| **ElastiCache Redis** | Caching layer | $15–80 / mo (cache.t3.micro → cache.r6g.large) |
| **S3** | CSV exports, dataset backups | < $1 / mo at 10k users |
| **CloudFront** | CDN for static assets | $10–50 / mo |
| **ALB** | Load balancer for API workers | $20 / mo |
| **Route53** | DNS | $0.50 / mo |

### Deployment Pipeline

```
Git push → GitHub Actions → Docker build → ECR → ECS deploy
```

### Monitoring Stack

| Tool | Purpose |
| :--- | :--- |
| **CloudWatch** | CPU, memory, request latency, error rates |
| **Sentry** | Application error tracking (Python + frontend) |
| **PagerDuty** | Alert on p99 latency > 2 s or error rate > 1% |

---

## 6. Cost Estimates

| Tier | Users | Monthly Infra Cost | Key Assumptions |
| :--- | :--- | :--- | :--- |
| **MVP** | 1k | **~$50–80** | 1× t3.medium EC2 (Streamlit + API), 1× db.t3.micro RDS, 1× cache.t3.micro Redis, no CDN |
| **Growth** | 10k | **~$300–500** | 2–3× t3.large ECS tasks (API), 1× db.r6g.large RDS + read replica, 1× cache.r6g.large Redis, CloudFront, ALB |
| **Enterprise** | 100k | **~$2,000–4,000** | 6–10× ECS tasks (auto-scale), 2× db.r6g.2xlarge RDS + 2 replicas, Redis cluster (3 shards), CloudFront, ALB, Elasticsearch (2 nodes), SNS/SES for notifications |

### Cost Breakdown at 100k Users

| Item | Monthly |
| :--- | :--- |
| ECS Fargate (10 tasks @ 2 vCPU / 4 GB) | ~$700 |
| RDS (2× db.r6g.2xlarge + 2 replicas) | ~$1,800 |
| ElastiCache Redis (3 shards) | ~$400 |
| ALB | ~$25 |
| CloudFront (10 TB) | ~$200 |
| Elasticsearch (2 nodes) | ~$200 |
| S3 + Data transfer | ~$50 |
| Monitoring (CloudWatch + Sentry) | ~$100 |
| **Total** | **~$3,475** |

---

## 7. Scaling Roadmap

### Phase 0 — Current State (0 users)

- File-based storage
- Single-process Streamlit
- No caching, no auth, no CI/CD
- **Time to implement: already deployed**

### Phase 1 — Foundation (0 → 1k users, 1–2 months)

| Step | Effort | Impact |
| :--- | :--- | :--- |
| Replace file storage with PostgreSQL + SQLAlchemy | 2 weeks | Eliminates file-corruption race conditions |
| Add basic nginx reverse proxy | 2 days | Enables multiple Streamlit workers |
| Parameterize config via `.env` | 1 day | Environment-agnostic deployments |
| Dockerize the app | 3 days | Reproducible deploys |
| GitHub Actions CI/CD | 2 days | Automated testing + deploy |
| **Cost: ~$80/mo** | | |

### Phase 2 — Growth (1k → 10k users, 2–4 months)

| Step | Effort | Impact |
| :--- | :--- | :--- |
| Decouple frontend (Next.js + FastAPI backend) | 4–6 weeks | Streamlit is the #1 bottleneck at scale |
| Add Redis caching layer | 1 week | 10× faster analytics page loads |
| Implement Celery background jobs | 1 week | Dataset imports no longer block UI |
| Add read replicas + PgBouncer | 3 days | 5× read throughput |
| Full-text search with PostgreSQL GIN indexes | 2 days | Sub-100 ms keyword queries |
| User authentication (Auth0 / Cognito) | 1 week | Tenant isolation |
| **Cost: ~$400/mo** | | |

### Phase 3 — High Scale (10k → 100k users, 4–8 months)

| Step | Effort | Impact |
| :--- | :--- | :--- |
| Horizontal auto-scaling for API | 1 week | Handles traffic spikes |
| Database sharding + Elasticsearch | 2–4 weeks | Sub-second queries at 100k datasets |
| CDN + edge caching | 1 week | Static assets served from 300+ PoPs |
| Premium monitoring + alerting | 3 days | Proactive incident response |
| Multi-region failover (active-passive) | 2 weeks | 99.99% uptime |
| **Cost: ~$3,500/mo** | | |

### Phase 4 — Maturity (100k+ users)

- **Streaming analytics** — Replace batch Celery with Kafka + Flink for real-time dataset processing
- **A/B testing infra** — LaunchDarkly / Flagsmith for feature flags
- **Custom query language** — DSL for syllabus graph traversal (e.g., "find all questions covering P3.1 and P3.2 but requiring calculation")
- **Data lake** — Export all datasets to S3 Parquet for Athena / Redshift analytics
