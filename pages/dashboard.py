import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
from backend.ui_components import init_page, check_analysis_guard
from backend.role_database import CAREER_DATABASE
from backend.gap_engine import normalize_skill

# 1. Initialize page configuration and sidebar
init_page("Placement Dashboard")

# 2. Guard to ensure analysis is ready
if not check_analysis_guard():
    res = st.session_state["analysis_results"]
    role = res.get("target_role")
    matched = res.get("matched_skills", [])
    missing = res.get("missing_skills", [])
    recommended = res.get("additional_recommended_skills", [])
    readiness = res.get("readiness_score", 0)
    level = res.get("performance_level", "Beginner")
    details = st.session_state["resume_details"]

    st.markdown("## 📊 Placement Readiness Dashboard")
    st.markdown(f"<p style='color: #aaa; margin-top: -15px;'>Comprehensive placement metrics and career mapping for <strong>{details.get('name', 'Student')}</strong></p>", unsafe_allow_html=True)

    # 3. Top Row Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
            <div class='glass-card metric-card' style='height: 100%;'>
                <p class='metric-label'>Readiness Score</p>
                <div class='metric-value'>{readiness}%</div>
                <span style='background-color: rgba(100,108,255,0.1); color: #646cff; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;'>
                    {level}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class='glass-card metric-card' style='height: 100%;'>
                <p class='metric-label'>Matched Skills</p>
                <div class='metric-value' style='background: linear-gradient(90deg, #2ecc71, #27ae60); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                    {len(matched)}
                </div>
                <span style='color: #888; font-size: 0.75rem;'>Core skills covered</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""
            <div class='glass-card metric-card' style='height: 100%;'>
                <p class='metric-label'>Missing Skills</p>
                <div class='metric-value' style='background: linear-gradient(90deg, #e74c3c, #c0392b); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                    {len(missing)}
                </div>
                <span style='color: #888; font-size: 0.75rem;'>Gaps to bridge</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col4:
        total_projects = 3 if st.session_state["projects"] else 0
        st.markdown(
            f"""
            <div class='glass-card metric-card' style='height: 100%;'>
                <p class='metric-label'>Recommended Projects</p>
                <div class='metric-value' style='background: linear-gradient(90deg, #3498db, #2980b9); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                    3
                </div>
                <span style='color: #888; font-size: 0.75rem;'>Custom project ideas</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # 4. Interactive Charts Section
    col_chart1, col_chart2 = st.columns([1, 1])
    
    with col_chart1:
        # Calculate Resume Strength scores dynamically from resume details
        required_skills = res.get("required_skills", [])
        skills_score = round((len(matched) / len(required_skills)) * 100) if required_skills else 0

        # Projects score: count vs quality tiers
        projs = details.get("projects", [])
        if not projs:
            projects_score = 0
        elif len(projs) == 1:
            projects_score = 30
        elif len(projs) == 2:
            projects_score = 55
        elif len(projs) == 3:
            projects_score = 80
        else:
            projects_score = 100

        # Certifications score: count-based tiers
        certs = details.get("certifications", [])
        if not certs:
            certs_score = 0
        elif len(certs) == 1:
            certs_score = 40
        elif len(certs) == 2:
            certs_score = 70
        else:
            certs_score = 100

        # Experience score: internship/work history count-based tiers
        internships = details.get("internships", [])
        if not internships:
            experience_score = 0
        elif len(internships) == 1:
            experience_score = 20
        elif len(internships) == 2:
            experience_score = 50
        else:
            experience_score = 80

        overall_strength = round((skills_score + projects_score + certs_score + experience_score) / 4, 1)

        # SVG Circle Calculations
        # Radius 100 -> Circumference = 628.3
        dash_skills = 628.3
        offset_skills = dash_skills * (1 - skills_score / 100)
        
        # Radius 80 -> Circumference = 502.7
        dash_projects = 502.7
        offset_projects = dash_projects * (1 - projects_score / 100)
        
        # Radius 60 -> Circumference = 377.0
        dash_certs = 377.0
        offset_certs = dash_certs * (1 - certs_score / 100)
        
        # Radius 40 -> Circumference = 251.3
        dash_exp = 251.3
        offset_exp = dash_exp * (1 - experience_score / 100)

        components.html(
            f"""
            <div style="width: 100%; height: 100%; box-sizing: border-box; padding: 22px 24px; border-radius: 18px; background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.03)); border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.22); display: grid; grid-template-columns: 260px 1fr; gap: 22px; align-items: center; overflow: hidden;">
                <div style="display: flex; justify-content: center; align-items: center; position: relative; width: 100%; min-height: 220px;">
                    <svg width="188" height="188" viewBox="0 0 240 240" style="transform: rotate(-90deg);">
                        <defs>
                            <linearGradient id="grad-skills" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#646cff" />
                                <stop offset="100%" stop-color="#8f94ff" />
                            </linearGradient>
                            <linearGradient id="grad-projects" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#e056fd" />
                                <stop offset="100%" stop-color="#f5bbfd" />
                            </linearGradient>
                            <linearGradient id="grad-certs" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#00d2d3" />
                                <stop offset="100%" stop-color="#a8f6f6" />
                            </linearGradient>
                            <linearGradient id="grad-exp" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#ff7675" />
                                <stop offset="100%" stop-color="#ffb3b2" />
                            </linearGradient>
                        </defs>
                        <circle cx="120" cy="120" r="100" stroke="rgba(255, 255, 255, 0.03)" stroke-width="14" fill="none" />
                        <circle cx="120" cy="120" r="80" stroke="rgba(255, 255, 255, 0.03)" stroke-width="14" fill="none" />
                        <circle cx="120" cy="120" r="60" stroke="rgba(255, 255, 255, 0.03)" stroke-width="14" fill="none" />
                        <circle cx="120" cy="120" r="40" stroke="rgba(255, 255, 255, 0.03)" stroke-width="14" fill="none" />
                        <circle cx="120" cy="120" r="100" stroke="url(#grad-skills)" stroke-width="14" fill="none" stroke-dasharray="628.3" stroke-dashoffset="{offset_skills}" stroke-linecap="round" />
                        <circle cx="120" cy="120" r="80" stroke="url(#grad-projects)" stroke-width="14" fill="none" stroke-dasharray="502.7" stroke-dashoffset="{offset_projects}" stroke-linecap="round" />
                        <circle cx="120" cy="120" r="60" stroke="url(#grad-certs)" stroke-width="14" fill="none" stroke-dasharray="377.0" stroke-dashoffset="{offset_certs}" stroke-linecap="round" />
                        <circle cx="120" cy="120" r="40" stroke="url(#grad-exp)" stroke-width="14" fill="none" stroke-dasharray="251.3" stroke-dashoffset="{offset_exp}" stroke-linecap="round" />
                    </svg>
                    <div style="position: absolute; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;">
                        <span style="font-family: 'Outfit', sans-serif; font-size: 1.6rem; font-weight: 800; color: #ffffff; line-height: 1;">{overall_strength}%</span>
                        <span style="font-family: 'Inter', sans-serif; font-size: 0.65rem; color: #888; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; margin-top: 3px;">Strength</span>
                    </div>
                </div>
                <div style="display: flex; flex-direction: column; justify-content: center; min-width: 0; padding-right: 8px;">
                    <h3 style="margin: 0 0 18px 0; font-family: 'Outfit', sans-serif; font-size: 1.5rem; font-weight: 700; color: #ffffff; line-height: 1.15; letter-spacing: -0.02em;">Resume Strength Analysis</h3>
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 14px;">
                        <div style="width: 13px; height: 13px; border-radius: 50%; background: #646cff; flex: 0 0 13px; box-shadow: 0 0 10px rgba(100, 108, 255, 0.65);"></div>
                        <div style="flex: 1; font-size: 0.9rem; color: #cfcfcf; font-weight: 500;">Skills</div>
                        <div style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1rem; color: #ffffff; min-width: 42px; text-align: right;">{skills_score}%</div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 14px;">
                        <div style="width: 13px; height: 13px; border-radius: 50%; background: #e056fd; flex: 0 0 13px; box-shadow: 0 0 10px rgba(224, 86, 253, 0.65);"></div>
                        <div style="flex: 1; font-size: 0.9rem; color: #cfcfcf; font-weight: 500;">Projects</div>
                        <div style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1rem; color: #ffffff; min-width: 42px; text-align: right;">{projects_score}%</div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 14px;">
                        <div style="width: 13px; height: 13px; border-radius: 50%; background: #00d2d3; flex: 0 0 13px; box-shadow: 0 0 10px rgba(0, 210, 211, 0.65);"></div>
                        <div style="flex: 1; font-size: 0.9rem; color: #cfcfcf; font-weight: 500;">Certifications</div>
                        <div style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1rem; color: #ffffff; min-width: 42px; text-align: right;">{certs_score}%</div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div style="width: 13px; height: 13px; border-radius: 50%; background: #ff7675; flex: 0 0 13px; box-shadow: 0 0 10px rgba(255, 118, 117, 0.65);"></div>
                        <div style="flex: 1; font-size: 0.9rem; color: #cfcfcf; font-weight: 500;">Experience</div>
                        <div style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1rem; color: #ffffff; min-width: 42px; text-align: right;">{experience_score}%</div>
                    </div>
                </div>
            </div>
            """,
            height=305,
            scrolling=False,
        )

    with col_chart2:
        # B. Horizontal Bar Chart: Skill Categories Strength
        # Group candidate's skills into 5 arbitrary categories for the target role
        required_skills = res.get("required_skills", [])
        n = len(required_skills)
        if n >= 5:
            categories = [
                "Languages & Basics",
                "Domain Core",
                "Frameworks",
                "Advanced Concepts",
                "Tools & Versioning"
            ]
            
            # Skill-aware mapping keeps the Tools & Versioning bucket intentionally compact.
            cat_skills = {cat: [] for cat in categories}

            def pick_category(skill_name: str) -> str:
                skill_norm = normalize_skill(skill_name)

                tool_keywords = [
                    "git", "github", "version control", "docker", "kubernetes",
                    "jenkins", "ci/cd", "ci cd", "linux", "shell", "bash",
                    "command line", "terminal", "postman"
                ]
                advanced_keywords = [
                    "system design", "design patterns", "architecture", "scalability",
                    "algorithms", "data structures", "oop", "object oriented",
                    "multithreading", "concurrency", "distributed systems"
                ]
                framework_keywords = [
                    "react", "angular", "vue", "django", "flask", "fastapi",
                    "spring", "express", "node", "tensorflow", "pytorch"
                ]
                language_keywords = [
                    "python", "java", "c++", "c ", "javascript", "typescript",
                    "html", "css", "sql", "r language", "go", "golang"
                ]

                if any(k in skill_norm for k in tool_keywords):
                    return "Tools & Versioning"
                if any(k in skill_norm for k in advanced_keywords):
                    return "Advanced Concepts"
                if any(k in skill_norm for k in framework_keywords):
                    return "Frameworks"
                if any(k in skill_norm for k in language_keywords):
                    return "Languages & Basics"
                return "Domain Core"

            for skill in required_skills:
                cat_skills[pick_category(skill)].append(skill)

            # Keep the tools bucket compact by moving overflow into advanced concepts.
            max_tool_skills = 2
            if len(cat_skills["Tools & Versioning"]) > max_tool_skills:
                overflow_tools = cat_skills["Tools & Versioning"][max_tool_skills:]
                cat_skills["Tools & Versioning"] = cat_skills["Tools & Versioning"][:max_tool_skills]
                cat_skills["Advanced Concepts"].extend(overflow_tools)
                
            # Compute match rate in each
            r_values = []
            category_skills = []
            for cat in categories:
                cat_req = cat_skills[cat]
                cat_match = [s for s in cat_req if s in matched]
                rate = (len(cat_match) / len(cat_req) * 100) if cat_req else 0
                r_values.append(rate)
                category_skills.append("<br>".join(cat_req) if cat_req else "No skills mapped")
        else:
            categories = ["Programming", "System Design", "Databases", "Version Control", "Soft Skills"]
            r_values = [70, 50, 80, 90, 60] # Default placeholder if skills list is too small
            category_skills = [
                "Core programming syntax, variables, loops, and problem solving",
                "Architecture basics, scaling ideas, and design patterns",
                "SQL, data modeling, queries, and database fundamentals",
                "Git, GitHub, branching, and version control workflows",
                "Communication, teamwork, and collaboration basics"
            ]

        # Sort values so highest matches appear at the top
        sorted_cats = sorted(zip(categories, r_values), key=lambda x: x[1], reverse=False)
        sorted_categories = [x[0] for x in sorted_cats]
        sorted_r_values = [x[1] for x in sorted_cats]

        # Generate colors: red for poor, orange for warning, green for good
        colors_bar = []
        for val in sorted_r_values:
            if val < 40:
                colors_bar.append("#e74c3c") # Red
            elif val < 80:
                colors_bar.append("#f39c12") # Orange
            else:
                colors_bar.append("#2ecc71") # Green

        fig_bar = go.Figure(go.Bar(
            x=sorted_r_values,
            y=sorted_categories,
            orientation='h',
            marker=dict(color=colors_bar),
            text=[f"{round(val)}%" for val in sorted_r_values],
            textposition='outside',
            textfont=dict(color='#ffffff', size=11),
            customdata=[category_skills[categories.index(cat)] for cat in sorted_categories],
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Match Rate: %{x:.0f}%<br>"
                "Included Skills:<br>%{customdata}<extra></extra>"
            )
        ))

        fig_bar.update_layout(
            title=dict(text="Skills Strength by Category", font=dict(size=18, color="#ffffff"), x=0.5),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff', family='Inter'),
            xaxis=dict(title="Match Rate (%)", range=[0, 115], gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(showgrid=False),
            height=280,
            margin=dict(t=50, b=10, l=120, r=40)
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # 5. Alternative Careers Matching Matrix
    st.markdown("### 🎯 Alternative Careers Match Matrix")
    st.markdown("<p style='color: #aaa; margin-top: -15px;'>See how your existing skills align with other roles in our industry database.</p>", unsafe_allow_html=True)

    # Calculate matches for all roles
    candidate_all_skills = (
        details.get("technical_skills", []) + 
        details.get("programming_languages", []) + 
        details.get("tools", [])
    )
    norm_candidate_skills = {normalize_skill(s) for s in candidate_all_skills}
    
    role_scores = []
    
    for r_name, r_data in CAREER_DATABASE.items():
        req_s = r_data["required_skills"]
        match_count = 0
        for s in req_s:
            ns = normalize_skill(s)
            for cs in norm_candidate_skills:
                if ns in cs or cs in ns:
                    match_count += 1
                    break
        score = (match_count / len(req_s)) * 100
        role_scores.append((r_name, round(score, 1)))
        
    # Sort roles by score
    role_scores.sort(key=lambda x: x[1], reverse=False) # Reverse False because plotly horizontal bar charts render bottom-up
    
    roles_labels = [x[0] for x in role_scores]
    scores_vals = [x[1] for x in role_scores]
    
    # Highlight current target role in a different color
    colors_bar = []
    for rl in roles_labels:
        if rl == role:
            colors_bar.append("#e056fd") # Highlight target in Purple
        else:
            colors_bar.append("#646cff") # Others in Blue
            
    fig_career = go.Figure(go.Bar(
        x=scores_vals,
        y=roles_labels,
        orientation='h',
        marker_color=colors_bar,
        text=[f"{s}%" for s in scores_vals],
        textposition='inside',
        insidetextfont=dict(color='#ffffff')
    ))
    
    fig_career.update_layout(
        title="Career Compatibility Score Across Roles",
        title_x=0.5,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff', family='Inter'),
        xaxis=dict(title="Match Percentage (%)", range=[0, 100], gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        height=400,
        margin=dict(t=55, b=40, l=150, r=40)
    )
    
    st.plotly_chart(fig_career, use_container_width=True)
