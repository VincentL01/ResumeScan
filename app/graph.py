import os
import uuid
import streamlit as st
from typing import Dict
import google.generativeai as genai
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.utils import is_acceptable_score, has_match_score
from app.parser import extract_score
import openai

GEMINI_MODEL_NAME = st.secrets.get("GEMINI_MODEL_NAME", "gemini-2.5-flash")
api_key=st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
geminiModel = genai.GenerativeModel(GEMINI_MODEL_NAME)

OPENAI_MODEL_NAME = st.secrets.get("OPENAI_MODEL_NAME", "gpt-4o-mini")
client = openai.OpenAI(
    base_url="https://aiportalapi.stu-platform.live/use",
    api_key=st.secrets["OPENAI_API_KEY"]
)

model = geminiModel

QUESTIONS = 5
VERBOSE = False

# Shared input/output schema
State = Dict[str, any]

def resume_parser_agent(state: State, verbose:bool = VERBOSE) -> State:
    prompt = f"""
You are a resume analyzer. Extract the following from this resume:
- Profile Summary
- Key Skills
- Work Experiences

Resume:
{state['resume_text']}
"""
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
    res = model.generate_content(prompt)
    if verbose:
        print("DEBUG JD Agent:", res.text)
    state["jd_analysis"] = res.text
    return state

def comparison_agent(state: Dict[str, str], model_type: str = "gemini", verbose:bool = VERBOSE) -> Dict[str, str]:
    prompt = f"""
**System prompt:**
You are a comparison engine. Given a resume and a job description (JD), do the following:

**Instructions:**
1. Identify and list **Matching Skills** using bullet points, with categories such as Programming, Cloud, Storage, etc.
2. Identify **Missing Skills**, even if partially present or indirectly implied. Use the format:
   * **<Skill Category>:** Explanation
3. Write a **Summary of Alignment** — 2 to 4 sentences summarizing the match.
4. Assign a **Match Score (/100)** considering both technical and soft skill alignment.
5. Use the following example format:

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
    if model_type == "openai":
        openai_response = client.chat.completions.create(
            model=OPENAI_MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
        result = openai_response.choices[0].message.content
        state["comparison_result_openai"] = result
        if verbose:
            print("DEBUG Comparison Agent (OpenAI):", result)
    else:
        res = model.generate_content(prompt)
        state["comparison_result_gemini"] = res.text
        if verbose:
            print("DEBUG Comparison Agent (Gemini):", res.text)
    genai.configure(api_key=api_key)
    return state

def average_comparison_results(state: Dict[str, str], verbose:bool = VERBOSE) -> Dict[str, str]:
    from app.parser import extract_score
    gemini_result = state.get("comparison_result_gemini", "")
    openai_result = state.get("comparison_result_openai", "")
    gemini_score = extract_score(gemini_result)
    openai_score = extract_score(openai_result)
    average_score = int(round((gemini_score + openai_score) / 2))
    
    if verbose:
        print("DEBUG Average Node (Gemini):", gemini_result)
        print("DEBUG Average Node (OpenAI):", openai_result)
        print("DEBUG Average Node (Average Score):", average_score)
    state["comparison_score"] = average_score
    return state

def question_generation_agent(state: State, verbose:bool = VERBOSE) -> State:
    prompt = f"""
**System prompt:**
You are an interview coach. Based on the following analysis, generate {QUESTIONS} interview questions with expected answers. The goal is to probe the candidate further on their strengths and address possible gaps.

**Instructions:**
1. The number of questions if not given in the user's request, it should be default to {QUESTIONS} questions.
2. For each question, return:
- The **Question**
- The **Expected Answer**
3. Use the following format:

**Question 1: Topic Title**

**Question:** "..."

**Expected Answer:** ...

**Question 2: Another Topic**

**Question:** "..."

**Expected Answer:** ...

Comparison Result:
{state['comparison_result_gemini']}
"""
    res = model.generate_content(prompt)
    if verbose:
        print("DEBUG Question Agent:", res.text)
    state["questions_raw"] = res.text
    return state

def question_refinement_agent(state: State, verbose: bool = VERBOSE) -> State:
    """
    Agent to refine interview questions based on user feedback.
    """
    user_message = state.get("user_message", "")
    history = state.get("conversation_history", [])

    original_questions = state.get("questions_raw", "")
    original_questions = f"""
        **Original Questions:**
        {original_questions}
    """ if original_questions else ""  
    
    prompt = f"""
**System prompt:**
You are an interview coach who is helping a user refine a set of interview questions.
Your task is to regenerate the interview questions based on new information provided by the user.
You must only respond with the regenerated questions in the same format as the original, or a warning if the user's request is off-topic.

**Guardrails:**
- Your ONLY function is to refine interview questions, add or remove questions based on user's request.
- DO NOT answer questions or engage in conversation about anything else.
- If the user asks for something other than refining the questions, respond with ONLY the following message: "I can only help with refining the interview questions. Please provide more information about the candidate or the role to help me improve the questions."

**Original Comparison Result:**
{state['comparison_result_gemini']}

{original_questions}

**Conversation History:**
{history}

**User's Request:**
{user_message}

**Instructions:**
1. Based on the user's request, regenerate the interview questions with expected answers.
2. The number of questions if not given in the user's request, it should be default to the same amount as the number of questions in the last response (if the last response is empty, it should be default to {QUESTIONS} questions)
3. If user asked for more questions, you must repeat the original questions and add more questions based on the quantities asked by the user.
4. If User asked you to modify a specific question, you must modify the specific question based on the user's request, other questions must be repeated exactly the same as original.
5. If user asked for less questions without specify which questions to remove, you must remove from the last questions.
6. If user asked for less questions and specify which questions to remove, you must remove the specified questions.
7. Use the following format:

**Question 1: Topic Title**

**Question:** "..."

**Expected Answer:** ...

**Question 2: Another Topic**

**Question:** "..."

**Expected Answer:** ...

**Question 3: Another Topic**

**Question:** "..."

**Expected Answer:** ...
"""
    res = model.generate_content(prompt)
    if verbose:
        print("DEBUG Refinement Agent:", res.text)
    
    warning_message = "I can only help with refining the interview questions."
    if warning_message in res.text:
        state["refined_questions"] = res.text
    else:
        state["refined_questions"] = res.text
        # Update history
        if isinstance(history, list):
            history.append({"role": "user", "content": user_message})
            history.append({"role": "assistant", "content": res.text})
            state["conversation_history"] = history

    return state

def build_resume_scan_graph():
    print("GEMINI_MODEL_NAME", GEMINI_MODEL_NAME)
    print("GEMINI_API_KEY", st.secrets["GEMINI_API_KEY"])
    builder = StateGraph(State)
    builder.add_node("ParseResume", resume_parser_agent)
    builder.add_node("ParseJD", jd_parser_agent)
    builder.add_node("CompareGemini", lambda state, verbose=VERBOSE: comparison_agent(state, model_type="gemini", verbose=verbose))
    builder.add_node("CompareOpenAI", lambda state, verbose=VERBOSE: comparison_agent(state, model_type="openai", verbose=verbose))
    builder.add_node("AverageCompare", average_comparison_results)
    builder.add_node("GenerateQuestions", question_generation_agent)

    builder.set_entry_point("ParseResume")
    builder.add_edge("ParseResume", "ParseJD")
    builder.add_edge("ParseJD", "CompareGemini")
    builder.add_edge("CompareGemini", "CompareOpenAI")
    builder.add_edge("CompareOpenAI", "AverageCompare")
    builder.add_conditional_edges("AverageCompare", lambda state:
        "GenerateQuestions" if is_acceptable_score(state["comparison_score"])
        else END,
        {
            "GenerateQuestions": "GenerateQuestions",
            END: END
        })
    builder.add_edge("GenerateQuestions", END)

    return builder.compile(checkpointer=MemorySaver())
