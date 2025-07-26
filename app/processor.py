import uuid
from typing import Dict
from app.graph import build_resume_scan_graph
from app.parser import extract_score, extract_summary, extract_missing_skills, question_raw_parser
from app.utils import extract_text_from_pdf, extract_text_from_md, is_acceptable_score

def analyze_resume(uploaded_resume, jd_path: str) -> Dict:
    resume_text = extract_text_from_pdf(uploaded_resume)
    jd_text = extract_text_from_md(jd_path)

    graph = build_resume_scan_graph()
    result = graph.invoke(
        {
            "resume_text": resume_text,
            "jd_text": jd_text,
        },
        config={"thread_id": str(uuid.uuid4())}  # Unique ID for this run
    )

    comparison = result.get("comparison_result", "")
    score = extract_score(comparison)
    summary = extract_summary(comparison)
    missing_skills = extract_missing_skills(comparison)
    questions = []

    if is_acceptable_score(score) and "questions_raw" in result:
        # Parse 3 questions from raw text
        raw = result["questions_raw"]
        questions = question_raw_parser(raw)
        if not questions:
            print("⚠️ No questions parsed from:\n", raw)

    return {
        "score": score,
        "missing_skills": missing_skills,
        "summary": summary,
        "questions": questions
    }
