import re
from backend.role_database import CAREER_DATABASE

def normalize_skill(skill):
    """
    Normalize skill string for robust comparison (lowercase, remove special chars/spaces).
    """
    skill = skill.lower().strip()
    skill = re.sub(r'[^a-z0-9\s\+#\-\.]', '', skill)
    # Map common synonyms
    synonyms = {
        "ml": "machine learning",
        "dl": "deep learning",
        "nlp": "natural language processing",
        "cv": "computer vision",
        "dbms": "database management systems",
        "js": "javascript",
        "ts": "typescript",
        "aws": "amazon web services",
        "gcp": "google cloud platform",
        "oop": "object-oriented programming",
        "ci cd": "ci/cd",
        "cicd": "ci/cd",
        "qa": "quality assurance",
        "devops": "development operations"
    }
    return synonyms.get(skill, skill)

def calculate_readiness_score(matched_count, total_required):
    """
    Calculate readiness score as a percentage.
    """
    if total_required == 0:
        return 0
    score = (matched_count / total_required) * 100
    return min(100, round(score, 1))

def get_performance_level(score):
    """
    Classify score:
    0-40 Beginner
    41-70 Intermediate
    71-90 Job Ready
    91-100 Industry Ready
    """
    if score <= 40:
        return "Beginner"
    elif score <= 70:
        return "Intermediate"
    elif score <= 90:
        return "Job Ready"
    else:
        return "Industry Ready"

def analyze_gaps(resume_skills, target_role):
    """
    Compares resume skills vs target role skills.
    Returns: matched, missing, additional recommended skills, and readiness score metrics.
    """
    role_data = CAREER_DATABASE.get(target_role)
    if not role_data:
        raise ValueError(f"Role '{target_role}' not found in database.")
    
    required_skills = role_data["required_skills"]
    
    # Normalize inputs
    norm_resume_skills = {normalize_skill(s) for s in resume_skills}
    
    matched_skills = []
    missing_skills = []
    
    for req_skill in required_skills:
        norm_req = normalize_skill(req_skill)
        
        # Check for substring match (e.g. "python" in "python programming")
        is_matched = False
        for norm_res in norm_resume_skills:
            if norm_req in norm_res or norm_res in norm_req:
                is_matched = True
                break
        
        if is_matched:
            matched_skills.append(req_skill)
        else:
            missing_skills.append(req_skill)
            
    # Calculate Readiness Score
    readiness_score = calculate_readiness_score(len(matched_skills), len(required_skills))
    performance_level = get_performance_level(readiness_score)
    
    # Generate Additional Recommended Skills
    # These are adjacent skills that the student has *not* matched, but could be useful.
    # We can pull some from related roles in our database, or define a small set of general tools/soft skills.
    all_database_skills = []
    for r, data in CAREER_DATABASE.items():
        if r != target_role:
            all_database_skills.extend(data["required_skills"])
            
    # Remove duplicates while preserving order
    seen = set()
    adjacent_skills = [x for x in all_database_skills if not (x in seen or seen.add(x))]
    
    # Find up to 4 recommended skills that are not in the required skills and not in the resume
    additional_recommended = []
    for skill in adjacent_skills:
        norm_skill = normalize_skill(skill)
        if (skill not in required_skills) and (norm_skill not in norm_resume_skills):
            additional_recommended.append(skill)
            if len(additional_recommended) >= 4:
                break
                
    # Fallback/Default additional recommended if list is short
    general_additions = ["Docker", "Git", "REST APIs", "System Design", "Agile Methodologies", "Communication"]
    for skill in general_additions:
        if len(additional_recommended) >= 5:
            break
        norm_skill = normalize_skill(skill)
        if (skill not in required_skills) and (skill not in matched_skills) and (norm_skill not in norm_resume_skills) and (skill not in additional_recommended):
            additional_recommended.append(skill)

    return {
        "target_role": target_role,
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "additional_recommended_skills": additional_recommended,
        "readiness_score": readiness_score,
        "performance_level": performance_level
    }
