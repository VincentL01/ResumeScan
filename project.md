# Project Requirements – ResumeScan

This project automates the evaluation of a candidate's resume against a job description (JD), and generates a tailored interview questionnaire based on both gaps and strengths.

---

## Input

### Supported Formats:
- `.txt` or `.md`

### Required Files:
- **Job Description (JD)**
- **Resume**

---

## Core
LangGraph + Gemini API

## Output

### Console Output:
- JD Match Score (/100)

### File Output (`outputs/`):
- `applicant_xx_questionnaire.md`:  
  - 10–14 interview questions  
  - Each question includes **Expected Answer**

---

## Demo Scope

- Evaluate **2 resumes**:
  - `resume_01_banca.md` (Bancassurance domain)
  - `resume_02_industrial.md` (Industrial / Oil & Gas domain)

---

## Extensions (Planned)

- Capture **Interviewee Answers**
- Auto-**Categorize Resume Domain** using LLM or rule-based classifier

---

## Checklist

- [x] JD sample (in `data/`)
- [x] 2 example matched resumes
- [x] 3 example non-matched resumes
- [ ] Ontology design for requirement normalization

---

## Challenges

- **Ontology Mapping**: Handle indirect matches via domain-specific relationships  
  _(e.g., JD requires “Cloud Platform Experience”, resume shows “Azure Synapse”)_
- **Taxonomy Normalization**: Map technologies, soft skills, and domain keywords to canonical terms

---

## Repository Structure

generate_questionnaire/
├── app/
│   ├── main.py
│   └── processor.py
│
├── models/
│   ├── matcher.py
│   ├── question_generator.py
│   └── domain_classifier.py
│
├── prompts/
│   ├── system_prompt.txt           # Base system prompt for LLM
│   ├── match_template.md           # Used for evaluating JD vs Resume
│   ├── question_template.txt       # Used to generate Q&A
│   └── prompt_examples.md          # ✅ Reference examples for few-shot prompting
│
├── ontology/
│   └── ontology.json               # ✅ Ontology map for skills, tools, roles, etc.
│
├── data/
│   ├── jd_banca.md
│   ├── resume_01_banca.md
│   ├── resume_02_industrial.md
│   └── resume_*.md
│
├── outputs/
│   ├── applicant_01_questionnaire.md
│   └── match_results.log
│
├── config/
│   └── settings.py
│
├── .env
├── requirements.txt
└── README.md


--

## Processing Flow

1. **JD & Resume Load**
2. **Ontology Normalization**:
   - Map technology concepts to canonical labels
   - Allow semantic matches (e.g., Cloud ↔ Azure/GCP/AWS)

3. **System Prompt Execution (LLM)**:
   - Score Resume vs JD (/100)
   - Identify matched and unmatched items

4. **Threshold Check**:
   - If score < 80 → Resume Rejected
   - Else → Proceed

5. **Gap Identifier**:
   - List unmet requirements
   - Categorize into: Technical, Tools, Soft Skills, Domain, Experience

6. **Generate Questions on Gaps**:
   - 3–4 questions directly addressing missing requirements

7. **Scan Matched Requirements**:
   - Tag each as:
     - Just Qualified
     - Over-Qualified

8. **Generate Strength-Based Questions**:
   - 6–10 questions, tailored by strength level

9. **Write to Output File**:
   - Markdown-formatted questionnaire saved as `applicant_xx_questionnaire.md`

---

## Samples:

`ontology/ontology.json`
```json
{
  "Cloud Platforms": ["AWS", "Azure", "GCP", "Amazon Web Services", "Microsoft Azure", "Google Cloud Platform"],
  "Workflow Orchestration": ["Airflow", "Dagster", "Prefect"],
  "Data Lake Formats": ["Delta Lake", "Apache Hudi", "Apache Iceberg"],
  "Languages": ["Python", "Scala", "SQL"],
  "Metadata Tools": ["Apache Atlas", "OpenMetadata", "DataHub"],
  "Streaming Tools": ["Kafka", "Kinesis", "Pub/Sub"],
  "Customer Communication": ["Client meeting", "Stakeholder interaction", "Requirement gathering", "Presentation skills"]
}
```

 