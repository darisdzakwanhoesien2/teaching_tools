import json
from pathlib import Path
from datetime import datetime
import re

BASE_DIR = Path("data")
DATASETS_DIR = BASE_DIR / "extracted_questions"
REGISTRY_PATH = BASE_DIR / "registry.json"

BASE_DIR.mkdir(exist_ok=True)
DATASETS_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------
# Helpers
# -----------------------------

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def load_registry():
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"datasets": []}


def save_registry(registry: dict):
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)


# -----------------------------
# Dataset Storage
# -----------------------------

def save_dataset(data: dict):
    topic = data.get("topic", "unknown")
    slug = slugify(topic)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"{slug}_{timestamp}.json"
    dataset_path = DATASETS_DIR / filename

    # Save dataset JSON
    with open(dataset_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Update registry
    registry = load_registry()
    entry = {
        "id": slug,
        "topic": topic,
        "filename": filename,
        "question_count": len(data.get("questions", [])),
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    registry["datasets"].append(entry)
    save_registry(registry)

    return dataset_path, entry


def load_dataset(filename: str):
    path = DATASETS_DIR / filename
    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# import json
# from pathlib import Path
# from datetime import datetime
# import re

# DATA_DIR = Path("data")
# DATASETS_DIR = DATA_DIR / "extracted_questions"
# REGISTRY_PATH = DATA_DIR / "registry.json"

# DATASETS_DIR.mkdir(parents=True, exist_ok=True)
# DATA_DIR.mkdir(parents=True, exist_ok=True)


# # ----------------------------------------
# # Helpers
# # ----------------------------------------

# def slugify(text: str) -> str:
#     text = text.lower()
#     text = re.sub(r"[^a-z0-9]+", "_", text)
#     return text.strip("_")


# def load_registry():
#     if REGISTRY_PATH.exists():
#         with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
#             return json.load(f)
#     return {"datasets": []}


# def save_registry(registry: dict):
#     with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
#         json.dump(registry, f, indent=2, ensure_ascii=False)


# # ----------------------------------------
# # Main Save Function
# # ----------------------------------------

# def save_dataset(data: dict):
#     """
#     Saves dataset JSON + updates registry.json
#     """
#     topic = data.get("topic", "unknown")
#     slug = slugify(topic)
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

#     filename = f"{slug}_{timestamp}.json"
#     dataset_path = DATASETS_DIR / filename

#     # Save dataset file
#     with open(dataset_path, "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)

#     # Update registry
#     registry = load_registry()
#     entry = {
#         "id": slug,
#         "topic": topic,
#         "filename": filename,
#         "question_count": len(data.get("questions", [])),
#         "created_at": datetime.now().isoformat(timespec="seconds"),
#     }

#     registry["datasets"].append(entry)
#     save_registry(registry)

#     return dataset_path, entry

# import json
# from pathlib import Path
# from datetime import datetime
# import re

# BASE_DIR = Path("data")
# DATASETS_DIR = BASE_DIR / "extracted_questions"
# REGISTRY_PATH = BASE_DIR / "registry.json"

# BASE_DIR.mkdir(exist_ok=True)
# DATASETS_DIR.mkdir(parents=True, exist_ok=True)


# # -----------------------------
# # Helpers
# # -----------------------------

# def slugify(text: str) -> str:
#     text = text.lower()
#     text = re.sub(r"[^a-z0-9]+", "_", text)
#     return text.strip("_")


# def load_registry():
#     if REGISTRY_PATH.exists():
#         with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
#             return json.load(f)
#     return {"datasets": []}


# def save_registry(registry: dict):
#     with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
#         json.dump(registry, f, indent=2, ensure_ascii=False)


# # -----------------------------
# # Dataset Storage
# # -----------------------------

# def save_dataset(data: dict):
#     topic = data.get("topic", "unknown")
#     slug = slugify(topic)
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

#     filename = f"{slug}_{timestamp}.json"
#     dataset_path = DATASETS_DIR / filename

#     # Save dataset JSON
#     with open(dataset_path, "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)

#     # Update registry
#     registry = load_registry()
#     entry = {
#         "id": slug,
#         "topic": topic,
#         "filename": filename,
#         "question_count": len(data.get("questions", [])),
#         "created_at": datetime.now().isoformat(timespec="seconds"),
#     }
#     registry["datasets"].append(entry)
#     save_registry(registry)

#     return dataset_path, entry


# def load_dataset(filename: str):
#     path = DATASETS_DIR / filename
#     if not path.exists():
#         return None
#     with open(path, "r", encoding="utf-8") as f:
#         return json.load(f)