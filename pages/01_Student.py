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

# Sort lessons by week if available
def lesson_sort_key(item):
    return item[1].get("week", 999)

sorted_lessons = sorted(lessons.items(), key=lesson_sort_key)

for lesson_id, lesson in sorted_lessons:
    with st.expander(f"📘 Week {lesson.get('week','?')} — {lesson.get('title')}"):

        # -----------------------------
        # Lesson Metadata
        # -----------------------------
        meta_cols = st.columns(4)

        meta_cols[0].metric("Week", lesson.get("week", "—"))
        meta_cols[1].metric("Date Range", lesson.get("date_range", "—"))
        meta_cols[2].metric("Syllabus", lesson.get("syllabus", "—"))
        meta_cols[3].metric("Datasets", len(lesson.get("datasets", [])))

        # -----------------------------
        # Objectives
        # -----------------------------
        st.markdown("### 🎯 Objectives")
        objectives = lesson.get("objectives", [])
        if objectives:
            for obj in objectives:
                st.write("•", obj)
        else:
            st.info("No objectives recorded.")

        # -----------------------------
        # Assessments
        # -----------------------------
        st.markdown("### 📝 Assessments")
        assessments = lesson.get("assessments", [])
        if assessments:
            for a in assessments:
                st.write("•", a)
        else:
            st.info("No assessments.")

        # -----------------------------
        # Practice Questions
        # -----------------------------
        st.markdown("### ❓ Practice Questions")
        questions = lesson.get("practice_questions", [])
        if questions:
            for q in questions:
                st.write("•", q)
        else:
            st.info("No practice questions.")

        # -----------------------------
        # Attached Datasets
        # -----------------------------
        st.markdown("### 📦 Attached Datasets")

        datasets = lesson.get("datasets", [])

        if not datasets:
            st.warning("No datasets attached to this lesson yet.")
        else:
            for dataset_file in datasets:
                st.write(f"📄 {dataset_file}")

                dataset = load_dataset(dataset_file)

                if dataset:
                    st.caption(f"Topic: {dataset.get('topic')}")
                    questions_df = pd.DataFrame(dataset.get("questions", []))

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
