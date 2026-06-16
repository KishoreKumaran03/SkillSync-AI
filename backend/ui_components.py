import streamlit as st
import os
from backend.parser import extract_text
from backend.gap_engine import analyze_gaps
from backend.groq_service import analyze_resume, API_KEY_STATUS, IS_API_KEY_CONFIGURED, _initialization_error
from backend.role_database import CAREER_DATABASE

def load_css():
    """
    Loads and injects the global style.css file.
    """
    css_path = os.path.join("assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        # Fallback inline basic styles if style.css is missing
        st.markdown("""
            <style>
                .glass-card { background: rgba(255, 255, 255, 0.05); border-radius: 10px; padding: 20px; margin-bottom: 15px; }
                .metric-card { border: 1px solid #333; padding: 15px; border-radius: 8px; text-align: center; }
                .gradient-text { background: linear-gradient(90deg, #646cff, #e056fd); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
            </style>
        """, unsafe_allow_html=True)

def init_page(page_name):
    """
    Initializes the page configuration, injects CSS, and renders the shared sidebar.
    Returns: bool (True if analysis is complete, False otherwise)
    """
    # 1. Set Page Configuration (must be called before other streamlit components)
    st.set_page_config(
        page_title=f"SkillSync AI - {page_name}",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 2. Inject CSS
    load_css()

    # 3. Initialize Session States
    if "analyzed" not in st.session_state:
        st.session_state["analyzed"] = False
    if "resume_text" not in st.session_state:
        st.session_state["resume_text"] = ""
    if "resume_details" not in st.session_state:
        st.session_state["resume_details"] = {}
    if "target_role" not in st.session_state:
        st.session_state["target_role"] = ""
    if "analysis_results" not in st.session_state:
        st.session_state["analysis_results"] = {}
    # Lazy loaded cache keys
    if "roadmap" not in st.session_state:
        st.session_state["roadmap"] = None
    if "projects" not in st.session_state:
        st.session_state["projects"] = None
    if "certifications" not in st.session_state:
        st.session_state["certifications"] = None
    if "interview_questions" not in st.session_state:
        st.session_state["interview_questions"] = None
    if "faq" not in st.session_state:
        st.session_state["faq"] = None
    if "api_key_exhausted" not in st.session_state:
        st.session_state["api_key_exhausted"] = False
    if "api_error_detail" not in st.session_state:
        st.session_state["api_error_detail"] = None
    if "api_error_category" not in st.session_state:
        st.session_state["api_error_category"] = None
    
    # If there was an initialization error, capture it now that session state is ready
    if _initialization_error and not st.session_state["api_error_detail"]:
        st.session_state["api_key_exhausted"] = True
        st.session_state["api_error_detail"] = _initialization_error

    # 4. Render Sidebar
    st.sidebar.markdown(
        """
        <div style='text-align: center; margin-bottom: 20px;'>
            <h1 style='margin-bottom: 0px;'>🎯 SkillSync AI</h1>
            <p style='font-size: 0.85rem; color: #aaa; margin-top: 0px;'>Know Your Gaps. Build Your Future.</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Custom Clean Navigation
    st.sidebar.markdown("### Navigation")
    st.sidebar.page_link("app.py", label="Home", icon="🏠")
    if st.sidebar.button("🧠 Career Guide", use_container_width=True):
        st.switch_page("pages/coach.py")
    if st.session_state.get("analyzed", False):
        st.sidebar.page_link("pages/dashboard.py", label="Placement Dashboard", icon="📊")
        st.sidebar.page_link("pages/skill_gap.py", label="Skill Gap Analysis", icon="🔍")
        st.sidebar.page_link("pages/roadmap.py", label="Career Roadmap", icon="📅")
        st.sidebar.page_link("pages/projects.py", label="Project & Prep", icon="💼")
        st.sidebar.page_link("pages/faq.py", label="Career FAQ", icon="❓")
    else:
        st.sidebar.markdown(
            "<p style='color: #888; font-size: 0.85rem; font-style: italic; margin-top: 10px;'>"
            "Upload resume on Home to unlock all pages.</p>", 
            unsafe_allow_html=True
        )
        
    st.sidebar.divider()

    # Check API key configuration status for a helpful banner in the sidebar
    if not IS_API_KEY_CONFIGURED:
        if API_KEY_STATUS == "placeholder":
            st.sidebar.warning("🔑 Offline Mode: GROQ_API_KEY is still the sample placeholder in .env. Add your real key.")
        else:
            st.sidebar.warning("🔑 Offline Mode: Groq API Key not detected in .env. Using local parser.")
    elif st.session_state.get("api_key_exhausted", False):
        error_detail = st.session_state.get("api_error_detail")
        error_category = st.session_state.get("api_error_category")
        
        if error_detail:
            # Show main warning
            st.sidebar.warning(
                f"⚠️ Offline Mode: API request failed\n\nUsing local fallback."
            )
            
            # Show error category and details in expandable section
            with st.sidebar.expander("📋 Error Details", expanded=False):
                st.write(error_detail)
                
                # Provide actionable remediation based on error category
                if error_category == "QUOTA_EXHAUSTED":
                    st.info(
                        "**What to do:**\n"
                        "1. Wait 1-24 hours for the restriction to be lifted\n"
                        "2. Check your [Google Cloud Console](https://console.cloud.google.com/) for quota status\n"
                        "3. Consider upgrading to a paid plan if quota is a recurring issue"
                    )
                elif error_category == "AUTH_ERROR":
                    st.warning(
                        "**What to do:**\n"
                        "1. Verify your API key in `.env` is correct\n"
                        "2. Check [Google Cloud Console](https://console.cloud.google.com/) that the API is enabled\n"
                        "3. Regenerate your API key if needed"
                    )
                elif error_category == "PROJECT_RESTRICTED":
                    st.error(
                        "**What to do:**\n"
                        "1. Visit [Google Cloud Console](https://console.cloud.google.com/)\n"
                        "2. Check the project status in Settings\n"
                        "3. Review API activity logs for unusual patterns\n"
                        "4. Contact Google Cloud support if needed"
                    )
                elif error_category == "NETWORK_ERROR":
                    st.info(
                        "**What to do:**\n"
                        "1. Check your internet connection\n"
                        "2. Try again in a moment\n"
                        "3. If the problem persists, check if Google's API service is experiencing outages"
                    )
        else:
            st.sidebar.warning("⚠️ Offline Mode: Groq API Key failed or exhausted. Using local fallback.")
    else:
        st.sidebar.success("⚡ Groq AI Connected.")

    # Footer elements in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.8rem;'>"
        "SkillSync AI v1.0.0<br/>"
        "Smart India Hackathon Demo"
        "</div>", 
        unsafe_allow_html=True
    )

    return st.session_state["analyzed"]

def check_analysis_guard():
    """
    Shows a warning message on pages if analysis has not been performed yet.
    Returns: bool (True if guard blocks execution, False if okay to proceed)
    """
    if not st.session_state.get("analyzed", False):
        st.markdown(
            f"""
            <div class='glass-card' style='text-align: center; margin-top: 50px;'>
                <h2 style='color: #e74c3c;'>⚠️ Resume Analysis Required</h2>
                <p style='font-size: 1.1rem; color: #ccc; margin: 15px 0 25px 0;'>
                    To view this page, you must first upload your resume and run the gap analysis on the Home Page.
                </p>
                <div style='display: flex; justify-content: center;'>
                    <a href="/" target="_self" style="text-decoration: none;">
                        <button style="
                            background-color: #646cff; 
                            color: white; 
                            border: none; 
                            padding: 10px 24px; 
                            border-radius: 8px; 
                            font-weight: 600; 
                            cursor: pointer;
                            transition: background-color 0.2s;
                        ">Go to Home Page</button>
                    </a>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        return True
    return False
