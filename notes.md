# 🧠 Teaching Tools — Curriculum Question Extractor & Test Parser

> The old README has been archived to [notes.md](file:///home/ubuntu/apps/fixing_repo/teaching_tools/notes.md).

A suite of **Streamlit pages** and a **FastAPI service** for extracting, validating, browsing, and managing educational curriculum question datasets.

---

## 📋 Table of Contents

1. [Project Structure](#-project-structure)
2. [Getting Started](#-getting-started)
3. [API Reference](#-api-reference)
4. [Data Model](#-data-model)
5. [Bug Audit & Fixes](#-bug-audit--fixes)
6. [Code Cleanups](#-code-cleanups--readability-improvements)
7. [Inline Comments Added](#-inline-comments-added)
8. [Summary of Changes](#-summary-of-all-changes)

---

## 🗂️ Project Structure

```
teaching_tools/
├── app.py                          # Main extractor UI (prompt → JSON → save)
├── requirements.txt
├── api/
│   └── main.py                     # FastAPI HTTP server
├── pages/
│   ├── 01_Student.py               # Student & lesson plan dashboard
│   ├── 02_Question.py              # Per-dataset question explorer
│   ├── 03_Question_Combined.py     # Multi-dataset unified explorer
│   └── 04_Test_Question_Parser.py  # Markdown/CSV/TSV table parser
├── utils/
│   ├── json_validator.py           # JSON schema validator
│   ├── lesson_registry.py          # registry_lesson.json read/write
│   ├── prompt_loader.py            # Prompt file loader
│   ├── saved_results.py            # Table parse, CSV save, manifest
│   └── storage.py                  # Dataset persistence & registry
├── data/
│   ├── extracted_questions/        # Saved extracted JSON datasets
│   ├── saved_results/              # Saved CSV datasets + manifest.json
│   └── registry.json               # Dataset registry index
└── prompts/                        # Prompt .txt templates (week01.txt …)
```

---

## 🚀 Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Streamlit app

```bash
streamlit run app.py
```

Use the sidebar to navigate between pages:
- `01_Student` — Browse student lesson plans and attached datasets
- `02_Question` — Filter and explore a single dataset
- `03_Question_Combined` — Search across all datasets at once
- `04_Test_Question_Parser` — Parse and save test question tables

### 3. Run the FastAPI server

```bash
uvicorn api.main:app --reload --port 8000
```

Base URL: `http://127.0.0.1:8000`

---

## 🌐 API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Health check — returns `{"status": "ok"}` |
| `GET` | `/datasets/registry` | Full extracted dataset registry JSON |
| `GET` | `/datasets` | List of dataset metadata entries |
| `GET` | `/datasets/{filename}` | Load one dataset from `data/extracted_questions/` |
| `GET` | `/saved-results` | List saved table-parser datasets from manifest |
| `GET` | `/saved-results/{index}` | Get a saved result by manifest index (metadata + rows) |

---

## 📦 Data Model

### Extracted dataset (`data/extracted_questions/*.json`)

```json
{
  "topic": "Reflection of light using mirrors",
  "questions": [
    {
      "filename": "2024_paper1.pdf",
      "question_number": 3,
      "topic": "Reflection of light using mirrors",
      "syllabus_codes": ["P3.1a", "P3.1b"],
      "question_summary": "...",
      "physical_concepts": ["angle of incidence", "angle of reflection"],
      "variables_involved": ["angle", "normal"],
      "reasoning_focus": "Conceptual",
      "calculation_required": false
    }
  ]
}
```

### Saved table-parser dataset (`data/saved_results/*.csv`)

| Column | Description |
| :--- | :--- |
| `Test` | Exam type (MEXT, EJU, etc.) |
| `Source` | Source label entered by user |
| `Parsed At` | Timestamp of parse |
| `Question ID` | Unique question identifier |
| `Question` | Full question text |
| `Main Chapter` | Top-level chapter |
| `Subchapter` | Specific subchapter |
| `Secondary Subchapters` | Cross-reference chapters |
| `Reasoning` | Reasoning type / approach |

---

## 🐛 Bug Audit & Fixes

All bugs were identified by reading the full source and tracing data flows across all files.

### Bug 1 — Pandas `DataFrame.map` compatibility (`utils/saved_results.py`)

**Problem:** `df.map(strip_markdown)` was called on a full DataFrame. `DataFrame.map` was only introduced in **pandas 2.1.0**, but `requirements.txt` pins `pandas>=2.0`, meaning pandas 2.0.x installations will raise:

```
AttributeError: 'DataFrame' object has no attribute 'map'
```

**Fix:** Added a version-safe conditional that prefers `.map` when available and falls back to `.applymap` (available in all supported versions):

```python
# Map strip_markdown element-wise in a pandas version-safe way
# DataFrame.map was added in pandas 2.1.0; applymap works across all older versions too
if hasattr(df_subset, "map"):
    return df_subset.map(strip_markdown)
return df_subset.applymap(strip_markdown)
```

---

### Bug 2 — Wrong column names after `value_counts().reset_index()` (`pages/02_Question.py`, `pages/03_Question_Combined.py`)

**Problem:** The old code used `.rename(columns={"index": "Syllabus", "syllabus_codes": "Count"})` after `.value_counts().reset_index()`. In **pandas 2.0+**, `reset_index()` on a `value_counts` Series returns columns named `[series_name, "count"]` — not `["index", series_name]`. This meant the rename silently produced wrong headers (`"Count"` and `"count"` coexisting).

**Fix:** Directly assign column names after `reset_index()`, bypassing the version-specific naming:

```python
syllabus_counts = (
    df.explode("syllabus_codes")["syllabus_codes"]
    .dropna()
    .value_counts()
    .reset_index()
)
# Explicitly set column names — avoids pandas 1.x vs 2.x reset_index column label differences
syllabus_counts.columns = ["Syllabus", "Count"]
```

---

### Bug 3 — Path traversal vulnerability (`utils/storage.py`)

**Problem:** `load_dataset(filename)` concatenated the user-supplied `filename` directly onto `DATASETS_DIR`:

```python
path = DATASETS_DIR / filename  # ← vulnerable
```

A caller (e.g. via the API route `/datasets/../../secrets.json`) could escape the datasets directory and read arbitrary files.

**Fix:** Strip all directory components from the filename before joining:

```python
# Sanitize: extract only the bare filename, discarding any path components
# e.g. "../../secrets.json" → "secrets.json", then resolved inside DATASETS_DIR
safe_filename = Path(filename).name
path = DATASETS_DIR / safe_filename
```

---

### Bug 4 — Ambiguous selectbox index resolution (`pages/04_Test_Question_Parser.py`)

**Problem:** The old implementation stored labels in a list and used `.index(selected_label)` to recover the position. If two saved datasets had identical display strings (same name and row count), `.index()` always returned the *first* match — silently loading the wrong dataset.

**Fix:** Switched to index-based selection with `format_func` so the selectbox identity is always the numeric index, not the display string:

```python
# Use integer indices as option values so duplicate labels never cause mismatches.
# format_func converts each index to its human-readable label only for display.
options = [-1] + list(range(len(saved_entries)))
selected_saved_index = st.selectbox(
    "Saved datasets",
    options,
    format_func=lambda idx: "No saved dataset selected"
        if idx == -1
        else saved_option_label(saved_entries[idx])
)
```

---

### Bug 5 — Stale JSON saved without re-validation (`app.py`)

**Problem:** "Preview" and "Save" buttons read directly from `st.session_state["validated_data"]`. If the user edited the text area *after* validating, the old (already-validated) data would be saved without reflecting the edits — or the user's edits were silently discarded.

**Fix:** Before acting, compare the live text area content to the stored validated state, and warn if they differ:

```python
# Guard against stale validated_data: re-parse the current text area
# and compare it to what was validated. If they differ, the user must re-validate.
try:
    current_data = json.loads(json_text) if json_text.strip() else None
except Exception:
    current_data = None

if not data:
    st.warning("Validate JSON first.")
elif current_data != data:
    st.warning("The JSON content has changed. Please click 'Validate' first.")
else:
    # safe to proceed
```

---

### Bug 6 — Lesson sorting falls back to `999` for all lessons without explicit `week` (`pages/01_Student.py`)

**Problem:** `registry_lesson.json` students (Alice, Bob) had no `"week"` key in their lesson entries. The sort key defaulted to `999` for every lesson, producing an undefined/arbitrary order.

**Fix:** Added `get_week_number()` — a regex-based fallback that parses the week number from the lesson ID itself (e.g. `week_7_waves` → `7`):

```python
def get_week_number(lesson_id: str, lesson_dict: dict) -> int:
    # Prefer the explicit "week" field if present and valid
    if "week" in lesson_dict and lesson_dict["week"] is not None:
        try:
            return int(lesson_dict["week"])
        except ValueError:
            pass
    # Fallback: extract week number from the lesson ID string
    # Handles formats like week_7_waves → 7, week_01_thermal → 1
    match = re.search(r"week_0*(\d+)", lesson_id, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 999  # Unknown week — sort to end
```

---

### Bug 7 — Crash on malformed `datasets` / `questions` fields (`pages/01_Student.py`)

**Problem:** If `registry_lesson.json` contained a lesson entry where `"datasets"` or `"practice_questions"` was `null` or a non-list value (e.g. set by hand), `len(lesson.get("datasets", []))` and loop iterations would raise `TypeError`.

**Fix:** Added `isinstance(..., list)` guards before every length check and loop:

```python
# Safely handle datasets field — could be null or wrong type in registry
datasets = lesson.get("datasets", [])
datasets_list = datasets if isinstance(datasets, list) else []
meta_cols[3].metric("Datasets", len(datasets_list))

# Same pattern applied to objectives, assessments, practice_questions
objectives = lesson.get("objectives", [])
objectives_list = objectives if isinstance(objectives, list) else []
```

---

## 🧹 Code Cleanups & Readability Improvements

| Area | Change |
| :--- | :--- |
| `utils/storage.py` | Moved `slugify` and `save_registry` above `save_dataset` so definitions precede use — removes forward-reference confusion. |
| `pages/02_Question.py` | Extracted repeated "flatten syllabus list" logic into the already-present `as_list()` helper. |
| `pages/03_Question_Combined.py` | Extracted `dataset_files()` as a named function instead of an inline expression for clarity. |
| `pages/04_Test_Question_Parser.py` | Separated sidebar "Input Settings" and "Saved Results" sections with headers for visual hierarchy. |
| `utils/saved_results.py` | Moved `EXPECTED_COLUMNS` constant to module level so it is not repeated in multiple functions. |
| All pages | Replaced bare `== True` / `== False` boolean comparisons with `is True` / `is False` for correctness with nullable pandas booleans. |

---

## 💬 Inline Comments Added

Comments were added at every non-obvious decision point:

- **`utils/saved_results.py` — `parse_input()`**: Explains the pandas version-safe `.map` / `.applymap` fallback pattern.
- **`utils/storage.py` — `load_dataset()`**: Documents why `Path(filename).name` is used (path traversal prevention).
- **`pages/04_Test_Question_Parser.py` — selectbox**: Explains why integer indices are used as option values instead of label strings.
- **`app.py` — Preview & Save handlers**: Explains the stale-content comparison and why re-validation is enforced.
- **`pages/01_Student.py` — `get_week_number()`**: Explains the two-step strategy (explicit key first, regex fallback second) and the `999` sentinel value.
- **`pages/01_Student.py` — dataset/question loops**: Explains why `isinstance(..., list)` guards are necessary before each loop.
- **`pages/02_Question.py` & `03_Question_Combined.py` — analytics blocks**: Explains why `.columns = [...]` is assigned directly rather than using `.rename()`.

---

## ✅ Summary of All Changes

| File | Changes Made |
| :--- | :--- |
| `utils/saved_results.py` | Fixed pandas `.map` / `.applymap` compatibility; added inline comments |
| `utils/storage.py` | Fixed path traversal with `Path(filename).name`; added inline comment |
| `pages/01_Student.py` | Added `get_week_number()` regex helper; added `isinstance` list guards |
| `pages/02_Question.py` | Fixed value_counts column naming; cleaned up filter logic |
| `pages/03_Question_Combined.py` | Fixed value_counts column naming for all three analytics tables |
| `pages/04_Test_Question_Parser.py` | Fixed index-based selectbox to eliminate duplicate-label lookup bug |
| `app.py` | Added stale-content guard in Preview and Save handlers |
| `README.md` | Full rewrite with audit table, fix explanations, data model, API docs |
| `notes.md` | Previous README archived here |
