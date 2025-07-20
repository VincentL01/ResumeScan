import os
import uuid
from typing import Dict
from dotenv import load_dotenv
import google.generativeai as genai
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.utils import is_acceptable_score, has_match_score
from app.parser import extract_score

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")
VERBOSE = False

# Shared input/output schema
State = Dict[str, str]

def resume_parser_agent(state: State, verbose:bool = VERBOSE) -> State:
    prompt = f"""
You are a resume analyzer. Extract the following from this resume:
- Profile Summary
- Key Skills
- Work Experiences

Resume:
{state['resume_text']}
"""
    model = genai.GenerativeModel(MODEL_NAME)
    res = model.generate_content(prompt)
    if verbose:
        print("DEBUG Resume Agent:", res.text)
    state["resume_analysis"] = res.text
    return state

def jd_parser_agent(state: State, verbose:bool = VERBOSE) -> State:
    prompt = f"""
You are a job description analyzer. Extract the following:
- Role Summary
- Core Responsibilities
- Required Skills and Qualifications

JD:
{state['jd_text']}
"""
    model = genai.GenerativeModel(MODEL_NAME)
    res = model.generate_content(prompt)
    if verbose:
        print("DEBUG JD Agent:", res.text)
    state["jd_analysis"] = res.text
    return state

def comparison_agent(state: Dict[str, str], verbose:bool = VERBOSE) -> Dict[str, str]:
    prompt = f"""
You are a comparison engine. Given a resume and a job description (JD), do the following:

1. Identify and list **Matching Skills** using bullet points, with categories such as Programming, Cloud, Storage, etc.
2. Identify **Missing Skills**, even if partially present or indirectly implied. Use the format:
   * **<Skill Category>:** Explanation
3. Write a **Summary of Alignment** — 2 to 4 sentences summarizing the match.
4. Assign a **Match Score (/100)** considering both technical and soft skill alignment.

### Example Format:

**Matching Skills:**

* **Programming:** Python, SQL (Both)
* **Data Platforms:** Spark, Trino (Resume stronger)
* ...

**Missing Skills:**

* **Cloud Platforms:** Resume lacks AWS Glue, ADF
* **CI/CD Tools:** GitHub Actions not mentioned
* ...

**Summary of Alignment:**

The candidate demonstrates strong core competencies... [etc.]

**Match Score (/100):**
87/100

---

Resume Analysis:
{state['resume_analysis']}

JD Analysis:
{state['jd_analysis']}
"""
    model = genai.GenerativeModel(MODEL_NAME)
    res = model.generate_content(prompt)
    if verbose:
        print("DEBUG Comparison Agent:", res.text)
    state["comparison_result"] = res.text
    return state

def question_generation_agent(state: State, verbose:bool = VERBOSE) -> State:
    prompt = f"""
You are an interview coach. Based on the following analysis, generate 3 interview questions with expected answers. The goal is to probe the candidate further on their strengths and address possible gaps.

For each question, return:
- The **Question**
- The **Expected Answer**

Use the following format:

**Question 1: Topic Title**

**Question:** "..."

**Expected Answer:** ...

**Question 2: Another Topic**

**Question:** "..."

**Expected Answer:** ...

Comparison Result:
{state['comparison_result']}
"""
    model = genai.GenerativeModel(MODEL_NAME)
    res = model.generate_content(prompt)
    if verbose:
        print("DEBUG Question Agent:", res.text)
    state["questions_raw"] = res.text
    return state

def build_resume_scan_graph():
    builder = StateGraph(State)
    builder.add_node("ParseResume", resume_parser_agent)
    builder.add_node("ParseJD", jd_parser_agent)
    builder.add_node("Compare", comparison_agent)
    builder.add_node("GenerateQuestions", question_generation_agent)

    builder.set_entry_point("ParseResume")
    builder.add_edge("ParseResume", "ParseJD")
    builder.add_edge("ParseJD", "Compare")
    builder.add_conditional_edges("Compare", lambda state:
        "GenerateQuestions" if has_match_score(state["comparison_result"]) and is_acceptable_score(extract_score(state["comparison_result"]))
        else END,
        {
            "GenerateQuestions": "GenerateQuestions",
            END: END
        })
    builder.add_edge("GenerateQuestions", END)

    return builder.compile(checkpointer=MemorySaver())