import streamlit as st
from backend.ui_components import init_page, check_analysis_guard
from backend.groq_service import generate_roadmap

# 1. Initialize page configuration and sidebar
init_page("Career Roadmap")

# 2. Guard to ensure analysis is ready
if not check_analysis_guard():
    res = st.session_state["analysis_results"]
    role = res.get("target_role")
    missing = res.get("missing_skills", [])
    details = st.session_state["resume_details"]

    st.markdown("## 📅 3-Month AI Learning Roadmap")
    st.markdown(f"<p style='color: #aaa; margin-top: -15px;'>A customized week-by-week study plan to master your missing skills for the <strong>{role}</strong> position.</p>", unsafe_allow_html=True)

    # 3. Check cache or generate roadmap
    if st.session_state["roadmap"] is None:
        with st.spinner("Analyzing skill gaps and generating your customized 12-week roadmap..."):
            try:
                # Call Groq Service
                roadmap_data = generate_roadmap(details, missing, role)
                st.session_state["roadmap"] = roadmap_data
            except Exception as e:
                st.error(f"Failed to generate roadmap: {str(e)}")
                
    roadmap_data = st.session_state["roadmap"]

    if roadmap_data and "roadmap" in roadmap_data:
        weeks = roadmap_data["roadmap"]
        
        # Display Roadmap summary
        st.markdown(
            f"""
            <div class='glass-card' style='margin-bottom: 30px;'>
                <h4 style='color: #646cff;'>📈 Timeline Overview</h4>
                <p style='color: #ccc; font-size: 0.9rem; line-height: 1.5;'>
                    This roadmap spans 12 weeks, broken down into study phases. 
                    Weeks 1–4 focus on foundational concepts, Weeks 5–8 cover intermediate applications, 
                    and Weeks 9–12 culminate in advanced implementation and deployment strategies.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Render the custom HTML timeline in chunks of 6 weeks
        timeline_html = ""
        
        chunk_size = 6
        for i in range(0, len(weeks), chunk_size):
            chunk = weeks[i:i + chunk_size]
            level_num = (i // chunk_size) + 1
            
            timeline_html += f"<h3 style='margin-top: 40px; color: #e056fd;'>Level {level_num}</h3>"
            timeline_html += "<div class='horizontal-timeline-wrapper'><div class='horizontal-timeline'>"
            
            for idx, week_item in enumerate(chunk):
                # Alternating timeline sides (even index is bottom, odd index is top for the curve)
                position_class = "position-bottom" if idx % 2 == 0 else "position-top"
                
                week_num = week_item.get("week", i + idx + 1)
                skills = ", ".join(week_item.get("skills_to_learn", []))
                
                # Formulate resources HTML list
                res_list = week_item.get("resources", [])
                resources_html = ""
                for r in res_list:
                    resources_html += f"<li>{r.get('name')} ({r.get('url')})</li>"
                
                timeline_html += f"""<div class='timeline-item {position_class}'>
<div class='timeline-dot'></div>
<div class='timeline-content'>
<div class='timeline-week'>Week {week_num}</div>
<div class='timeline-title'>📚 Focus: {skills}</div>
<div class='timeline-details'>
<strong>🎯 Mini-Goal:</strong> {week_item.get('mini_goals')}<br/>
<strong style='display:inline-block; margin-top:8px;'>💻 Practice:</strong> {week_item.get('practice_exercises')}<br/>
<strong style='display:inline-block; margin-top:8px;'>📖 Resources:</strong>
<ul style='margin: 4px 0 0 0; padding-left: 20px; font-size: 0.85rem; color: #aaa;'>
{resources_html}
</ul>
</div>
</div>
</div>
"""
                
            timeline_html += "</div></div>"
        
        # Inject the timeline HTML
        st.markdown(timeline_html, unsafe_allow_html=True)
    else:
        st.warning("Roadmap content could not be displayed. Try running the analysis again.")
