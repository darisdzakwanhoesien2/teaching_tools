https://chatgpt.com/c/696b5421-66fc-832f-8c5b-0a61d199f29f

Perfect 👍
Let’s lock this into a **production-ready mini project** that you can directly run, extend, and integrate into your broader Streamlit ecosystem.

You’ll get:

✅ Clean project structure
✅ Prompt registry
✅ Dataset storage + registry
✅ JSON validation
✅ Streamlit UI
✅ Dataset browser
✅ Zero hidden dependencies

This fits nicely with how you’ve been organizing your Streamlit tooling lately.

---

# 🗂️ Project Directory Structure

Create this structure:

```
curriculum_question_extractor/
│
├── app.py
├── requirements.txt
│
├── data/
│   ├── extracted_questions/
│   └── registry.json
│
├── prompts/
│   ├── week01.txt
│   ├── week02.txt
│   ├── week03.txt
│   ├── week04.txt
│   ├── week05.txt
│   ├── week06.txt
│   ├── week07.txt
│   └── week08.txt
│
└── utils/
    ├── __init__.py
    ├── prompt_loader.py
    ├── json_validator.py
    ├── storage.py
```

Great — this is exactly the kind of structured data your pipeline should be storing 👍
You already have **valid JSON objects per topic**. Now the question is:

> ✅ How do we store these reliably so that:
>
> * Multiple topic files can be saved
> * They are discoverable later
> * Streamlit can list, load, filter, and visualize them
> * A registry tracks what has been saved

This aligns very well with your existing dataset registry patterns (which you’ve used in other projects).

---

# 🗂️ Recommended Storage Design

## 📁 Folder Structure

data/extracted_questions/reflection_of_light_20260117_101522.json

```
data/
├── extracted_questions/
│   ├── reflection_of_light_20260117_101522.json
│   ├── wave_properties_20260117_101735.json
│   └── ...
│
└── registry.json
```

---

## 🧾 Example: Stored File (unchanged)

You store each topic as its own JSON file exactly as you already have:

```json
{
  "topic": "Reflection of light using mirrors",
  "questions": [ ... ]
}
```

✔ No modification needed
✔ Human readable
✔ Easy to version
✔ Easy to diff

---

---

# 🧠 Registry Design

This file tracks what has been saved.

## 📄 `data/registry.json`

```json

```

This enables:

✅ Dropdown selection
✅ Dataset tracking
✅ Analytics later
✅ No hardcoding

---

---

# 🧩 Storage Utility Code

Create this file:

---

## 📄 `utils/storage.py`

```python

```

---

---

# 🖥️ Update Streamlit Save Button

In your Streamlit app replace the save logic with this:

```python
from utils.storage import save_dataset

if st.button("💾 Save Dataset"):
    data = st.session_state.get("validated_data")
    if not data:
        st.warning("Validate JSON first.")
    else:
        path, entry = save_dataset(data)
        st.success("Dataset saved successfully!")
        st.json(entry)
```

---

---

# 📊 Optional: Registry Viewer (Highly Recommended)

Add this block in Streamlit:

```python
from utils.storage import load_registry

st.divider()
st.subheader("📚 Dataset Registry")

registry = load_registry()
if registry["datasets"]:
    st.dataframe(registry["datasets"], use_container_width=True)
else:
    st.info("No datasets saved yet.")
```

---

---

# ✅ What You Get

---

---

# 🚀 Next Up (Your Choice)

We can now:

✅ Build Dataset Browser Page
✅ Filter questions by syllabus code
✅ Merge datasets
✅ Export CSV / Excel
✅ Analytics dashboard
✅ Question coverage heatmap
✅ Auto-tagging
✅ Prompt version tracking

Just tell me what you’d like next 😄


---

# 📦 requirements.txt

```
streamlit>=1.31
pandas>=2.0
```

Install:

```bash
pip install -r requirements.txt
```

---

# 🧠 utils/prompt_loader.py

```python

```

---

# ✅ utils/json_validator.py

```python

```

---

# 💾 utils/storage.py

```python

```

---

# 🚀 app.py (Main Streamlit App)

```python

```

---

# ▶️ How To Run

From project root:

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

# ✅ What This Gives You

✔ Prompt management
✔ Structured extraction workflow
✔ JSON validation
✔ Dataset storage
✔ Registry tracking
✔ Dataset browser
✔ DataFrame visualization
✔ Extensible architecture

This matches the kind of modular tooling you’ve been building across your Streamlit ecosystem 👌

---

# 🚀 Optional Next Enhancements

If you want, we can add:

🔥 Auto-merge datasets
🔥 Syllabus coverage analytics
🔥 CSV / Excel export
🔥 Search + filter UI
🔥 Question deduplication
🔥 Prompt versioning
🔥 Batch ingestion
🔥 Visual dashboards

Just say which direction you want next 😄

Great — let’s reset cleanly and give you a **fully working, copy-paste ready project** so there are no more import mismatches or missing functions.
If you follow this exactly, the error you saw will disappear ✅

---

# ✅ STEP 1 — Project Folder Structure

Create this structure exactly:

```
teaching_tools/
│
├── app.py
├── requirements.txt
│
├── prompts/
│   ├── week01.txt
│   ├── week02.txt
│   └── week08.txt
│
├── data/
│   ├── extracted_questions/
│   └── registry.json
│
└── utils/
    ├── __init__.py
    ├── prompt_loader.py
    ├── json_validator.py
    └── storage.py
```

> ⚠️ Make sure `utils/__init__.py` exists (even empty).

---

# ✅ STEP 2 — requirements.txt

Create:

📄 `requirements.txt`

```
streamlit>=1.31
pandas>=2.0
```

Install:

```bash
pip install -r requirements.txt
```

---

# ✅ STEP 3 — utils/prompt_loader.py  (FIXED)

📄 `utils/prompt_loader.py`

```python

```

---

# ✅ STEP 4 — utils/json_validator.py

📄 `utils/json_validator.py`

```python

```

---

# ✅ STEP 5 — utils/storage.py

📄 `utils/storage.py`

```python

```

---

# ✅ STEP 6 — utils/**init**.py

📄 `utils/__init__.py`

```python
# required for Python package detection
```

(Empty file is fine.)

---

# ✅ STEP 7 — app.py  (FULL WORKING APP)

📄 `app.py`

```python

```

---

# ✅ STEP 8 — Run It

From inside `teaching_tools/`:

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

# 🎉 You Now Have

✅ Prompt loader
✅ JSON validator
✅ Dataset storage
✅ Registry tracking
✅ Dataset browser
✅ Zero import errors
✅ Clean project layout

---

---

# 🚀 If You Want Next

We can now add:

✅ Search / filter
✅ CSV export
✅ Merge datasets
✅ Analytics
✅ Prompt editor
✅ Auto-run LLM

Just say 👍
# teaching_tools

---

# 📁 Original README.md (Archived)

# Teaching Tools

Streamlit-based tooling for:
- Curriculum question extraction from OCR/PDF text into validated JSON datasets
- Test question table parsing (Markdown/CSV/TSV) into reusable saved datasets
- Local dataset browsing and analytics
- HTTP API access to existing datasets

## Features

- Prompt-driven extraction workflow (`app.py`)
- Schema validation and JSON dataset registry (`data/registry.json`)
- Single and combined question explorers (`pages/02_Question.py`, `pages/03_Question_Combined.py`)
- Integrated test question parser (migrated from `_temp`) (`pages/04_Test_Question_Parser.py`)
- Saved result manifest + CSV storage (`data/saved_results/manifest.json`)
- FastAPI endpoints for existing extracted datasets and saved results (`api/main.py`)

## Project Structure

- `app.py`: Main Curriculum Question Extractor UI
- `pages/01_Student.py`: Student and lesson dashboard
- `pages/02_Question.py`: Per-dataset question explorer
- `pages/03_Question_Combined.py`: Unified multi-dataset explorer
- `pages/04_Test_Question_Parser.py`: Test question parser and saved-results manager
- `api/main.py`: HTTP API for datasets and saved results
- `utils/storage.py`: Extracted dataset persistence and registry utilities
- `utils/json_validator.py`: JSON schema validator for extracted question datasets
- `utils/saved_results.py`: Parser + saved-results storage/manifests for table-based datasets
- `prompts/`: Prompt templates
- `data/extracted_questions/`: Saved extracted JSON datasets
- `data/saved_results/`: Saved CSV datasets and manifest

## Installation

```bash
pip install -r requirements.txt
```

## Run Streamlit App

```bash
streamlit run app.py
```

Then use page navigation in Streamlit sidebar to access:
- `01_Student`
- `02_Question`
- `03_Question_Combined`
- `04_Test_Question_Parser`

## Run API Server

```bash
uvicorn api.main:app --reload --port 8000
```

Base URL: `http://127.0.0.1:8000`

## API Endpoints

- `GET /health`
  - Health check

- `GET /datasets/registry`
  - Full extracted dataset registry

- `GET /datasets`
  - List extracted dataset metadata entries

- `GET /datasets/{filename}`
  - Get one extracted dataset JSON file from `data/extracted_questions/`

- `GET /saved-results`
  - List saved table-parser datasets from `data/saved_results/manifest.json`

- `GET /saved-results/{index}`
  - Get saved result by manifest index, including metadata + row data

## Data Model Overview

### Extracted dataset JSON (`data/extracted_questions/*.json`)

Root keys:
- `topic`
- `questions` (array)

Per-question required fields:
- `filename`
- `question_number`
- `topic`
- `syllabus_codes`
- `question_summary`
- `physical_concepts`
- `variables_involved`
- `reasoning_focus`
- `calculation_required`

### Saved table-parser datasets (`data/saved_results/*.csv`)

Typical columns:
- `Test`
- `Source`
- `Parsed At`
- `Question ID`
- `Question`
- `Main Chapter`
- `Subchapter`
- `Secondary Subchapters`
- `Reasoning`

## Notes

- Legacy temp files existed as `README_temp.md` and `app_temp.py`; their functionality is integrated.
- Historical draft notes remain in `notes.md`.
