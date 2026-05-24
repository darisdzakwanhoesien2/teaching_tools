import json
from datetime import datetime
from pathlib import Path

LESSON_REGISTRY_PATH = Path("data/registry_lesson.json")
LESSON_REGISTRY_PATH.parent.mkdir(exist_ok=True)


def _empty_registry():
    return {"students": {}}


def load_lesson_registry():
    if not LESSON_REGISTRY_PATH.exists():
        return _empty_registry()

    try:
        with open(LESSON_REGISTRY_PATH, "r", encoding="utf-8") as f:
            registry = json.load(f)
    except (OSError, json.JSONDecodeError):
        return _empty_registry()

    if not isinstance(registry, dict):
        return _empty_registry()

    students = registry.get("students", {})
    registry["students"] = students if isinstance(students, dict) else {}
    return registry


def save_lesson_registry(registry: dict):
    with open(LESSON_REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)


def ensure_student(registry, student_id: str, name: str):
    students = registry.setdefault("students", {})
    if student_id not in students:
        students[student_id] = {"name": name, "lessons": {}}


def add_lesson(
    student_id: str,
    student_name: str,
    lesson_id: str,
    title: str,
    syllabus: str,
    dataset_filename: str,
):
    registry = load_lesson_registry()
    ensure_student(registry, student_id, student_name)

    lessons = registry["students"][student_id]["lessons"]

    if lesson_id not in lessons:
        lessons[lesson_id] = {
            "title": title,
            "syllabus": syllabus,
            "datasets": [],
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }

    if dataset_filename not in lessons[lesson_id]["datasets"]:
        lessons[lesson_id]["datasets"].append(dataset_filename)

    save_lesson_registry(registry)
    return registry


def list_students():
    registry = load_lesson_registry()
    return registry["students"]


def get_student_lessons(student_id: str):
    registry = load_lesson_registry()
    return registry["students"].get(student_id, {}).get("lessons", {})
