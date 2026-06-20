# 🧠 Teaching Tools: Curriculum Question Extractor & Test Parser

Welcome to the modernized and audited **Teaching Tools** repository. This project provides Streamlit-based tools and a FastAPI service to extract, validate, and manage educational curriculum question datasets.

As requested, the old `README.md` has been safely archived inside [notes.md](file:///home/ubuntu/apps/fixing_repo/teaching_tools/notes.md).

---

## 🛠️ Codebase Audit & Fixed Issues

During the comprehensive audit of the codebase, several major bugs, compatibility issues, and security vulnerabilities were identified and resolved. Below is a detailed summary of the fixes applied:

### 1. Identify Bugs, Errors, or Broken Logic & Applied Fixes

| Component | Identified Issue | Impact | Action Taken / Fix |
| :--- | :--- | :--- | :--- |
| **Pandas Compatibility**<br>`utils/saved_results.py` | Used `df.map(strip_markdown)`. The `DataFrame.map` method was introduced in pandas 2.1.0. | Will raise `AttributeError: 'DataFrame' object has no attribute 'map'` on environments running pandas 2.0.x (as specified in `requirements.txt`). | Modified the mapping logic to use a version-safe conditional execution. It checks for `.map` availability, falling back to `.applymap` (which is supported globally across all versions of pandas). |
| **Pandas 2.0 Value Counts**<br>`pages/02_Question.py`<br>`pages/03_Question_Combined.py` | Used `.rename(columns={"index": "Syllabus", "syllabus_codes": "Count"})` after calling `.value_counts().reset_index()`. | In pandas 2.0+, `Series.value_counts().reset_index()` returns columns `[Series.name, "count"]` instead of `["index", Series.name]`. The old rename call failed to rename `"count"`, and renamed `"syllabus_codes"` to `"Count"`, resulting in wrong column headers (`"Count"` and `"count"`). | Updated the logic to explicitly assign `.columns = [...]` directly to the `reset_index` output, bypassing version-specific column label assumptions. |
| **Path Traversal Security**<br>`utils/storage.py` | `load_dataset(filename)` directly appended `filename` to the dataset path directory: `DATASETS_DIR / filename`. | A malicious user could perform a path-traversal exploit (e.g. via API `/datasets/../../secrets.json`) to read arbitrary JSON files outside of the target datasets directory. | Sanitized the filename input using `Path(filename).name`, which isolates the file name from any directory structure. |
| **Streamlit Key Index Lookup**<br>`pages/04_Test_Question_Parser.py` | Stored `saved_labels = ["No saved dataset selected"] + ...` and resolved selections using `saved_labels.index(selected_saved_label) - 1`. | If multiple saved results had identical names and row counts, the `.index()` lookup would always resolve to the first matching index, loading the wrong file. | Rewrote the selectbox option mapping to use list indices (`range(len(saved_entries))`) with a custom `format_func` formatter to ensure robust mapping. |
| **Stale/Unvalidated JSON Save**<br>`app.py` | "Preview" and "Save" buttons used `st.session_state["validated_data"]` directly without ensuring it matched the current text area. | A user could edit the JSON text area and click "Save" or "Preview" without re-validating, causing stale/mismatched data to be saved. | Added checks inside the "Preview" and "Save" click handlers to verify that the current text area content matches the validated session state, showing a warning to re-validate if they differ. |
| **Student Lesson Sorting**<br>`pages/01_Student.py` | Alice and Bob did not have explicit `week` numbers defined in `registry_lesson.json`. | The lesson sorting returned default values of `999`, sorting them arbitrarily or incorrectly. | Implemented a regex helper `get_week_number` to parse week numbers out of lesson IDs (e.g., `week_7_waves` -> 7) if the `"week"` key is missing. |
| **Missing List Validation**<br>`pages/01_Student.py` | Directly computed `len(lesson.get("datasets", []))` and looped over nested lists. | If registry datasets or questions keys were present but malformed/None, the page crashed. | Added type guards (`isinstance(..., list)`) to all nested list operations. |

### 2. Code Cleanups & Readability
- **Removed Redundant Lookups**: Replaced nested list index lookups with direct object mappings.
- **Unified Path Resolution**: Standardized `Path` operations and added explicit directory sanitization.
- **Enhanced Visual State Indicators**: Replaced generic error blocks with helpful warnings and formatting inside the Streamlit user interfaces.

### 3. Inline Comments Added
Detailed inline comments were added to all complex blocks, particularly:
- The version-safe Pandas DataFrame element mapping.
- The Streamlit index-based selection formatting mechanism.
- Stale content validation mechanisms in `app.py`.
- Lesson key regex week extraction in the student dashboard.

---

## 🗂️ Project Directory Structure

- [app.py](file:///home/ubuntu/apps/fixing_repo/teaching_tools/app.py): Main Streamlit application UI for curriculum extraction.
- **pages/**:
  - [pages/01_Student.py](file:///home/ubuntu/apps/fixing_repo/teaching_tools/pages/01_Student.py): Student profile and lesson plan dashboard.
  - [pages/02_Question.py](file:///home/ubuntu/apps/fixing_repo/teaching_tools/pages/02_Question.py): Individual dataset question search and coverage explorer.
  - [pages/03_Question_Combined.py](file:///home/ubuntu/apps/fixing_repo/teaching_tools/pages/03_Question_Combined.py): Unified curriculum search across all datasets.
  - [pages/04_Test_Question_Parser.py](file:///home/ubuntu/apps/fixing_repo/teaching_tools/pages/04_Test_Question_Parser.py): Test question table parser (from Markdown, CSV, TSV) and CSV saver.
- **utils/**:
  - [utils/storage.py](file:///home/ubuntu/apps/fixing_repo/teaching_tools/utils/storage.py): JSON persistence, registry management, and path sanitization.
  - [utils/json_validator.py](file:///home/ubuntu/apps/fixing_repo/teaching_tools/utils/json_validator.py): Standard JSON schema validation for curriculum questions.
  - [utils/saved_results.py](file:///home/ubuntu/apps/fixing_repo/teaching_tools/utils/saved_results.py): Table parsing, CSV saving, and manifest handlers.
  - [utils/lesson_registry.py](file:///home/ubuntu/apps/fixing_repo/teaching_tools/utils/lesson_registry.py): Operations for `registry_lesson.json`.
- [api/main.py](file:///home/ubuntu/apps/fixing_repo/teaching_tools/api/main.py): FastAPI server providing external HTTP access to extracted datasets and CSV records.

---

## 🚀 Getting Started

### 1. Installation

Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Running the Streamlit App

```bash
streamlit run app.py
```

### 3. Running the FastAPI Server

```bash
uvicorn api.main:app --reload --port 8000
```
API endpoints are served at `http://127.0.0.1:8000`. Refer to `api/main.py` for GET routes:
- `/health`
- `/datasets/registry`
- `/datasets/{filename}`
- `/saved-results`
- `/saved-results/{index}`
