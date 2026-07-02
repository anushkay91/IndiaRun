# TalentPool | AI Recruiter Hub 💼

TalentPool is a state-of-the-art AI-powered recruiter hub designed for streamlined semantic parsing, intelligent job description matching, and candidate screening report generation. Built with a fast, modern FastAPI backend and a beautiful Streamlit frontend.

---

## 🚀 Features

- **Profile Details**: View candidate profiles with semantic parsing.
- **AI Competency Analysis**: Extract skills and competencies automatically using Gemini.
- **Stage-2 Re-Ranking**: Perform semantic and hybrid search to match resumes with job descriptions.
- **Skill Gap Analysis**: Identify missing requirements and skill gaps.
- **Interview Planner**: Automatically generate targeted interview questions based on the candidate's profile and the job role.
- **Screening Report**: Beautifully formatted reports showing fit scores, pros, cons, and summaries.

---

## 🛠️ Project Structure

```
├── backend/            # FastAPI App (API Endpoints, Services, Database)
├── frontend/           # Streamlit App (UI & Interactive Visualizations)
├── prompts/            # System & LLM Prompts
├── storage/            # Local SQLite database storage
├── utils/              # Document parsers & utility functions
├── .env.example        # Environment variables template
└── .gitignore          # Files ignored by git (e.g. SQLite DB, keys)
```

---

## ⚙️ Setup & Installation

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd IndiaRun
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory and copy the contents from `.env.example`:
```bash
cp .env.example .env
```
Open the `.env` file and insert your **Gemini API Key**:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 3. Run the Backend (FastAPI)
Navigate to the root directory, create a virtual environment, install backend requirements, and start the FastAPI server:
```bash
# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Start the backend server
uvicorn backend.main:app --reload --port 8000
```
The API documentation will be available at: http://localhost:8000/docs

### 4. Run the Frontend (Streamlit)
Open a new terminal window, activate the virtual environment, and run the Streamlit application:
```bash
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install frontend dependencies
pip install -r frontend/requirements.txt

# Start Streamlit app
streamlit run frontend/app.py
```
The web interface will open in your browser at: http://localhost:8501

---

## 🐳 Deployment Notes

- **Database**: The app uses a local SQLite database (`storage/recruiter.db`). This file is ignored by Git to prevent state loss.
- **API Connection**: The frontend streamlit app connects to the backend API via the `BACKEND_URL` environment variable. In production, set `BACKEND_URL` to your hosted backend API URL.
