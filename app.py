"""
app.py  –  College Admission Agent
Flask backend powered by IBM Watsonx.ai (Granite models)
"""
from __future__ import annotations

import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, session
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

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

    # Granite chat format
    prompt = (
        f"<|system|>\n{system_prompt}\n<|user|>\n{user_message}\n<|assistant|>\n"
    )

    response = model.generate_text(prompt=prompt)
    return response.strip() if response else "I'm sorry, I could not generate a response. Please try again."


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

    # Merge any profile fields sent with this message
    for field in ("name", "education_level", "gpa", "test_scores", "interests", "country"):
        if field in data:
            profile[field] = data[field]
    session["profile"] = profile

    try:
        reply = _ask_model(user_message, profile if any(profile.values()) else None)
        return jsonify({"reply": reply, "timestamp": datetime.utcnow().isoformat()})
    except EnvironmentError as exc:
        return jsonify({"error": str(exc), "setup_required": True}), 503
    except Exception as exc:  # noqa: BLE001
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
