# 🔍 Prompt Examples – LangChain + Gemini / OpenAI

## 1. JD to Resume Matching

> ### System Prompt:
You are an expert resume evaluator. Match the resume to the job description by checking each requirement. Normalize concepts using an ontology if needed. Score each match and produce a total match score (/100).

> ### Example Input:
**JD Requirement**: Experience with cloud platforms  
**Resume**: "Built pipelines using Azure Data Factory and Synapse"

> ### Expected Output:
✅ Matched (via ontology: Azure → Cloud Platform)

---

## 2. Gap Identification

> ### JD Requirement:
Familiarity with orchestration tools like Airflow

> ### Resume:
No mention of Airflow, Dagster, or Prefect.

> ### Result:
❌ Not matched  
→ Category: Tools

---

## 3. Question Generation for Gaps

> ### Gap:
Customer communication skill missing

> ### Generated Question:
"Describe a time when you had to present technical results to a non-technical stakeholder. How did you ensure clarity?"

---

## 4. Question Generation for Strengths

> ### Matched:
Strong PySpark experience

> ### Level:
Over-Qualified

> ### Generated Question:
"What optimizations do you apply to PySpark jobs for datasets over 100 million records?"

---

## Usage in Chain:
These examples are inserted into prompts via string templates or LangChain's few-shot chain constructor.

```