import os
import re
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
from backend.role_database import CAREER_DATABASE

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from groq import Groq
except ImportError:
    Groq = None

def _load_env_value(name: str) -> str | None:
    """Load and normalize a value from the project .env file."""
    env_path = Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(dotenv_path=env_path, override=False)
    value = os.getenv(name)
    if value is None:
        return None
    return value.strip().strip('"').strip("'")


def _is_placeholder_api_key(value: str | None) -> bool:
    """Return True when the env value is still one of the sample placeholders."""
    if not value:
        return True
    return value.lower() in {
        "your_groq_api_key",
        "your_groq_api_key_here",
        "replace_with_your_groq_api_key",
    }


api_key = _load_env_value("GROQ_API_KEY")

# Check if API Key is set and valid
IS_API_KEY_CONFIGURED = False
API_KEY_STATUS = "missing"
_client = None
_initialization_error = None  # Store initialization error for UI display

if api_key and not _is_placeholder_api_key(api_key):
    try:
        if Groq is None:
            raise ImportError("groq is not installed. Install it with: pip install groq")
        _client = Groq(api_key=api_key)
        IS_API_KEY_CONFIGURED = True
        API_KEY_STATUS = "configured"
        logger.info("✅ Groq API configured successfully")
    except Exception as e:
        error_msg = f"[API Initialization] {type(e).__name__}: {str(e)}"
        _initialization_error = error_msg
        API_KEY_STATUS = "invalid"
        logger.error(error_msg)
        print(error_msg)
        # Immediately update Streamlit session state if available
        try:
            import streamlit as st
            st.session_state["api_key_exhausted"] = True
            st.session_state["api_error_detail"] = error_msg
        except Exception:
            pass
else:
    if api_key:
        error_msg = (
            "[API Initialization] GROQ_API_KEY is still set to the sample placeholder in .env. "
            "Replace it with your real Groq API key."
        )
        API_KEY_STATUS = "placeholder"
    else:
        error_msg = "[API Initialization] Groq API Key not configured in .env (use GROQ_API_KEY)"
    _initialization_error = error_msg
    logger.warning(error_msg)
    print(error_msg)

MODEL_ID = "llama-3.3-70b-versatile"

def _categorize_error(error: Exception) -> tuple[str, str]:
    """
    Categorizes API errors and provides user-friendly messages.
    Returns: (error_category, user_friendly_message)
    """
    err_str = str(error).lower()
    error_type = type(error).__name__
    
    # Check for quota/rate limiting errors
    if "quota" in err_str or "rate" in err_str or "too many" in err_str or "429" in err_str or "resource_exhausted" in err_str:
        return "QUOTA_EXHAUSTED", (
            "API quota exceeded or rate limited. Your Groq account has hit the rate limit. "
            "Please wait before making more requests or upgrade your plan."
        )
    
    # Check for authentication errors
    if "unauthenticated" in err_str or "401" in err_str or "unauthorized" in err_str or "invalid api key" in err_str:
        return "AUTH_ERROR", (
            "API authentication failed. Please verify your Groq API key (GROQ_API_KEY) in .env is valid."
        )
    
    # Check for permission errors
    if "permission" in err_str or "forbidden" in err_str or "403" in err_str:
        return "PERMISSION_ERROR", (
            "Permission denied. Your Groq API key may not have the required permissions."
        )
    
    # Check for network errors
    if "connection" in err_str or "timeout" in err_str or "network" in err_str or "refused" in err_str:
        return "NETWORK_ERROR", "Network error connecting to Groq API. Please check your internet connection."
    
    # Check for model not found
    if "not found" in err_str or "model" in err_str or "404" in err_str:
        return "MODEL_ERROR", f"Model '{MODEL_ID}' not found or not available in your region."
    
    # Default to unknown error
    return "UNKNOWN_ERROR", f"{error_type}: {str(error)}"

def _handle_api_error(operation_name: str, error: Exception) -> str:
    """
    Centralized error handling for API failures.
    Categorizes errors, logs details, and updates session state with error info.
    """
    error_category, user_message = _categorize_error(error)
    full_error = f"[{operation_name}] {type(error).__name__}: {str(error)}"
    
    logger.error(f"❌ Groq API failed ({error_category}) - {full_error}")
    logger.info(f"📋 User message: {user_message}")
    
    # Create detailed error message for display
    error_detail = f"[{error_category}] {user_message}\n\nTechnical details: {full_error}"
    
    # Update session state for UI display
    try:
        import streamlit as st
        st.session_state["api_key_exhausted"] = True
        st.session_state["api_error_detail"] = error_detail
        st.session_state["api_error_category"] = error_category
    except Exception:
        pass
    
    return error_detail

def _extract_json_text(content: str) -> str:
    """
    Pull a JSON object/array out of common LLM response wrappers.
    Handles markdown fences and stray explanatory text.
    """
    if not content:
        raise ValueError("Groq returned an empty response")

    text = content.strip().lstrip("\ufeff")

    # Remove fenced code blocks like ```json ... ```
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        json.loads(text)
        return text
    except Exception:
        pass

    # Fall back to the first top-level JSON-looking span.
    start = min((idx for idx in [text.find("{"), text.find("[")] if idx != -1), default=-1)
    end = max(text.rfind("}"), text.rfind("]"))
    if start != -1 and end != -1 and end > start:
        candidate = text[start:end + 1].strip()
        json.loads(candidate)
        return candidate

    raise json.JSONDecodeError("Could not locate JSON payload", text, 0)

def _generate_json(prompt: str) -> dict:
    """Helper: calls Groq and parses JSON response."""
    if _client is None:
        raise RuntimeError("Groq client is not available")
    try:
        response = _client.chat.completions.create(
            model=MODEL_ID,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2048
        )
        raw_content = response.choices[0].message.content
        json_text = _extract_json_text(raw_content)
        return json.loads(json_text)
    except Exception as e:
        _handle_api_error("generate_json", e)
        raise e

def _generate_text(prompt: str) -> str:
    """Helper: calls Groq and returns plain text response."""
    if _client is None:
        raise RuntimeError("Groq client is not available")
    try:
        response = _client.chat.completions.create(
            model=MODEL_ID,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2048
        )
        text = response.choices[0].message.content
        if not text:
            raise RuntimeError("Groq returned an empty response")
        return text.strip()
    except Exception as e:
        _handle_api_error("generate_text", e)
        raise e

def analyze_resume(resume_text):
    """
    Sends resume text to Groq API to extract details in structured JSON format.
    """
    prompt = f"""
    Analyze the following resume text and extract the candidate's details into a structured JSON format.
    Identify:
    - Candidate Name (if not clear, use "Student Candidate")
    - Contact Email & Phone Number (if available)
    - Technical Skills (e.g. Machine Learning, React, SQL, etc.)
    - Soft Skills (e.g. Communication, Leadership, Teamwork, etc.)
    - Projects (with title, short description, and technologies used)
    - Certifications (list of certification names)
    - Internships / Work Experience (company, role, duration, description)
    - Education (degree, institution, graduation year)
    - Tools (e.g. Git, Docker, JIRA, VS Code)
    - Programming Languages (e.g. Python, Java, C++, JavaScript)

    Resume Text:
    ---
    {resume_text}
    ---

    Return ONLY a valid JSON object matching the following structure:
    {{
        "name": "Name",
        "email": "Email",
        "phone": "Phone",
        "technical_skills": ["Skill1", "Skill2"],
        "soft_skills": ["Skill1", "Skill2"],
        "programming_languages": ["Lang1", "Lang2"],
        "tools": ["Tool1", "Tool2"],
        "projects": [
            {{
                "title": "Project Title",
                "description": "Project Description",
                "technologies": ["Tech1", "Tech2"]
            }}
        ],
        "certifications": ["Cert1", "Cert2"],
        "internships": [
            {{
                "role": "Role Name",
                "company": "Company Name",
                "duration": "Duration (e.g. June 2024 - Aug 2024)",
                "description": "Description of work done"
            }}
        ],
        "education": [
            {{
                "degree": "Degree (e.g. B.Tech Computer Science)",
                "institution": "Institution Name",
                "year": "Graduation Year"
            }}
        ]
    }}
    """
    try:
        if not IS_API_KEY_CONFIGURED:
            raise RuntimeError("Groq API key is not configured.")
        return _generate_json(prompt)
    except Exception as e:
        error_detail = _handle_api_error("analyze_resume", e)
        logger.info(f"ℹ️ Falling back to local rule-based parsing for resume analysis")
        return get_mock_resume_analysis(resume_text)


def generate_roadmap(resume_details, missing_skills, target_role):
    """
    Generates a personalized 3-month week-by-week roadmap.
    """
    prompt = f"""
    Create a highly personalized 3-month (12 weeks) learning roadmap for a student transitioning to a '{target_role}' role.
    
    Student's Current Profile:
    - Existing Skills: {resume_details.get('technical_skills', [])}
    - Programming Languages: {resume_details.get('programming_languages', [])}
    - Missing Skills to Target: {missing_skills}
    
    The output must contain exactly 12 weeks of learning tasks. For EVERY single week, provide:
    - Week number (1 to 12)
    - Skills to learn that week (concise, max 3-4 words)
    - Strictly limit resources to EXACTLY 1 best-in-class resource (e.g. Coursera or YouTube link)
    - Concrete mini-goals (extremely concise, max 1 short sentence)
    - Practice exercises (max 1 short sentence)

    Return ONLY a valid JSON object matching the following structure:
    {{
        "roadmap": [
            {{
                "week": 1,
                "skills_to_learn": ["Skill A", "Skill B"],
                "resources": [
                    {{
                        "name": "Resource Course/Tutorial Title",
                        "url": "Platform name (e.g. Coursera - Python for Everybody, NPTEL - Intro to ML, Official Docs)"
                    }}
                ],
                "mini_goals": "Goal description",
                "practice_exercises": "Practical exercise description"
            }}
        ]
    }}
    """
    try:
        if not IS_API_KEY_CONFIGURED:
            raise RuntimeError("Groq API key is not configured.")
        return _generate_json(prompt)
    except Exception as e:
        error_detail = _handle_api_error("generate_roadmap", e)
        logger.info(f"ℹ️ Falling back to local roadmap generation")
        return get_mock_roadmap(target_role, missing_skills)

def generate_projects(missing_skills, target_role):
    """
    Generates Beginner, Intermediate, and Advanced project recommendations to bridge missing skills.
    """
    prompt = f"""
    Generate exactly 3 project recommendations (1 Beginner, 1 Intermediate, 1 Advanced) specifically designed to help a student learn these missing skills: {missing_skills} and prepare for a '{target_role}' career.
    
    IMPORTANT: Frame each project as a solution to a real-world social problem (similar to the themes in the Smart India Hackathon - SIH). Topics can include agriculture, rural healthcare, education, sustainability, or smart cities.

    For each project, provide:
    - Title
    - Difficulty level (strictly "Beginner", "Intermediate", or "Advanced")
    - Simple description (Explain the social problem being solved. Use very simple, beginner-friendly language. Avoid overly complex technical jargon.)
    - Technologies required (including the missing skills)
    - Estimated completion time (e.g., "1 week", "3 weeks", "5 weeks")

    Return ONLY a valid JSON object matching the following structure:
    {{
        "projects": [
            {{
                "title": "Project Title",
                "difficulty": "Beginner / Intermediate / Advanced",
                "description": "Project Description",
                "technologies_required": ["Tech1", "Tech2"],
                "estimated_time": "Time estimation"
            }}
        ]
    }}
    """
    try:
        if not IS_API_KEY_CONFIGURED:
            raise RuntimeError("Groq API key is not configured.")
        return _generate_json(prompt)
    except Exception as e:
        error_detail = _handle_api_error("generate_projects", e)
        logger.info(f"ℹ️ Falling back to local project generation")
        return get_mock_projects(target_role, missing_skills)

def generate_interview_questions(target_role, resume_details, missing_skills):
    """
    Generates interview questions categorized by Technical, Coding, HR, and Scenario.
    """
    prompt = f"""
    Generate interview preparation questions for a candidate seeking a '{target_role}' position.
    Tailor questions based on:
    - Candidate Resume Projects: {[p.get('title') for p in resume_details.get('projects', [])]}
    - Candidate Missing Skills: {missing_skills}
    
    Provide:
    - 3 Technical Questions (core concepts, concepts from missing skills)
    - 3 Coding / Practical Questions (specific challenges with code output/instructions)
    - 2 HR Questions (behavioral, culture fit)
    - 2 Scenario-Based Questions (problem-solving on the job)

    For each question, provide a detailed sample Answer/Solution.

    Return ONLY a valid JSON object matching the following structure:
    {{
        "technical": [
            {{"question": "Question text", "answer": "Detailed sample answer"}}
        ],
        "coding": [
            {{"question": "Coding question text", "answer": "Code logic or step-by-step solution"}}
        ],
        "hr": [
            {{"question": "HR question text", "answer": "Behavioral answer advice/sample"}}
        ],
        "scenario": [
            {{"question": "Scenario question text", "answer": "Solution to the scenario challenge"}}
        ]
    }}
    """
    try:
        if not IS_API_KEY_CONFIGURED:
            raise RuntimeError("Groq API key is not configured.")
        return _generate_json(prompt)
    except Exception as e:
        error_detail = _handle_api_error("generate_interview_questions", e)
        logger.info(f"ℹ️ Falling back to local interview questions generation")
        return get_mock_interview_questions(target_role, missing_skills)

def recommend_certifications(missing_skills, target_role):
    """
    Recommends certifications (NPTEL, Coursera, Google, Microsoft, AWS) to cover missing skills.
    """
    prompt = f"""
    Recommend 4 professional certifications (specifically from NPTEL, Coursera, Google Certifications, Microsoft Certifications, AWS Certifications) that directly address these missing skills: {missing_skills} for the role '{target_role}'.
    
    For each certification, provide:
    - Name
    - Platform (e.g. Coursera, NPTEL, AWS, Google, Microsoft)
    - Target Skill (which missing skill this certification teaches)
    - Difficulty (Beginner, Intermediate, Advanced)
    - Estimated Duration (e.g. 6 weeks, 3 months)

    Return ONLY a valid JSON object matching the following structure:
    {{
        "certifications": [
            {{
                "name": "Certification Name",
                "platform": "NPTEL / Coursera / Google / Microsoft / AWS",
                "target_skill": "Skill Name",
                "difficulty": "Beginner / Intermediate / Advanced",
                "duration": "Duration estimation"
            }}
        ]
    }}
    """
    try:
        if not IS_API_KEY_CONFIGURED:
            raise RuntimeError("Groq API key is not configured.")
        return _generate_json(prompt)
    except Exception as e:
        error_detail = _handle_api_error("recommend_certifications", e)
        logger.info(f"ℹ️ Falling back to local certification recommendations")
        return get_mock_certifications(target_role, missing_skills)


def generate_faq(missing_skills, target_role):
    """
    Generates personalized FAQ content for a specific role and missing skills.
    """
    prompt = f"""
    Generate a set of 8 frequently asked questions (FAQ) for a student preparing for a '{target_role}' role.
    The student is currently missing these skills: {missing_skills}.

    The FAQs should cover:
    - What the role actually involves day-to-day
    - How to start learning the missing skills (practical first steps)
    - Common mistakes beginners make when preparing for this role
    - What kind of projects impress recruiters for this role
    - How to prepare for technical interviews for this role
    - How long it realistically takes to become job-ready
    - Which skills to prioritize first
    - Any tips specific to the Indian job market (placements, SIH, hackathons, etc.)

    Use simple, beginner-friendly language. Answers should be 3-5 sentences each — specific, actionable, and encouraging.

    Return ONLY a valid JSON object matching this structure:
    {{
        "faqs": [
            {{
                "question": "The FAQ question",
                "answer": "The detailed answer",
                "category": "One of: Role Overview, Learning Path, Projects, Interview Prep, Career Tips"
            }}
        ]
    }}
    """
    try:
        if not IS_API_KEY_CONFIGURED:
            raise RuntimeError("Groq API key is not configured.")
        return _generate_json(prompt)
    except Exception as e:
        error_detail = _handle_api_error("generate_faq", e)
        logger.info(f"ℹ️ Falling back to local FAQ generation")
        return get_mock_faq(target_role, missing_skills)


def get_fallback_coach_reply(user_message, target_role, missing_skills, readiness):
    msg = user_message.lower()
    skills_str = ", ".join(missing_skills) if missing_skills else "none"
    if "skill" in msg or "gap" in msg:
        return f"Since you are targeting the **{target_role}** position, the key missing skills in your profile are: **{skills_str}**. Focus on learning these first to bridge your gaps. You can view a tailored 12-week study plan in the **Career Roadmap** tab!"
    elif "project" in msg or "build" in msg or "portfolio" in msg:
        return f"Building projects is the best way to prove your technical skills for **{target_role}**. I recommend checking the **Project & Prep** page. There you will find beginner, intermediate, and advanced project ideas themed around real-world problems."
    elif "cert" in msg or "course" in msg or "learn" in msg:
        return f"Certifications help validate your learning path. For the **{target_role}** role, courses from platforms like Coursera or NPTEL that cover **{skills_str}** are ideal. Look at the **Project & Prep** tab to see specific matched credentials!"
    elif "interview" in msg or "prepare" in msg or "question" in msg:
        return f"To ace technical interviews for **{target_role}**, practice coding challenges daily (arrays, lists, recursion) and review core system design or OOP concepts. I have prepared a list of practice questions for you on the **Project & Prep** page."
    else:
        return f"As your career coach for the **{target_role}** role (current readiness: {readiness}%), I'm here to support you! You can ask me about specific skills, project plans, or interview strategies. (Running in Offline Fallback Mode)."


def generate_coach_reply(user_message, chat_history, resume_details, analysis_results, target_role=None):
    """
    Generates a helpful coaching reply for placement preparation guidance.
    """
    history_text = "\n".join(
        [f"{item['role'].upper()}: {item['content']}" for item in chat_history[-8:]]
    ) if chat_history else "No prior chat history."

    role = target_role or analysis_results.get("target_role", "your target role")
    readiness = analysis_results.get("readiness_score", 0)
    matched = analysis_results.get("matched_skills", [])
    missing = analysis_results.get("missing_skills", [])
    recommended = analysis_results.get("additional_recommended_skills", [])
    technical = resume_details.get("technical_skills", [])
    languages = resume_details.get("programming_languages", [])
    tools = resume_details.get("tools", [])
    projects = [p.get("title", "") for p in resume_details.get("projects", [])]
    has_analysis = bool(analysis_results.get("target_role"))

    prompt = f"""
    You are SkillSync AI's friendly career coach. Your job is to guide a student on how to prepare for their next job interview, improve weak areas, and use the app's analysis intelligently.

    Response style:
    - Be warm, encouraging, and practical.
    - Answer directly and clearly.
    - If the user asks about a skill, explain it simply and give concrete next steps.
    - If the user asks for preparation, give a short action plan with bullet points.
    - If the answer depends on the app analysis, connect it back to the user's skills and gaps.
    - Do not mention that you are an AI model.
    - Keep the response concise but useful, ideally 4-8 short bullets or a few short paragraphs.
    - If no resume analysis is available, give general but practical career guidance for the chosen role.

    Candidate context:
    - Target role: {role}
    - Resume analysis available: {has_analysis}
    - Readiness score: {readiness}%
    - Matched skills: {matched}
    - Missing skills: {missing}
    - Additional recommended skills: {recommended}
    - Technical skills: {technical}
    - Programming languages: {languages}
    - Tools: {tools}
    - Projects: {projects}

    Conversation history:
    {history_text}

    User message:
    {user_message}

    Now respond as a career coach with practical guidance, next steps, and suggestions relevant to the user's app analysis.
    """

    try:
        if not IS_API_KEY_CONFIGURED:
            raise RuntimeError("Groq API key is not configured.")
        return _generate_text(prompt)
    except Exception as e:
        error_detail = _handle_api_error("generate_coach_reply", e)
        logger.info(f"ℹ️ Falling back to template-based coach response")
        return get_fallback_coach_reply(user_message, role, missing, readiness)

# ==========================================
# LEGACY MOCK DATA GENERATORS
# Kept for local experimentation, but not used by the app flow.
# ==========================================

def get_mock_resume_analysis(resume_text=None):
    if not resume_text:
        return {
            "name": "Arjun Sharma",
            "email": "arjun.sharma@gmail.com",
            "phone": "+91 98765 43210",
            "technical_skills": ["Python", "SQL", "Pandas", "Matplotlib", "Git", "Data Analysis", "Data Cleaning"],
            "soft_skills": ["Communication", "Problem Solving", "Team Collaboration"],
            "programming_languages": ["Python", "SQL", "JavaScript"],
            "tools": ["Jupyter Notebook", "VS Code", "GitHub", "Excel"],
            "projects": [
                {
                    "title": "E-Commerce Customer Segmentation",
                    "description": "Performed exploratory data analysis and clustered customers based on buying behaviors using Python and Pandas.",
                    "technologies": ["Python", "Pandas", "Matplotlib", "Seaborn"]
                },
                {
                    "title": "Movie Recommendation Script",
                    "description": "Built a simple recommendation engine using cosine similarity to recommend movies based on genre and user ratings.",
                    "technologies": ["Python", "NumPy", "Pandas"]
                }
            ],
            "certifications": ["Google Data Analytics Professional Certificate"],
            "internships": [
                {
                    "role": "Data Analyst Intern",
                    "company": "TechInfo Solutions",
                    "duration": "Dec 2025 - Feb 2026",
                    "description": "Assisted in cleaning database records, wrote SQL queries to generate weekly sales reports, and created spreadsheets for executive review."
                }
            ],
            "education": [
                {
                    "degree": "B.Tech in Computer Science and Engineering",
                    "institution": "Vellore Institute of Technology (VIT)",
                    "year": "2027"
                }
            ]
        }

    # 1. Extract Email
    email = "candidate@example.com"
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', resume_text)
    if email_match:
        email = email_match.group(0)
        
    # 2. Extract Phone
    phone = "+91 99999 88888"
    phone_match = re.search(r'\+?\d[\d\s-]{8,14}\d', resume_text)
    if phone_match:
        phone = phone_match.group(0).strip()

    # 3. Extract Name
    name = "Student Candidate"
    # Try guessing from email (e.g. devansh.verma@gmail.com -> Devansh Verma)
    if email_match:
        local_part = email.split('@')[0]
        local_part = re.sub(r'\d+', '', local_part)
        parts = re.split(r'[_.-]', local_part)
        parts = [p.capitalize() for p in parts if len(p) > 1]
        if parts:
            name = " ".join(parts)
    
    # If name is still generic, try taking the first non-empty line of the resume
    if name == "Student Candidate" or len(name) < 3:
        lines = [line.strip() for line in resume_text.split('\n') if line.strip()]
        for line in lines[:5]:
            # Simple check: no emails, no digits, less than 40 chars, has 2-3 words
            if "@" not in line and not any(c.isdigit() for c in line) and len(line) < 40 and 1 < len(line.split()) < 5:
                cleaned_name = re.sub(r'[^a-zA-Z\s]', '', line).strip()
                if cleaned_name:
                    name = " ".join([p.capitalize() for p in cleaned_name.split()])
                    break

    # 4. Extract Technical Skills, Programming Languages, and Tools by matching keywords
    all_known_skills = set()
    for role, data in CAREER_DATABASE.items():
        all_known_skills.update(data["required_skills"])
    
    languages_pool = ["python", "javascript", "typescript", "java", "c++", "c#", "ruby", "go", "rust", "php", "sql", "html", "css", "kotlin", "swift"]
    tools_pool = ["git", "github", "docker", "kubernetes", "jenkins", "jira", "vs code", "linux", "aws", "azure", "gcp", "postman", "figma", "excel"]
    
    matched_skills = []
    matched_languages = []
    matched_tools = []
    
    # Normalize resume text for matching
    norm_text = " " + re.sub(r'[^a-z0-9\s\+#\-\.]', ' ', resume_text.lower()) + " "
    
    # Match languages
    for lang in languages_pool:
        pattern = r'\b' + re.escape(lang) + r'\b'
        if lang == "c++":
            pattern = r'\bc\+\+\b'
        elif lang == "c#":
            pattern = r'\bc#\b'
        if re.search(pattern, norm_text):
            matched_languages.append(lang.upper() if lang not in ["python", "javascript", "typescript", "kotlin", "swift"] else lang.capitalize())
            
    # Match tools
    for tool in tools_pool:
        pattern = r'\b' + re.escape(tool) + r'\b'
        if re.search(pattern, norm_text):
            matched_tools.append(tool.upper() if tool in ["aws", "gcp", "jira", "vs code"] else tool.capitalize())
            
    # Match other skills
    for skill in all_known_skills:
        skill_lower = skill.lower()
        if skill_lower in languages_pool or skill_lower in tools_pool:
            continue
        # Use word boundaries for short skills (length <= 3) to prevent partial substring matches
        if len(skill_lower) <= 3:
            pattern = r'\b' + re.escape(skill_lower) + r'\b'
            if re.search(pattern, norm_text):
                matched_skills.append(skill)
        else:
            if skill_lower in norm_text:
                matched_skills.append(skill)
            
    # If no skills matched, supply some defaults
    if not matched_skills and not matched_languages:
        matched_languages = ["Python", "SQL"]
        matched_skills = ["Data Analysis", "Git", "Problem Solving"]
        matched_tools = ["VS Code", "GitHub"]

    # 5. Extract projects dynamically
    projects = []
    projects_match = re.search(r'(?i)(projects|academic projects|key projects)([\s\S]*?)(experience|education|skills|certifications|$)', resume_text)
    if projects_match:
        projects_section = projects_match.group(2)
        proj_lines = [line.strip().replace('• ', '').replace('- ', '') for line in projects_section.split('\n') if line.strip()]
        valid_projs = []
        for line in proj_lines:
            if len(line) < 60 and not line.lower().startswith("tech") and any(w.istitle() or w.isupper() for w in line.split()[:2]):
                valid_projs.append(line)
        for vp in valid_projs[:2]:
            projects.append({
                "title": vp,
                "description": f"Developed an application centered around {vp} using candidate core technologies.",
                "technologies": matched_languages[:2]
            })
        
    if not projects:
        p1_tech = matched_languages[:2] + matched_tools[:1]
        p2_tech = matched_skills[:2] + matched_languages[-1:]
        if not p1_tech: p1_tech = ["Python"]
        if not p2_tech: p2_tech = ["SQL"]
        
        projects = [
            {
                "title": f"Personalized {p1_tech[0]} Development Project",
                "description": f"Developed a custom application using {', '.join(p1_tech)} focusing on clean code practices and modular architecture.",
                "technologies": p1_tech
            },
            {
                "title": f"Data Pipeline with {p2_tech[0]} Integration",
                "description": f"Designed and implemented a processing system integrating {', '.join(p2_tech)} to structure and query database records.",
                "technologies": p2_tech
            }
        ]

    # 6. Education
    education = []
    edu_match = re.search(r'(?i)(education|academic qualification|academic profile)([\s\S]*?)(experience|projects|skills|certifications|$)', resume_text)
    if edu_match:
        edu_section = edu_match.group(2)
        edu_lines = [line.strip() for line in edu_section.split('\n') if line.strip()][:2]
        if edu_lines:
            education.append({
                "degree": edu_lines[0][:50],
                "institution": edu_lines[1][:50] if len(edu_lines) > 1 else "Technical University",
                "year": "2027"
            })
    if not education:
        education.append({
            "degree": "B.Tech in Computer Science and Engineering",
            "institution": "Vellore Institute of Technology (VIT)",
            "year": "2027"
        })

    # 7. Internships / Experience
    internships = []
    exp_match = re.search(r'(?i)(experience|work experience|internship|employment history)([\s\S]*?)(projects|education|skills|certifications|$)', resume_text)
    if exp_match:
        exp_section = exp_match.group(2)
        exp_lines = [line.strip() for line in exp_section.split('\n') if line.strip()][:3]
        if exp_lines:
            internships.append({
                "role": exp_lines[0][:50],
                "company": exp_lines[1][:50] if len(exp_lines) > 1 else "Tech Solutions Ltd",
                "duration": "June 2025 - Aug 2025",
                "description": exp_lines[2][:120] if len(exp_lines) > 2 else "Developed features, resolved issues, and assisted team members."
            })
    if not internships:
        internships.append({
            "role": "Software Engineering Intern",
            "company": "Innovative Solutions",
            "duration": "Dec 2025 - Feb 2026",
            "description": "Assisted in cleaning database records, wrote script utilities, and built test coverage reports."
        })

    # 8. Certifications
    certifications = []
    certs_match = re.search(r'(?i)(certifications|licenses|courses)([\s\S]*?)(experience|education|projects|skills|$)', resume_text)
    if certs_match:
        certs_section = certs_match.group(2)
        certifications = [line.strip().replace('• ', '').replace('- ', '') for line in certs_section.split('\n') if line.strip() and len(line.strip()) < 80][:2]
    if not certifications:
        certifications = ["Google Data Analytics Professional Certificate"]

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "technical_skills": matched_skills,
        "soft_skills": ["Communication", "Problem Solving", "Teamwork"],
        "programming_languages": matched_languages,
        "tools": matched_tools,
        "projects": projects,
        "certifications": certifications,
        "internships": internships,
        "education": education
    }

def get_mock_roadmap(target_role, missing_skills):
    # Setup some default missing skills if empty
    skills = missing_skills if missing_skills else ["Deep Learning", "TensorFlow", "PyTorch", "NLP"]
    
    roadmap = []
    
    # We will generate 12 weeks of items
    for week in range(1, 13):
        # Determine focus skill for the week based on what is missing
        focus_index = (week - 1) % len(skills)
        current_skill = skills[focus_index]
        
        if week <= 4:
            phase = "Foundations"
            goals = f"Understand the core syntax and fundamental mathematics of {current_skill}."
            exercise = f"Write a simple Python script to implement the mathematical foundation of {current_skill} from scratch."
        elif week <= 8:
            phase = "Intermediate Practice"
            goals = f"Apply {current_skill} in a standard project setting using libraries and frameworks."
            exercise = f"Complete a mini-project integrating {current_skill} with previously learned tools."
        else:
            phase = "Advanced Applications"
            goals = f"Optimize models/systems built on {current_skill} and integrate them into REST endpoints."
            exercise = f"Build and deploy a complete web interface for a {current_skill} system."

        roadmap.append({
            "week": week,
            "skills_to_learn": [current_skill],
            "resources": [
                {
                    "name": f"Coursera: {current_skill}",
                    "url": "Coursera"
                }
            ],
            "mini_goals": goals,
            "practice_exercises": exercise
        })
        
    return {"roadmap": roadmap}

def get_mock_projects(target_role, missing_skills):
    skills = missing_skills if missing_skills else ["Machine Learning", "FastAPI", "Docker"]
    s1 = skills[0] if len(skills) > 0 else "ML Models"
    s2 = skills[1] if len(skills) > 1 else "Database Integration"
    s3 = skills[2] if len(skills) > 2 else "Cloud Deployments"

    return {
        "projects": [
            {
                "title": f"Smart Agriculture Tool with {s1}",
                "difficulty": "Beginner",
                "description": "Create a simple program to help local farmers. It takes daily weather data, does basic calculations, and prints out simple advice on whether they should water their crops today.",
                "technologies_required": ["Python", s1, "Git"],
                "estimated_time": "1-2 Weeks"
            },
            {
                "title": f"Rural Healthcare Web Server using {s2}",
                "difficulty": "Intermediate",
                "description": "Build a simple website for village clinics. Allow doctors to log in safely and save patient appointment information to a basic database so they don't have to use paper records.",
                "technologies_required": ["FastAPI", "SQL", s2, "Git"],
                "estimated_time": "3 Weeks"
            },
            {
                "title": f"City Pollution Dashboard with {s3}",
                "difficulty": "Advanced",
                "description": "Make a dashboard that tracks city air pollution in real-time to help the government reduce emissions. Put it live on the internet so any citizen can see it without the website crashing.",
                "technologies_required": [s3, "Docker", "Kubernetes", "Plotly", "GitHub Actions"],
                "estimated_time": "4-5 Weeks"
            }
        ]
    }

def get_mock_interview_questions(target_role, missing_skills):
    skills = missing_skills if missing_skills else ["Machine Learning", "System Design"]
    s1 = skills[0] if len(skills) > 0 else "Object Oriented Principles"
    
    return {
        "technical": [
            {
                "question": f"Explain the core concept of {s1} and how it differs from traditional approaches?",
                "answer": f"{s1} represents a paradigm shift. Unlike standard procedures, it structures components around modular, self-contained elements with specific attributes. This enhances code reusability, isolation, and system extensibility."
            },
            {
                "question": "What is the difference between a Relational Database (SQL) and a Non-Relational Database (NoSQL)? When would you choose one over the other?",
                "answer": "SQL databases are table-based with strict, predefined schemas, supporting ACID transactions. They are best for structured data with complex relationships. NoSQL databases are document or key-value based with dynamic schemas, designed for horizontal scalability and handling unstructured/hierarchical data."
            },
            {
                "question": f"How do you handle debugging or diagnosing performance issues in an application that relies heavily on {s1}?",
                "answer": "Diagnosing involves using profilers to track execution times and memory allocations, analyzing log traces for errors, isolating specific modules for unit testing, and inspecting database query execution plans to optimize index queries."
            }
        ],
        "coding": [
            {
                "question": "Write a Python function to reverse a linked list in-place.",
                "answer": "def reverse_list(head):\n    prev = None\n    current = head\n    while current:\n        next_node = current.next\n        current.next = prev\n        prev = current\n        current = next_node\n    return prev"
            },
            {
                "question": "Implement a binary search algorithm in Python and state its time complexity.",
                "answer": "def binary_search(arr, target):\n    low, high = 0, len(arr) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    return -1\n# Time Complexity: O(log N)"
            },
            {
                "question": "Write a SQL query to find the second highest salary from an Employee table.",
                "answer": "SELECT MAX(Salary) FROM Employee WHERE Salary < (SELECT MAX(Salary) FROM Employee);"
            }
        ],
        "hr": [
            {
                "question": "Why do you want to join our organization as a junior team member?",
                "answer": "Your organization is known for building cutting-edge solutions and fostering a culture of mentorship. I am eager to contribute my strong foundations, learn from industry leaders, and work on scalable products."
            },
            {
                "question": "Tell us about a time you faced a difficult conflict during a academic/project team task, and how you resolved it.",
                "answer": "During a group project, we disagreed on the tech stack. I set up a call to objectively list the pros and cons of both architectures, mapped them to our project requirements, and reached a consensus to build a hybrid prototype first, which worked out successfully."
            }
        ],
        "scenario": [
            {
                "question": "You are tasked with deploying a critical hotfix to the system, but the build pipeline fails due to an outdated dependency. How do you respond?",
                "answer": "First, I notify the lead developer and team about the issue. I look at the build log to identify the breaking dependency. I try to pin the dependency to the last working version locally to isolate the issue. If it builds, I test the fix thoroughly, make a temporary override branch, and work with DevOps to merge the hotfix while documenting the dependency patch."
            },
            {
                "question": "A business client reports that a data visualization dashboard is loading too slowly. Where do you begin your analysis?",
                "answer": "I would check the network tab in the developer console to see if the slow load is due to huge payload sizes, un-indexed database queries, or client-side rendering issues. Then, I would implement caching for static queries, compress API responses, and pagination or lazy loading on the UI."
            }
        ]
    }

def get_mock_certifications(target_role, missing_skills):
    skills = missing_skills if missing_skills else ["Deep Learning", "Docker"]
    s1 = skills[0] if len(skills) > 0 else "Cloud Architecting"
    s2 = skills[1] if len(skills) > 1 else "Modern Software Engineering"
    
    return {
        "certifications": [
            {
                "name": f"Coursera: {s1} Specialization",
                "platform": "Coursera",
                "target_skill": s1,
                "difficulty": "Beginner",
                "duration": "6 Weeks"
            },
            {
                "name": f"NPTEL: Modern {s2} Practices",
                "platform": "NPTEL",
                "target_skill": s2,
                "difficulty": "Intermediate",
                "duration": "8 Weeks"
            },
            {
                "name": "AWS Certified Solutions Architect - Associate",
                "platform": "AWS",
                "target_skill": "Cloud Services",
                "difficulty": "Intermediate",
                "duration": "3 Months"
            },
            {
                "name": "Google Professional Data Engineer Certificate",
                "platform": "Google",
                "target_skill": "Data Architecture",
                "difficulty": "Advanced",
                "duration": "4 Months"
            }
        ]
    }

def get_mock_faq(target_role, missing_skills):
    skills = missing_skills if isinstance(missing_skills, list) else [missing_skills]
    s1 = skills[0] if len(skills) > 0 else "Core Programming"
    s2 = skills[1] if len(skills) > 1 else "System Design"

    return {
        "faqs": [
            {
                "question": f"What does a {target_role} actually do on a daily basis?",
                "answer": f"A {target_role} typically writes code, reviews pull requests, attends team standups, and debugs issues. You will work closely with other developers and product managers to build features that users need. It's a mix of problem-solving, coding, and teamwork.",
                "category": "Role Overview"
            },
            {
                "question": f"How do I start learning {s1} from scratch?",
                "answer": f"Start with a free YouTube crash course on {s1} to understand the basics. Then pick one small project and build it from start to finish. Consistency matters more than speed — even 1 hour a day for 30 days will get you very far.",
                "category": "Learning Path"
            },
            {
                "question": f"Which skill should I learn first — {s1} or {s2}?",
                "answer": f"Start with {s1} because it is more foundational and will make learning {s2} much easier later. Think of it like building blocks — you need the base layer before stacking more advanced concepts on top.",
                "category": "Learning Path"
            },
            {
                "question": f"What kind of projects will impress recruiters for a {target_role} position?",
                "answer": "Recruiters love projects that solve real-world problems. Try building something that helps your college, local community, or a social cause (like an SIH problem statement). A working deployed project beats 10 incomplete ones.",
                "category": "Projects"
            },
            {
                "question": f"How should I prepare for technical interviews for {target_role}?",
                "answer": "Practice 2-3 coding problems daily on LeetCode or GeeksforGeeks. Focus on arrays, strings, and trees first — they cover 60% of interview questions. Also prepare 2-3 project explanations you can walk through confidently.",
                "category": "Interview Prep"
            },
            {
                "question": "What are the most common mistakes students make while preparing?",
                "answer": "The biggest mistake is tutorial hell — watching course after course without building anything. Another common mistake is trying to learn too many technologies at once. Focus on one stack, build projects, and go deep before going wide.",
                "category": "Career Tips"
            },
            {
                "question": f"How long will it realistically take me to become job-ready as a {target_role}?",
                "answer": "With focused daily practice of 3-4 hours, most students can become interview-ready in 3-4 months. This includes learning core skills, building 2-3 solid projects, and practicing DSA problems. Don't rush — steady progress beats burnout.",
                "category": "Career Tips"
            },
            {
                "question": "How can hackathons like SIH help me get placed?",
                "answer": "Hackathons like Smart India Hackathon (SIH) give you real problem statements to solve, team collaboration experience, and something impressive to put on your resume. Many companies specifically look for hackathon participation during campus placements.",
                "category": "Career Tips"
            }
        ]
    }
