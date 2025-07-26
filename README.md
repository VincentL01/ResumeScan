# ResumeScan: AI-Powered Resume & JD Analyzer

ResumeScan is a Streamlit web application that leverages AI to analyze a candidate's resume against a job description (JD). It provides a match score, a summary of alignment, and a list of missing skills. If the match is strong, it automatically generates a set of tailored interview questions.

A key feature of this tool is the **interactive question refiner**. After the initial questions are generated, you can chat with an AI agent to modify them, providing additional context or requesting specific changes to better suit the interview's focus.

---

## 🚀 Core Features

-   **📄 Resume Upload**: Supports resumes in PDF format.
-   **📂 JD Selection**: Select a Job Description from a list of markdown files.
-   **🤖 AI-Powered Analysis**:
    -   **Match Score**: A percentage indicating how well the resume matches the JD.
    -   **Profile Summary**: A brief overview of the candidate's alignment with the role.
    -   **Missing Skills**: A list of key skills required by the JD but not found in the resume.
-   **❓ Automatic Question Generation**: If the match score is 75% or higher, the tool generates a set of interview questions.
-   **💬 Interactive Question Refinement**: A chat interface allows you to provide feedback to an AI agent to refine and regenerate the interview questions in real-time.

---

## 🛠️ Tech Stack

-   **Backend**: Python
-   **Frontend**: Streamlit
-   **AI Orchestration**: LangGraph
-   **Language Model**: Google Gemini API
-   **PDF Parsing**: `pdfplumber`

---

## ⚙️ How to Run

### 1. Prerequisites

-   Python 3.8+
-   `uv` (or `pip`) for package management.

### 2. Installation

Clone the repository and install the required packages:

```bash
git clone <repository-url>
cd ResumeScan
uv venv
uv pip install -r requirements.txt
```

### 3. API Key Configuration

Create a `.env` file in the root of the project and add your Google Gemini API key:

```
GEMINI_API_KEY="YOUR_API_KEY_HERE"
GEMINI_MODEL_NAME="gemini-1.5-flash"
```

### 4. Run the Application

```bash
streamlit run main.py
```

The application will open in your web browser.

---

## 🕹️ How to Use

1.  **Upload a Resume**: Use the file uploader to select a PDF resume.
2.  **Select a JD**: Choose a job description from the dropdown menu.
3.  **Analyze**: Click the "Analyze Resume" button. The analysis results will be displayed.
4.  **Refine Questions**: If questions are generated, a chat box will appear. Type your instructions to the AI to modify the questions and press Enter. The questions will be updated based on your feedback.

---

## 📂 Project Structure

```
ResumeScan/
├── main.py                 # The main Streamlit application file
├── app/
│   ├── graph.py            # Defines the LangGraph agents and workflow
│   ├── processor.py        # Core logic for analysis and question refinement
│   ├── parser.py           # Utility functions for parsing AI model outputs
│   └── utils.py            # Helper functions (e.g., text extraction)
├── documents/
│   └── JD/                 # Contains the job descriptions in .md format
├── prompts/                # Example prompts (not directly used in the app)
├��─ .env                    # For API key storage (you need to create this)
└── requirements.txt        # Python package dependencies
```