import pandas as pd
import streamlit as st

from utils.saved_results import (
    add_metadata,
    build_summary,
    dataframe_to_csv,
    dataframe_to_json,
    load_manifest,
    load_saved_result,
    parse_input,
    save_result,
    saved_option_label,
)


SAMPLE_TABLE = """| Question ID | Question | Main Chapter | Subchapter | Secondary Subchapters | Reasoning |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **I-Q1** | Calculate the ratio of force between two moving objects in contact. | 3 Dynamics | 3.1 Momentum and Newton's laws of motion | | Requires applying Newton's second law ($F=ma$) to a system of connected masses. |
| **I-Q2** | Determine speed from a force-time graph. | 3 Dynamics | 3.1 Momentum and Newton's laws of motion | | Involves the concept of impulse as the change in momentum (area under $F-t$ graph). |
"""


st.set_page_config(page_title="Test Question Parser", page_icon=":books:", layout="wide")

st.title("Test Question Parser")
st.caption("Paste a question mapping table, choose the exam label, then review and export structured data.")

with st.sidebar:
    st.header("Input Settings")
    test_name = st.selectbox("Test type", ["MEXT", "EJU", "A-Level", "SAT", "ACT", "Custom"], index=0)
    if test_name == "Custom":
        test_name = st.text_input("Custom test name", placeholder="e.g. IB Physics")

    source_label = st.text_input("Source label", placeholder="e.g. 2024 Physics Set 1")
    input_format = st.selectbox("Input format", ["Auto-detect", "Markdown table", "CSV", "TSV"])
    use_sample = st.toggle("Load sample table", value=True)

    st.header("Saved Results")
    saved_entries = load_manifest()
    saved_labels = ["No saved dataset selected"] + [saved_option_label(entry) for entry in saved_entries]
    selected_saved_label = st.selectbox("Saved datasets", saved_labels)
    selected_saved_index = saved_labels.index(selected_saved_label) - 1

    if st.button("Load selected", disabled=selected_saved_index < 0):
        selected_entry = saved_entries[selected_saved_index]
        try:
            st.session_state["loaded_df"] = load_saved_result(selected_entry)
            st.session_state["loaded_name"] = selected_entry["name"]
            st.success(f"Loaded {selected_entry['name']}.")
        except Exception as exc:
            st.error(f"Could not load saved results: {exc}")

    if st.button("Clear loaded dataset", disabled="loaded_df" not in st.session_state):
        st.session_state.pop("loaded_df", None)
        st.session_state.pop("loaded_name", None)

raw_text = st.text_area(
    "Question table",
    value=SAMPLE_TABLE if use_sample else "",
    height=360,
    placeholder="Paste a Markdown, CSV, or TSV table here.",
)

try:
    parsed_df = parse_input(raw_text, input_format)
except Exception as exc:
    st.error(f"Could not parse the table: {exc}")
    st.stop()

filled_df = parsed_df[parsed_df["Question ID"].astype(str).str.strip() != ""].copy()
enriched_df = add_metadata(filled_df, test_name, source_label)

if "loaded_df" in st.session_state:
    enriched_df = st.session_state["loaded_df"].copy()
    filled_df = enriched_df[enriched_df["Question ID"].astype(str).str.strip() != ""].copy()
    st.info(f"Editing saved dataset: {st.session_state.get('loaded_name', 'saved results')}")

metric_columns = st.columns(4)
metric_columns[0].metric("Questions", len(filled_df))
metric_columns[1].metric("Main chapters", filled_df["Main Chapter"].replace("", pd.NA).nunique())
metric_columns[2].metric("Subchapters", filled_df["Subchapter"].replace("", pd.NA).nunique())
metric_columns[3].metric(
    "Secondary links",
    int(filled_df["Secondary Subchapters"].astype(str).str.strip().ne("").sum()) if not filled_df.empty else 0,
)

tab_data, tab_summary, tab_export, tab_saved = st.tabs(["Parsed Data", "Chapter Summary", "Export", "Saved Results"])

with tab_data:
    edited_df = st.data_editor(
        enriched_df,
        width="stretch",
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "Reasoning": st.column_config.TextColumn(width="large"),
            "Question": st.column_config.TextColumn(width="large"),
        },
    )

with tab_summary:
    st.dataframe(build_summary(filled_df), width="stretch", hide_index=True)

    if not filled_df.empty:
        st.bar_chart(filled_df["Main Chapter"].value_counts())

with tab_export:
    default_save_name = source_label.strip() or f"{test_name or 'test'} question mapping"
    save_name = st.text_input("Save result as", value=default_save_name)
    if st.button("Save to local storage", disabled=edited_df.empty):
        saved_entry = save_result(edited_df, save_name)
        st.success(f"Saved {saved_entry['rows']} rows to {saved_entry['file']}.")

    st.download_button(
        "Download CSV",
        data=dataframe_to_csv(edited_df),
        file_name=f"{(test_name or 'test').lower().replace(' ', '_')}_questions.csv",
        mime="text/csv",
    )
    st.download_button(
        "Download JSON",
        data=dataframe_to_json(edited_df),
        file_name=f"{(test_name or 'test').lower().replace(' ', '_')}_questions.json",
        mime="application/json",
    )

with tab_saved:
    saved_entries = load_manifest()
    if saved_entries:
        saved_df = pd.DataFrame(saved_entries)
        st.dataframe(saved_df, width="stretch", hide_index=True)

        preview_label = st.selectbox(
            "Preview saved dataset",
            [saved_option_label(entry) for entry in saved_entries],
            key="preview_saved_dataset",
        )
        preview_entry = saved_entries[[saved_option_label(entry) for entry in saved_entries].index(preview_label)]
        try:
            st.dataframe(load_saved_result(preview_entry), width="stretch", hide_index=True)
        except Exception as exc:
            st.error(f"Could not preview saved results: {exc}")
    else:
        st.info("No saved results yet.")
