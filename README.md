# SkillSync AI - AI Skill Gap Analyzer & Career Roadmap Generator

> **Tagline:** "Know Your Gaps. Build Your Future."
>
> A complete, production-ready AI-powered web application that helps students analyze their resumes against industry-standard requirements, identifies missing skills, certifications, and projects, and generates a personalized 3-month timeline learning roadmap.

---

## 🚀 Key Features

1. **Resume Text Extraction:** Seamless support for PDF and DOCX uploads using robust parsers (`pdfplumber`, `PyPDF2`, `docx2txt`).
2. **AI Resume Analysis:** Leverages Groq API to extract Technical Skills, Soft Skills, Projects, Certifications, Internships, Education, Tools, and Programming Languages into structured JSON formats.
3. **Target Career Selection:** Choose from 10 industry standard career paths (e.g., AI Engineer, Full Stack Developer, VLSI Engineer, Cloud Engineer).
4. **Skill Gap Engine:** Compares resume profiles with career requirements, determining matched, missing, and recommended skills.
5. **Job Readiness Score:** Computes a placement readiness percentage and classifies students from *Beginner* to *Industry Ready*.
6. **AI Career Roadmap:** Generates a weekly, personalized 12-week learning roadmap detailing focus topics, real-world resources, mini-goals, and coding exercises.
7. **Portfolio Recommendations:** Suggests tailored Beginner, Intermediate, and Advanced projects to bridge skill gaps.
8. **Certification Matches:** Recommends relevant certifications from NPTEL, Coursera, Google, Microsoft, and AWS.
9. **AI Interview Prep:** Provides targeted Technical, Coding, HR, and Scenario-based questions with comprehensive sample answers.
10. **Placement Readiness Dashboard:** Includes dynamic visualizations (Placement Gauge, Skills Radar Chart, and Alternative Career Compatibility Matrix) using Plotly.
11. **PDF Report Exporter:** Compiles all session analytics into a professionally styled PDF report using ReportLab for offline review.

---

## 📂 Project Structure

```text
SkillSyncAI/
├── app.py                      # Multi-page App entry point (Home page)
├── requirements.txt            # Project dependencies
├── .env.example                # Example environment variables template
├── .env                        # Local environment variables (created from template)
├── README.md                   # Setup and usage guide
├── pages/                      # Streamlit native sub-pages
│   ├── resume_analysis.py      # Resume extraction details card UI
│   ├── skill_gap.py            # Skill gap comparisons, charts, progress bars
│   ├── roadmap.py              # 3-Month interactive timeline learning roadmap
│   ├── projects.py             # Level-based recommended projects & certs
│   ├── interview.py            # Interview preparation tabs (Tech, Coding, HR, Scenario)
│   ├── dashboard.py            # Readiness score, Radar/Bar/Pie charts
│   └── export_report.py        # PDF Report builder and downloader
├── backend/                    # Python backend logic & services
│   ├── parser.py               # PDF and DOCX text extractor
│   ├── gap_engine.py           # Skill comparison logic and readiness score calculations
│   ├── groq_service.py         # Groq LLM API integration client & mock fallback
│   ├── role_database.py        # Python dictionary containing target career profiles
│   └── ui_components.py        # Unified page loader, CSS injector, and shared sidebar
└── assets/                     # Styles and static styling assets
    └── style.css               # Global custom CSS for premium styling (glassmorphic cards, timelines)
```

---

## 🛠️ Setup & Installation

### Prerequisite
Ensure Python 3.10 or higher is installed on your system.

### 1. Install Dependencies
Navigate to the project root directory and run:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
For local development, copy `.env.example` to a new file named `.env`:
```bash
copy .env.example .env
```
Add your Groq API key either in Streamlit Secrets or in `.env`:
```toml
# .streamlit/secrets.toml
GROQ_API_KEY = "your_actual_groq_api_key_here"
```
or
```env
GROQ_API_KEY=your_actual_groq_api_key_here
```
*Note: If the key is missing, still set to the placeholder, or invalid, the application will automatically enter **Mock Fallback Mode** so you can test all features with realistic student data.*

---

## 🖥️ Running the Application

### Launch Streamlit Frontend (Recommended)
Launch the frontend dashboard by running:
```bash
streamlit run app.py
```
This launches a browser tab at `http://localhost:8501`.



---

## 🎯 Smart India Hackathon Demonstration Flow
1. **Explore Careers:** Navigate to the **Home** page. Use the target career dropdown at the bottom to explore the core skills required for various industry paths.
2. **Submit Resume:** Upload a sample resume (PDF/DOCX) in the sidebar. Select a target role (e.g., *AI Engineer* or *Cybersecurity Analyst*).
3. **Analyze:** Click **"Run Gap Analysis"**.
4. **Inspect Extracted Info:** Go to **Resume Analysis** to verify how accurately the AI extracted contact info, education, skills, and projects.
5. **Analyze Gaps:** Check **Skill Gap Analysis** to see progress bars and pie charts indicating missing vs. matched skills.
6. **Dashboard Review:** Open **Placement Dashboard** to see the readiness gauge, categories radar chart, and alternative career compatibility bars.
7. **Get Study Guide:** Go to **Career Roadmap** and **Project Recommendations** to view the timeline roadmap, suggested course matches, and coding projects.
8. **Test Interview Prep:** Open **Interview Preparation** and try answering the generated questions.
9. **Export PDF:** Go to **Export Report** and click download to get a formatted PDF summary of your entire profile.
