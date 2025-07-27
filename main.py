import streamlit as st
from app.processor import analyze_resume, refine_questions
from app.utils import is_acceptable_score
import os

st.set_page_config(page_title="ResumeScan", layout="centered")
st.title("Resume & JD Analyzer")

st.markdown("""
Upload your resume (PDF) and select a job description (JD) below.
The app will analyze your resume and generate a match score, missing keywords, and tailored interview questions.
""")

# --- State Management ---
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'questions' not in st.session_state:
    st.session_state.questions = []

# --- UI Components ---
JD_DIR = os.path.join(os.path.dirname(__file__), "documents", "JD")
jd_files = [f for f in os.listdir(JD_DIR) if f.endswith(".md")]
selected_jd = st.selectbox("Select Job Description (JD)", jd_files)

uploaded_resume = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

if st.button("Analyze Resume"):
    if uploaded_resume and selected_jd:
        with st.spinner("Analyzing..."):
            jd_path = os.path.join(JD_DIR, selected_jd)
            result = analyze_resume(uploaded_resume, jd_path)
            st.session_state.analysis_result = result
            st.session_state.questions = result.get('questions', [])
            st.session_state.conversation_history = [] # Reset history
            st.rerun() # Rerun to display results immediately
    else:
        st.warning("Please upload a resume and select a job description.")

# --- Display Analysis and Chat ---
if st.session_state.analysis_result:
    result = st.session_state.analysis_result
    st.subheader(f"Match Score: {result['score']} / 100")
    st.markdown(f"**Missing Skills:** {', '.join(result['missing_skills'])}")
    st.markdown(f"**Profile Summary:**\n{result['summary']}")

    if is_acceptable_score(result.get('score', 0)):
        st.markdown("### Interview Questionnaire")
        
        # Display current questions
        for i, q in enumerate(st.session_state.questions, 1):
            st.markdown(f"**{i}. {q['question']}**")
            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;*Expected Answer:* {q['expected_answer']}")

        st.markdown("---")
        st.markdown("#### Refine Questions")
        st.markdown("You can chat with the AI to refine these questions. Provide additional context or ask for changes.")

        # Chat input
        user_prompt = st.chat_input("Your message...")
        if user_prompt:
            with st.spinner("Thinking..."):
                refinement_result = refine_questions(
                    comparison_result=result['comparison_result_gemini'],
                    user_message=user_prompt,
                    conversation_history=st.session_state.conversation_history
                )

                if "warning" in refinement_result:
                    st.warning(refinement_result["warning"])
                else:
                    st.session_state.questions = refinement_result.get('questions', [])
                    st.session_state.conversation_history = refinement_result.get('conversation_history', [])
                    st.rerun()
