import sys
import json
import tempfile
import os

# Clear all cached src modules before importing
# This ensures any code change in src/ reflects immediately in UI
for mod_name in list(sys.modules.keys()):
    if mod_name.startswith("src."):
        del sys.modules[mod_name]

import streamlit as st
from src.pipeline import run_pipeline, run_pipeline_with_config

st.set_page_config(page_title="Candidate Data Transformer", layout="wide")

st.title("Multi-Source Candidate Data Transformer")
st.write(
    "Upload a recruiter CSV (with an optional `github_username` column) and "
    "pick an output config to see the merged, normalized, validated candidate profiles."
)

# --- Sidebar controls ---
st.sidebar.header("Input")

uploaded_csv = st.sidebar.file_uploader("Recruiter CSV", type=["csv"])

use_sample = st.sidebar.checkbox("Use bundled sample CSV instead", value=True)

config_choice = st.sidebar.selectbox(
    "Output config",
    options=["Full output (no config)", "configs/default.json", "configs/minimal.json"]
)

run_button = st.sidebar.button("Run Pipeline")

# --- Main logic ---
if run_button:
    if use_sample:
        csv_path = "sample_inputs/recruiter.csv"
    elif uploaded_csv is not None:
        tmp_dir = tempfile.mkdtemp()
        csv_path = os.path.join(tmp_dir, uploaded_csv.name)
        with open(csv_path, "wb") as f:
            f.write(uploaded_csv.getbuffer())
    else:
        st.warning("Please upload a CSV file or check 'Use bundled sample CSV'.")
        st.stop()

    try:
        with st.spinner("Running pipeline..."):
            if config_choice == "Full output (no config)":
                result = run_pipeline(csv_path)
            else:
                result = run_pipeline_with_config(csv_path, config_choice)
    except Exception as e:
        st.error(f"Pipeline failed: {e}")
        st.stop()

    st.success(f"Generated {len(result)} candidate profile(s).")

    for profile in result:
        name = profile.get("full_name") or profile.get("primary_email") or "Unknown candidate"
        with st.expander(f"{name}"):
            st.json(profile)

    st.download_button(
        label="Download output JSON",
        data=json.dumps(result, indent=2),
        file_name="output.json",
        mime="application/json"
    )
else:
    st.info("Configure your input on the left, then click 'Run Pipeline'.")