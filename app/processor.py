import uuid
from typing import Dict
from app.graph import build_resume_scan_graph, question_refinement_agent
from app.parser import extract_score, extract_summary, extract_missing_skills, question_raw_parser
from app.utils import get_resume_text, get_jd_text, is_acceptable_score

def analyze_resume(uploaded_resume, jd_path: str) -> Dict:
    resume_text = get_resume_text(uploaded_resume)
    jd_text = get_jd_text(jd_path)

    graph = build_resume_scan_graph()
    result = graph.invoke(
        {
            "resume_text": resume_text,
            "jd_text": jd_text,
        },
        config={"configurable": {"thread_id": str(uuid.uuid4())}}
    )

    comparison = result.get("comparison_result", "")
    score = extract_score(comparison)
    summary = extract_summary(comparison)
    missing_skills = extract_missing_skills(comparison)
    questions = []

    if is_acceptable_score(score) and "questions_raw" in result:
        raw = result["questions_raw"]
        questions = question_raw_parser(raw)

    return {
        "score": score,
        "missing_skills": missing_skills,
        "summary": summary,
        "questions": questions,
        "comparison_result": comparison
    }

def refine_questions(comparison_result: str, user_message: str, conversation_history: list) -> dict:
    """
    Calls the question refinement agent.
    """
    state = {
        "comparison_result": comparison_result,
        "user_message": user_message,
        "conversation_history": conversation_history,
    }
    
    result_state = question_refinement_agent(state)
    
    refined_questions_raw = result_state.get("refined_questions", "")
    
    warning_message = "I can only help with refining the interview questions."
    if warning_message in refined_questions_raw:
        return {"warning": refined_questions_raw, "conversation_history": result_state.get("conversation_history", [])}

    questions = question_raw_parser(refined_questions_raw)
    
    return {"questions": questions, "conversation_history": result_state.get("conversation_history", [])}

