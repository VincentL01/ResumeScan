# ResumeScan: AI-Powered Resume & JD Analyzer

ResumeScan is a Streamlit web application that leverages AI to analyze a candidate's resume against a job description (JD). It provides a match score, a summary of alignment, and a list of missing skills. If the match is strong, it automatically generates a set of tailored interview questions.

A key feature of this tool is the **interactive question refiner**. After the initial questions are generated, you can chat with an AI agent to modify them, providing additional context or requesting specific changes to better suit the interview's focus.

## 🚀 Core Features

-   **📄 Resume Upload**: Supports resumes in PDF format.
-   **📂 JD Selection**: Select a Job Description from a list of markdown files.
-   **🤖 AI-Powered Analysis**:
    -   **Match Score**: A percentage indicating how well the resume matches the JD.
    -   **Profile Summary**: A brief overview of the candidate's alignment with the role.
    -   **Missing Skills**: A list of key skills required by the JD but not found in the resume.
-   **❓ Automatic Question Generation**: If the match score is 75% or higher, the tool generates a set of interview questions.
-   **💬 Interactive Question Refinement**: A chat interface allows you to provide feedback to an AI agent to refine and regenerate the interview questions in real-time.
-   **💾 MongoDB Integration**: All uploaded CVs and analysis results are stored in MongoDB with GridFS for efficient file storage.
-   **🔍 CV Database Management**: Search, view, and reload previously analyzed CVs from the sidebar.
-   **🔄 Duplicate Detection**: Automatic detection and handling of duplicate CV uploads.

---

## 🛠️ Tech Stack

-   **Backend**: Python
-   **Frontend**: Streamlit
-   **AI Orchestration**: LangGraph
-   **Language Model**: Google Gemini API (with OpenAI fallback)
-   **PDF Parsing**: `pdfplumber`
-   **Database**: MongoDB with GridFS

---

## ⚙️ How to Run

### 1. Prerequisites

-   Python 3.8+
-   `uv` (or `pip`) for package management.
-   MongoDB Atlas account (or local MongoDB instance)

### 2. Installation

Clone the repository and install the required packages:

```bash
git clone <repository-url>
cd ResumeScan
uv venv
uv pip install -r requirements.txt
```

### 3. MongoDB Setup

ResumeScan requires MongoDB for storing uploaded CVs and analysis results. You can use either MongoDB Atlas (cloud) or a local MongoDB instance.

#### Option A: MongoDB Atlas (Recommended)

1.  **Create a MongoDB Atlas Account**:
    -   Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
    -   Sign up for a free account
    -   Create a new cluster (M0 free tier is sufficient)

2.  **Configure Network Access**:
    -   In the Atlas dashboard, go to "Network Access"
    -   Add your current IP address to the whitelist (or 0.0.0.0/0 for development only)

3.  **Create Database User**:
    -   Go to "Database Access" in the Atlas dashboard
    -   Create a new database user with read/write permissions

4.  **Get Connection String**:
    -   Click "Connect" on your cluster
    -   Choose "Connect your application"
    -   Copy the connection string

#### Option B: Local MongoDB

1.  **Install MongoDB**:
    -   Follow the [official MongoDB installation guide](https://docs.mongodb.com/manual/installation/)
    -   Start the MongoDB service

2.  **Verify Installation**:
    ```bash
    mongod --version
    ```

### 4. API Key Configuration

Create a secrets file at `.streamlit/secrets.toml` and add your API keys:

#### For Google Gemini (Primary):
```toml
# .streamlit/secrets.toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
GEMINI_MODEL_NAME = "gemini-1.5-flash"

# MongoDB Configuration
MONGODB_URI = "mongodb+srv://username:password@cluster.mongodb.net/resumeScan?retryWrites=true&w=majority"
MONGODB_DATABASE = "resumeScan"
MONGODB_COLLECTION = "cv_files"
```

#### For OpenAI (Fallback):
```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY_HERE"
OPENAI_MODEL_NAME = "gpt-4o-mini"

# MongoDB Configuration
MONGODB_URI = "mongodb+srv://username:password@cluster.mongodb.net/resumeScan?retryWrites=true&w=majority"
MONGODB_DATABASE = "resumeScan"
MONGODB_COLLECTION = "cv_files"
```

#### For Both (Best - Automatic Fallback):
```toml
# .streamlit/secrets.toml
# Google Gemini (Primary)
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
GEMINI_MODEL_NAME = "gemini-1.5-flash"

# OpenAI (Fallback)
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY_HERE"
OPENAI_MODEL_NAME = "gpt-4o-mini"

# MongoDB Configuration
MONGODB_URI = "mongodb+srv://username:password@cluster.mongodb.net/resumeScan?retryWrites=true&w=majority"
MONGODB_DATABASE = "resumeScan"
MONGODB_COLLECTION = "cv_files"
```

### 5. MongoDB Setup Verification

Run the setup script to verify your MongoDB connection and create necessary indexes:

```bash
python scripts/setup_mongodb.py
```

This script will:
- Test your MongoDB connection
- Create required indexes for efficient querying
- Verify GridFS configuration

### 6. Run the Application

```bash
streamlit run main.py
```

The application will open in your web browser.

---

## 🕹️ How to Use

1.  **Upload a Resume**: Use the file uploader to select a PDF resume.
2.  **Select a JD**: Choose a job description from the dropdown menu.
3.  **Analyze**: Click the "Analyze Resume" button. The analysis results will be displayed.
    - CV is automatically stored in MongoDB
    - Analysis results are saved to the database
    - Duplicate files are detected and handled
4.  **Refine Questions**: If questions are generated, a chat box will appear. Type your instructions to the AI to modify the questions and press Enter. The questions will be updated based on your feedback.
5.  **Manage CV Database**: Use the sidebar to:
    - View database statistics (Total CVs, Analyzed CVs, Avg Match Score)
    - Search for previously uploaded CVs by filename or match score
    - Load and view previous analysis results

---

## 📂 Project Structure

```
ResumeScan/
├── main.py                 # The main Streamlit application file
├── app/
│   ├── graph.py            # Defines the LangGraph agents and workflow
│   ├── processor.py        # Core logic for analysis and question refinement
│   ├── parser.py           # Utility functions for parsing AI model outputs
│   ├── utils.py            # Helper functions (e.g., text extraction)
│   └── ai_provider.py      # AI provider manager (Gemini/OpenAI)
├── db/
│   ├── connection.py       # MongoDB connection manager
│   ├── cv_storage.py       # CV file storage service (GridFS)
│   └── models.py           # Data models for CV metadata
├── scripts/
│   ├── setup_mongodb.py    # MongoDB setup and verification script
│   └── test_mongodb.py     # Comprehensive MongoDB test suite
├── documents/
│   └── JD/                 # Contains the job descriptions in .md format
├── prompts/                # Example prompts (not directly used in the app)
├── .streamlit/secrets.toml # For API key storage (you need to create this)
├── .streamlit/config.toml  # For Streamlit configuration (you need to create this)
└── requirements.txt        # Python package dependencies
```

.streamlit/config.toml content
```toml
[server]
runOnSave = false
```

---

## 🧪 Testing

### MongoDB Integration Tests

Run the comprehensive MongoDB test suite to verify all database operations:

```bash
python scripts/test_mongodb.py
```

This test suite validates:
- Connection to MongoDB
- File storage and retrieval with GridFS
- Analysis result updates
- Search functionality
- Database statistics
- Cleanup operations

### Manual Testing Checklist

After running the application, verify these features work:

1. ✅ Upload a new CV and confirm it's stored in MongoDB
2. ✅ View database statistics in the sidebar
3. ✅ Search for uploaded CVs by filename
4. ✅ Load previous analysis results from the database
5. ✅ Handle duplicate file uploads correctly
6. ✅ Verify analysis results are saved after processing

---

## 🛠️ Troubleshooting

### Common Issues

1.  **MongoDB Connection Errors**:
    - Verify your `MONGODB_URI` in secrets.toml
    - Check network access for MongoDB Atlas
    - Ensure MongoDB service is running for local instances

2.  **AI Provider Errors**:
    - Confirm API keys are correctly set in secrets.toml
    - Check that you have access to the specified model
    - Verify internet connectivity

3.  **GridFS Storage Issues**:
    - Ensure sufficient disk space
    - Check MongoDB database permissions

### MongoDB Debugging

Use the test scripts to diagnose issues:

```bash
# Test basic MongoDB connection
python scripts/test_mongo.py

# Run comprehensive MongoDB tests
python scripts/test_mongodb.py
```

### Logs

Enable detailed logging by setting the environment variable:

```bash
export LOG_LEVEL=DEBUG
streamlit run main.py
```

---

## 📚 Additional Resources

-   [MongoDB Documentation](https://docs.mongodb.com/)
-   [GridFS Documentation](https://docs.mongodb.com/manual/core/gridfs/)
-   [Google Gemini API Documentation](https://ai.google.dev/)
-   [OpenAI API Documentation](https://platform.openai.com/docs/)
-   [Streamlit Documentation](https://docs.streamlit.io/)