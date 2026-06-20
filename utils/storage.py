import json
import re
from datetime import datetime
from pathlib import Path

BASE_DIR = Path("data")
DATASETS_DIR = BASE_DIR / "extracted_questions"
REGISTRY_PATH = BASE_DIR / "registry.json"

BASE_DIR.mkdir(exist_ok=True)
DATASETS_DIR.mkdir(parents=True, exist_ok=True)


def slugify(text: str) -> str:
    """Convert free-form text into a filesystem-friendly slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "unknown"


def load_registry():
    """Load the dataset registry and fall back to an empty structure."""
    if not REGISTRY_PATH.exists():
        return {"datasets": []}

    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            registry = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {"datasets": []}

    if not isinstance(registry, dict):
        return {"datasets": []}

    datasets = registry.get("datasets", [])
    registry["datasets"] = datasets if isinstance(datasets, list) else []
    return registry


def save_registry(registry: dict):
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)


def save_dataset(data: dict):
    """Persist a validated dataset and append its metadata to the registry."""
    topic = str(data.get("topic", "unknown"))
    slug = slugify(topic)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"{slug}_{timestamp}.json"
    dataset_path = DATASETS_DIR / filename

    with open(dataset_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    questions = data.get("questions", [])
    entry = {
        "id": slug,
        "topic": topic,
        "filename": filename,
        "question_count": len(questions) if isinstance(questions, list) else 0,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    registry = load_registry()
    registry["datasets"].append(entry)
    save_registry(registry)

    return dataset_path, entry


def load_dataset(filename: str):
    """Load a single extracted JSON dataset by filename.
    
    Includes sanitization to prevent directory traversal exploits.
    """
    # Sanitize to prevent path traversal (extract only the file name)
    safe_filename = Path(filename).name
    path = DATASETS_DIR / safe_filename
    
    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None

