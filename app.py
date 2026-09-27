from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from blood_work_analyzer.service import analyze_blood_work

ROOT = Path(__file__).parent
SAMPLE_REPORT = ROOT / "sample_data" / "blood_work.txt"

load_dotenv()

st.set_page_config(page_title="Blood Work Analyzer", page_icon="🩸", layout="wide")
st.title("Blood Work Analyzer")
st.caption(
    "Two-stage LLM pipeline: extract and classify report values first, "
    "then generate a plain-language summary and diet guidance."
)

left, right = st.columns(2, gap="large")

with left:
    st.header("Blood Work Report")
    blood_report = st.text_area(
        "Blood work report",
        value=SAMPLE_REPORT.read_text(),
        height=620,
        label_visibility="collapsed",
    )
    analyze = st.button("Analyze", type="primary", disabled=not blood_report.strip())

if analyze:
    try:
        with right, st.spinner("Analyzing blood work..."):
            summary, diet_plan = analyze_blood_work(blood_report)
            st.session_state["summary"] = summary
            st.session_state["diet_plan"] = diet_plan
    except Exception as exc:
        st.error(f"Analysis failed: {exc}")

with right:
    st.header("Health Summary")
    with st.container(border=True, height=240):
        st.markdown(st.session_state.get("summary", ""))

    st.header("Suggested Diet Plan")
    with st.container(border=True, height=420):
        st.markdown(st.session_state.get("diet_plan", ""))

st.caption(
    "Technical demonstration only. This application is not a medical diagnosis "
    "or substitute for professional medical advice."
)
