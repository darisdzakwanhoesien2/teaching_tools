import streamlit as st
import json
import pandas as pd

from utils.prompt_loader import list_prompts, load_prompt
from utils.json_validator import validate_schema
from utils.storage import save_dataset, load_registry, load_dataset


# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="🧠 Curriculum Question Extractor",
    layout="wide"
)

st.title("🧠 Curriculum Question Extractor")
st.caption("Prompt-driven extraction · Dataset registry · Visualization")

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.header("📚 Prompt Selection")

prompt_names = list_prompts()

if not prompt_names:
    st.sidebar.warning("No prompts found in /prompts folder.")
    selected_prompt = ""
else:
    selected_prompt = st.sidebar.selectbox(
        "Select Week Prompt",
        prompt_names
    )

prompt_text = load_prompt(selected_prompt) if selected_prompt else ""

# ---------------------------------------------------
# PROMPT + INPUT
# ---------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Active Prompt")
    st.text_area(
        "Prompt",
        value=prompt_text,
        height=350,
        disabled=True
    )

with col2:
    st.subheader("📄 Source Text")
    st.text_area(
        "Paste OCR / PDF text here",
        height=350,
        placeholder="Paste extracted content here..."
    )

# ---------------------------------------------------
# JSON INPUT
# ---------------------------------------------------

st.divider()
st.subheader("🧾 Generated JSON")

json_text = st.text_area(
    "Paste model JSON output here",
    height=260
)

colA, colB, colC = st.columns(3)

# ---------------- Validate ----------------
with colA:
    if st.button("✅ Validate"):
        try:
            data = json.loads(json_text)
            ok, msg = validate_schema(data)
            if ok:
                st.success(msg)
                st.session_state["validated"] = data
            else:
                st.error(msg)
        except Exception as e:
            st.error(f"Invalid JSON: {e}")

# ---------------- Preview ----------------
with colB:
    if st.button("👁 Preview"):
        data = st.session_state.get("validated")
        if not data:
            st.warning("Validate JSON first.")
        else:
            st.json(data)
            st.dataframe(
                pd.DataFrame(data["questions"]),
                use_container_width=True
            )

# ---------------- Save ----------------
with colC:
    if st.button("💾 Save"):
        data = st.session_state.get("validated")
        if not data:
            st.warning("Validate JSON first.")
        else:
            path, entry = save_dataset(data)
            st.success("Dataset saved successfully!")
            st.json(entry)

# ---------------------------------------------------
# DATASET BROWSER
# ---------------------------------------------------

st.divider()
st.subheader("📚 Dataset Registry")

registry = load_registry()

if not registry["datasets"]:
    st.info("No datasets saved yet.")
else:
    df_registry = pd.DataFrame(registry["datasets"])
    st.dataframe(df_registry, use_container_width=True)

    selected_file = st.selectbox(
        "Open dataset",
        df_registry["filename"].tolist()
    )

    if selected_file:
        dataset = load_dataset(selected_file)
        if dataset:
            st.write("### 📦 Dataset Content")
            st.json(dataset)

            st.write("### 📊 Questions Table")
            st.dataframe(
                pd.DataFrame(dataset["questions"]),
                use_container_width=True
            )

# import streamlit as st
# import json
# import pandas as pd

# from utils.prompt_loader import list_prompts, load_prompt
# from utils.json_validator import validate_schema
# from utils.storage import (
#     save_dataset,
#     load_registry,
#     load_dataset
# )

# # ---------------------------------------------------
# # PAGE CONFIG
# # ---------------------------------------------------

# st.set_page_config(
#     page_title="🧠 Curriculum Question Extractor",
#     layout="wide"
# )

# st.title("🧠 Curriculum Question Extractor")
# st.caption("Prompt-driven extraction · Dataset registry · Visualization")

# # ---------------------------------------------------
# # SIDEBAR
# # ---------------------------------------------------

# st.sidebar.header("📚 Prompt Selection")

# prompt_names = list_prompts()
# selected_prompt = st.sidebar.selectbox(
#     "Select Week Prompt",
#     prompt_names if prompt_names else ["(no prompts found)"]
# )

# prompt_text = load_prompt(selected_prompt)

# # ---------------------------------------------------
# # PROMPT + INPUT
# # ---------------------------------------------------

# col1, col2 = st.columns(2)

# with col1:
#     st.subheader("📝 Active Prompt")
#     st.text_area(
#         "Prompt",
#         value=prompt_text,
#         height=380,
#         disabled=True
#     )

# with col2:
#     st.subheader("📄 Source Text")
#     st.text_area(
#         "Paste OCR / PDF text here",
#         height=380,
#         placeholder="Paste extracted content here..."
#     )

# # ---------------------------------------------------
# # JSON INPUT
# # ---------------------------------------------------

# st.divider()
# st.subheader("🧾 Generated JSON")

# json_text = st.text_area(
#     "Paste model JSON output",
#     height=280
# )

# colA, colB, colC = st.columns(3)

# # ---------------- Validate ----------------
# with colA:
#     if st.button("✅ Validate"):
#         try:
#             data = json.loads(json_text)
#             ok, msg = validate_schema(data)
#             if ok:
#                 st.success(msg)
#                 st.session_state["validated"] = data
#             else:
#                 st.error(msg)
#         except Exception as e:
#             st.error(f"Invalid JSON: {e}")

# # ---------------- Preview ----------------
# with colB:
#     if st.button("👁 Preview"):
#         data = st.session_state.get("validated")
#         if not data:
#             st.warning("Validate JSON first.")
#         else:
#             st.json(data)
#             st.dataframe(
#                 pd.DataFrame(data["questions"]),
#                 use_container_width=True
#             )

# # ---------------- Save ----------------
# with colC:
#     if st.button("💾 Save"):
#         data = st.session_state.get("validated")
#         if not data:
#             st.warning("Validate JSON first.")
#         else:
#             path, entry = save_dataset(data)
#             st.success("Dataset saved successfully!")
#             st.json(entry)

# # ---------------------------------------------------
# # DATASET BROWSER
# # ---------------------------------------------------

# st.divider()
# st.subheader("📚 Dataset Registry")

# registry = load_registry()

# if not registry["datasets"]:
#     st.info("No datasets saved yet.")
# else:
#     df_registry = pd.DataFrame(registry["datasets"])
#     st.dataframe(df_registry, use_container_width=True)

#     selected = st.selectbox(
#         "Open dataset",
#         df_registry["filename"].tolist()
#     )

#     if selected:
#         dataset = load_dataset(selected)
#         if dataset:
#             st.write("### 📦 Dataset Content")
#             st.json(dataset)

#             st.write("### 📊 Questions Table")
#             st.dataframe(
#                 pd.DataFrame(dataset["questions"]),
#                 use_container_width=True
#             )