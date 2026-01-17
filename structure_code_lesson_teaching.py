import json
from pathlib import Path
from utils.storage import load_registry, save_dataset
from utils.lesson_registry import load_lesson_registry, save_lesson_registry

# ---------------------------------------
# Paths
# ---------------------------------------

DATASET_DIR = Path("data/extracted_questions")

# ---------------------------------------
# Topic → Lesson Mapping Rules
# ---------------------------------------

LESSON_MATCH_RULES = {
    "thermal": "week_01_thermal_particle",
    "particle": "week_01_thermal_particle",

    "pressure": "week_02_pressure_temperature",
    "temperature": "week_02_pressure_temperature",

    "gas": "week_03_gas_laws_temperature",

    "expansion": "week_04_specific_heat_expansion",
    "specific": "week_04_specific_heat_expansion",

    "energy": "week_05_energy_transfer",
    "transfer": "week_05_energy_transfer",

    "radiation": "week_06_radiation_consequences",

    "wave": "week_07_wave_properties",

    "reflection": "week_08_reflection_light",
    "mirror": "week_08_reflection_light",
}


# ---------------------------------------
# Helpers
# ---------------------------------------

def detect_lesson_from_topic(topic: str):
    topic_lower = topic.lower()
    for keyword, lesson_id in LESSON_MATCH_RULES.items():
        if keyword in topic_lower:
            return lesson_id
    return None


# ---------------------------------------
# Main Linking Logic
# ---------------------------------------

def auto_attach_datasets(student_id="ashaz"):
    print("🔍 Scanning extracted datasets...")

    lesson_registry = load_lesson_registry()
    students = lesson_registry["students"]

    if student_id not in students:
        raise ValueError(f"Student not found: {student_id}")

    lessons = students[student_id]["lessons"]

    attached = []

    for dataset_path in DATASET_DIR.glob("*.json"):
        try:
            with open(dataset_path, "r", encoding="utf-8") as f:
                dataset = json.load(f)

            topic = dataset.get("topic", "")
            lesson_id = detect_lesson_from_topic(topic)

            if not lesson_id:
                print(f"⚠️ No lesson match for: {dataset_path.name}")
                continue

            if lesson_id not in lessons:
                print(f"⚠️ Lesson not found in registry: {lesson_id}")
                continue

            if dataset_path.name not in lessons[lesson_id]["datasets"]:
                lessons[lesson_id]["datasets"].append(dataset_path.name)
                attached.append((dataset_path.name, lesson_id))

        except Exception as e:
            print(f"❌ Failed to process {dataset_path.name}: {e}")

    save_lesson_registry(lesson_registry)

    print("\n✅ Auto-attachment complete!")
    for file, lesson in attached:
        print(f"  📎 {file} → {lesson}")

    if not attached:
        print("⚠️ No datasets were attached.")


# ---------------------------------------
# Run
# ---------------------------------------

if __name__ == "__main__":
    auto_attach_datasets()
