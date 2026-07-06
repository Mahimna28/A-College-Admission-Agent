"""
==============================================================
  AGENT INSTRUCTIONS  –  Customize the College Admission Agent
==============================================================
Edit the constants below to tailor the agent to your institution,
region, tone, safety rules, and specialization without touching
any other code.
"""

# ------------------------------------------------------------------
# 1.  IDENTITY & TONE
# ------------------------------------------------------------------
AGENT_NAME = "AdmitAI"

AGENT_PERSONA = (
    "You are AdmitAI, a friendly, knowledgeable, and empathetic Indian college "
    "admission counsellor. You guide prospective students through every "
    "step of the Indian admission process with clarity, encouragement, and "
    "precision. You understand Indian entrance exams, reservation categories, "
    "state quotas, and fee structures. You are professional yet approachable."
)

# Tone options: "formal" | "friendly" | "concise" | "encouraging"
AGENT_TONE = "friendly"

# ------------------------------------------------------------------
# 2.  INSTITUTION SPECIALIZATION (INDIAN)
# ------------------------------------------------------------------
INSTITUTION_NAME = "Your College Name"  # <-- CHANGE THIS
INSTITUTION_LOCATION = "India"

# Highlight up to 5 flagship programmes
FLAGSHIP_PROGRAMS = [
    "B.Tech Computer Science & Engineering",
    "B.Tech Artificial Intelligence & Data Science",
    "BBA / B.Com",
    "MBBS / BDS",
    "B.Sc. Biotechnology",
]

# ------------------------------------------------------------------
# 3.  REGIONAL ADMISSION PREFERENCES (INDIAN)
# ------------------------------------------------------------------
REGION = "India"

# Accepted Indian entrance exams and typical cut-off ranges
ACCEPTED_TESTS = {
    "JEE Main": {"min": 60, "competitive": 150, "max": 300},
    "JEE Advanced": {"min": 50, "competitive": 120, "max": 300},
    "NEET": {"min": 300, "competitive": 550, "max": 720},
    "MHT-CET": {"min": 80, "competitive": 140, "max": 200},
    "WBJEE": {"min": 70, "competitive": 120, "max": 200},
    "CAT": {"min": 50, "competitive": 90, "max": 100},
    "MAT": {"min": 400, "competitive": 600, "max": 800},
    "CLAT": {"min": 80, "competitive": 100, "max": 150},
    "NATA": {"min": 70, "competitive": 120, "max": 200},
}

# Indian academic scale (percentage or 10-point CGPA)
GPA_SCALE = 10.0
MINIMUM_GPA = 6.0          # 60% or 6.0 CGPA
COMPETITIVE_GPA = 8.5      # 85% or 8.5 CGPA

# Academic year structure
ACADEMIC_YEAR_START = "July"
APPLICATION_ROUNDS = [
    "Round 1 (May 1)",
    "Round 2 (June 15)",
    "Spot Round (July 30)",
    "Management Quota (Aug 1 - Aug 15)"
]

# ------------------------------------------------------------------
# 4.  COURSE & PROGRAMME CATALOGUE (INDIAN)
# ------------------------------------------------------------------
COURSES = [
    {
        "name": "B.Tech Computer Science & Engineering",
        "level": "Undergraduate",
        "duration": "4 years",
        "min_gpa": 7.5,
        "required_tests": ["JEE Main"],
        "min_test_score": {"JEE Main": 120},
        "tuition_inr_per_year": 250000,
        "description": "Core CS, AI, ML, cloud computing, and full-stack development.",
        "career_paths": ["Software Engineer", "Data Scientist", "Product Manager"],
    },
    {
        "name": "B.Tech AI & Data Science",
        "level": "Undergraduate",
        "duration": "4 years",
        "min_gpa": 7.0,
        "required_tests": ["JEE Main"],
        "min_test_score": {"JEE Main": 100},
        "tuition_inr_per_year": 280000,
        "description": "Deep learning, NLP, computer vision, and big data analytics.",
        "career_paths": ["AI Engineer", "ML Engineer", "Data Analyst"],
    },
    {
        "name": "B.Tech Electronics & Communication",
        "level": "Undergraduate",
        "duration": "4 years",
        "min_gpa": 6.5,
        "required_tests": ["JEE Main", "MHT-CET"],
        "min_test_score": {"JEE Main": 90, "MHT-CET": 100},
        "tuition_inr_per_year": 220000,
        "description": "VLSI, embedded systems, IoT, and wireless communication.",
        "career_paths": ["Hardware Engineer", "IoT Developer", "Telecom Engineer"],
    },
    {
        "name": "BBA",
        "level": "Undergraduate",
        "duration": "3 years",
        "min_gpa": 6.0,
        "required_tests": [],
        "min_test_score": {},
        "tuition_inr_per_year": 150000,
        "description": "Business management, marketing, finance, and entrepreneurship.",
        "career_paths": ["Manager", "Entrepreneur", "Marketing Executive"],
    },
    {
        "name": "MBBS",
        "level": "Undergraduate",
        "duration": "5.5 years",
        "min_gpa": 8.0,
        "required_tests": ["NEET"],
        "min_test_score": {"NEET": 400},
        "tuition_inr_per_year": 800000,
        "description": "Medical sciences, clinical practice, and healthcare.",
        "career_paths": ["Doctor", "Surgeon", "Medical Researcher"],
    },
    {
        "name": "M.Tech Computer Science",
        "level": "Graduate",
        "duration": "2 years",
        "min_gpa": 8.0,
        "required_tests": ["GATE"],
        "min_test_score": {"GATE": 500},
        "tuition_inr_per_year": 200000,
        "description": "Advanced algorithms, research methodology, and thesis.",
        "career_paths": ["Research Scientist", "Professor", "Tech Lead"],
    },
    {
        "name": "MBA",
        "level": "Graduate",
        "duration": "2 years",
        "min_gpa": 7.0,
        "required_tests": ["CAT", "MAT"],
        "min_test_score": {"CAT": 70, "MAT": 500},
        "tuition_inr_per_year": 400000,
        "description": "Leadership, strategy, finance, and global business management.",
        "career_paths": ["Executive", "Consultant", "Startup Founder"],
    },
]

# ------------------------------------------------------------------
# 5.  SAFETY & CONTENT RULES
# ------------------------------------------------------------------
SAFETY_RULES = """
- Never fabricate admission statistics, acceptance rates, or scholarship amounts.
- Do not make guarantees about admission outcomes.
- Do not provide legal, medical, or financial advice beyond general guidance.
- Decline to discuss unrelated, offensive, or harmful topics politely.
- If unsure about specific data, advise the user to verify with the official admissions office.
- Always respect the student's autonomy and choices.
- Do not discriminate based on caste, religion, gender, nationality, or socioeconomic status.
- Respect Indian reservation policies (SC/ST/OBC/EWS) and provide accurate quota information.
"""

# ------------------------------------------------------------------
# 6.  RESPONSE FORMATTING PREFERENCES
# ------------------------------------------------------------------
# Max tokens for AI responses — kept low to conserve token budget.
# Increase only if you have ample tokens available.
MAX_RESPONSE_TOKENS = 450

# Temperature — 0.5 gives focused, predictable answers (saves tokens via greedy decoding)
RESPONSE_TEMPERATURE = 0.5

# Use bullet points and structured output where helpful
USE_STRUCTURED_RESPONSES = True

# ------------------------------------------------------------------
# 7.  BUILD THE SYSTEM PROMPT  (auto-assembled – do not edit below)
#
#  Prompt is kept intentionally compact to minimise input tokens.
#  Every extra line here costs tokens on EVERY API call.
# ------------------------------------------------------------------
def build_system_prompt(applicant_profile: dict | None = None) -> str:
    # Compact programme list — name + level only (no duration) to save tokens
    programmes_list = " | ".join(f"{c['name']} ({c['level']})" for c in COURSES)

    # Compact test benchmarks — one line
    test_line = ", ".join(f"{k}≥{v['min']}" for k, v in ACCEPTED_TESTS.items())

    # Compact admission rounds
    rounds_line = " | ".join(APPLICATION_ROUNDS)

    # Only inject profile if it has meaningful data
    profile_section = ""
    if applicant_profile:
        filled = {k: v for k, v in applicant_profile.items() if v}
        if filled:
            parts = [f"{k}: {v}" for k, v in filled.items()]
            profile_section = "\nStudent: " + ", ".join(parts)

    return (
        f"{AGENT_PERSONA}\n\n"
        f"Institution: {INSTITUTION_NAME}, {INSTITUTION_LOCATION}.\n"
        f"Programmes: {programmes_list}.\n"
        f"Rounds: {rounds_line}.\n"
        f"Tests: {test_line}. Min GPA: {MINIMUM_GPA}/{GPA_SCALE}.\n"
        f"Rules: Never guarantee outcomes. Fees in INR. Use reservation context (SC/ST/OBC/EWS).\n"
        f"Reply in {AGENT_TONE} tone. Use short bullet points. Be concise — max 5-6 bullets."
        f"{profile_section}"
    ).strip()