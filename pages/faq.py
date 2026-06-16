import streamlit as st
from backend.ui_components import init_page, check_analysis_guard
from backend.groq_service import generate_faq

# Category icons and colors
CATEGORY_STYLES = {
    "Role Overview": {"icon": "🎯", "color": "#646cff"},
    "Learning Path": {"icon": "📚", "color": "#22c55e"},
    "Projects": {"icon": "💡", "color": "#f59e0b"},
    "Interview Prep": {"icon": "🧠", "color": "#e056fd"},
    "Career Tips": {"icon": "🚀", "color": "#06b6d4"},
}

def render_faq():
    analyzed = init_page("Career FAQ")
    if check_analysis_guard():
        return

    res = st.session_state.get("analysis_results", {})
    missing = res.get("missing_skills", [])
    target_role = st.session_state.get("target_role", "Software Engineer")

    # Header
    st.markdown(
        f"""
        <div style='text-align: center; margin-bottom: 30px;'>
            <h1 style='font-size: 2.2rem; margin-bottom: 5px;'>
                ❓ <span class='gradient-text'>Career FAQ</span>
            </h1>
            <p style='color: #aaa; font-size: 1.05rem;'>
                Personalized answers for your <strong style='color: #646cff;'>{target_role}</strong> preparation
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Lazy-load FAQ data
    if st.session_state.get("faq") is None:
        with st.spinner("🤖 AI is generating your personalized FAQ..."):
            st.session_state["faq"] = generate_faq(missing, target_role)

    faq_data = st.session_state["faq"]
    faqs = faq_data.get("faqs", [])

    if not faqs:
        st.warning("No FAQ data available. Please try re-running the analysis.")
        return

    # Group by category
    categories = {}
    for faq in faqs:
        cat = faq.get("category", "General")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(faq)

    # Render each category
    for cat_name, cat_faqs in categories.items():
        style = CATEGORY_STYLES.get(cat_name, {"icon": "📌", "color": "#888"})

        st.markdown(
            f"""
            <div style='margin-top: 30px; margin-bottom: 15px;'>
                <h3 style='color: {style["color"]}; font-size: 1.3rem; margin-bottom: 0;'>
                    {style["icon"]} {cat_name}
                </h3>
                <hr style='border: 1px solid {style["color"]}30; margin-top: 8px;'>
            </div>
            """,
            unsafe_allow_html=True
        )

        for faq in cat_faqs:
            with st.expander(f"**{faq['question']}**"):
                st.markdown(
                    f"""
                    <div style='
                        padding: 12px 16px;
                        background: rgba(255,255,255,0.03);
                        border-left: 3px solid {style["color"]};
                        border-radius: 0 8px 8px 0;
                        line-height: 1.7;
                        color: #ddd;
                        font-size: 0.95rem;
                    '>
                        {faq['answer']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


render_faq()
