import streamlit as st
from home_page import render_home


pages = [
    st.Page(render_home, title="Home", icon="🏠"),
    st.Page("pages/coach.py", title="Career Guide", icon="🧠"),
    st.Page("pages/dashboard.py", title="Placement Dashboard", icon="📊"),
    st.Page("pages/export_report.py", title="Export Report", icon="📄"),
    st.Page("pages/faq.py", title="Career FAQ", icon="❓"),
    st.Page("pages/interview.py", title="Interview", icon="🎤"),
    st.Page("pages/projects.py", title="Project & Prep", icon="💼"),
    st.Page("pages/resume_analysis.py", title="Resume Analysis", icon="📝"),
    st.Page("pages/roadmap.py", title="Career Roadmap", icon="📅"),
    st.Page("pages/skill_gap.py", title="Skill Gap Analysis", icon="🔍"),
]

st.navigation(pages, position="hidden").run()
