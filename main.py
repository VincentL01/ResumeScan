import streamlit as st
from app.processor import analyze_resume
from pprint import pprint

st.set_page_config(page_title="ResumeScan", layout="centered")
st.title("Resume & JD Analyzer")

st.markdown("""
Upload your resume (PDF) and paste or upload the job description (JD) below.\nThe app will analyze your resume and generate a match score, missing keywords, and a profile summary.
""")

import os

JD_DIR = os.path.join(os.path.dirname(__file__), "documents", "JD")
jd_files = [f for f in os.listdir(JD_DIR) if f.endswith(".md")]
selected_jd = st.selectbox("Select Job Description (JD)", jd_files)

uploaded_resume = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

if st.button("Analyze Resume"):
    if uploaded_resume and selected_jd:
        with st.spinner("Analyzing..."):
            jd_path = os.path.join(JD_DIR, selected_jd)
            result = analyze_resume(uploaded_resume, jd_path)
            pprint(result)
            st.subheader(f"Match Score: {result['score']} / 100")
            st.markdown(f"**Missing Skills:** {', '.join(result['missing_skills'])}")
            st.markdown(f"**Profile Summary:**\n{result['summary']}")
            if result.get('score', 0) > 75 and result.get('questions'):
                st.markdown("### Auto-Generated Interview Questionnaire")
                for i, q in enumerate(result['questions'], 1):
                    st.markdown(f"{i}. {q['question']}")
                    st.markdown(f"    *Expected Answer:* {q['expected_answer']}")
    else:
        st.warning("Please upload a resume and select a job description.")
