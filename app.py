"""
app.py  –  College Admission Agent
Flask backend powered by IBM Watsonx.ai (Granite models)
"""
from __future__ import annotations

import re
import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, session
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from rag_engine import retrieve_context

from agent_config import (
    ACCEPTED_TESTS,
    AGENT_NAME,
    APPLICATION_ROUNDS,
    COMPETITIVE_GPA,
    COURSES,
    FLAGSHIP_PROGRAMS,
    INSTITUTION_NAME,
    MAX_RESPONSE_TOKENS,
    MINIMUM_GPA,
    RESPONSE_TEMPERATURE,
    build_system_prompt,
)

# ------------------------------------------------------------------
# Bootstrap
# ------------------------------------------------------------------
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")

# ------------------------------------------------------------------
# Watsonx.ai client (lazy-initialised so the app starts even if
# credentials are missing – useful for UI-only development runs)
# ------------------------------------------------------------------
_watsonx_model: ModelInference | None = None


def _parse_profile_from_message(message: str) -> dict:
    """Extract profile fields from user messages like 'name :- Aarav Sharma'"""
    profile = {}
    
    # Pattern: field_name :- value
    # Handles multi-word values until next field or end of string
    pattern = r'(\w+(?:_\w+)*)\s*:-\s*([^\n]+?)(?=(?:\s+\w+(?:_\w+)*\s*:-|\Z))'
    matches = re.findall(pattern, message, re.DOTALL)
    
    field_map = {
        "name": "name",
        "age": "age",
        "12th_percentage": "gpa",
        "percentage": "gpa",
        "gpa": "gpa",
        "cgpa": "gpa",
        "entrance_exam": "test_scores",
        "entrance_score": "test_scores",
        "preferred_course": "interests",
        "course": "interests",
        "category": "category",
        "state": "state",
        "budget_per_year": "budget",
        "hostel_required": "hostel",
        "college_type": "college_type",
        "location_preference": "location",
        "specialization_interest": "interests",
        "goal": "goals",
        "preferences": "preferences",
        "backlog_history": "backlogs",
        "gap_year": "gap_year",
        "documents_ready": "documents",
    }
    
    for key, value in matches:
        value = value.strip()
        mapped_key = field_map.get(key.lower(), key)
        
        if mapped_key == "test_scores":
            # Build test_scores dict from entrance_exam and entrance_score
            if "test_scores" not in profile:
                profile["test_scores"] = {}
            if "entrance_exam" in [k.lower() for k, v in matches]:
                exam_name = dict(matches).get("entrance_exam", "JEE Main")
                profile["test_scores"][exam_name] = value
            else:
                profile["test_scores"]["score"] = value
        elif mapped_key == "interests":
            existing = profile.get("interests", [])
            if isinstance(existing, str):
                existing = [existing]
            existing.append(value)
            profile["interests"] = existing
        else:
            profile[mapped_key] = value
    
    # Also try to extract education_level from context
    if "b.tech" in message.lower() or "engineering" in message.lower():
        profile["education_level"] = "High School"
    elif "mba" in message.lower() or "m.tech" in message.lower():
        profile["education_level"] = "Bachelor's Degree"
    
    return profile

def _get_model() -> ModelInference:
    global _watsonx_model
    if _watsonx_model is not None:
        return _watsonx_model

    api_key = os.getenv("WATSONX_API_KEY", "")
    project_id = os.getenv("WATSONX_PROJECT_ID", "")
    url = os.getenv("WATSONX_URL", "https://au-syd.ml.cloud.ibm.com")
    model_id = os.getenv("GRANITE_MODEL_ID", "ibm/granite-3-3-8b")

    if not api_key or api_key == "your_ibm_cloud_api_key_here":
        raise EnvironmentError(
            "WATSONX_API_KEY is not set. Copy env.example → .env and fill in your credentials."
        )
    if not project_id or project_id == "your_watsonx_project_id_here":
        raise EnvironmentError(
            "WATSONX_PROJECT_ID is not set. Copy env.example → .env and fill in your credentials."
        )

    credentials = Credentials(url=url, api_key=api_key)
    client = APIClient(credentials=credentials, project_id=project_id)

    _watsonx_model = ModelInference(
        model_id=model_id,
        api_client=client,
        params={
            GenParams.MAX_NEW_TOKENS: MAX_RESPONSE_TOKENS,
            GenParams.TEMPERATURE: RESPONSE_TEMPERATURE,
            GenParams.REPETITION_PENALTY: 1.05,
        },
    )
    return _watsonx_model


# ------------------------------------------------------------------
# Helper: call the model
# ------------------------------------------------------------------
def _ask_model(user_message: str, profile: dict | None = None) -> str:
    model = _get_model()
    system_prompt = build_system_prompt(profile)

    # 🔥 RAG: Retrieve relevant context from documents
    rag_context = retrieve_context(user_message)

    # Build enhanced prompt with retrieved context
    context_block = ""
    if rag_context:
        context_block = f"\n\n## Relevant Institutional Knowledge\n{rag_context}\n"

    # Llama 3.x chat format
    prompt = f"""<|start_header_id|>system<|end_header_id|>
{system_prompt}{context_block}
<|eot_id|><|start_header_id|>user<|end_header_id|>
{user_message}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""

    try:
        response = model.generate(prompt=prompt)

        # Handle different response formats
        if isinstance(response, dict):
            results = response.get("results", [])
            if results and len(results) > 0:
                return results[0].get("generated_text", "").strip()
            return "I'm sorry, I couldn't generate a response. Please try again."
        elif isinstance(response, str):
            return response.strip()
        elif isinstance(response, list) and len(response) > 0:
            return response[0].strip()
        else:
            return str(response).strip()

    except Exception as e:
        app.logger.error("Watsonx generate error: %s", e)
        return _get_fallback_response(user_message)

def _get_fallback_response(query: str) -> str:
    """Smart fallback when AI is down — Indian context"""
    q = query.lower()
    
    if any(word in q for word in ["eligibility", "qualify", "cutoff", "eligible", "report"]):
        return """📋 **Eligibility Quick Guide**

• **B.Tech CSE**: 75% in 12th (PCM) + JEE Main 120+
• **B.Tech AI & DS**: 70% in 12th + JEE Main 100+
• **BBA**: 60% in 12th (any stream)
• **MBBS**: 80% in 12th (PCB) + NEET 400+

**Reservation**: SC/ST/OBC/EWS quotas as per Govt. of India norms.
**Scholarships**: Merit-based for JEE Main 200+ scorers.

Use the **Eligibility Checker** below for a detailed personalized report!"""
    
    elif any(word in q for word in ["course", "program", "b.tech", "mbbs", "bba"]):
        return """🎓 **Our Programmes**

• **B.Tech CSE** — ₹2,50,000/year | JEE Main required
• **B.Tech AI & DS** — ₹2,80,000/year | JEE Main required  
• **B.Tech ECE** — ₹2,20,000/year | JEE Main/MHT-CET
• **BBA** — ₹1,50,000/year | Direct admission
• **MBBS** — ₹8,00,000/year | NEET required
• **M.Tech CSE** — ₹2,00,000/year | GATE required
• **MBA** — ₹4,00,000/year | CAT/MAT

Browse the **Course Explorer** for full details!"""
    
    elif any(word in q for word in ["deadline", "date", "last date", "when"]):
        return """📅 **Important Dates**

• **Round 1**: May 1
• **Round 2**: June 15  
• **Spot Round**: July 30
• **Management Quota**: Aug 1 - Aug 15

Don't miss the deadlines! Check the **Deadlines** section for a live countdown."""
    
    elif any(word in q for word in ["fee", "cost", "tuition", "₹", "rs", "price"]):
        return """💰 **Fee Structure (per year)**

• **B.Tech CSE**: ₹2,50,000
• **B.Tech AI & DS**: ₹2,80,000
• **B.Tech ECE**: ₹2,20,000
• **BBA**: ₹1,50,000
• **MBBS**: ₹8,00,000
• **M.Tech**: ₹2,00,000
• **MBA**: ₹4,00,000

**Hostel**: ₹60,000/year (mess included)
**Scholarships**: Up to 100% fee waiver for merit students!"""
    
    elif any(word in q for word in ["scholarship", "financial aid", "fee waiver"]):
        return """🎁 **Scholarship Opportunities**

• **100% Fee Waiver**: JEE Main 250+ | NEET 600+
• **50% Fee Waiver**: JEE Main 200+ | NEET 500+
• **State Scholarships**: Available for SC/ST/OBC students
• **Minority Scholarships**: As per state government norms

Apply before **July 15**! Contact our Financial Aid Office for details."""
    
    elif any(word in q for word in ["document", "required", "need", "marksheet"]):
        return """📄 **Required Documents**

1. 10th Marksheet
2. 12th Marksheet  
3. Entrance Exam Scorecard (JEE/NEET/CET)
4. Caste Certificate (if applicable)
5. Domicile Certificate
6. Aadhaar Card
7. Passport Size Photos (6)
8. Application Fee Receipt (₹1,500)

Keep originals + 2 photocopies ready!"""
    
    else:
        return """👋 **Welcome to AdmitAI!**

I'm your Indian college admission counsellor. I can help you with:

• **JEE/NEET/CET** cutoffs and eligibility
• **Course selection** (B.Tech, MBBS, BBA, MBA)
• **Fee structure** and scholarships
• **Admission deadlines** and document checklists
• **Reservation quotas** and counselling process

**Tip**: You can type your details like this:
`name :- Aarav Sharma, 12th_percentage :- 87.5, entrance_exam :- JEE Main, entrance_score :- 156`

Or use the **Eligibility Checker** below for instant analysis!"""

# ------------------------------------------------------------------
# Eligibility analysis helper (pure Python, no LLM needed)
# ------------------------------------------------------------------
def _check_eligibility(profile: dict) -> dict:
    gpa = float(profile.get("gpa") or 0)
    test_scores: dict = profile.get("test_scores") or {}
    interests: list[str] = profile.get("interests") or []

    eligible, borderline, ineligible = [], [], []

    for course in COURSES:
        if interests and not any(
            i.lower() in course["name"].lower() for i in interests
        ):
            pass  # still evaluate all courses

        gpa_ok = gpa >= course["min_gpa"]
        score_ok = False
        for test in course["required_tests"]:
            score = float(test_scores.get(test) or 0)
            if score >= course["min_test_score"].get(test, 0):
                score_ok = True
                break

        if gpa_ok and score_ok:
            eligible.append(course)
        elif gpa >= course["min_gpa"] - 0.3 or score_ok:
            borderline.append(course)
        else:
            ineligible.append(course)

    return {
        "eligible": eligible,
        "borderline": borderline,
        "ineligible": ineligible,
        "summary": {
            "gpa": gpa,
            "min_required": MINIMUM_GPA,
            "competitive_gpa": COMPETITIVE_GPA,
            "eligible_count": len(eligible),
            "borderline_count": len(borderline),
        },
    }


# ------------------------------------------------------------------
# Routes – pages
# ------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html", agent_name=AGENT_NAME, institution=INSTITUTION_NAME)


# ------------------------------------------------------------------
# Routes – API
# ------------------------------------------------------------------
@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    # Persist profile in session
    if "profile" not in session:
        session["profile"] = {}
    profile = session["profile"]

    # 🔥 NEW: Parse profile data from user's natural language message
    parsed_profile = _parse_profile_from_message(user_message)
    for key, value in parsed_profile.items():
        if value:  # Only overwrite if we got a value
            profile[key] = value

    # Also merge any explicit profile fields sent from frontend
    for field in ("name", "education_level", "gpa", "test_scores", "interests", "country", "state", "category"):
        if field in data:
            profile[field] = data[field]
    
    session["profile"] = profile

    try:
        reply = _ask_model(user_message, profile if any(profile.values()) else None)
        return jsonify({"reply": reply, "timestamp": datetime.utcnow().isoformat()})
    except EnvironmentError as exc:
        return jsonify({"error": str(exc), "setup_required": True}), 503
    except Exception as exc:
        app.logger.error("Watsonx error: %s", exc)
        return jsonify({"error": "AI service temporarily unavailable. Please try again."}), 500


@app.route("/api/eligibility", methods=["POST"])
def api_eligibility():
    data = request.get_json(silent=True) or {}
    required = ("gpa",)
    if not all(data.get(f) for f in required):
        return jsonify({"error": "GPA is required for eligibility check"}), 400

    result = _check_eligibility(data)
    return jsonify(result)


@app.route("/api/courses", methods=["GET"])
def api_courses():
    level = request.args.get("level", "").strip()
    keyword = request.args.get("q", "").strip().lower()

    filtered = COURSES
    if level:
        filtered = [c for c in filtered if c["level"].lower() == level.lower()]
    if keyword:
        filtered = [
            c for c in filtered
            if keyword in c["name"].lower() or keyword in c["description"].lower()
        ]
    return jsonify({"courses": filtered, "total": len(filtered)})


@app.route("/api/dashboard", methods=["GET"])
def api_dashboard():
    return jsonify({
        "institution": INSTITUTION_NAME,
        "flagship_programs": FLAGSHIP_PROGRAMS,
        "application_rounds": APPLICATION_ROUNDS,
        "accepted_tests": ACCEPTED_TESTS,
        "stats": {
            "total_programs": len(COURSES),
            "undergraduate": sum(1 for c in COURSES if c["level"] == "Undergraduate"),
            "graduate": sum(1 for c in COURSES if c["level"] == "Graduate"),
        },
    })


@app.route("/api/profile", methods=["GET", "POST"])
def api_profile():
    if "profile" not in session:
        session["profile"] = {}

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        for field in ("name", "education_level", "gpa", "test_scores", "interests", "country"):
            if field in data:
                session["profile"][field] = data[field]
        session.modified = True
        return jsonify({"status": "saved", "profile": session["profile"]})

    return jsonify({"profile": session["profile"]})


@app.route("/api/deadlines", methods=["GET"])
def api_deadlines():
    today = datetime.utcnow()
    year = today.year

    deadlines = [
        {"round": "Early Decision",    "date": f"{year}-11-01", "label": "Early Decision"},
        {"round": "Regular Decision",  "date": f"{year+1}-01-15","label": "Regular Decision"},
        {"round": "Transfer",          "date": f"{year+1}-03-01","label": "Transfer"},
        {"round": "Financial Aid FAFSA","date": f"{year+1}-02-15","label": "Financial Aid (FAFSA)"},
        {"round": "Scholarship",       "date": f"{year}-12-01", "label": "Merit Scholarship"},
    ]

    for d in deadlines:
        delta = (datetime.strptime(d["date"], "%Y-%m-%d") - today).days
        d["days_remaining"] = delta
        d["status"] = "passed" if delta < 0 else ("urgent" if delta <= 30 else "upcoming")

    return jsonify({"deadlines": deadlines})

@app.route("/api/test-watsonx", methods=["GET"])
def test_watsonx():
    """Debug endpoint to verify Watsonx connection"""
    try:
        model = _get_model()
        test_response = model.generate(prompt="Say 'IBM Watsonx is working!'")
        return jsonify({
            "status": "connected",
            "model": os.getenv("GRANITE_MODEL_ID", "ibm/granite-3-3-8b-instruct"),
            "test_response": str(test_response)[:200]
        })
    except Exception as e:
        return jsonify({
            "status": "failed",
            "error": str(e),
            "hint": "Check your WATSONX_API_KEY and WATSONX_PROJECT_ID in .env"
        }), 503


# ------------------------------------------------------------------
# Health check
# ------------------------------------------------------------------
@app.route("/health")
def health():
    return jsonify({"status": "ok", "agent": AGENT_NAME, "institution": INSTITUTION_NAME})


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV", "production") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
