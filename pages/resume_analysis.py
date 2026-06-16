import streamlit as st
from backend.ui_components import init_page, check_analysis_guard

# 1. Initialize page configuration and sidebar
init_page("Resume Analysis")

# 2. Check if a resume has been analyzed
if not check_analysis_guard():
    # Retrieve details from session state
    details = st.session_state["resume_details"]
    
    st.markdown("## 📄 Extracted Resume Details")
    st.markdown("<p style='color: #aaa; margin-top: -15px;'>Review the information extracted from your resume by Groq.</p>", unsafe_allow_html=True)
    
    # Grid Layout for basic info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            f"""
            <div class='glass-card' style='text-align: center; height: 100%;'>
                <p class='metric-label'>👤 Name</p>
                <h3 style='margin: 10px 0;'>{details.get("name", "N/A")}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col2:
        st.markdown(
            f"""
            <div class='glass-card' style='text-align: center; height: 100%;'>
                <p class='metric-label'>📧 Email</p>
                <h3 style='margin: 10px 0; font-size: 1.15rem; word-break: break-all;'>{details.get("email", "N/A")}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col3:
        st.markdown(
            f"""
            <div class='glass-card' style='text-align: center; height: 100%;'>
                <p class='metric-label'>📞 Phone</p>
                <h3 style='margin: 10px 0;'>{details.get("phone", "N/A")}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    st.markdown("---")
    
    # Split layout for Skills and Education
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.markdown("### 🛠️ Skills & Competencies")
        
        # Technical Skills
        tech_skills_badges = "".join([f"<span class='custom-badge badge-matched'>{skill}</span>" for skill in details.get("technical_skills", [])])
        st.markdown(
            f"""
            <div class='glass-card'>
                <h4 style='color: #646cff; margin-bottom: 15px;'>Technical Skills</h4>
                {tech_skills_badges if tech_skills_badges else "<p style='color: #888;'>No technical skills detected.</p>"}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Programming Languages & Tools in nested columns
        sub_col1, sub_col2 = st.columns(2)
        
        with sub_col1:
            lang_badges = "".join([f"<span class='custom-badge badge-recommended'>{lang}</span>" for lang in details.get("programming_languages", [])])
            st.markdown(
                f"""
                <div class='glass-card' style='height: 100%;'>
                    <h4 style='color: #e056fd; margin-bottom: 12px;'>Programming Languages</h4>
                    {lang_badges if lang_badges else "<p style='color: #888;'>None detected.</p>"}
                </div>
                """,
                unsafe_allow_html=True
            )
            
        with sub_col2:
            tool_badges = "".join([f"<span class='custom-badge badge-matched'>{tool}</span>" for tool in details.get("tools", [])])
            st.markdown(
                f"""
                <div class='glass-card' style='height: 100%;'>
                    <h4 style='color: #3498db; margin-bottom: 12px;'>Tools & Frameworks</h4>
                    {tool_badges if tool_badges else "<p style='color: #888;'>None detected.</p>"}
                </div>
                """,
                unsafe_allow_html=True
            )
            
        # Soft Skills
        soft_badges = "".join([f"<span class='custom-badge badge-recommended' style='background-color: rgba(155, 89, 182, 0.15); color: #9b59b6; border: 1px solid rgba(155, 89, 182, 0.3);'>{skill}</span>" for skill in details.get("soft_skills", [])])
        st.markdown(
            f"""
            <div class='glass-card' style='margin-top: 20px;'>
                <h4 style='color: #2ecc71; margin-bottom: 12px;'>Soft Skills</h4>
                {soft_badges if soft_badges else "<p style='color: #888;'>No soft skills detected.</p>"}
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with c2:
        st.markdown("### 🎓 Education")
        education_list = details.get("education", [])
        if education_list:
            for edu in education_list:
                st.markdown(
                    f"""
                    <div class='glass-card'>
                        <h4 style='color: #646cff; margin-bottom: 4px;'>{edu.get("degree", "N/A")}</h4>
                        <p style='font-size: 0.95rem; font-weight: 500; margin-bottom: 4px; color: #fff;'>{edu.get("institution", "N/A")}</p>
                        <p class='metric-label' style='font-size: 0.75rem; text-align: left;'>Graduation Year: {edu.get("year", "N/A")}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                """
                <div class='glass-card'>
                    <p style='color: #888; text-align: center;'>No education details detected.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        # Certifications List
        st.markdown("### 🏅 Existing Certifications")
        certs = details.get("certifications", [])
        if certs:
            certs_html = "".join([f"<li style='margin-bottom: 8px; color: #ccc; font-size: 0.9rem;'>{cert}</li>" for cert in certs])
            st.markdown(
                f"""
                <div class='glass-card'>
                    <ul style='padding-left: 20px; margin: 0;'>
                        {certs_html}
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div class='glass-card'>
                    <p style='color: #888; text-align: center;'>No certifications detected.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("---")

    # Bottom layout for Experience & Projects
    st.markdown("### 💼 Internships / Experience & Projects")
    col_exp, col_proj = st.columns(2)
    
    with col_exp:
        st.markdown("#### 🏢 Experience & Internships")
        internships = details.get("internships", [])
        if internships:
            for intern in internships:
                st.markdown(
                    f"""
                    <div class='glass-card'>
                        <h4 style='color: #646cff; margin-bottom: 2px;'>{intern.get("role", "N/A")}</h4>
                        <div style='display: flex; justify-content: space-between; margin-bottom: 8px;'>
                            <span style='font-weight: 600; font-size: 0.9rem; color: #fff;'>{intern.get("company", "N/A")}</span>
                            <span style='font-size: 0.8rem; color: #888; font-weight: 500;'>{intern.get("duration", "N/A")}</span>
                        </div>
                        <p style='font-size: 0.85rem; color: #ccc; line-height: 1.4;'>{intern.get("description", "N/A")}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                """
                <div class='glass-card'>
                    <p style='color: #888; text-align: center;'>No work or internship experience detected.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
    with col_proj:
        st.markdown("#### 💻 Resume Projects")
        projects = details.get("projects", [])
        if projects:
            for proj in projects:
                techs = "".join([f"<span class='custom-badge badge-matched' style='font-size: 0.65rem; padding: 2px 6px;'>{tech}</span>" for tech in proj.get("technologies", [])])
                st.markdown(
                    f"""
                    <div class='glass-card'>
                        <h4 style='color: #e056fd; margin-bottom: 6px;'>{proj.get("title", "N/A")}</h4>
                        <p style='font-size: 0.85rem; color: #ccc; line-height: 1.4; margin-bottom: 10px;'>{proj.get("description", "N/A")}</p>
                        <div style='margin-top: 8px;'>
                            {techs}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                """
                <div class='glass-card'>
                    <p style='color: #888; text-align: center;'>No projects detected.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
