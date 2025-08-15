import streamlit as st
import streamlit.components.v1 as components
from app.processor import ResumeProcessor
from app.utils import is_acceptable_score
import os

st.set_page_config(page_title="ResumeScan", layout="centered")
st.title("Resume & JD Analyzer")

# --- State Management ---
if 'sessions' not in st.session_state:
    st.session_state.sessions = {}
if 'current_session' not in st.session_state:
    st.session_state.current_session = None

processor = ResumeProcessor()

def inline_rename(name: str, comp_id: str):
    """
    Returns {'action':'rename', 'name': '<new name>'} when Enter is pressed after double-click.
    Esc or clicking outside cancels. Otherwise returns None.
    comp_id should be unique per session row (e.g., f"rename_{session_id}").
    """
    wrap_id   = f"{comp_id}_wrap"
    label_id  = f"{comp_id}_label"
    input_id  = f"{comp_id}_editor"

    html = f"""
    <div id="{wrap_id}" style="display:flex; align-items:center; gap:8px; font-family:inherit;">
      <div id="{label_id}" title="Double-click to rename"
           style="cursor:text; padding:4px 8px; border-radius:8px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:220px;">
        {name}
      </div>
      <input id="{input_id}" value="{name}"
             style="display:none; padding:4px 8px; border:1px solid #ddd; border-radius:8px; width:220px; font:inherit;" />
    </div>
    <script>
      const wrap   = document.getElementById('{wrap_id}');
      const label  = document.getElementById('{label_id}');
      const editor = document.getElementById('{input_id}');
      let original = editor.value;

      function startEdit() {{
        label.style.display = 'none';
        editor.style.display = 'block';
        editor.focus();
        editor.select();
      }}

      function sendValue(obj) {{
        // deliver value back to this component
        window.parent.postMessage({{ type: 'streamlit:setComponentValue', value: obj }}, '*');
      }}

      function finish(save) {{
        if (save) {{
          const v = editor.value.trim();
          if (v && v !== original) {{
            sendValue({{ action: 'rename', name: v }});
          }} else {{
            sendValue(null);
          }}
        }} else {{
          editor.value = original;
          sendValue(null);
        }}
        editor.style.display = 'none';
        label.style.display = 'block';
      }}

      label.ondblclick = () => startEdit();

      editor.addEventListener('keydown', (e) => {{
        if (e.key === 'Enter') {{
          e.preventDefault();
          finish(true);
        }} else if (e.key === 'Escape') {{
          e.preventDefault();
          finish(false);
        }}
      }});

      document.addEventListener('click', (e) => {{
        const editing = editor.style.display === 'block';
        if (editing && !wrap.contains(e.target)) {{
          finish(false);
        }}
      }});
    </script>
    """
    # NOTE: no 'key' argument here
    return components.html(html, height=40, scrolling=False)

# --- Helper Functions ---
def create_new_session():
    session_id = f"session_{len(st.session_state.sessions) + 1}"
    st.session_state.sessions[session_id] = {
        "name": f"Session {len(st.session_state.sessions) + 1}",
        "analysis_result": None,
        "conversation_history": [],
        "questions": []
    }
    st.session_state.current_session = session_id

def switch_session(session_id):
    st.session_state.current_session = session_id

def rename_session(session_id, new_name):
    if session_id in st.session_state.sessions:
        st.session_state.sessions[session_id]["name"] = new_name

def delete_session(session_id):
    if session_id in st.session_state.sessions:
        del st.session_state.sessions[session_id]
        if st.session_state.current_session == session_id:
            st.session_state.current_session = None

def add_jd(uploaded_file):
    if uploaded_file:
        file_path = os.path.join("documents", "JD", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"JD '{uploaded_file.name}' added successfully.")
        st.rerun()

# --- Sidebar for Session Management ---
with st.sidebar:
    st.title("Sessions")

    if 'confirm_delete' not in st.session_state:
        st.session_state.confirm_delete = None  # session_id awaiting confirmation

    if st.button("New Session", icon="➕"):
        create_new_session()

    # Sessions list
    for session_id, session_data in list(st.session_state.sessions.items()):
        with st.container(border=True):
            col_name, col_x = st.columns([0.9, 0.1])

            with col_name:
                # Inline rename (double-click)
                comp_result = inline_rename(session_data['name'], comp_id=f"rename_{session_id}")

                if isinstance(comp_result, dict) and comp_result.get("action") == "rename":
                    new_name = comp_result.get("name", "").strip()
                    if new_name:
                        rename_session(session_id, new_name)
                        st.rerun()

                # Optional "Open" button
                st.caption("Double-click to rename • Enter to save • Esc/click outside to cancel")
                if st.button("Open", key=f"open_{session_id}"):
                    switch_session(session_id)
                    st.rerun()

            with col_x:
                # X delete button → trigger confirmation
                if st.button("✖", key=f"delete_btn_{session_id}"):
                    st.session_state.confirm_delete = session_id
                    st.rerun()

    # Delete confirmation section (rendered when triggered)
    if st.session_state.confirm_delete is not None:
        sid = st.session_state.confirm_delete
        st.warning(f"Delete **{st.session_state.sessions[sid]['name']}**? This cannot be undone.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Yes, delete", type="primary", use_container_width=True):
                delete_session(sid)
                st.session_state.confirm_delete = None
                st.rerun()
        with c2:
            if st.button("Cancel", use_container_width=True):
                st.session_state.confirm_delete = None
                st.rerun()

    st.title("Add JD")
    uploaded_jd = st.file_uploader("Upload JD", type=["md", "txt"])
    if st.button("Add JD"):
        add_jd(uploaded_jd)


# --- Main App ---
if not st.session_state.current_session and not st.session_state.sessions:
    create_new_session()

if st.session_state.current_session:
    current_session_data = st.session_state.sessions[st.session_state.current_session]

    st.markdown("""
    Upload your resume (PDF) and select a job description (JD) below.
    The app will analyze your resume and generate a match score, missing keywords, and tailored interview questions.
    """)

    # --- UI Components ---
    JD_DIR = os.path.join(os.path.dirname(__file__), "documents", "JD")
    jd_files = [f for f in os.listdir(JD_DIR) if f.endswith((".md", ".txt"))]
    selected_jd = st.selectbox("Select Job Description (JD)", jd_files)

    uploaded_resume = st.file_uploader("Upload Resume", type=["pdf", "docx"])

    if st.button("Analyze Resume"):
        if uploaded_resume and selected_jd:
            with st.spinner("Analyzing..."):
                jd_path = os.path.join(JD_DIR, selected_jd)
                result = processor.analyze_resume(uploaded_resume, jd_path)
                current_session_data['analysis_result'] = result
                current_session_data['questions'] = result.get('questions', [])
                current_session_data['conversation_history'] = [] # Reset history
                st.rerun()
        else:
            st.warning("Please upload a resume and select a job description.")

    # --- Display Analysis and Chat ---
    if current_session_data['analysis_result']:
        result = current_session_data['analysis_result']
        st.subheader(f"Match Score: {result['score']} / 100")
        st.markdown(f"**Missing Skills:** {', '.join(result['missing_skills'])}")
        st.markdown(f"**Profile Summary:**\n{result['summary']}")

        if is_acceptable_score(result.get('score', 0)):
            st.markdown("### Interview Questionnaire")
            
            # Display current questions
            for i, q in enumerate(current_session_data['questions'], 1):
                st.markdown(f"**{i}. {q['question']}**")
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;*Expected Answer:* {q['expected_answer']}")

            st.markdown("---")
            st.markdown("#### Refine Questions")
            st.markdown("You can chat with the AI to refine these questions. Provide additional context or ask for changes.")

            # Chat input
            user_prompt = st.chat_input("Your message...")
            if user_prompt:
                with st.spinner("Thinking..."):
                    refinement_result = processor.refine_questions(
                        comparison_result=result['comparison_result'],
                        user_message=user_prompt,
                        conversation_history=current_session_data['conversation_history']
                    )

                    if "warning" in refinement_result:
                        st.warning(refinement_result["warning"])
                    else:
                        current_session_data['questions'] = refinement_result.get('questions', [])
                        current_session_data['conversation_history'] = refinement_result.get('conversation_history', [])
                        st.rerun()
else:
    st.info("Create a new session to start.")
