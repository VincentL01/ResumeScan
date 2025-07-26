import re
from typing import List, Dict

def extract_score(text: str) -> int:
    match = re.search(r"(\d{1,3})\s*/\s*100", text)
    return int(match.group(1)) if match else 0

def extract_summary(comparison: str) -> str:
    match = re.search(r"\*\*Summary of Alignment:\*\*(.*?)\*\*Match Score", comparison, re.DOTALL)
    return match.group(1).strip() if match else comparison.strip()

def question_raw_parser(text: str) -> List[Dict[str, str]]:
    """
    Extracts question-answer pairs from raw markdown-style Gemini output.
    Looks for **Question:** and **Expected Answer:** blocks.
    """
    questions = []
    blocks = re.split(r"\*\*Question \d+:.*?\*\*", text)

    for block in blocks:
        q_match = re.search(r"\*\*Question:\*\*\s*(.*?)(?=\*\*Expected Answer:\*\*)", block, re.DOTALL)
        a_match = re.search(r"\*\*Expected Answer:\*\*\s*(.*?)(?=\n{2,}|\Z)", block, re.DOTALL)
        if q_match and a_match:
            questions.append({
                "question": q_match.group(1).strip().replace('\n', ' '),
                "expected_answer": a_match.group(1).strip().replace('\n', ' ')
            })
    return questions

def extract_missing_skills(text: str) -> List[str]:
    """
    Extracts missing skill entries from the 'Missing Skills' section.
    """
    section_match = re.search(r"\*\*Missing Skills:\*\*(.*?)(\n\*\*|$)", text, re.DOTALL)
    if not section_match:
        return []

    section = section_match.group(1)
    # Match bullet points that start with `* **<something>:** <desc>`
    matches = re.findall(r"\*\s*\*\*(.*?)\*\*:\s*(.*?)(?=\n\*|\Z)", section, re.DOTALL)

    parsed = []
    for title, desc in matches:
        clean_desc = desc.strip().replace("\n", " ")
        parsed.append(f"{title.strip()}: {clean_desc}")
    return parsed