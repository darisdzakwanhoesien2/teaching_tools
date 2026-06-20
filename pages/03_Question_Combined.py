from pathlib import Path

import pandas as pd
import streamlit as st

from utils.storage import load_dataset


st.set_page_config(
    page_title="📚 Combined Question Explorer",
    layout="wide",
)

st.title("📚 Combined Question Explorer")
st.caption("Unified, safe view across all extracted question datasets")

DATASET_DIR = Path("data/extracted_questions")


def as_list(value):
    return value if isinstance(value, list) else []


def dataset_files():
    return sorted(p.name for p in DATASET_DIR.glob("*.json"))


files = dataset_files()
if not files:
    st.error("No datasets found in data/extracted_questions/")
    st.stop()

all_rows = []
loaded_files = []
skipped_files = []

for file_name in files:
    try:
        dataset = load_dataset(file_name)
        if not dataset:
            skipped_files.append(file_name)
            continue
    except Exception:
        skipped_files.append(file_name)
        continue

    topic = dataset.get("topic", "Unknown")
    for question in as_list(dataset.get("questions")):
        if not isinstance(question, dict):
            continue
        row = question.copy()
        row["dataset_file"] = file_name
        row["dataset_topic"] = topic
        all_rows.append(row)

    loaded_files.append(file_name)

if skipped_files:
    with st.expander("⚠️ Skipped Corrupted / Invalid Files"):
        for file_name in skipped_files:
            st.write("•", file_name)

if not all_rows:
    st.warning("No valid questions found in datasets.")
    st.stop()

df = pd.DataFrame(all_rows)

st.subheader("📊 Global Overview")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Datasets Loaded", len(loaded_files))
m2.metric("Total Questions", len(df))
m3.metric("Unique Topics", df["dataset_topic"].nunique())
m4.metric("Calculation Questions", int(df["calculation_required"].sum()))

st.divider()
st.subheader("🔎 Global Filters")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    selected_datasets = st.multiselect(
        "Dataset File",
        sorted(df["dataset_file"].unique()),
        default=sorted(df["dataset_file"].unique()),
    )

with col2:
    selected_topics = st.multiselect(
        "Topic",
        sorted(df["dataset_topic"].unique()),
        default=sorted(df["dataset_topic"].unique()),
    )

with col3:
    # Flatten nested syllabus lists so the global filter operates on codes, not rows.
    if "syllabus_codes" in df and not df.empty:
        syllabus_flat = sorted({code for codes in df["syllabus_codes"] for code in as_list(codes)})
    else:
        syllabus_flat = []
    selected_syllabus = st.multiselect("Syllabus Code", syllabus_flat, default=syllabus_flat)

with col4:
    calc_filter = st.radio("Calculation", ["All", "Yes", "No"], horizontal=True)

with col5:
    keyword = st.text_input("Keyword Search", placeholder="radiation, wave, pressure...")

filtered_df = df.copy()
filtered_df = filtered_df[filtered_df["dataset_file"].isin(selected_datasets)]
filtered_df = filtered_df[filtered_df["dataset_topic"].isin(selected_topics)]

if "syllabus_codes" in filtered_df:
    filtered_df = filtered_df[
        filtered_df["syllabus_codes"].apply(lambda value: any(code in selected_syllabus for code in as_list(value)))
    ]

if calc_filter == "Yes":
    filtered_df = filtered_df[filtered_df["calculation_required"] == True]
elif calc_filter == "No":
    filtered_df = filtered_df[filtered_df["calculation_required"] == False]

if keyword.strip():
    kw = keyword.lower()
    filtered_df = filtered_df[filtered_df.apply(lambda row: kw in str(row).lower(), axis=1)]

st.divider()
st.subheader(f"📋 Combined Questions ({len(filtered_df)})")

if filtered_df.empty:
    st.warning("No matching questions.")
else:
    # Reindex keeps the combined table readable even when one file is missing a field.
    st.dataframe(
        filtered_df.reindex(
            columns=[
                "dataset_topic",
                "dataset_file",
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
        label = f"{row['dataset_topic']} | {row['filename']} — Q{row['question_number']}"
        with st.expander(label):
            meta_cols = st.columns(4)
            meta_cols[0].metric("Calculation", "Yes" if row.get("calculation_required") else "No")
            meta_cols[1].metric("Syllabus", ", ".join(as_list(row.get("syllabus_codes"))))
            meta_cols[2].metric("Dataset", row.get("dataset_file", "—"))
            meta_cols[3].metric("Source File", row.get("filename", "—"))

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
st.subheader("📈 Curriculum Analytics")

col_a, col_b, col_c = st.columns(3)

with col_a:
    if "syllabus_codes" in df and not df.empty:
        syllabus_counts = (
            df.explode("syllabus_codes")["syllabus_codes"]
            .dropna()
            .value_counts()
            .reset_index()
        )
        # Explicitly assign column names to be compatible across pandas 1.x and 2.x
        syllabus_counts.columns = ["Syllabus", "Count"]
    else:
        syllabus_counts = pd.DataFrame(columns=["Syllabus", "Count"])
    st.write("### 📚 Syllabus Coverage")
    st.dataframe(syllabus_counts, use_container_width=True)

with col_b:
    topic_counts = (
        df["dataset_topic"]
        .value_counts()
        .reset_index()
    )
    # Explicitly assign column names to be compatible across pandas 1.x and 2.x
    topic_counts.columns = ["Topic", "Count"]
    st.write("### 🧩 Topic Distribution")
    st.dataframe(topic_counts, use_container_width=True)

with col_c:
    if "physical_concepts" in df and not df.empty:
        concept_counts = (
            df.explode("physical_concepts")["physical_concepts"]
            .dropna()
            .value_counts()
            .reset_index()
        )
        # Explicitly assign column names to be compatible across pandas 1.x and 2.x
        concept_counts.columns = ["Concept", "Count"]
    else:
        concept_counts = pd.DataFrame(columns=["Concept", "Count"])
    st.write("### 🧠 Concept Frequency")
    st.dataframe(concept_counts, use_container_width=True)

st.divider()
with st.expander("📂 View Raw Combined Table"):
    st.dataframe(df, use_container_width=True)
