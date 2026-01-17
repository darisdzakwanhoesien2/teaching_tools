import streamlit as st
import pandas as pd
from pathlib import Path
import json

from utils.storage import load_dataset


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="📘 Question Explorer",
    layout="wide"
)

st.title("📘 Extracted Questions Explorer")
st.caption("Browse, filter, and analyze extracted question datasets")

# =========================================================
# DATASET DISCOVERY
# =========================================================

DATASET_DIR = Path("data/extracted_questions")
dataset_files = sorted([p.name for p in DATASET_DIR.glob("*.json")])

if not dataset_files:
    st.error("No datasets found in data/extracted_questions/")
    st.stop()

# =========================================================
# DATASET SELECTION
# =========================================================

selected_file = st.selectbox(
    "Select Dataset",
    dataset_files
)

dataset = load_dataset(selected_file)

if not dataset:
    st.error("Failed to load dataset.")
    st.stop()

questions = dataset.get("questions", [])

df = pd.DataFrame(questions)

# =========================================================
# DATASET HEADER
# =========================================================

st.subheader("📦 Dataset Overview")

header_cols = st.columns(4)

header_cols[0].metric("Topic", dataset.get("topic", "—"))
header_cols[1].metric("Questions", len(questions))
header_cols[2].metric("Unique Files", df["filename"].nunique())
header_cols[3].metric("Calculation Qs", df["calculation_required"].sum())

# =========================================================
# FILTER CONTROLS
# =========================================================

st.divider()
st.subheader("🔎 Filters")

col1, col2, col3, col4 = st.columns(4)

# Filename filter
with col1:
    filenames = sorted(df["filename"].dropna().unique().tolist())
    selected_files = st.multiselect(
        "Filter by Source File",
        filenames,
        default=filenames
    )

# Syllabus filter
with col2:
    syllabus_flat = sorted(
        {code for codes in df["syllabus_codes"] for code in codes}
    )
    selected_syllabus = st.multiselect(
        "Filter by Syllabus Code",
        syllabus_flat,
        default=syllabus_flat
    )

# Calculation filter
with col3:
    calc_filter = st.radio(
        "Calculation Required",
        ["All", "Yes", "No"],
        horizontal=True
    )

# Keyword search
with col4:
    keyword = st.text_input(
        "Search keyword",
        placeholder="e.g. radiation, mirror, wave"
    )

# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = df.copy()

# File filter
filtered_df = filtered_df[
    filtered_df["filename"].isin(selected_files)
]

# Syllabus filter
filtered_df = filtered_df[
    filtered_df["syllabus_codes"].apply(
        lambda codes: any(c in selected_syllabus for c in codes)
    )
]

# Calculation filter
if calc_filter == "Yes":
    filtered_df = filtered_df[filtered_df["calculation_required"] == True]
elif calc_filter == "No":
    filtered_df = filtered_df[filtered_df["calculation_required"] == False]

# Keyword filter
if keyword.strip():
    keyword_lower = keyword.lower()
    filtered_df = filtered_df[
        filtered_df.apply(
            lambda row: keyword_lower in str(row).lower(),
            axis=1
        )
    ]

# =========================================================
# TABLE VIEW
# =========================================================

st.divider()
st.subheader(f"📋 Questions ({len(filtered_df)})")

if filtered_df.empty:
    st.warning("No questions match the filters.")
else:
    st.dataframe(
        filtered_df[
            [
                "filename",
                "question_number",
                "question_summary",
                "syllabus_codes",
                "calculation_required"
            ]
        ],
        use_container_width=True
    )

# =========================================================
# QUESTION DETAIL VIEW
# =========================================================

st.divider()
st.subheader("🔍 Question Details")

if filtered_df.empty:
    st.info("No questions to display.")
else:
    for idx, row in filtered_df.iterrows():
        label = f"{row['filename']} — Q{row['question_number']}"
        with st.expander(label):

            meta_cols = st.columns(3)

            meta_cols[0].metric("Calculation", "Yes" if row["calculation_required"] else "No")
            meta_cols[1].metric("Syllabus Codes", ", ".join(row["syllabus_codes"]))
            meta_cols[2].metric("Source File", row["filename"])

            st.markdown("### 🧾 Summary")
            st.write(row["question_summary"])

            st.markdown("### 🧠 Physical Concepts")
            for c in row["physical_concepts"]:
                st.write("•", c)

            st.markdown("### 📊 Variables Involved")
            for v in row["variables_involved"]:
                st.write("•", v)

            st.markdown("### 🎯 Reasoning Focus")
            st.write(row["reasoning_focus"])

# =========================================================
# ANALYTICS
# =========================================================

st.divider()
st.subheader("📊 Dataset Analytics")

colA, colB = st.columns(2)

# Syllabus distribution
with colA:
    syllabus_counts = (
        df.explode("syllabus_codes")
        ["syllabus_codes"]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "Syllabus", "syllabus_codes": "Count"})
    )
    st.write("### 📚 Syllabus Coverage")
    st.dataframe(syllabus_counts, use_container_width=True)

# Physical concept distribution
with colB:
    concept_counts = (
        df.explode("physical_concepts")
        ["physical_concepts"]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "Concept", "physical_concepts": "Count"})
    )
    st.write("### 🧠 Physical Concept Frequency")
    st.dataframe(concept_counts, use_container_width=True)

# =========================================================
# RAW JSON VIEW
# =========================================================

st.divider()
with st.expander("📂 View Raw Dataset JSON"):
    st.json(dataset)
