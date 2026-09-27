from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from blood_work_analyzer.service import analyze_blood_work

ROOT = Path(__file__).parent
SAMPLE_REPORT = ROOT / "sample_data" / "blood_work.txt"

load_dotenv()

st.set_page_config(
    page_title="Blood Work Analyzer",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🩸 Blood Work Analyzer")
st.caption(
    "A two-stage LLM pipeline that separates report extraction from explanation."
)

st.warning(
    "Technical demonstration only — this app is not a medical diagnosis or a "
    "substitute for professional medical advice.",
    icon="⚠️",
)

stage1, stage2, stage3 = st.columns(3)
with stage1:
    with st.container(border=True):
        st.markdown("**1 · Extract**")
        st.caption("Read test values and reference ranges from the report.")
with stage2:
    with st.container(border=True):
        st.markdown("**2 · Classify**")
        st.caption("Create an intermediate HIGH / LOW / NORMAL representation.")
with stage3:
    with st.container(border=True):
        st.markdown("**3 · Explain**")
        st.caption("Generate a plain-language summary and diet guidance.")

with st.expander("Why use two stages?"):
    st.markdown(
        """
        A single prompt would have to parse numbers, classify them, explain the result,
        and create diet guidance at the same time. This demo separates those jobs:

        `raw report → extraction/classification → intermediate result → interpretation`

        The separation makes the workflow easier to inspect and test. The current
        prototype still relies on the model for extraction and classification; a
        production version should validate units and reference ranges deterministically.
        """
    )

with st.sidebar:
    st.header("Demo guide")
    st.markdown(
        """
        1. Keep the preloaded sample report or edit it.
        2. Click **Analyze report**.
        3. Review the summary and diet guidance.
        4. Change a value and run the pipeline again.
        """
    )

    if st.button("Reset sample report", use_container_width=True):
        st.session_state["report_text"] = SAMPLE_REPORT.read_text()
        st.session_state.pop("summary", None)
        st.session_state.pop("diet_plan", None)
        st.rerun()

    if st.button("Clear results", use_container_width=True):
        st.session_state.pop("summary", None)
        st.session_state.pop("diet_plan", None)
        st.rerun()

if "report_text" not in st.session_state:
    st.session_state["report_text"] = SAMPLE_REPORT.read_text()

left, right = st.columns(2, gap="large")

with left:
    st.subheader("Input report")
    st.caption("Use the sample below or paste another text-based report.")
    blood_report = st.text_area(
        "Blood work report",
        key="report_text",
        height=590,
        label_visibility="collapsed",
    )
    analyze = st.button(
        "Analyze report",
        type="primary",
        use_container_width=True,
        disabled=not blood_report.strip(),
    )

if analyze:
    try:
        with st.spinner("Running Stage 1 extraction, then Stage 2 interpretation…"):
            summary, diet_plan = analyze_blood_work(blood_report)
            st.session_state["summary"] = summary
            st.session_state["diet_plan"] = diet_plan
        st.success("Analysis complete.")
    except Exception:
        st.error(
            "The analysis could not be completed. Check the report format or try again later."
        )

with right:
    st.subheader("Output")

    st.markdown("**Health summary**")
    with st.container(border=True, height=245):
        summary = st.session_state.get("summary")
        if summary:
            st.markdown(summary)
        else:
            st.caption("Run the analysis to generate a plain-language summary.")

    st.markdown("**Suggested diet plan**")
    with st.container(border=True, height=355):
        diet_plan = st.session_state.get("diet_plan")
        if diet_plan:
            st.markdown(diet_plan)
        else:
            st.caption("Diet guidance will appear here after the second pipeline stage.")

st.divider()
st.caption(
    "Portfolio demo · The pipeline is not clinically validated and model output can be wrong."
)
