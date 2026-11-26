"""
Content-Based Career, Stream & Course Recommender
=================================================
Designed specifically for real-world 10th & 12th pass-out students:
- For 10th pass-outs: recommends ideal Class 11-12 streams / diplomas AND
  long-term career directions.
- For 12th pass-outs / college freshmen: recommends job roles, degrees,
  skill-gap targets, certifications, and starter projects.
"""
from typing import Dict, List

CAREER_CATALOG = [
    {
        "title": "ML Engineer / AI Specialist",
        "stage_fit": ["12th", "college", "10th"],
        "rec_type": "career",
        "stream_hint": "Science (PCM) -> B.Tech CSE / B.Sc AI & Data Science",
        "summary": "Build smart systems that learn from data, predict outcomes, and power modern apps.",
        "weights": {"math": 0.30, "science": 0.15, "coding": 0.35, "analytical": 0.20, "creativity": 0.0, "communication": 0.0},
        "required_skills": {"Python": 85, "Mathematics & Statistics": 80, "Machine Learning": 75, "Data Handling": 75},
        "courses": [
            {"title": "Python & NumPy Foundations", "provider": "freeCodeCamp / Coursera", "duration": "4 weeks", "type": "Course"},
            {"title": "Supervised Machine Learning", "provider": "DeepLearning.AI", "duration": "3 weeks", "type": "Certification"},
            {"title": "Student Marks Predictor App", "provider": "Guided Project", "duration": "2 weeks", "type": "Project"},
        ],
    },
    {
        "title": "Data Analyst",
        "stage_fit": ["12th", "college", "10th"],
        "rec_type": "career",
        "stream_hint": "Science (PCM) / Commerce with Math -> B.Sc Data Science / BCA / BBA Analytics",
        "summary": "Turn numbers and spreadsheets into clear charts and decisions for businesses and hospitals.",
        "weights": {"math": 0.25, "science": 0.10, "coding": 0.20, "analytical": 0.30, "creativity": 0.0, "communication": 0.15},
        "required_skills": {"Excel & SQL": 80, "Python / Pandas": 70, "Data Visualization": 75, "Analytical Thinking": 80},
        "courses": [
            {"title": "Google Data Analytics Certificate", "provider": "Coursera", "duration": "6 weeks", "type": "Certification"},
            {"title": "SQL & Tableau Visual Dashboards", "provider": "Khan Academy / Kaggle", "duration": "3 weeks", "type": "Course"},
            {"title": "Board Exam Trend Dashboard", "provider": "Guided Project", "duration": "1 week", "type": "Project"},
        ],
    },
    {
        "title": "Full-Stack Web Developer",
        "stage_fit": ["12th", "college", "10th"],
        "rec_type": "career",
        "stream_hint": "PCM / Any Stream + Computer Science -> B.Tech / BCA / Polytechnic CS",
        "summary": "Design and build interactive websites, portals, and mobile-friendly web applications.",
        "weights": {"math": 0.15, "science": 0.05, "coding": 0.40, "analytical": 0.15, "creativity": 0.20, "communication": 0.05},
        "required_skills": {"HTML / CSS / JS": 85, "React & TypeScript": 75, "APIs & Databases": 75, "Problem Solving": 75},
        "courses": [
            {"title": "Modern Web Development (HTML, JS, React)", "provider": "The Odin Project", "duration": "6 weeks", "type": "Course"},
            {"title": "Meta Front-End Developer", "provider": "Coursera", "duration": "5 weeks", "type": "Certification"},
            {"title": "Personal Portfolio & Study Tracker", "provider": "Guided Project", "duration": "2 weeks", "type": "Project"},
        ],
    },
    {
        "title": "UI/UX & Product Designer",
        "stage_fit": ["10th", "12th", "college"],
        "rec_type": "career",
        "stream_hint": "Arts / Commerce / PCM -> B.Des / B.Sc Multimedia & Design",
        "summary": "Shape how apps look and feel so everyday people can use technology effortlessly.",
        "weights": {"math": 0.05, "science": 0.0, "coding": 0.10, "analytical": 0.15, "creativity": 0.45, "communication": 0.25},
        "required_skills": {"Figma & Wireframing": 85, "Visual Hierarchy": 80, "User Research": 75, "Communication": 80},
        "courses": [
            {"title": "Google UX Design Essentials", "provider": "Coursera", "duration": "5 weeks", "type": "Certification"},
            {"title": "Figma UI Systems Crash Course", "provider": "DesignCourse", "duration": "2 weeks", "type": "Course"},
            {"title": "Redesign a School Portal App", "provider": "Guided Project", "duration": "2 weeks", "type": "Project"},
        ],
    },
    {
        "title": "Financial Analyst & FinTech (CA / BBA)",
        "stage_fit": ["10th", "12th", "college"],
        "rec_type": "career",
        "stream_hint": "Commerce (Accounts + Math) -> B.Com (Hons) / BBA Finance / CA",
        "summary": "Help companies plan budgets, evaluate investments, and grow responsibly.",
        "weights": {"math": 0.30, "science": 0.0, "coding": 0.05, "analytical": 0.30, "creativity": 0.05, "communication": 0.30},
        "required_skills": {"Accounting Basics": 80, "Financial Excel": 85, "Business Communication": 80, "Quantitative Aptitude": 75},
        "courses": [
            {"title": "Financial Markets & Accounting Basics", "provider": "NPTEL / Yale Coursera", "duration": "4 weeks", "type": "Course"},
            {"title": "Excel Modeling for Beginners", "provider": "CFI", "duration": "3 weeks", "type": "Certification"},
            {"title": "Monthly Student Budget & Investment Plan", "provider": "Guided Project", "duration": "1 week", "type": "Project"},
        ],
    },
    {
        "title": "Biotech & Healthcare Researcher",
        "stage_fit": ["10th", "12th", "college"],
        "rec_type": "career",
        "stream_hint": "Science (PCB) -> MBBS / B.Sc Biotechnology / B.Pharm",
        "summary": "Apply biology, chemistry, and lab science to improve medicine, nutrition, and diagnostics.",
        "weights": {"math": 0.10, "science": 0.45, "coding": 0.05, "analytical": 0.25, "creativity": 0.05, "communication": 0.10},
        "required_skills": {"Biology & Chemistry": 85, "Lab & Research Analysis": 80, "Scientific Writing": 75, "Statistics Basics": 65},
        "courses": [
            {"title": "Bioinformatics & Genetics Intro", "provider": "NPTEL / Coursera", "duration": "4 weeks", "type": "Course"},
            {"title": "Clinical Research Fundamentals", "provider": "NIH / FutureLearn", "duration": "3 weeks", "type": "Certification"},
            {"title": "Health Survey Data Analysis", "provider": "Guided Project", "duration": "2 weeks", "type": "Project"},
        ],
    },
]

STREAM_CATALOG_10TH = [
    {
        "title": "Class 11–12 Science (PCM + CS)",
        "summary": "Best if you enjoy Maths, Physics, and Technology. Opens Engineering, AI, Data Science, Aviation, and Architecture.",
        "weights": {"math": 0.35, "science": 0.30, "coding": 0.25, "analytical": 0.10, "creativity": 0.0, "communication": 0.0},
    },
    {
        "title": "Class 11–12 Science (PCB)",
        "summary": "Best if you love Biology and Chemistry. Opens Medicine, Biotechnology, Pharmacy, and Healthcare Research.",
        "weights": {"math": 0.10, "science": 0.55, "coding": 0.0, "analytical": 0.20, "creativity": 0.05, "communication": 0.10},
    },
    {
        "title": "Class 11–12 Commerce + Maths",
        "summary": "Ideal if you like numbers, business, and leadership. Opens CA, BBA, Finance, Economics, and FinTech.",
        "weights": {"math": 0.30, "science": 0.0, "coding": 0.05, "analytical": 0.30, "creativity": 0.05, "communication": 0.30},
    },
    {
        "title": "Arts / Humanities & Design",
        "summary": "Great for strong communicators and creative thinkers. Opens Law (CLAT), UX Design, Journalism, Psychology, and Civil Services.",
        "weights": {"math": 0.05, "science": 0.05, "coding": 0.05, "analytical": 0.15, "creativity": 0.35, "communication": 0.35},
    },
]


def recommend_careers(profile: Dict, skills_map: Dict[str, int], interests: List[str]) -> List[Dict]:
    """Return top 3 content-based career recommendations + 10th stream match when relevant."""
    scores = {
        "math": float(profile.get("math_score", 72)),
        "science": float(profile.get("science_score", 70)),
        "coding": float(profile.get("coding_interest", 65)),
        "analytical": float(profile.get("analytical_score", 70)),
        "creativity": float(profile.get("creativity_score", 65)),
        "communication": float(profile.get("communication_score", 70)),
    }
    interests_lower = " ".join(interests).lower()
    stage = profile.get("education_stage", "12th")

    ranked: List[Dict] = []
    for item in CAREER_CATALOG:
        w = item["weights"]
        raw_score = sum(scores[k] * w[k] for k in w)

        # Interest alignment bonus (bounded <= 12 pts)
        bonus = 0.0
        title_lower = item["title"].lower()
        if any(tok in interests_lower for tok in ["ai", "ml", "data", "math"]) and ("ml" in title_lower or "data" in title_lower):
            bonus += 8.5
        if any(tok in interests_lower for tok in ["web", "app", "coding", "software"]) and "web" in title_lower:
            bonus += 8.5
        if any(tok in interests_lower for tok in ["design", "art", "ui", "ux", "creative"]) and "design" in title_lower:
            bonus += 9.0
        if any(tok in interests_lower for tok in ["finance", "business", "commerce", "management"]) and "financial" in title_lower:
            bonus += 9.0
        if any(tok in interests_lower for tok in ["bio", "med", "health", "doctor"]) and "biotech" in title_lower:
            bonus += 9.0

        match_pct = round(min(97.0, max(54.0, raw_score * 0.96 + bonus)), 1)

        # Compute realistic skill gaps from user's skills_map or baseline scores
        skill_gaps = []
        for req_skill, target in item["required_skills"].items():
            current = None
            for sk_name, sk_val in skills_map.items():
                if sk_name.lower() in req_skill.lower() or req_skill.lower() in sk_name.lower():
                    current = sk_val
                    break
            if current is None:
                if "math" in req_skill.lower() or "quant" in req_skill.lower():
                    current = int(scores["math"] * 0.85)
                elif "python" in req_skill.lower() or "html" in req_skill.lower() or "coding" in req_skill.lower():
                    current = int(scores["coding"] * 0.85)
                elif "bio" in req_skill.lower() or "lab" in req_skill.lower():
                    current = int(scores["science"] * 0.85)
                elif "comm" in req_skill.lower() or "writing" in req_skill.lower():
                    current = int(scores["communication"] * 0.85)
                elif "figma" in req_skill.lower() or "visual" in req_skill.lower():
                    current = int(scores["creativity"] * 0.82)
                else:
                    current = int(scores["analytical"] * 0.8)
            current = max(25, min(95, int(current)))
            skill_gaps.append({"skill": req_skill, "current": current, "target": target})

        summary = item["summary"]
        if stage == "10th":
            summary = f"{summary} Recommended 11th/12th path: {item['stream_hint']}."

        ranked.append(
            {
                "rec_type": "career",
                "title": item["title"],
                "match_pct": match_pct,
                "summary": summary,
                "stream_hint": item["stream_hint"],
                "required_skills": list(item["required_skills"].keys()),
                "skill_gaps": skill_gaps,
                "suggested_courses": item["courses"],
            }
        )

    ranked.sort(key=lambda x: x["match_pct"], reverse=True)
    return ranked[:3]


def recommend_10th_stream(profile: Dict) -> Dict:
    """Return top recommended 11th/12th stream for 10th pass-out students."""
    scores = {
        "math": float(profile.get("math_score", 72)),
        "science": float(profile.get("science_score", 70)),
        "coding": float(profile.get("coding_interest", 65)),
        "analytical": float(profile.get("analytical_score", 70)),
        "creativity": float(profile.get("creativity_score", 65)),
        "communication": float(profile.get("communication_score", 70)),
    }
    best = None
    best_score = -1.0
    for st in STREAM_CATALOG_10TH:
        sc = sum(scores[k] * st["weights"][k] for k in st["weights"])
        if sc > best_score:
            best_score = sc
            best = st
    return {
        "title": best["title"],
        "match_pct": round(min(96.0, max(62.0, best_score * 1.05)), 1),
        "summary": best["summary"],
    }
