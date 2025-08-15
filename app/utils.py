import os
import docx
import pdfplumber
import pytesseract
from typing import IO
from app.configs import ACCEPTABLE_SCORE_THRESHOLD


def is_acceptable_score(score: int, threshold: int = ACCEPTABLE_SCORE_THRESHOLD) -> bool:
    return score >= threshold

def has_match_score(text: str) -> bool:
    return "match score" in text.lower()

def get_resume_text(resume_file: IO[bytes]) -> str:
    """
    Extracts text from an uploaded file.
    Supports PDF (with OCR fallback) and DOCX.
    """
    file_extension = os.path.splitext(resume_file.name)[1].lower()

    if file_extension == ".pdf":
        with pdfplumber.open(resume_file) as pdf:
            text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
        
        if not text:
            # If no text was extracted, try OCR
            resume_file.seek(0)
            try:
                images = []
                with pdfplumber.open(resume_file) as pdf:
                    for page in pdf.pages:
                        images.extend(page.to_image().original)
                
                ocr_text = "[OCR TEXT]\n"
                for img in images:
                    ocr_text += pytesseract.image_to_string(img)
                
                ocr_text += "\n[END OCR TEXT]"
                
                # Save the OCR text to a file
                if not os.path.exists("documents/ocr_texts"):
                    os.makedirs("documents/ocr_texts")
                
                file_name = os.path.splitext(os.path.basename(resume_file.name))[0]
                with open(f"documents/ocr_texts/{file_name}.txt", "w", encoding="utf-8") as f:
                    f.write(ocr_text)
                
                text = ocr_text
            except Exception as e:
                print(f"OCR failed: {e}")
                return ""
        return text
    
    elif file_extension == ".docx":
        doc = docx.Document(resume_file)
        return "\n".join([para.text for para in doc.paragraphs])
    
    else:
        return ""

def get_jd_text(jd_path: str) -> str:
    """
    Extracts text from a markdown file.
    """
    with open(jd_path, 'r', encoding='utf-8') as f:
        return f.read()


