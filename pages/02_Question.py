from pathlib import Path

import pandas as pd
import streamlit as st

from utils.storage import load_dataset


st.set_page_config(
    page_title="📘 Question Explorer",
    layout="wide",
)

st.title("📘 Extracted Questions Explorer")
st.caption("Browse, filter, and analyze extracted question datasets")

DATASET_DIR = Path("data/extracted_questions")

def as_list(value):
    return value if isinstance(value, list) else []


def codes_from_row(value):
    return [code for code in as_list(value) if code]


dataset_files = sorted(p.name for p in DATASET_DIR.glob("*.json"))
if not dataset_files:
    st.error("No datasets found in data/extracted_questions/")
    st.stop()

selected_file = st.selectbox("Select Dataset", dataset_files)
dataset = load_dataset(selected_file)
if not dataset:
    st.error("Failed to load dataset.")
    st.stop()

questions = as_list(dataset.get("questions"))
df = pd.DataFrame(questions)

st.subheader("📦 Dataset Overview")
header_cols = st.columns(4)
header_cols[0].metric("Topic", dataset.get("topic", "—"))
header_cols[1].metric("Questions", len(questions))
header_cols[2].metric("Unique Files", df["filename"].nunique() if "filename" in df else 0)
header_cols[3].metric(
    "Calculation Qs",
    int(df["calculation_required"].sum()) if "calculation_required" in df else 0,
)

st.divider()
st.subheader("🔎 Filters")
col1, col2, col3, col4 = st.columns(4)

with col1:
    filenames = sorted(df["filename"].dropna().unique().tolist()) if "filename" in df else []
    selected_files = st.multiselect("Filter by Source File", filenames, default=filenames)

with col2:
    # Flatten nested syllabus lists so the filter works on individual codes.
    if "syllabus_codes" in df and not df.empty:
        syllabus_flat = sorted({code for codes in df["syllabus_codes"] for code in as_list(codes)})
    else:
        syllabus_flat = []
    selected_syllabus = st.multiselect("Filter by Syllabus Code", syllabus_flat, default=syllabus_flat)

with col3:
    calc_filter = st.radio("Calculation Required", ["All", "Yes", "No"], horizontal=True)

with col4:
    keyword = st.text_input("Search keyword", placeholder="e.g. radiation, mirror, wave")

filtered_df = df.copy()

if not filtered_df.empty and "filename" in filtered_df:
    filtered_df = filtered_df[filtered_df["filename"].isin(selected_files)]

if not filtered_df.empty and "syllabus_codes" in filtered_df:
    filtered_df = filtered_df[
        filtered_df["syllabus_codes"].apply(lambda value: any(code in selected_syllabus for code in as_list(value)))
    ]

if calc_filter == "Yes" and "calculation_required" in filtered_df:
    filtered_df = filtered_df[filtered_df["calculation_required"] == True]
elif calc_filter == "No" and "calculation_required" in filtered_df:
    filtered_df = filtered_df[filtered_df["calculation_required"] == False]

if keyword.strip():
    keyword_lower = keyword.lower()
    filtered_df = filtered_df[filtered_df.apply(lambda row: keyword_lower in str(row).lower(), axis=1)]

st.divider()
st.subheader(f"📋 Questions ({len(filtered_df)})")

if filtered_df.empty:
    st.warning("No questions match the filters.")
else:
    # Reindex keeps the table stable even if a field is absent in older files.
    st.dataframe(
        filtered_df.reindex(
            columns=[
                "filename",
                "question_number",
                "question_summary",
                "syllabus_codes",
                "calculation_required",
            ]
        ),
        use_container_width=True,
    )

st.divider()
st.subheader("🔍 Question Details")

if filtered_df.empty:
    st.info("No questions to display.")
else:
    for _, row in filtered_df.iterrows():
        label = f"{row['filename']} — Q{row['question_number']}"
        with st.expander(label):
            meta_cols = st.columns(3)
            meta_cols[0].metric("Calculation", "Yes" if row.get("calculation_required") else "No")
            meta_cols[1].metric("Syllabus Codes", ", ".join(as_list(row.get("syllabus_codes"))))
            meta_cols[2].metric("Source File", row.get("filename", "—"))

            st.markdown("### 🧾 Summary")
            st.write(row.get("question_summary", "—"))

            st.markdown("### 🧠 Physical Concepts")
            for concept in as_list(row["physical_concepts"]):
                st.write("•", concept)

            st.markdown("### 📊 Variables Involved")
            for variable in as_list(row["variables_involved"]):
                st.write("•", variable)

            st.markdown("### 🎯 Reasoning Focus")
            st.write(row.get("reasoning_focus", "—"))

st.divider()
st.subheader("📊 Dataset Analytics")

col_a, col_b = st.columns(2)

with col_a:
    if "syllabus_codes" in df and not df.empty:
        syllabus_counts = (
            df.explode("syllabus_codes")["syllabus_codes"]
            .dropna()
            .value_counts()
            .reset_index()
        )
        # Explicitly set column names to support both pandas 1.x and 2.x reset_index behaviors
        syllabus_counts.columns = ["Syllabus", "Count"]
    else:
        syllabus_counts = pd.DataFrame(columns=["Syllabus", "Count"])
    st.write("### 📚 Syllabus Coverage")
    st.dataframe(syllabus_counts, use_container_width=True)

with col_b:
    if "physical_concepts" in df and not df.empty:
        concept_counts = (
            df.explode("physical_concepts")["physical_concepts"]
            .dropna()
            .value_counts()
            .reset_index()
        )
        # Explicitly set column names to support both pandas 1.x and 2.x reset_index behaviors
        concept_counts.columns = ["Concept", "Count"]
    else:
        concept_counts = pd.DataFrame(columns=["Concept", "Count"])
    st.write("### 🧠 Physical Concept Frequency")
    st.dataframe(concept_counts, use_container_width=True)

st.divider()
with st.expander("📂 View Raw Dataset JSON"):
    st.json(dataset)
