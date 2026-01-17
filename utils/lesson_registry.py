import json
from pathlib import Path
from datetime import datetime

LESSON_REGISTRY_PATH = Path("data/registry_lesson.json")
LESSON_REGISTRY_PATH.parent.mkdir(exist_ok=True)


# -------------------------------------
# Core Load / Save
# -------------------------------------

def load_lesson_registry():
    if LESSON_REGISTRY_PATH.exists():
        with open(LESSON_REGISTRY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    return {"students": {}}


def save_lesson_registry(registry: dict):
    with open(LESSON_REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)


# -------------------------------------
# Student Management
# -------------------------------------

def ensure_student(registry, student_id: str, name: str):
    if student_id not in registry["students"]:
        registry["students"][student_id] = {
            "name": name,
            "lessons": {}
        }


# -------------------------------------
# Lesson Management
# -------------------------------------

def add_lesson(
    student_id: str,
    student_name: str,
    lesson_id: str,
    title: str,
    syllabus: str,
    dataset_filename: str
):
    registry = load_lesson_registry()
    ensure_student(registry, student_id, student_name)

    lessons = registry["students"][student_id]["lessons"]

    if lesson_id not in lessons:
        lessons[lesson_id] = {
            "title": title,
            "syllabus": syllabus,
            "datasets": [],
            "created_at": datetime.now().isoformat(timespec="seconds")
        }

    if dataset_filename not in lessons[lesson_id]["datasets"]:
        lessons[lesson_id]["datasets"].append(dataset_filename)

    save_lesson_registry(registry)
    return registry


# -------------------------------------
# Query Helpers
# -------------------------------------

def list_students():
    registry = load_lesson_registry()
    return registry["students"]


def get_student_lessons(student_id: str):
    registry = load_lesson_registry()
    return registry["students"].get(student_id, {}).get("lessons", {})
