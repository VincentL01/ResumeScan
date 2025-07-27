import streamlit as st
from app.processor import analyze_resume, refine_questions
from app.utils import is_acceptable_score
from db.cv_storage import cv_storage
from db.models import CVSearchQuery
from pymongo.errors import DuplicateKeyError
import os

st.set_page_config(page_title="ResumeScan", layout="centered")
st.title("Resume & JD Analyzer")

# Display AI provider information
try:
    from app.ai_provider import ai_provider
    provider_info = ai_provider.get_provider_info()
    st.info(f"🤖 Using {provider_info['provider']} ({provider_info['model']}) for AI analysis")
except Exception as e:
    st.error(f"❌ AI Provider Error: {e}")
    st.error("Please configure GEMINI_API_KEY or OPENAI_API_KEY in .streamlit/secrets.toml")
    st.stop()

st.markdown("""
Upload your resume (PDF) and select a job description (JD) below.
The app will analyze your resume and generate a match score, missing keywords, and tailored interview questions.
All uploaded CVs are stored securely in the database for future reference.
""")

# --- State Management ---
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'current_file_id' not in st.session_state:
    st.session_state.current_file_id = None

# --- Sidebar for CV Management ---
with st.sidebar:
    st.header("📁 CV Database")
    
    # Display database statistics
    try:
        stats = cv_storage.get_file_stats()
        if stats:
            st.metric("Total CVs", stats.get('total_files', 0))
            st.metric("Analyzed CVs", stats.get('analyzed_files', 0))
            if stats.get('average_match_score', 0) > 0:
                st.metric("Avg Match Score", f"{stats.get('average_match_score', 0)}%")
    except Exception as e:
        st.error(f"Database connection error: {e}")
    
    # Search stored CVs
    st.subheader("🔍 Search CVs")
    search_filename = st.text_input("Search by filename", placeholder="Enter filename...")
    min_score = st.number_input("Min match score", min_value=0, max_value=100, value=0)
    
    if st.button("Search CVs"):
        try:
            search_query = CVSearchQuery(
                filename=search_filename if search_filename else None,
                min_match_score=min_score if min_score > 0 else None
            )
            results = cv_storage.search_cv_files(search_query, limit=10)
            
            if results:
                st.write(f"Found {len(results)} CVs:")
                for cv in results:
                    with st.expander(f"📄 {cv['filename']}"):
                        st.write(f"**Upload Date:** {cv['upload_date']}")
                        if cv.get('match_score'):
                            st.write(f"**Match Score:** {cv['match_score']}%")
                        if cv.get('job_description'):
                            st.write(f"**Job Description:** {cv['job_description']}")
                        
                        # Load analysis button
                        if st.button(f"Load Analysis", key=f"load_{cv['_id']}"):
                            st.session_state.current_file_id = cv.get('gridfs_file_id', cv['_id'])
                            if cv.get('analysis_results'):
                                st.session_state.analysis_result = cv['analysis_results']
                                st.session_state.questions = cv.get('questions', [])
                                st.rerun()
            else:
                st.info("No CVs found matching your criteria.")
        except Exception as e:
            st.error(f"Search failed: {e}")

# --- UI Components ---
JD_DIR = os.path.join(os.path.dirname(__file__), "documents", "JD")
jd_files = [f for f in os.listdir(JD_DIR) if f.endswith(".md")]
selected_jd = st.selectbox("Select Job Description (JD)", jd_files)

uploaded_resume = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

# Show file upload status
if uploaded_resume:
    st.success(f"✅ File uploaded: {uploaded_resume.name} ({uploaded_resume.size} bytes)")

if st.button("Analyze Resume"):
    if uploaded_resume and selected_jd:
        with st.spinner("Analyzing and storing resume..."):
            try:
                # Read file content
                file_content = uploaded_resume.read()
                uploaded_resume.seek(0)  # Reset file pointer for analysis
                
                # Store in MongoDB first
                try:
                    file_id, metadata = cv_storage.store_cv_file(
                        uploaded_resume, 
                        file_content, 
                        job_description=selected_jd
                    )
                    st.session_state.current_file_id = file_id
                    st.success(f"✅ CV stored in database with ID: {file_id[:8]}...")
                except DuplicateKeyError:
                    st.warning("⚠️ This file has already been uploaded. Using existing version.")
                    # Find existing file by hash
                    from db.models import CVFileMetadata
                    file_hash = CVFileMetadata.calculate_file_hash(file_content)
                    existing_files = cv_storage.search_cv_files(CVSearchQuery())
                    for existing_file in existing_files:
                        if existing_file.get('file_hash') == file_hash:
                            st.session_state.current_file_id = existing_file.get('gridfs_file_id', existing_file['_id'])
                            if existing_file.get('analysis_results'):
                                st.session_state.analysis_result = existing_file['analysis_results']
                                st.session_state.questions = existing_file.get('questions', [])
                                st.session_state.conversation_history = []
                                st.rerun()
                            break
                
                # Perform analysis
                jd_path = os.path.join(JD_DIR, selected_jd)
                result = analyze_resume(uploaded_resume, jd_path)
                st.session_state.analysis_result = result
                st.session_state.questions = result.get('questions', [])
                st.session_state.conversation_history = [] # Reset history
                
                # Update database with analysis results
                if st.session_state.current_file_id:
                    success = cv_storage.update_analysis_results(
                        st.session_state.current_file_id, 
                        result
                    )
                    if success:
                        st.success("✅ Analysis results saved to database")
                    else:
                        st.warning("⚠️ Failed to save analysis results")
                
                st.rerun() # Rerun to display results immediately
                
            except Exception as e:
                st.error(f"❌ Error during analysis: {e}")
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
                    comparison_result=result['comparison_result'],
                    user_message=user_prompt,
                    conversation_history=st.session_state.conversation_history
                )

                if "warning" in refinement_result:
                    st.warning(refinement_result["warning"])
                else:
                    st.session_state.questions = refinement_result.get('questions', [])
                    st.session_state.conversation_history = refinement_result.get('conversation_history', [])
                    st.rerun()
