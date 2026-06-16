import streamlit as st
import io
from backend.ui_components import init_page, check_analysis_guard

# ReportLab imports for generating structured PDF reports
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# 1. Initialize page configuration and sidebar
init_page("Export Report")

def build_pdf(resume_details, gap_results, roadmap, projects, interview):
    """
    Generates a professional PDF report using ReportLab in an in-memory buffer.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=40, 
        leftMargin=40, 
        topMargin=40, 
        bottomMargin=40
    )
    
    story = []
    
    # ----------------------------------------------------
    # Styles Configuration
    # ----------------------------------------------------
    styles = getSampleStyleSheet()
    
    # Custom colors matching SkillSync theme
    c_primary = colors.HexColor("#646cff") # Blue/Indigo
    c_secondary = colors.HexColor("#e056fd") # Magenta/Purple
    c_dark = colors.HexColor("#1e1e24") # Dark Background
    c_text = colors.HexColor("#2c3e50") # Deep charcoal
    c_gray = colors.HexColor("#7f8c8d")
    
    # Modify normal body text
    styles['Normal'].textColor = c_text
    styles['Normal'].fontSize = 10
    styles['Normal'].leading = 14
    
    # Custom paragraph styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=c_primary,
        alignment=0, # Left aligned
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_gray,
        spaceAfter=20
    )
    
    h1_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=c_primary,
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'SubSectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    
    meta_label_style = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.white
    )
    
    meta_val_style = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.white
    )
    
    # ----------------------------------------------------
    # Document Header
    # ----------------------------------------------------
    story.append(Paragraph("SkillSync AI - Career Readiness Report", title_style))
    story.append(Paragraph("Know Your Gaps. Build Your Future.", subtitle_style))
    story.append(Spacer(1, 10))
    
    # ----------------------------------------------------
    # Student Metadata Banner Table
    # ----------------------------------------------------
    meta_data = [
        [
            Paragraph("Candidate Name:", meta_label_style),
            Paragraph(resume_details.get("name", "Student Candidate"), meta_val_style),
            Paragraph("Target Role:", meta_label_style),
            Paragraph(gap_results.get("target_role"), meta_val_style)
        ],
        [
            Paragraph("Email Address:", meta_label_style),
            Paragraph(resume_details.get("email", "N/A"), meta_val_style),
            Paragraph("Readiness Score:", meta_label_style),
            Paragraph(f"<b>{gap_results.get('readiness_score')}%</b> ({gap_results.get('performance_level')})", meta_val_style)
        ]
    ]
    
    meta_table = Table(meta_data, colWidths=[110, 160, 110, 150])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_primary),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#858cff")),
        ('BOX', (0, 0), (-1, -1), 1, c_primary)
    ]))
    
    story.append(meta_table)
    story.append(Spacer(1, 25))
    
    # ----------------------------------------------------
    # Section 1: Skill Gap Analysis Table
    # ----------------------------------------------------
    story.append(Paragraph("1. Detailed Skill Gap Breakdown", h1_style))
    
    # Formulate Matched and Missing skills list
    matched_skills = gap_results.get("matched_skills", [])
    missing_skills = gap_results.get("missing_skills", [])
    recommended_skills = gap_results.get("additional_recommended_skills", [])
    
    # Wrap text for table paragraphs
    p_matched = Paragraph(", ".join(matched_skills) if matched_skills else "None", styles['Normal'])
    p_missing = Paragraph(", ".join(missing_skills) if missing_skills else "None", styles['Normal'])
    p_recommended = Paragraph(", ".join(recommended_skills) if recommended_skills else "None", styles['Normal'])
    
    gap_table_data = [
        [Paragraph("<b>Status</b>", styles['Normal']), Paragraph("<b>Skill List</b>", styles['Normal'])],
        [Paragraph("<font color='green'><b>Matched Skills</b></font>", styles['Normal']), p_matched],
        [Paragraph("<font color='red'><b>Missing Skills</b></font>", styles['Normal']), p_missing],
        [Paragraph("<font color='blue'><b>Recommended</b></font>", styles['Normal']), p_recommended]
    ]
    
    gap_table = Table(gap_table_data, colWidths=[120, 410])
    gap_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f8f9fa")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10)
    ]))
    
    story.append(gap_table)
    story.append(Spacer(1, 20))
    
    # Page break for timeline clarity
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # Section 2: 3-Month Study Roadmap
    # ----------------------------------------------------
    story.append(Paragraph("2. 12-Week Interactive Learning Roadmap", h1_style))
    
    if roadmap and "roadmap" in roadmap:
        weeks = roadmap["roadmap"]
        for week_item in weeks:
            w_num = week_item.get("week")
            skills_to_learn = ", ".join(week_item.get("skills_to_learn", []))
            mini_goals = week_item.get("mini_goals")
            practice = week_item.get("practice_exercises")
            
            story.append(Paragraph(f"<b>Week {w_num}: {skills_to_learn}</b>", h2_style))
            
            # Format text bullets
            w_details = f"• <b>Goal:</b> {mini_goals}<br/>• <b>Practice Exercise:</b> {practice}"
            story.append(Paragraph(w_details, styles['Normal']))
            story.append(Spacer(1, 8))
    else:
        story.append(Paragraph("Learning Roadmap details not available.", styles['Normal']))
        
    story.append(Spacer(1, 15))
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # Section 3: Recommended Projects & Certifications
    # ----------------------------------------------------
    story.append(Paragraph("3. Recommended Portfolio Builders", h1_style))
    
    # Projects
    story.append(Paragraph("Project Recommendations", h2_style))
    if projects and "projects" in projects:
        projs = projects["projects"]
        for p in projs:
            p_title = p.get("title")
            p_diff = p.get("difficulty")
            p_desc = p.get("description")
            p_tech = ", ".join(p.get("technologies_required", []))
            p_time = p.get("estimated_time", "N/A")
            
            p_text = f"<b>{p_title} ({p_diff})</b><br/>{p_desc}<br/><i>Required Technologies: {p_tech} | Duration: {p_time}</i>"
            story.append(Paragraph(p_text, styles['Normal']))
            story.append(Spacer(1, 12))
    else:
        story.append(Paragraph("Project ideas not available.", styles['Normal']))
        
    # Certifications
    story.append(Paragraph("Certification Matches", h2_style))
    if st.session_state["certifications"] and "certifications" in st.session_state["certifications"]:
        certs = st.session_state["certifications"]["certifications"]
        cert_text = ""
        for c in certs:
            cert_text += f"• <b>{c.get('name')}</b> ({c.get('platform')}) - Matches skill: <i>{c.get('target_skill')}</i> (Duration: {c.get('duration')})<br/>"
        story.append(Paragraph(cert_text, styles['Normal']))
    else:
        story.append(Paragraph("Certification recommendations not available.", styles['Normal']))
        
    story.append(Spacer(1, 15))
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # Section 4: Interview Preparation Questions
    # ----------------------------------------------------
    story.append(Paragraph("4. Targeted Interview Preparation Sheet", h1_style))
    
    if interview:
        # Technical
        story.append(Paragraph("Core Technical Questions", h2_style))
        for idx, item in enumerate(interview.get("technical", [])):
            story.append(Paragraph(f"<b>Q{idx + 1}: {item.get('question')}</b>", styles['Normal']))
            story.append(Paragraph(f"<i>Suggested Answer:</i> {item.get('answer')}", styles['Normal']))
            story.append(Spacer(1, 10))
            
        # Coding
        story.append(Paragraph("Coding & Practical Challenges", h2_style))
        for idx, item in enumerate(interview.get("coding", [])):
            story.append(Paragraph(f"<b>Q{idx + 1}: {item.get('question')}</b>", styles['Normal']))
            story.append(Paragraph(f"<i>Approach/Solution:</i><br/>{item.get('answer')}", styles['Normal']))
            story.append(Spacer(1, 10))
            
        # Scenarios
        story.append(Paragraph("Scenario & Problem-Solving Cases", h2_style))
        for idx, item in enumerate(interview.get("scenario", [])):
            story.append(Paragraph(f"<b>Q{idx + 1}: {item.get('question')}</b>", styles['Normal']))
            story.append(Paragraph(f"<i>Resolution Plan:</i> {item.get('answer')}", styles['Normal']))
            story.append(Spacer(1, 10))
    else:
        story.append(Paragraph("Interview preparation sheet not available.", styles['Normal']))
        
    # Build PDF Doc
    doc.build(story)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

# 3. Guard check
if not check_analysis_guard():
    # Load all generated profile data from states
    details = st.session_state["resume_details"]
    gap_results = st.session_state["analysis_results"]
    
    # For sub-objects (roadmap, projects, interviews), make sure they exist, otherwise generate them through Groq
    roadmap = st.session_state["roadmap"]
    projects = st.session_state["projects"]
    interview = st.session_state["interview_questions"]

    st.markdown("## 📥 Export Readiness Report")
    st.markdown("<p style='color: #aaa; margin-top: -15px;'>Generate and download a professional PDF report containing your roadmap, skills analysis, project matches, and interview questions.</p>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div class='glass-card' style='margin-bottom: 30px;'>
            <h4 style='color: #646cff;'>📄 Export Instructions</h4>
            <p style='color: #ccc; font-size: 0.9rem; line-height: 1.5;'>
                Clicking the button below compiles all analyses generated during this session into a multi-page,
                printable PDF document. This is ideal for placement tracking, academic review, or sharing with mentors.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # We want to make sure all elements are generated before building the PDF
    # Check if lazy loaded items exist. If they do not, trigger their generation on PDF build so the PDF contains complete details!
    if roadmap is None or projects is None or interview is None:
        st.info("ℹ️ Some report sections are being finalized. Generating complete dataset...")
        
        # We can dynamically trigger calls in background if not already cached
        from backend.groq_service import generate_roadmap, generate_projects, generate_interview_questions, recommend_certifications
        role = gap_results.get("target_role")
        missing = gap_results.get("missing_skills", [])
        
        with st.spinner("Generating and compiling career roadmap, portfolio projects, and interview questions..."):
            try:
                if roadmap is None:
                    roadmap = generate_roadmap(details, missing, role)
                    st.session_state["roadmap"] = roadmap
                if projects is None:
                    projects = generate_projects(missing, role)
                    st.session_state["projects"] = projects
                if st.session_state["certifications"] is None:
                    st.session_state["certifications"] = recommend_certifications(missing, role)
                if interview is None:
                    interview = generate_interview_questions(role, details, missing)
                    st.session_state["interview_questions"] = interview
                st.success("✅ Dataset compiled successfully!")
            except Exception as e:
                st.error(f"Error during compilation: {str(e)}")

    # Proceed to build PDF
    if roadmap and projects and interview:
        try:
            pdf_data = build_pdf(details, gap_results, roadmap, projects, interview)
            
            # Draw Center aligned download button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("<br/>", unsafe_allow_html=True)
                st.download_button(
                    label="📥 Download PDF Readiness Report",
                    data=pdf_data,
                    file_name=f"SkillSync_AI_{gap_results.get('target_role').replace(' ', '_')}_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary"
                )
                st.markdown("<br/>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Failed to build PDF document: {str(e)}")
    else:
        st.warning("Please ensure all analysis pages have loaded completely before exporting.")
