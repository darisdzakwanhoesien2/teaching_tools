import streamlit as st
import pandas as pd
from pathlib import Path

from utils.storage import load_dataset


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="📚 Combined Question Explorer",
    layout="wide"
)

st.title("📚 Combined Question Explorer")
st.caption("Unified, safe view across all extracted question datasets")

# =========================================================
# LOAD ALL DATASETS (SAFE)
# =========================================================

DATASET_DIR = Path("data/extracted_questions")
dataset_files = sorted([p.name for p in DATASET_DIR.glob("*.json")])

if not dataset_files:
    st.error("No datasets found in data/extracted_questions/")
    st.stop()

all_rows = []
loaded_files = []
skipped_files = []

for file in dataset_files:
    try:
        dataset = load_dataset(file)
        if not dataset:
            skipped_files.append(file)
            continue
    except Exception:
        skipped_files.append(file)
        continue

    topic = dataset.get("topic", "Unknown")

    for q in dataset.get("questions", []):
        row = q.copy()
        row["dataset_file"] = file
        row["dataset_topic"] = topic
        all_rows.append(row)

    loaded_files.append(file)

# -----------------------------------------
# Status
# -----------------------------------------

if skipped_files:
    with st.expander("⚠️ Skipped Corrupted / Invalid Files"):
        for f in skipped_files:
            st.write("•", f)

if not all_rows:
    st.warning("No valid questions found in datasets.")
    st.stop()

df = pd.DataFrame(all_rows)

# =========================================================
# GLOBAL METRICS
# =========================================================

st.subheader("📊 Global Overview")

m1, m2, m3, m4 = st.columns(4)

m1.metric("Datasets Loaded", len(loaded_files))
m2.metric("Total Questions", len(df))
m3.metric("Unique Topics", df["dataset_topic"].nunique())
m4.metric("Calculation Questions", int(df["calculation_required"].sum()))

# =========================================================
# FILTER CONTROLS
# =========================================================

st.divider()
st.subheader("🔎 Global Filters")

col1, col2, col3, col4, col5 = st.columns(5)

# Dataset filter
with col1:
    selected_datasets = st.multiselect(
        "Dataset File",
        sorted(df["dataset_file"].unique()),
        default=sorted(df["dataset_file"].unique())
    )

# Topic filter
with col2:
    selected_topics = st.multiselect(
        "Topic",
        sorted(df["dataset_topic"].unique()),
        default=sorted(df["dataset_topic"].unique())
    )

# Syllabus filter
with col3:
    syllabus_flat = sorted(
        {code for codes in df["syllabus_codes"] for code in codes}
    )
    selected_syllabus = st.multiselect(
        "Syllabus Code",
        syllabus_flat,
        default=syllabus_flat
    )

# Calculation filter
with col4:
    calc_filter = st.radio(
        "Calculation",
        ["All", "Yes", "No"],
        horizontal=True
    )

# Keyword search
with col5:
    keyword = st.text_input(
        "Keyword Search",
        placeholder="radiation, wave, pressure..."
    )

# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = df.copy()

filtered_df = filtered_df[
    filtered_df["dataset_file"].isin(selected_datasets)
]

filtered_df = filtered_df[
    filtered_df["dataset_topic"].isin(selected_topics)
]

filtered_df = filtered_df[
    filtered_df["syllabus_codes"].apply(
        lambda codes: any(c in selected_syllabus for c in codes)
    )
]

if calc_filter == "Yes":
    filtered_df = filtered_df[filtered_df["calculation_required"] == True]
elif calc_filter == "No":
    filtered_df = filtered_df[filtered_df["calculation_required"] == False]

if keyword.strip():
    kw = keyword.lower()
    filtered_df = filtered_df[
        filtered_df.apply(
            lambda row: kw in str(row).lower(),
            axis=1
        )
    ]

# =========================================================
# TABLE VIEW
# =========================================================

st.divider()
st.subheader(f"📋 Combined Questions ({len(filtered_df)})")

if filtered_df.empty:
    st.warning("No matching questions.")
else:
    st.dataframe(
        filtered_df[
            [
                "dataset_topic",
                "dataset_file",
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
        label = f"{row['dataset_topic']} | {row['filename']} — Q{row['question_number']}"
        with st.expander(label):

            meta_cols = st.columns(4)

            meta_cols[0].metric("Calculation", "Yes" if row["calculation_required"] else "No")
            meta_cols[1].metric("Syllabus", ", ".join(row["syllabus_codes"]))
            meta_cols[2].metric("Dataset", row["dataset_file"])
            meta_cols[3].metric("Source File", row["filename"])

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
st.subheader("📈 Curriculum Analytics")

colA, colB, colC = st.columns(3)

# Syllabus coverage
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

# Topic distribution
with colB:
    topic_counts = (
        df["dataset_topic"]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "Topic", "dataset_topic": "Count"})
    )
    st.write("### 🧩 Topic Distribution")
    st.dataframe(topic_counts, use_container_width=True)

# Physical concept distribution
with colC:
    concept_counts = (
        df.explode("physical_concepts")
        ["physical_concepts"]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "Concept", "physical_concepts": "Count"})
    )
    st.write("### 🧠 Concept Frequency")
    st.dataframe(concept_counts, use_container_width=True)

# =========================================================
# RAW VIEW
# =========================================================

st.divider()
with st.expander("📂 View Raw Combined Table"):
    st.dataframe(df, use_container_width=True)


# import streamlit as st
# import pandas as pd
# from pathlib import Path
# import json

# from utils.storage import load_dataset


# # =========================================================
# # PAGE CONFIG
# # =========================================================

# st.set_page_config(
#     page_title="📚 Combined Question Explorer",
#     layout="wide"
# )

# st.title("📚 Combined Question Explorer")
# st.caption("Unified view across all extracted question datasets")

# # =========================================================
# # LOAD ALL DATASETS
# # =========================================================

# DATASET_DIR = Path("data/extracted_questions")
# dataset_files = sorted([p.name for p in DATASET_DIR.glob("*.json")])

# if not dataset_files:
#     st.error("No datasets found in data/extracted_questions/")
#     st.stop()

# all_rows = []

# for file in dataset_files:
#     dataset = load_dataset(file)
#     if not dataset:
#         continue

#     topic = dataset.get("topic", "Unknown")

#     for q in dataset.get("questions", []):
#         row = q.copy()
#         row["dataset_file"] = file
#         row["dataset_topic"] = topic
#         all_rows.append(row)

# df = pd.DataFrame(all_rows)

# if df.empty:
#     st.warning("No questions loaded.")
#     st.stop()

# # =========================================================
# # GLOBAL METRICS
# # =========================================================

# st.subheader("📊 Global Overview")

# m1, m2, m3, m4 = st.columns(4)

# m1.metric("Total Datasets", len(dataset_files))
# m2.metric("Total Questions", len(df))
# m3.metric("Unique Topics", df["dataset_topic"].nunique())
# m4.metric("Calculation Questions", int(df["calculation_required"].sum()))

# # =========================================================
# # FILTER CONTROLS
# # =========================================================

# st.divider()
# st.subheader("🔎 Global Filters")

# col1, col2, col3, col4, col5 = st.columns(5)

# # Dataset filter
# with col1:
#     selected_datasets = st.multiselect(
#         "Dataset File",
#         sorted(df["dataset_file"].unique()),
#         default=sorted(df["dataset_file"].unique())
#     )

# # Topic filter
# with col2:
#     selected_topics = st.multiselect(
#         "Topic",
#         sorted(df["dataset_topic"].unique()),
#         default=sorted(df["dataset_topic"].unique())
#     )

# # Syllabus filter
# with col3:
#     syllabus_flat = sorted(
#         {code for codes in df["syllabus_codes"] for code in codes}
#     )
#     selected_syllabus = st.multiselect(
#         "Syllabus Code",
#         syllabus_flat,
#         default=syllabus_flat
#     )

# # Calculation filter
# with col4:
#     calc_filter = st.radio(
#         "Calculation",
#         ["All", "Yes", "No"],
#         horizontal=True
#     )

# # Keyword search
# with col5:
#     keyword = st.text_input(
#         "Keyword Search",
#         placeholder="radiation, wave, pressure..."
#     )

# # =========================================================
# # APPLY FILTERS
# # =========================================================

# filtered_df = df.copy()

# filtered_df = filtered_df[
#     filtered_df["dataset_file"].isin(selected_datasets)
# ]

# filtered_df = filtered_df[
#     filtered_df["dataset_topic"].isin(selected_topics)
# ]

# filtered_df = filtered_df[
#     filtered_df["syllabus_codes"].apply(
#         lambda codes: any(c in selected_syllabus for c in codes)
#     )
# ]

# if calc_filter == "Yes":
#     filtered_df = filtered_df[filtered_df["calculation_required"] == True]
# elif calc_filter == "No":
#     filtered_df = filtered_df[filtered_df["calculation_required"] == False]

# if keyword.strip():
#     kw = keyword.lower()
#     filtered_df = filtered_df[
#         filtered_df.apply(
#             lambda row: kw in str(row).lower(),
#             axis=1
#         )
#     ]

# # =========================================================
# # TABLE VIEW
# # =========================================================

# st.divider()
# st.subheader(f"📋 Combined Questions ({len(filtered_df)})")

# if filtered_df.empty:
#     st.warning("No matching questions.")
# else:
#     st.dataframe(
#         filtered_df[
#             [
#                 "dataset_topic",
#                 "dataset_file",
#                 "filename",
#                 "question_number",
#                 "question_summary",
#                 "syllabus_codes",
#                 "calculation_required"
#             ]
#         ],
#         use_container_width=True
#     )

# # =========================================================
# # QUESTION DETAIL VIEW
# # =========================================================

# st.divider()
# st.subheader("🔍 Question Details")

# if filtered_df.empty:
#     st.info("No questions to display.")
# else:
#     for idx, row in filtered_df.iterrows():
#         label = f"{row['dataset_topic']} | {row['filename']} — Q{row['question_number']}"
#         with st.expander(label):

#             meta_cols = st.columns(4)

#             meta_cols[0].metric("Calculation", "Yes" if row["calculation_required"] else "No")
#             meta_cols[1].metric("Syllabus", ", ".join(row["syllabus_codes"]))
#             meta_cols[2].metric("Dataset", row["dataset_file"])
#             meta_cols[3].metric("Source File", row["filename"])

#             st.markdown("### 🧾 Summary")
#             st.write(row["question_summary"])

#             st.markdown("### 🧠 Physical Concepts")
#             for c in row["physical_concepts"]:
#                 st.write("•", c)

#             st.markdown("### 📊 Variables Involved")
#             for v in row["variables_involved"]:
#                 st.write("•", v)

#             st.markdown("### 🎯 Reasoning Focus")
#             st.write(row["reasoning_focus"])

# # =========================================================
# # ANALYTICS
# # =========================================================

# st.divider()
# st.subheader("📈 Curriculum Analytics")

# colA, colB, colC = st.columns(3)

# # Syllabus coverage
# with colA:
#     syllabus_counts = (
#         df.explode("syllabus_codes")
#         ["syllabus_codes"]
#         .value_counts()
#         .reset_index()
#         .rename(columns={"index": "Syllabus", "syllabus_codes": "Count"})
#     )
#     st.write("### 📚 Syllabus Coverage")
#     st.dataframe(syllabus_counts, use_container_width=True)

# # Topic distribution
# with colB:
#     topic_counts = (
#         df["dataset_topic"]
#         .value_counts()
#         .reset_index()
#         .rename(columns={"index": "Topic", "dataset_topic": "Count"})
#     )
#     st.write("### 🧩 Topic Distribution")
#     st.dataframe(topic_counts, use_container_width=True)

# # Physical concept distribution
# with colC:
#     concept_counts = (
#         df.explode("physical_concepts")
#         ["physical_concepts"]
#         .value_counts()
#         .reset_index()
#         .rename(columns={"index": "Concept", "physical_concepts": "Count"})
#     )
#     st.write("### 🧠 Concept Frequency")
#     st.dataframe(concept_counts, use_container_width=True)

# # =========================================================
# # RAW VIEW
# # =========================================================

# st.divider()
# with st.expander("📂 View Raw Combined Table"):
#     st.dataframe(df, use_container_width=True)
