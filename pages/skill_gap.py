import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from backend.ui_components import init_page, check_analysis_guard
from backend.role_database import CAREER_DATABASE

# 1. Initialize page configuration and sidebar
init_page("Skill Gap Analysis")

# 2. Guard to ensure analysis is ready
if not check_analysis_guard():
    res = st.session_state["analysis_results"]
    role = res.get("target_role")
    matched = res.get("matched_skills", [])
    missing = res.get("missing_skills", [])
    recommended = res.get("additional_recommended_skills", [])
    required_skills = res.get("required_skills", [])
    readiness = res.get("readiness_score", 0)
    level = res.get("performance_level", "Beginner")

    if not required_skills and role in CAREER_DATABASE:
        required_skills = CAREER_DATABASE[role].get("required_skills", [])

    st.markdown("## 🔍 Skill Gap Analysis")
    st.markdown(f"<p style='color: #aaa; margin-top: -15px;'>Analyzing gaps for <strong>{role}</strong></p>", unsafe_allow_html=True)

    # 3. Detailed Skill Cards at the top
    st.markdown("### 🛠️ Detailed Skill Gap Breakdown")

    matched_html = "".join([f"<span class='custom-badge badge-matched'>{skill}</span>" for skill in matched])
    st.markdown(
        f"""
        <div class='glass-card'>
            <h4 style='color: #2ecc71; margin-bottom: 15px;'>✅ Matched Skills ({len(matched)})</h4>
            <p style='color: #aaa; font-size: 0.85rem; margin-top: -10px; margin-bottom: 15px;'>These skills are present on your resume and match the target role requirements.</p>
            {matched_html if matched_html else "<p style='color: #888; font-style: italic;'>No skills matched yet. Boost your portfolio!</p>"}
        </div>
        """,
        unsafe_allow_html=True
    )

    missing_html = "".join([f"<span class='custom-badge badge-missing'>{skill}</span>" for skill in missing])
    st.markdown(
        f"""
        <div class='glass-card'>
            <h4 style='color: #e74c3c; margin-bottom: 15px;'>⚠️ Missing Skills ({len(missing)})</h4>
            <p style='color: #aaa; font-size: 0.85rem; margin-top: -10px; margin-bottom: 15px;'>These skills are required for the target role but were not detected on your resume.</p>
            {missing_html if missing_html else "<p style='color: #2ecc71; font-style: italic;'>Excellent! You have matched all required core skills.</p>"}
        </div>
        """,
        unsafe_allow_html=True
    )

    recommended_html = "".join([f"<span class='custom-badge badge-recommended'>{skill}</span>" for skill in recommended])
    st.markdown(
        f"""
        <div class='glass-card'>
            <h4 style='color: #3498db; margin-bottom: 15px;'>💡 Additional Recommended Skills</h4>
            <p style='color: #aaa; font-size: 0.85rem; margin-top: -10px; margin-bottom: 15px;'>These are industry-adjacent skills that will give you a competitive edge in your career.</p>
            {recommended_html}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    # 4. Overview row
    col_score, col_progress = st.columns([1, 2])
    
    with col_score:
        st.markdown(
            f"""
            <div class='glass-card' style='text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center;'>
                <p class='metric-label'>Readiness Level</p>
                <div class='metric-value'>{readiness}%</div>
                <p style='font-weight: 700; color: #e056fd; font-size: 1.25rem; margin-top: 5px; margin-bottom: 0px;'>{level}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col_progress:
        st.markdown(
            f"""
            <div class='glass-card' style='height: 100%;'>
                <h4 style='margin-top: 0px; margin-bottom: 15px;'>📈 Core Skills Match Progress</h4>
                <div style='background-color: rgba(255, 255, 255, 0.08); border-radius: 10px; height: 16px; width: 100%; overflow: hidden; margin-bottom: 10px;'>
                    <div style='background: linear-gradient(90deg, #646cff, #e056fd); height: 100%; width: {readiness}%;'></div>
                </div>
                <div style='display: flex; justify-content: space-between; margin-top: 25px;'>
                    <div>
                        <span style='color: #2ecc71; font-weight: 700; font-size: 1.5rem;'>{len(matched)}</span>
                        <p style='color: #888; font-size: 0.8rem; margin: 0;'>MATCHED SKILLS</p>
                    </div>
                    <div>
                        <span style='color: #e74c3c; font-weight: 700; font-size: 1.5rem;'>{len(missing)}</span>
                        <p style='color: #888; font-size: 0.8rem; margin: 0;'>MISSING SKILLS</p>
                    </div>
                    <div>
                        <span style='color: #3498db; font-weight: 700; font-size: 1.5rem;'>{len(matched) + len(missing)}</span>
                        <p style='color: #888; font-size: 0.8rem; margin: 0;'>TOTAL REQUIRED</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 5. Market Demand Analysis
    st.markdown("### 📈 Market Demand Analysis ")
    st.markdown(
        "<p style='color: #aaa; margin-top: -10px; margin-bottom: 18px;'>"
        "Shows how frequently each skill appears across job requirements in the role database."
        "</p>",
        unsafe_allow_html=True
    )

    all_roles = list(CAREER_DATABASE.items())
    total_roles = len(all_roles) if all_roles else 1

    def skill_coverage(skill_name: str) -> tuple[float, int]:
        skill_norm = skill_name.lower().strip()
        hit_count = 0
        for _, role_data in all_roles:
            role_skills = {s.lower().strip() for s in role_data["required_skills"]}
            if any(skill_norm == s or skill_norm in s or s in skill_norm for s in role_skills):
                hit_count += 1
        return round((hit_count / total_roles) * 100, 1), hit_count

    demand_rows = []
    for skill in required_skills:
        demand_pct, demand_count = skill_coverage(skill)
        demand_rows.append((skill, demand_pct, demand_count))

    demand_rows.sort(key=lambda x: x[1], reverse=True)
    demand_skills = [x[0] for x in demand_rows]
    demand_values = [x[1] for x in demand_rows]
    demand_hits = [x[2] for x in demand_rows]

    demand_colors = []
    for val in demand_values:
        if val >= 80:
            demand_colors.append("#2ecc71")
        elif val >= 60:
            demand_colors.append("#f39c12")
        else:
            demand_colors.append("#e74c3c")

    fig_demand = go.Figure(go.Bar(
        x=demand_values,
        y=demand_skills,
        orientation='h',
        marker=dict(color=demand_colors),
        text=[f"{val}%" for val in demand_values],
        textposition='outside',
        customdata=[f"{hits}/{total_roles} roles" for hits in demand_hits],
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Market demand: %{x:.0f}%<br>"
            "Appears in %{customdata}<extra></extra>"
        )
    ))

    fig_demand.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff', family='Inter'),
        xaxis=dict(title="Job Requirement Coverage (%)", range=[0, 110], gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(showgrid=False, autorange="reversed"),
        height=max(320, 28 * len(demand_skills) + 110),
        margin=dict(t=40, b=30, l=160, r=30)
    )

    st.plotly_chart(fig_demand, use_container_width=True)

    st.markdown("---")

    # 6. Skill Priority Matrix
    st.markdown("### Skill Priority Matrix")
    st.markdown(
        "<p style='color: #aaa; margin-top: -10px; margin-bottom: 18px;'>"
        "Ranks missing skills by importance, difficulty, and priority so you know what to tackle first."
        "</p>",
        unsafe_allow_html=True
    )

    def classify_importance(skill_name: str, demand_pct: float) -> str:
        skill_norm = skill_name.lower()
        high_keywords = [
            "git", "docker", "kubernetes", "system design", "sql", "python",
            "java", "algorithms", "data structures", "linux", "aws", "react",
            "javascript", "cloud"
        ]
        if demand_pct >= 70 or any(keyword in skill_norm for keyword in high_keywords):
            return "High"
        return "Medium"

    def classify_difficulty(skill_name: str) -> str:
        skill_norm = skill_name.lower()
        if any(keyword in skill_norm for keyword in ["git", "sql", "excel", "html", "css", "python"]):
            return "Easy"
        if any(keyword in skill_norm for keyword in ["docker", "aws", "linux", "react", "node", "pandas", "tableau", "power bi"]):
            return "Medium"
        return "Hard"

    def classify_priority(importance: str, difficulty: str) -> str:
        if importance == "High" and difficulty in ("Easy", "Medium"):
            return " High"
        if importance == "High" and difficulty == "Hard":
            return " Medium"
        if importance == "Medium" and difficulty == "Easy":
            return " Medium"
        return " Medium"

    priority_rows = []
    for skill in missing:
        demand_pct, _ = skill_coverage(skill)
        importance = classify_importance(skill, demand_pct)
        difficulty = classify_difficulty(skill)
        priority = classify_priority(importance, difficulty)
        priority_rows.append((skill, importance, difficulty, priority, demand_pct))

    priority_rows.sort(key=lambda row: (0 if row[3] == " High" else 1, -row[4], row[0]))

    st.markdown(
        """
        <div class='glass-card' style='padding: 0; overflow: hidden;'>
            <div style='padding: 20px 22px 10px 22px;'>
                <h4 style='margin: 0; color: #ffffff; font-size: 1.05rem;'>Skill Priority Matrix</h4>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if priority_rows:
        priority_df = pd.DataFrame(
            priority_rows,
            columns=["Skill", "Importance", "Difficulty", "Priority", "Demand %"]
        )[["Skill", "Importance", "Difficulty", "Priority"]]
        st.table(priority_df)
    else:
        st.info("No missing skills detected. Great job!")

    st.markdown("---")

    # 7. Salary Projection
    st.markdown("### 💼 Salary Projection")

    if readiness < 40:
        entry_package = "₹3-5 LPA"
        roadmap_package = "₹6-8 LPA"
    elif readiness < 70:
        entry_package = "₹4-6 LPA"
        roadmap_package = "₹8-10 LPA"
    else:
        entry_package = "₹6-8 LPA"
        roadmap_package = "₹10-14 LPA"

    st.markdown(
        f"""
        <div class='glass-card' style='border: 1px solid rgba(100, 108, 255, 0.25); background: linear-gradient(135deg, rgba(100,108,255,0.10), rgba(224,86,253,0.08));'>
            <div style='display: flex; justify-content: space-between; align-items: flex-start; gap: 18px; flex-wrap: wrap;'>
                <div style='flex: 1; min-width: 220px;'>
                    <p style='margin: 0; color: #aaa; text-transform: uppercase; letter-spacing: 1.5px; font-size: 0.75rem; font-weight: 700;'>Current Readiness</p>
                    <div style='font-family: "Outfit", sans-serif; font-size: 3rem; font-weight: 800; color: #ffffff; line-height: 1; margin: 10px 0 14px 0;'>{readiness}%</div>
                    <div style='background: rgba(255,255,255,0.08); border-radius: 999px; height: 12px; overflow: hidden;'>
                        <div style='width: {readiness}%; height: 100%; border-radius: 999px; background: linear-gradient(90deg, #646cff, #e056fd);'></div>
                    </div>
                    <p style='margin: 12px 0 0 0; color: #ccc; font-size: 0.92rem;'>Estimated market value based on your current readiness and role fit.</p>
                </div>
                <div style='display: grid; gap: 12px; min-width: 240px; flex: 1;'>
                    <div style='background: rgba(0,0,0,0.18); border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 14px 16px;'>
                        <p style='margin: 0 0 6px 0; color: #aaa; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;'>Expected Entry Package</p>
                        <div style='font-family: "Outfit", sans-serif; font-size: 1.7rem; font-weight: 800; color: #2ecc71;'>{entry_package}</div>
                    </div>
                    <div style='background: rgba(0,0,0,0.18); border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 14px 16px;'>
                        <p style='margin: 0 0 6px 0; color: #aaa; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;'>After Completing Roadmap</p>
                        <div style='font-family: "Outfit", sans-serif; font-size: 1.7rem; font-weight: 800; color: #e056fd;'>{roadmap_package}</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
