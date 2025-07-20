# 📄 ResumeScan – Resume & JD Analyzer

ResumeScan is a Streamlit-based web application that helps job applicants analyze how well their resumes align with a selected job description (JD). It leverages Gemini API and LangGraph to provide a structured comparison, a match score, missing skill highlights, and even auto-generated interview questions.

---

## 🚀 Features

- ✅ Upload a resume (PDF format)
- ✅ Select a JD from markdown files
- ✅ Get:
  - 📊 Match Score (/100)
  - 🧩 Missing Keywords / Skills
  - 📋 Profile Summary
  - ❓ Auto-generated interview questions with expected answers
- ✅ Built with LangGraph + Gemini (LLM orchestration)
- ✅ Modular architecture for easy extension

---

## 🧠 How It Works

Under the hood, ResumeScan uses the following **LangGraph agents**:

1. **ResumeParserAgent** – Extracts profile summary, key skills, and work experiences.
2. **JDParserAgent** – Extracts role summary, responsibilities, and requirements from JD.
3. **ComparisonAgent** – Compares resume and JD to compute a match score and extract missing skills.
4. **QuestionGenAgent** – Generates custom interview questions based on gaps and strengths.

---

## 📂 Project Structure

ResumeScan/
├── main.py # Streamlit frontend
├── .env # Your Gemini API key
├── app/
│ ├── processor.py # Core business logic
│ ├── graph.py # LangGraph setup
│ ├── parser.py # Extract score, summary, missing skills, questions
│ └── utils.py # PDF/MD extraction, string parsers
├── documents/
│ └── JD/ # Sample job descriptions in markdown format
└── .streamlit/
  └── config.toml # Streamlit config to disable reload bug

---

## 📦 Dependencies

```bash
uv venv
uv pip install -r requirements.txt
```

## 🧪 Demo

1. Run locally:

```bash
uv run streamlit run main.py
```

2. Upload a PDF resume

3. Select a JD (.md file) from documents/JD

4. Click Analyze Resume

5. View results

## 🔐 .env Configuration
Create a .env file in the project root:

```ini
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL_NAME=gemini-1.5-flash
```

---

## 🛠 Tech Stack
* Streamlit – Frontend framework
* Google Gemini – LLM API
* LangGraph – LLM orchestration
* PyPDF2 – PDF text extraction
* Markdown (.md) – For JD files

---

## 📌 Roadmap
* Add support for DOCX resumes
* Add live editing for JD text
* Add support for multiple JDs (different formats as well, currently only .md)
* Improve prompt robustness via JSON schema output from Gemini  
* Add resume categorization (domain classification)
* Add support for multiple resumes (different formats as well, currently only .pdf)
* Add support for multiple LLMs (currently only Gemini)

--- 

## 🧑‍💻 Maintainer
Developed by Thang Luong Cao (Vincent)
For support or collaboration, reach out via GitHub or LinkedIn.

---

## 📝 License
MIT License – Feel free to use, modify, and contribute.

---

