# Streamlit app entry point
import streamlit as st
from backend.ui_components import init_page
from backend.role_database import CAREER_DATABASE
from backend.parser import extract_text
from backend.gap_engine import analyze_gaps
from backend.groq_service import analyze_resume

# 1. Initialize UI elements, styling, and session variables via helper
analyzed = init_page("Home")

# Make the coach entry visible on the Home page even if the shared sidebar module
# is still cached in the running Streamlit session.
st.sidebar.markdown("### Quick Access")
if st.sidebar.button("🧠 Career Guide", use_container_width=True, key="home_coach_sidebar"):
    st.switch_page("pages/coach.py")

# 2. Hero Section
st.markdown(
    """
    <div style='text-align: center; margin-top: 20px; margin-bottom: 40px;'>
        <h1 style='font-size: 3rem; margin-bottom: 0px;'>
            <span class='gradient-text'>SkillSync AI</span>
        </h1>
        <h3 style='font-weight: 400; color: #ccc; margin-top: 5px; margin-bottom: 25px;'>
            "Know Your Gaps. Build Your Future."
        </h3>
        <p style='font-size: 1.15rem; max-width: 800px; margin: 0 auto; color: #aaa; line-height: 1.6;'>
            Analyze your resume against industry-standard requirements, identify missing skills,
            and generate a personalized 3-month timeline roadmap to land your dream career.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# 3. Main Dashboard Redirect / Action Callout
if analyzed:
    res = st.session_state["analysis_results"]
    st.markdown(
        f"""
        <div class='glass-card' style='border: 1px solid rgba(100, 108, 255, 0.4); text-align: center; margin-bottom: 40px;'>
            <h3 style='color: #646cff; margin-bottom: 8px;'>🎉 Resume Successfully Analyzed!</h3>
            <p style='color: #ccc; font-size: 0.95rem; margin-bottom: 15px;'>
                Candidate Name: <strong>{st.session_state["resume_details"].get("name", "Student")}</strong> | 
                Target Career: <strong>{res.get("target_role")}</strong>
            </p>
            <p style='font-size: 1.1rem; font-weight: 700; margin-bottom: 20px;'>
                Readiness Score: <span style='color: #e056fd; font-size: 1.5rem;'>{res.get("readiness_score")}%</span> ({res.get("performance_level")})
            </p>
            <p style='color: #888; font-size: 0.85rem; margin-bottom: 10px;'>
                Use the sidebar menu or navigation links to view detailed analyses.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Render quick navigation buttons in columns
    cols = st.columns(5)
    with cols[0]:
        if st.button("📊 Placement Dashboard", use_container_width=True):
            st.switch_page("pages/dashboard.py")
    with cols[1]:
        if st.button("🔍 Skill Gap Analysis", use_container_width=True):
            st.switch_page("pages/skill_gap.py")
    with cols[2]:
        if st.button("📅 Career Roadmap", use_container_width=True):
            st.switch_page("pages/roadmap.py")
    with cols[3]:
        if st.button("💼 Project & Prep", use_container_width=True):
            st.switch_page("pages/projects.py")
    with cols[4]:
        if st.button("🧠 Career Guide", use_container_width=True):
            st.switch_page("pages/coach.py")
else:
    st.markdown(
        """
        <div class='glass-card' style='text-align: center; border: 1px dashed rgba(255,255,255,0.15); margin-bottom: 40px; padding: 30px;'>
            <h3 style='color: #646cff; margin-bottom: 15px;'>👋 Let's Get Started!</h3>
            <p style='color: #ccc; font-size: 1.05rem; margin-bottom: 25px;'>
                Upload your resume (PDF/DOCX) and select your target role, then click 
                <strong>"Run Gap Analysis"</strong> to generate your career insights.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Form layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💼 Career Settings")
        roles_list = list(CAREER_DATABASE.keys())
        default_role_idx = 0
        if st.session_state.get("target_role") in roles_list:
            default_role_idx = roles_list.index(st.session_state["target_role"])
        
        selected_role = st.selectbox(
            "Select Target Career Role", 
            roles_list, 
            index=default_role_idx
        )
        st.session_state["target_role"] = selected_role

    with col2:
        st.markdown("### 📄 Resume Submission")
        uploaded_file = st.file_uploader(
            "Drag & Drop or Upload Resume", 
            type=["pdf", "docx"], 
            help="Upload PDF or DOCX format resumes only"
        )

    # Core Action Button
    st.markdown("<br/>", unsafe_allow_html=True)
    analyze_button = st.button("🔍 Run Gap Analysis", use_container_width=True, type="primary")

    if analyze_button:
        if not uploaded_file:
            st.error("⚠️ Please upload a resume first.")
        else:
            with st.spinner("Processing resume & analyzing skills..."):
                try:
                    # Clear older caches if new analysis is triggered
                    st.session_state["roadmap"] = None
                    st.session_state["projects"] = None
                    st.session_state["certifications"] = None
                    st.session_state["interview_questions"] = None

                    # A. Parse Text
                    file_bytes = uploaded_file.read()
                    text = extract_text(uploaded_file.name, file_bytes)
                    st.session_state["resume_text"] = text

                    # B. Extract Details via Groq
                    details = analyze_resume(text)
                    st.session_state["resume_details"] = details

                    # C. Compute Skill Gap Analysis
                    resume_skills = details.get("technical_skills", [])
                    # Append languages & tools to skills for a broader search
                    resume_skills.extend(details.get("programming_languages", []))
                    resume_skills.extend(details.get("tools", []))
                    
                    analysis = analyze_gaps(resume_skills, selected_role)
                    st.session_state["analysis_results"] = analysis
                    
                    st.session_state["analyzed"] = True
                    st.success("✅ Analysis completed successfully!")
                    # Rerun to refresh the current page with new results
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# 4. Interactive Step-by-Step Workflow
st.markdown("## 🚀 How it Works")
workflow_cols = st.columns(3)

with workflow_cols[0]:
    st.markdown(
        """
        <div class='glass-card' style='height: 200px;'>
            <h3 style='color: #646cff;'>1. Upload & Extract</h3>
            <p style='color: #bbb; font-size: 0.9rem; line-height: 1.5;'>
                Submit your PDF or Word resume. Our parser extracts the text, and Groq extracts structured technical and soft skills, projects, and work history.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with workflow_cols[1]:
    st.markdown(
        """
        <div class='glass-card' style='height: 200px;'>
            <h3 style='color: #e056fd;'>2. Gap Analysis</h3>
            <p style='color: #bbb; font-size: 0.9rem; line-height: 1.5;'>
                We map your skills against industry standards for your selected role, calculating your Job Readiness Score and identifying matched vs. missing competencies.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with workflow_cols[2]:
    st.markdown(
        """
        <div class='glass-card' style='height: 200px;'>
            <h3 style='color: #2ecc71;'>3. Personalize & Prep</h3>
            <p style='color: #bbb; font-size: 0.9rem; line-height: 1.5;'>
                Get a week-by-week learning roadmap, level-based projects, targeted certifications, and role-specific interview prep to bridge your gaps.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()

# 5. Role Explorer Section
st.markdown("## 🔍 Target Career Explorer")
st.markdown("<p style='color: #aaa; margin-top: -15px; margin-bottom: 25px;'>Select a role below to explore required skills, recommended projects, and certifications.</p>", unsafe_allow_html=True)

role_options = list(CAREER_DATABASE.keys())
selected_explorer_role = st.selectbox("Select Role to Inspect", role_options)

if selected_explorer_role:
    role_data = CAREER_DATABASE[selected_explorer_role]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            f"""
            <div class='glass-card' style='height: 100%;'>
                <h3 style='color: #646cff;'>🛠️ Required Core Skills</h3>
                <div style='margin-top: 15px;'>
                    {" ".join([f"<span class='custom-badge badge-matched'>{skill}</span>" for skill in role_data['required_skills']])}
                </div>
                <h3 style='color: #e056fd; margin-top: 25px;'>💡 Interview Topics</h3>
                <ul style='color: #ccc; font-size: 0.95rem; margin-top: 10px; line-height: 1.6;'>
                    {"".join([f"<li>{topic}</li>" for topic in role_data['interview_topics']])}
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col2:
        st.markdown(
            f"""
            <div class='glass-card' style='height: 100%;'>
                <h3 style='color: #2ecc71;'>🏅 Recommended Certifications</h3>
                <ul style='color: #ccc; font-size: 0.95rem; margin-top: 10px; line-height: 1.6;'>
                    {"".join([f"<li>{cert}</li>" for cert in role_data['recommended_certifications']])}
                </ul>
                <h3 style='color: #3498db; margin-top: 25px;'>💻 Suggested Practice Projects</h3>
                <ul style='color: #ccc; font-size: 0.95rem; margin-top: 10px; line-height: 1.6;'>
                    {"".join([f"<li>{proj}</li>" for proj in role_data['recommended_projects']])}
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )
