import streamlit as st
from backend.ui_components import init_page, check_analysis_guard
from backend.groq_service import generate_interview_questions

# 1. Initialize page configuration and sidebar
init_page("Interview Preparation")

# 2. Guard to ensure analysis is ready
if not check_analysis_guard():
    res = st.session_state["analysis_results"]
    role = res.get("target_role")
    missing = res.get("missing_skills", [])
    details = st.session_state["resume_details"]

    st.markdown("## 💼 AI Interview Preparation")
    st.markdown(f"<p style='color: #aaa; margin-top: -15px;'>Tailored interview questions based on your resume, projects, and target role: <strong>{role}</strong></p>", unsafe_allow_html=True)

    # 3. Check cache or generate questions
    if st.session_state["interview_questions"] is None:
        with st.spinner("Analyzing candidate profile and generating tailored interview prep material..."):
            try:
                questions_data = generate_interview_questions(role, details, missing)
                st.session_state["interview_questions"] = questions_data
            except Exception as e:
                st.error(f"Failed to generate interview questions: {str(e)}")
                
    questions_data = st.session_state["interview_questions"]

    if questions_data:
        st.markdown(
            """
            <div class='glass-card' style='margin-bottom: 25px;'>
                <p style='color: #ccc; font-size: 0.9rem; line-height: 1.5; margin: 0;'>
                    Use the tabs below to practice different types of questions. Take a moment to think of your own answer 
                    before expanding the dropdown to reveal the AI-suggested model solution.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 4. Create Tabs
        tab_tech, tab_coding, tab_hr, tab_scenario = st.tabs([
            "🛠️ Technical Questions", 
            "💻 Coding & Practical", 
            "👥 HR & Behavioral", 
            "💡 Scenario-Based"
        ])

        # Helper function to render questions inside a tab
        def render_questions(q_list, color_prefix):
            if not q_list:
                st.info("No questions generated for this section.")
                return
            
            for idx, item in enumerate(q_list):
                q_text = item.get("question", "Question")
                ans_text = item.get("answer", "Answer")
                
                st.markdown(
                    f"""
                    <div style='margin-top: 15px; margin-bottom: 10px;'>
                        <strong style='color: {color_prefix}; font-size: 1.05rem;'>Q{idx + 1}: {q_text}</strong>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                with st.expander("🔑 Reveal Suggested Answer"):
                    st.markdown(
                        f"""
                        <div style='background: rgba(255,255,255,0.02); border-left: 3px solid {color_prefix}; padding: 12px 16px; border-radius: 4px; font-size: 0.9rem; color: #ddd; line-height: 1.6; white-space: pre-wrap;'>
{ans_text}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                st.divider()

        # Render each tab
        with tab_tech:
            render_questions(questions_data.get("technical", []), "#646cff")
            
        with tab_coding:
            render_questions(questions_data.get("coding", []), "#e056fd")
            
        with tab_hr:
            render_questions(questions_data.get("hr", []), "#2ecc71")
            
        with tab_scenario:
            render_questions(questions_data.get("scenario", []), "#3498db")
    else:
        st.warning("Interview questions could not be displayed. Try running the analysis again.")
