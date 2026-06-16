import streamlit as st

from backend.groq_service import generate_coach_reply
from backend.role_database import CAREER_DATABASE
from backend.ui_components import init_page


def _ensure_chat_state():
    if "coach_messages" not in st.session_state:
        st.session_state["coach_messages"] = [
            {
                "role": "assistant",
                "content": (
                    "Hi, I'm your Career Guide. Ask me about a skill, a role, an interview, "
                    "or what to learn next. You can use this even without uploading a resume."
                ),
            }
        ]


def _suggested_prompts():
    return [
        "What should I focus on first to improve my readiness?",
        "How can I prepare for the skills I want to learn?",
        "Give me a short interview preparation plan for this role.",
    ]


def _get_reply(user_message):
    return generate_coach_reply(
        user_message,
        st.session_state["coach_messages"],
        st.session_state.get("resume_details", {}),
        st.session_state.get("analysis_results", {}),
        st.session_state.get("coach_role"),
    )


init_page("Career Guide")
_ensure_chat_state()

analyzed = st.session_state.get("analyzed", False)
analysis = st.session_state.get("analysis_results", {})
roles = list(CAREER_DATABASE.keys())
default_role = analysis.get("target_role") if analyzed else None
default_idx = roles.index(default_role) if default_role in roles else 0

st.markdown("## 🧠 Career Guide")
st.markdown(
    "<p style='color: #aaa; margin-top: -15px;'>Ask Groq for practical guidance on skills, preparation steps, interview practice, and what to learn next. You can use this with or without uploading a resume.</p>",
    unsafe_allow_html=True,
)

if analyzed and default_role:
    st.markdown(
        f"""
        <div class='glass-card' style='margin-bottom: 18px;'>
            <p style='color: #ccc; margin: 0; line-height: 1.6;'>
                Using your existing analysis for <strong>{default_role}</strong>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div class='glass-card' style='margin-bottom: 18px;'>
            <p style='color: #ccc; margin: 0; line-height: 1.6;'>
                No resume upload is required here. Pick a role, then ask about the skills you want to learn or the job you want to prepare for.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div style="margin-bottom: 8px; color: #ffffff; font-size: 0.98rem; font-weight: 600;">
        Choose a role to guide your questions
    </div>
    """,
    unsafe_allow_html=True,
)

col_role, col_clear = st.columns([3, 1], vertical_alignment="bottom")
with col_role:
    chosen_role = st.selectbox(
        "Guide role",
        roles,
        index=default_idx,
        key="coach_role_select",
        label_visibility="collapsed",
    )
    st.session_state["coach_role"] = chosen_role
with col_clear:
    if st.button("Clear Chat", use_container_width=True):
        st.session_state["coach_messages"] = [st.session_state["coach_messages"][0]]
        st.rerun()

st.markdown(
    f"""
    <div class='glass-card' style='text-align:center; padding: 14px 18px; margin-bottom: 16px;'>
        <p class='metric-label' style='margin-bottom: 6px;'>Focused Role</p>
        <div style='font-family: Outfit, sans-serif; font-size: 1.2rem; font-weight: 700; color: #ffffff;'>{chosen_role}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class='glass-card' style='margin-bottom: 18px;'>
        <p style='color: #ccc; margin: 0; line-height: 1.6;'>
            This guide uses Groq to explain the skill itself, the learning order, common mistakes, and a practical next step.
            If your resume is uploaded, it will also tailor the guidance to your current gaps.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

prompt_cols = st.columns(len(_suggested_prompts()))
for idx, prompt in enumerate(_suggested_prompts()):
    with prompt_cols[idx]:
        if st.button(prompt, use_container_width=True, key=f"coach_prompt_{idx}"):
            st.session_state["coach_messages"].append({"role": "user", "content": prompt})
            try:
                with st.spinner("Groq is preparing guidance..."):
                    reply = _get_reply(prompt)
                st.session_state["coach_messages"].append({"role": "assistant", "content": reply})
                st.rerun()
            except Exception as e:
                st.error(f"Groq could not generate guidance: {str(e)}")

st.markdown("---")

for message in st.session_state["coach_messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_message = st.chat_input("Ask about any skill, roadmap step, or interview concern...")
if user_message:
    st.session_state["coach_messages"].append({"role": "user", "content": user_message})
    with st.chat_message("user"):
        st.markdown(user_message)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Groq is crafting your guidance..."):
                reply = _get_reply(user_message)
            st.markdown(reply)
            st.session_state["coach_messages"].append({"role": "assistant", "content": reply})
        except Exception as e:
            st.error(f"Groq could not generate guidance: {str(e)}")
