from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException

from utils.storage import load_dataset, load_registry
from utils.saved_results import load_manifest


app = FastAPI(title="Teaching Tools API", version="1.0.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/datasets/registry")
def datasets_registry() -> dict:
    return load_registry()


@app.get("/datasets")
def list_datasets() -> dict:
    registry = load_registry()
    return {"datasets": registry.get("datasets", [])}


@app.get("/datasets/{filename}")
def get_dataset(filename: str) -> dict:
    data = load_dataset(filename)
    if not data:
        raise HTTPException(status_code=404, detail=f"Dataset not found: {filename}")
    return data


@app.get("/saved-results")
def list_saved_results() -> dict:
    manifest = load_manifest()
    return {"saved_results": manifest}


@app.get("/saved-results/{index}")
def get_saved_result(index: int) -> dict:
    manifest = load_manifest()
    if index < 0 or index >= len(manifest):
        raise HTTPException(status_code=404, detail=f"Saved result index out of range: {index}")

    entry = manifest[index]
    csv_path = Path(entry.get("file", ""))
    if not csv_path.exists():
        raise HTTPException(status_code=404, detail=f"Saved result file missing: {csv_path}")

    try:
        df = pd.read_csv(csv_path, dtype=str).fillna("")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to read saved result: {exc}")

    return {
        "meta": entry,
        "rows": df.to_dict(orient="records"),
        "columns": list(df.columns),
        "row_count": int(len(df)),
    }
