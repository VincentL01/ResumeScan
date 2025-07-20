import re
from typing import List, Dict
import PyPDF2
import tempfile

def extract_text_from_pdf(uploaded_file) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    text = ""
    with open(tmp_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_md(md_path: str) -> str:
    with open(md_path, "r", encoding="utf-8") as f:
        return f.read()

def is_acceptable_score(score: int) -> bool:
    return score >= 75

def has_match_score(comparison: str) -> bool:
    return "match score" in comparison.lower()


