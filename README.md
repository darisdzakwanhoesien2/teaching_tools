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
