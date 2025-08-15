import os
import streamlit as st
import streamlit.components.v1 as components

from app.processor import ResumeProcessor
from app.utils import is_acceptable_score
from app.chat_memory import ChatMemory


st.set_page_config(page_title="ResumeScan", layout="centered")
st.title("Resume & JD Analyzer")

# ----------------- Inline rename (same as before) -----------------
def inline_rename(name: str, comp_id: str):
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
        window.parent.postMessage({{ type: 'streamlit:setComponentValue', value: obj }}, '*');
      }}

      function finish(save) {{
        if (save) {{
          const v = editor.value.trim();
          if (v && v !== original) {{
            label.textContent = v;
            original = v;
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
    return components.html(html, height=40, scrolling=False)

# ----------------- Services -----------------
processor = ResumeProcessor()
memory = ChatMemory()
memory.ensure_one_session()

# UI state
if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = None
if "show_extra_criteria" not in st.session_state:
    st.session_state.show_extra_criteria = False

# ----------------- Sidebar: Sessions -----------------
with st.sidebar:
    st.title("Sessions")

    if st.button("New Session", icon="➕"):
        memory.create_session()
        st.rerun()

    for session_id, session_data in list(memory.sessions.items()):
        with st.container(border=True):
            col_name, col_x = st.columns([0.9, 0.1])

            with col_name:
                name_hash = abs(hash(session_data["name"])) % 1_000_000
                comp_result = inline_rename(session_data["name"], comp_id=f"rename_{session_id}_{name_hash}")
                if isinstance(comp_result, dict) and comp_result.get("action") == "rename":
                    new_name = comp_result.get("name", "").strip()
                    if new_name:
                        memory.rename_session(session_id, new_name)
                        st.rerun()

                st.caption("Double-click to rename • Enter to save • Esc/click outside to cancel")
                if st.button("Open", key=f"open_{session_id}"):
                    memory.switch_session(session_id)
                    st.rerun()

            with col_x:
                if st.button("✖", key=f"delete_btn_{session_id}"):
                    st.session_state.confirm_delete = session_id
                    st.rerun()

    if st.session_state.confirm_delete is not None:
        sid = st.session_state.confirm_delete
        if sid not in memory.sessions:
            st.session_state.confirm_delete = None
            st.rerun()
        else:
            st.warning(f"Delete **{memory.sessions[sid]['name']}**? This cannot be undone.")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Yes, delete", type="primary", use_container_width=True):
                    memory.delete_session(sid)
                    st.session_state.confirm_delete = None
                    st.rerun()
            with c2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.confirm_delete = None
                    st.rerun()

    st.title("Add JD")
    uploaded_jd = st.file_uploader("Upload JD", type=["md", "txt"])
    if st.button("Add JD"):
        if uploaded_jd:
            file_path = os.path.join("documents", "JD", uploaded_jd.name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(uploaded_jd.getbuffer())
            st.success(f"JD '{uploaded_jd.name}' added successfully.")
            st.rerun()
        else:
            st.warning("Please choose a JD file first.")

# ----------------- Main App -----------------
if not memory.current_session:
    memory.ensure_one_session()

current = memory.get_current()

if current:
    st.markdown("""
    Upload your resume (PDF) and select a job description (JD) below.
    The app will analyze your resume and generate a match score, missing keywords, and tailored interview questions.
    """)

    # -------- Extra Scoring Criteria (MAIN SCREEN) --------
    extra_val = memory.get_extra_criteria(memory.current_session)
    if not st.session_state.show_extra_criteria:
        if st.button("➕ Extra Scoring Criteria"):
            st.session_state.show_extra_criteria = True
            st.rerun()
    else:
        with st.expander("Extra Scoring Criteria", expanded=True):
            new_extra = st.text_area(
                "Add bullet-pointed criteria that should influence the score",
                value=extra_val,
                placeholder="Enter around 5 extra criteria, in bulletpoints for maxium efficiency",
                height=160,
                key="extra_criteria_text",
            )
            col_apply, col_clear = st.columns([0.3, 0.7])
            with col_apply:
                if st.button("Save Criteria", type="primary"):
                    memory.set_extra_criteria(memory.current_session, new_extra.strip())
                    st.success("Saved.")
            with col_clear:
                if st.button("Clear"):
                    memory.set_extra_criteria(memory.current_session, "")
                    st.session_state.extra_criteria_text = ""
                    st.experimental_rerun()

    # -------- JD / Resume --------
    JD_DIR = os.path.join(os.path.dirname(__file__), "documents", "JD")
    os.makedirs(JD_DIR, exist_ok=True)
    jd_files = [f for f in os.listdir(JD_DIR) if f.endswith((".md", ".txt"))]
    selected_jd = st.selectbox("Select Job Description (JD)", jd_files)

    uploaded_resume = st.file_uploader("Upload Resume", type=["pdf", "docx"])

    if st.button("Analyze Resume"):
        if uploaded_resume and selected_jd:
            with st.spinner("Analyzing..."):
                jd_path = os.path.join(JD_DIR, selected_jd)
                # Pass extra criteria when analyzing (ensure your ResumeProcessor forwards it into the graph state)
                extra_criteria = memory.get_extra_criteria(memory.current_session).strip()
                result = processor.analyze_resume(
                    uploaded_resume,
                    jd_path,
                    extra_criteria=extra_criteria if extra_criteria else None,  # None -> omit in graph
                )
                memory.update_analysis(
                    memory.current_session,
                    analysis_result=result,
                    questions=result.get("questions", []),
                    reset_history=True,
                )
                st.rerun()
        else:
            st.warning("Please upload a resume and select a job description.")

    # -------- Results & Chat --------
    current = memory.get_current()
    if current and current["analysis_result"]:
        result = current["analysis_result"]

        st.subheader(f"Match Score: {result.get('score', 0)} / 100")
        missing = result.get("missing_skills") or []
        st.markdown(f"**Missing Skills:** {', '.join(missing) if missing else 'None'}")
        st.markdown(f"**Profile Summary:**\n{result.get('summary', '')}")

        if is_acceptable_score(result.get("score", 0)):
            st.markdown("### Interview Questionnaire")

            for i, q in enumerate(current.get("questions", []), 1):
                st.markdown(f"**{i}. {q.get('question','')}**")
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;*Expected Answer:* {q.get('expected_answer','')}")

            st.markdown("---")
            st.markdown("#### Refine Questions")
            st.markdown("You can chat with the AI to refine these questions. Provide additional context or ask for changes.")

            user_prompt = st.chat_input("Your message...")
            if user_prompt:
                with st.spinner("Thinking..."):
                    refinement_result = processor.refine_questions(
                        comparison_result=result.get("comparison_result"),
                        user_message=user_prompt,
                        conversation_history=current.get("conversation_history", []),
                    )

                    if "warning" in refinement_result:
                        st.warning(refinement_result["warning"])
                    else:
                        memory.set_questions(memory.current_session, refinement_result.get("questions", []))
                        memory.replace_conversation(
                            memory.current_session,
                            refinement_result.get("conversation_history", []),
                        )
                        st.rerun()
else:
    st.info("Create a new session to start.")
