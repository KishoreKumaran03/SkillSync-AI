import streamlit as st
from home_page import render_home


def build_pages():
    """Register the app pages in one place."""
    page_specs = [
        (render_home, "Home", "🏠"),
        ("pages/coach.py", "Career Guide", "🧠"),
        ("pages/dashboard.py", "Placement Dashboard", "📊"),
        ("pages/faq.py", "Career FAQ", "❓"),
        ("pages/projects.py", "Project & Prep", "💼"),
        ("pages/roadmap.py", "Career Roadmap", "📅"),
        ("pages/skill_gap.py", "Skill Gap Analysis", "🔍"),
    ]

    return [st.Page(page, title=title, icon=icon) for page, title, icon in page_specs]

st.navigation(build_pages(), position="hidden").run()
