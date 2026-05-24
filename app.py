import json

import pandas as pd
import streamlit as st

from utils.json_validator import validate_schema
from utils.prompt_loader import list_prompts, load_prompt
from utils.storage import load_dataset, load_registry, save_dataset


st.set_page_config(
    page_title="🧠 Curriculum Question Extractor",
    layout="wide",
)

st.title("🧠 Curriculum Question Extractor")
st.caption("Prompt-driven extraction · Dataset registry · Visualization")


def questions_to_frame(data: dict) -> pd.DataFrame:
    """Build a table view for any question list we load from JSON."""
    questions = data.get("questions", [])
    return pd.DataFrame(questions if isinstance(questions, list) else [])


st.sidebar.header("📚 Prompt Selection")

prompt_names = list_prompts()
if not prompt_names:
    st.sidebar.warning("No prompts found in /prompts folder.")
    selected_prompt = ""
else:
    selected_prompt = st.sidebar.selectbox("Select Week Prompt", prompt_names)

prompt_text = load_prompt(selected_prompt) if selected_prompt else ""

col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Active Prompt")
    st.text_area("Prompt", value=prompt_text, height=350, disabled=True)

with col2:
    st.subheader("📄 Source Text")
    st.text_area(
        "Paste OCR / PDF text here",
        height=350,
        placeholder="Paste extracted content here...",
    )

st.divider()
st.subheader("🧾 Generated JSON")

json_text = st.text_area("Paste model JSON output here", height=260)
col_a, col_b, col_c = st.columns(3)

with col_a:
    if st.button("✅ Validate"):
        try:
            data = json.loads(json_text)
            ok, msg = validate_schema(data)
            if ok:
                st.success(msg)
                st.session_state["validated_data"] = data
            else:
                st.error(msg)
        except Exception as exc:
            st.error(f"Invalid JSON: {exc}")

with col_b:
    if st.button("👁 Preview"):
        data = st.session_state.get("validated_data")
        if not data:
            st.warning("Validate JSON first.")
        else:
            st.json(data)
            questions_df = questions_to_frame(data)
            if questions_df.empty:
                st.info("No questions found in the validated JSON.")
            else:
                st.dataframe(questions_df, use_container_width=True)

with col_c:
    if st.button("💾 Save"):
        data = st.session_state.get("validated_data")
        if not data:
            st.warning("Validate JSON first.")
        else:
            _, entry = save_dataset(data)
            st.success("Dataset saved successfully!")
            st.json(entry)

st.divider()
st.subheader("📚 Dataset Registry")

registry = load_registry()
if not registry["datasets"]:
    st.info("No datasets saved yet.")
else:
    df_registry = pd.DataFrame(registry["datasets"])
    st.dataframe(df_registry, use_container_width=True)

    selected_file = st.selectbox("Open dataset", df_registry["filename"].tolist())
    if selected_file:
        dataset = load_dataset(selected_file)
        if not dataset:
            st.error("Dataset file could not be loaded.")
        else:
            st.write("### 📦 Dataset Content")
            st.json(dataset)

            st.write("### 📊 Questions Table")
            questions_df = questions_to_frame(dataset)
            if questions_df.empty:
                st.info("No questions found in the saved dataset.")
            else:
                st.dataframe(questions_df, use_container_width=True)
