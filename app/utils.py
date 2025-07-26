import re
import pdfplumber
from typing import IO

def is_acceptable_score(score: int, threshold: int = 75) -> bool:
    return score >= threshold

def has_match_score(text: str) -> bool:
    return "match score" in text.lower()

def get_resume_text(resume_file: IO[bytes]) -> str:
    """
    Extracts text from an uploaded PDF file.
    """
    with pdfplumber.open(resume_file) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages)

def get_jd_text(jd_path: str) -> str:
    """
    Extracts text from a markdown file.
    """
    with open(jd_path, 'r', encoding='utf-8') as f:
        return f.read()


