import streamlit as st
from backend.ui_components import init_page, check_analysis_guard
from backend.groq_service import generate_projects, recommend_certifications

# 1. Initialize page configuration and sidebar
init_page("Project & Certification Recommendations")

# 2. Guard to ensure analysis is ready
if not check_analysis_guard():
    res = st.session_state["analysis_results"]
    role = res.get("target_role")
    missing = res.get("missing_skills", [])

    st.markdown("## 🛠️ Portfolio Builders")
    st.markdown(f"<p style='color: #aaa; margin-top: -15px;'>Bridge your gaps for <strong>{role}</strong> with hands-on projects and targeted industry certifications.</p>", unsafe_allow_html=True)

    # 3. Setup Tabs
    tab_projects, tab_certs = st.tabs(["💻 AI Project Recommendations", "🏅 Recommended Certifications"])

    # --- TAB 1: PROJECTS ---
    with tab_projects:
        # Check cache or generate
        if st.session_state["projects"] is None:
            with st.spinner("Generating custom project recommendations to bridge your skill gaps..."):
                try:
                    projects_data = generate_projects(missing, role)
                    st.session_state["projects"] = projects_data
                except Exception as e:
                    st.error(f"Failed to generate projects: {str(e)}")
                    
        projects_data = st.session_state["projects"]

        if projects_data and "projects" in projects_data:
            projs = projects_data["projects"]
            st.markdown("<p style='color: #aaa;'>Implement these projects to gain practical experience with your missing skills.</p>", unsafe_allow_html=True)
            
            for proj in projs:
                diff = proj.get("difficulty", "Beginner")
                # Define color code based on difficulty
                color = "#2ecc71"  # green
                if diff.lower() == "intermediate":
                    color = "#f39c12"  # orange
                elif diff.lower() == "advanced":
                    color = "#e74c3c"  # red
                
                tech_badges = "".join([f"<span class='custom-badge badge-matched' style='font-size:0.7rem;'>{t}</span>" for t in proj.get("technologies_required", [])])
                
                # Render using Streamlit expander
                with st.expander(f"⭐ {proj.get('title')} ({diff})"):
                    st.markdown(
                        f"""
                        <div style='padding: 5px 0;'>
                            <p style='color: #ddd; font-size: 0.95rem; line-height: 1.5;'>{proj.get('description')}</p>
                            <div style='margin: 15px 0;'>
                                <strong style='color: {color};'>Difficulty:</strong> {diff} | 
                                <strong>Estimated Time:</strong> {proj.get('estimated_time', 'N/A')}
                            </div>
                            <div style='margin-top: 10px;'>
                                <strong style='display: block; margin-bottom: 6px;'>Technologies Required:</strong>
                                {tech_badges}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        else:
            st.warning("Could not load project recommendations.")

    # --- TAB 2: CERTIFICATIONS ---
    with tab_certs:
        # Check cache or generate
        if st.session_state["certifications"] is None:
            with st.spinner("Matching industry certifications with your missing skills..."):
                try:
                    certs_data = recommend_certifications(missing, role)
                    st.session_state["certifications"] = certs_data
                except Exception as e:
                    st.error(f"Failed to fetch certification recommendations: {str(e)}")
                    
        certs_data = st.session_state["certifications"]

        if certs_data and "certifications" in certs_data:
            certs = certs_data["certifications"]
            st.markdown("<p style='color: #aaa;'>Earn these credentials to validate your skills and strengthen your job profile.</p>", unsafe_allow_html=True)
            
            # Draw as cards in a grid
            col_idx = 0
            cols = st.columns(2)
            
            for cert in certs:
                current_col = cols[col_idx % 2]
                platform = cert.get("platform", "Coursera")
                
                # Determine platform logo class or label color
                plat_color = "#3498db" # blue
                if platform.lower() == "nptel":
                    plat_color = "#f39c12" # orange
                elif platform.lower() == "aws":
                    plat_color = "#ff9900" # yellow/orange
                elif platform.lower() == "google":
                    plat_color = "#4285f4" # google blue
                elif platform.lower() == "microsoft":
                    plat_color = "#00a4ef" # microsoft blue

                current_col.markdown(
                    f"""
                    <div class='glass-card' style='min-height: 200px; display: flex; flex-direction: column; justify-content: space-between; background: rgba(255,255,255,0.06);'>
                        <div>
                            <span style='background-color: {plat_color}22; color: {plat_color}; border: 1px solid {plat_color}55; padding: 3px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;'>
                                {platform}
                            </span>
                            <h4 style='margin-top: 12px; margin-bottom: 6px; font-size: 1rem; line-height: 1.4; color: {plat_color};'>
                                📘 {cert.get('name')}
                            </h4>
                            <p style='font-size: 0.85rem; margin: 0; opacity: 0.7;'>
                                Target Skill: <strong style='color:#e056fd;'>{cert.get('target_skill')}</strong>
                            </p>
                        </div>
                        <div style='display: flex; justify-content: space-between; border-top: 1px solid rgba(128,128,128,0.2); padding-top: 10px; font-size: 0.8rem; margin-top: 14px; opacity: 0.75;'>
                            <span>Difficulty: <strong>{cert.get('difficulty')}</strong></span>
                            <span>Duration: <strong>{cert.get('duration')}</strong></span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                col_idx += 1
        else:
            st.warning("Could not load certification recommendations.")
