# 🎓 College Admission Agent — IBM Watsonx.ai + Flask

An AI-powered college admission counselling web application built with **Python Flask** and **IBM Watsonx.ai Granite models**. Features a full chat UI, admission dashboard, course explorer, eligibility checker, deadline tracker, and applicant profile management.

---

## 📁 Project Structure

```
college-admission-agent/
├── app.py                  ← Flask backend + all API routes
├── agent_config.py         ← ⭐ AGENT INSTRUCTIONS — customize here
├── requirements.txt        ← Python dependencies
├── env.example             ← Credentials template → copy to .env
├── templates/
│   └── index.html          ← Single-page frontend (Jinja2)
└── static/
    ├── css/style.css       ← All styles, dark mode, animations
    └── js/app.js           ← Frontend logic (chat, courses, eligibility…)
```

---

## ⚡ Quick Start

### 1 · Clone / Download

```bash
git clone https://github.com/your-repo/college-admission-agent.git
cd college-admission-agent
```

### 2 · Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3 · Install dependencies

```bash
pip install -r requirements.txt
```

### 4 · Configure IBM Watsonx.ai credentials

```bash
# Copy the template
cp env.example .env        # macOS / Linux
copy env.example .env      # Windows
```

Open `.env` and fill in your values:

```env
WATSONX_API_KEY=<your IBM Cloud API key>
WATSONX_PROJECT_ID=<your Watsonx project ID>
WATSONX_URL=https://us-south.ml.cloud.ibm.com
FLASK_SECRET_KEY=<a long random string>
GRANITE_MODEL_ID=ibm/granite-3-3-8b-instruct
```

> **How to get credentials:**
> 1. Sign up / log in at [cloud.ibm.com](https://cloud.ibm.com)
> 2. Create an **IBM Watson Machine Learning** service instance
> 3. Create an **API key** under *Manage → IAM → API Keys*
> 4. Open [dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com), create a project, and copy the **Project ID**

### 5 · Run the development server

```bash
python app.py
```

Open your browser at **http://localhost:5000**

---

## ✏️ Customizing the Agent (`agent_config.py`)

All agent behaviour is controlled from **`agent_config.py`** — no other file needs to change.

| Section | What to edit |
|---------|-------------|
| **Identity & Tone** | `AGENT_NAME`, `AGENT_PERSONA`, `AGENT_TONE` |
| **Institution** | `INSTITUTION_NAME`, `INSTITUTION_LOCATION`, `FLAGSHIP_PROGRAMS` |
| **Region & Tests** | `REGION`, `ACCEPTED_TESTS`, `GPA_SCALE`, `MINIMUM_GPA` |
| **Course Catalogue** | `COURSES` list — add/edit/remove programme dictionaries |
| **Application Rounds** | `APPLICATION_ROUNDS` list |
| **Safety Rules** | `SAFETY_RULES` string |
| **AI Parameters** | `MAX_RESPONSE_TOKENS`, `RESPONSE_TEMPERATURE` |

### Example: Change institution

```python
INSTITUTION_NAME = "Pacific Tech University"
INSTITUTION_LOCATION = "California, USA"
FLAGSHIP_PROGRAMS = ["Robotics", "Marine Biology", "Film Production"]
```

### Example: Add a programme

```python
COURSES.append({
    "name": "M.Sc. Cybersecurity",
    "level": "Graduate",
    "duration": "2 years",
    "min_gpa": 3.0,
    "required_tests": ["GRE"],
    "min_test_score": {"GRE": 308},
    "tuition_usd_per_year": 36000,
    "description": "Network security, cryptography, ethical hacking, and compliance.",
    "career_paths": ["Security Analyst", "Penetration Tester", "CISO"],
})
```

---

## 🌐 API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| `GET`  | `/` | Main web UI |
| `POST` | `/api/chat` | Send a message to the AI agent |
| `GET`  | `/api/dashboard` | Institution stats and test benchmarks |
| `GET`  | `/api/courses` | Course list (supports `?level=` and `?q=` filters) |
| `POST` | `/api/eligibility` | Check eligibility for all programmes |
| `GET`  | `/api/deadlines` | Application deadlines with days-remaining |
| `GET`/`POST` | `/api/profile` | Get or save applicant profile (session-based) |
| `GET`  | `/health` | Health check |

### Chat API example

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What GPA do I need for the MBA programme?"}'
```

### Eligibility API example

```bash
curl -X POST http://localhost:5000/api/eligibility \
  -H "Content-Type: application/json" \
  -d '{"gpa": 3.4, "test_scores": {"GRE": 315, "TOEFL": 105}}'
```

---

## 🚀 Production Deployment

### Option A · Gunicorn (Linux/macOS)

```bash
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

### Option B · Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
```

```bash
docker build -t admission-agent .
docker run -p 5000:5000 --env-file .env admission-agent
```

### Option C · IBM Code Engine / Cloud Foundry

```bash
ibmcloud login
ibmcloud ce app create --name admission-agent \
  --image <your-image> \
  --env-from-secret admission-secrets
```

### Option D · Railway / Render / Heroku

- Set environment variables in the platform dashboard (same keys as `.env`)
- Set start command: `gunicorn -w 2 -b 0.0.0.0:$PORT app:app`

---

## 🔒 Security Notes

- Never commit your `.env` file (it is in `.gitignore`)
- Rotate `FLASK_SECRET_KEY` before going to production
- Use HTTPS in production (reverse proxy with nginx or platform TLS)
- The `.env` file is loaded via `python-dotenv` and never exposed to the browser

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| AI    | IBM Watsonx.ai · Granite 3.3 8B Instruct |
| Backend | Python 3.11 · Flask 3 |
| Frontend | Bootstrap 5.3 · Bootstrap Icons · Vanilla JS |
| Styling | Custom CSS · CSS variables · Dark mode |
| Deployment | Gunicorn · Docker-ready |

---

## 📄 License

MIT — feel free to adapt for your institution.
