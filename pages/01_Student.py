import streamlit as st
import pandas as pd

from utils.lesson_registry import load_lesson_registry
from utils.storage import load_dataset


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="🎓 Student Viewer",
    layout="wide"
)

st.title("🎓 Student Dashboard")
st.caption("Browse students, lessons, and attached datasets")

# =========================================================
# LOAD REGISTRY
# =========================================================

lesson_registry = load_lesson_registry()
students = lesson_registry.get("students", {})

if not students:
    st.error("No students found in registry_lesson.json")
    st.stop()

# =========================================================
# STUDENT SELECTION
# =========================================================

student_ids = list(students.keys())

selected_student_id = st.selectbox(
    "Select Student",
    student_ids,
    format_func=lambda sid: f"{sid} — {students[sid].get('name','')}"
)

student = students[selected_student_id]

# =========================================================
# STUDENT PROFILE
# =========================================================

st.subheader("👤 Student Profile")

profile_cols = st.columns(4)

profile_cols[0].metric("Name", student.get("name", "—"))
profile_cols[1].metric("Grade", student.get("grade", "—"))
profile_cols[2].metric("School", student.get("school", "—"))
profile_cols[3].metric("Lessons", len(student.get("lessons", {})))

# =========================================================
# LESSON LIST
# =========================================================

st.divider()
st.subheader("📚 Lessons")

lessons = student.get("lessons", {})

if not lessons:
    st.warning("This student has no lessons.")
    st.stop()

# Sort lessons by week if available, fallback to extracting it from the lesson ID
def get_week_number(lesson_id: str, lesson_dict: dict) -> int:
    import re
    if "week" in lesson_dict and lesson_dict["week"] is not None:
        try:
            return int(lesson_dict["week"])
        except ValueError:
            pass
    # Extract week number from ID (e.g. week_7_waves -> 7, week_01_thermal -> 1)
    match = re.search(r"week_0*(\d+)", lesson_id, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 999

def lesson_sort_key(item):
    return get_week_number(item[0], item[1])

sorted_lessons = sorted(lessons.items(), key=lesson_sort_key)

for lesson_id, lesson in sorted_lessons:
    week_num = get_week_number(lesson_id, lesson)
    week_str = str(week_num) if week_num != 999 else "?"
    
    with st.expander(f"📘 Week {week_str} — {lesson.get('title', 'Untitled Lesson')}"):

        # -----------------------------
        # Lesson Metadata
        # -----------------------------
        meta_cols = st.columns(4)

        meta_cols[0].metric("Week", week_str if week_str != "?" else "—")
        meta_cols[1].metric("Date Range", lesson.get("date_range", "—"))
        meta_cols[2].metric("Syllabus", lesson.get("syllabus", "—"))
        
        # Ensure datasets is a valid list to prevent metric crash
        datasets = lesson.get("datasets", [])
        datasets_list = datasets if isinstance(datasets, list) else []
        meta_cols[3].metric("Datasets", len(datasets_list))

        # -----------------------------
        # Objectives
        # -----------------------------
        st.markdown("### 🎯 Objectives")
        objectives = lesson.get("objectives", [])
        objectives_list = objectives if isinstance(objectives, list) else []
        if objectives_list:
            for obj in objectives_list:
                st.write("•", obj)
        else:
            st.info("No objectives recorded.")

        # -----------------------------
        # Assessments
        # -----------------------------
        st.markdown("### 📝 Assessments")
        assessments = lesson.get("assessments", [])
        assessments_list = assessments if isinstance(assessments, list) else []
        if assessments_list:
            for a in assessments_list:
                st.write("•", a)
        else:
            st.info("No assessments.")

        # -----------------------------
        # Practice Questions
        # -----------------------------
        st.markdown("### ❓ Practice Questions")
        questions = lesson.get("practice_questions", [])
        questions_list = questions if isinstance(questions, list) else []
        if questions_list:
            for q in questions_list:
                st.write("•", q)
        else:
            st.info("No practice questions.")

        # -----------------------------
        # Attached Datasets
        # -----------------------------
        st.markdown("### 📦 Attached Datasets")

        if not datasets_list:
            st.warning("No datasets attached to this lesson yet.")
        else:
            for dataset_file in datasets_list:
                st.write(f"📄 {dataset_file}")

                dataset = load_dataset(dataset_file)

                if dataset:
                    st.caption(f"Topic: {dataset.get('topic')}")
                    
                    # Ensure dataset['questions'] is a list to prevent DataFrame crash
                    raw_questions = dataset.get("questions", [])
                    dataset_questions_list = raw_questions if isinstance(raw_questions, list) else []
                    questions_df = pd.DataFrame(dataset_questions_list)

                    if not questions_df.empty:
                        st.dataframe(
                            questions_df,
                            use_container_width=True
                        )
                    else:
                        st.info("Dataset contains no questions.")
                else:
                    st.error("Dataset file not found.")

# =========================================================
# RAW REGISTRY VIEWER
# =========================================================

st.divider()
with st.expander("📂 View Raw registry_lesson.json"):
    st.json(lesson_registry)
