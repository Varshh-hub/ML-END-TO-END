from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import re
import json
import pdfplumber
import numpy as np
import joblib
import urllib.request
import urllib.error

# Google GenAI is optional at startup. The app will show a useful setup
# error from the AI endpoints if the package/key is missing.
try:
    from google import genai
except ImportError:
    genai = None


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ===== Gemini key loader =====
KEY_FILE = os.path.join(BASE_DIR, "gemini_api_key.txt")

def load_gemini_key():
    # 1. Text file beside app2.py
    if os.path.isfile(KEY_FILE):
        try:
            with open(KEY_FILE, "r", encoding="utf-8") as f:
                key = f.read().strip()
                if key:
                    return key, "gemini_api_key.txt"
        except Exception as e:
            print("Gemini key file error:", e)

    # 2. Environment variable
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if key:
        return key, "environment"

    return "", "not configured"

GEMINI_API_KEY, GEMINI_KEY_SOURCE = load_gemini_key()
MODEL_PATH = os.path.join(BASE_DIR, "resumatch_model.pkl")

app = Flask(
    __name__,
    template_folder=BASE_DIR,
    static_folder=None
)

# ---------------------------------------------------------------------------
# MODEL
# ---------------------------------------------------------------------------

def load_model_bundle():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"resumatch_model.pkl was not found in: {BASE_DIR}"
        )

    bundle = joblib.load(MODEL_PATH)

    # The notebook saves a dictionary containing the complete preprocessing
    # pipeline. Keep the whole bundle; using only best_model breaks inference.
    if not isinstance(bundle, dict):
        raise TypeError(
            "resumatch_model.pkl must be the model bundle exported by "
            "the ResuMatch notebook."
        )

    required = {
        "best_model",
        "selector",
        "scaler",
        "label_encoder",
        "numeric_columns",
        "encoded_columns",
        "engineered_columns",
        "all_training_skills",
        "resume_roles",
        "resume_industries",
        "job_titles",
        "job_industries",
        "education_values",
        "skill_aliases",
    }

    missing = sorted(required.difference(bundle.keys()))
    if missing:
        raise KeyError(
            "The saved ResuMatch model bundle is missing: "
            + ", ".join(missing)
        )

    return bundle


model_bundle = load_model_bundle()
model = model_bundle["best_model"]
selector = model_bundle["selector"]
scaler = model_bundle["scaler"]
label_encoder = model_bundle["label_encoder"]

NUMERIC_COLUMNS = list(model_bundle["numeric_columns"])
ENCODED_COLUMNS = list(model_bundle["encoded_columns"])
ENGINEERED_COLUMNS = list(model_bundle["engineered_columns"])
TRAINING_SKILLS = list(model_bundle["all_training_skills"])
RESUME_ROLES = list(model_bundle["resume_roles"])
RESUME_INDUSTRIES = list(model_bundle["resume_industries"])
JOB_TITLES = list(model_bundle["job_titles"])
JOB_INDUSTRIES = list(model_bundle["job_industries"])
EDUCATION_VALUES = list(model_bundle["education_values"])
SKILL_ALIASES = dict(model_bundle["skill_aliases"])

SELECTED_COLUMNS = list(
    model_bundle.get(
        "selected_columns",
        []
    )
)

# UI role list retained from the original website.
ROLES = [
    "Associate Product Manager",
    "BI Analyst",
    "Backend Engineer",
    "Business Analyst",
    "Computer Vision Engineer",
    "Cybersecurity Analyst",
    "Data Analyst",
    "Data Scientist",
    "DevOps Engineer",
    "Generative AI Engineer",
    "Machine Learning Engineer",
    "NLP Engineer",
    "Performance Marketer",
    "Product Manager",
    "Software Engineer",
    "Technical Product Manager",
]

# ---------------------------------------------------------------------------
# STATIC FILES
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/styles.css")
def styles_css():
    return send_from_directory(BASE_DIR, "styles.css", max_age=0)


@app.route("/script.js")
def script_js():
    return send_from_directory(BASE_DIR, "script.js", max_age=0)


# ---------------------------------------------------------------------------
# TEXT / FEATURE ENGINEERING — mirrors the notebook's inference logic
# ---------------------------------------------------------------------------

def clean_input_text(text):
    if text is None:
        return ""
    text = str(text).lower()
    text = re.sub(r"[\n\r\t]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_skill(skill):
    skill = clean_input_text(skill)

    aliases = {
        "machine learning": "machine learning",
        "ml": "machine learning",
        "artificial intelligence": "artificial intelligence",
        "ai": "artificial intelligence",
        "deep learning": "deep learning",
        "dl": "deep learning",
        "natural language processing": "nlp",
        "nlp": "nlp",
        "python": "python",
        "py": "python",
        "sql": "sql",
        "power bi": "power bi",
        "powerbi": "power bi",
        "tableau": "tableau",
        "scikit-learn": "scikit-learn",
        "sklearn": "scikit-learn",
        "pandas": "pandas",
        "numpy": "numpy",
        "tensorflow": "tensorflow",
        "keras": "keras",
        "pytorch": "pytorch",
        "excel": "excel",
        "microsoft excel": "excel",
        "aws": "aws",
        "amazon web services": "aws",
        "azure": "azure",
        "microsoft azure": "azure",
        "gcp": "gcp",
        "google cloud": "gcp",
        "git": "git",
        "github": "github",
        "docker": "docker",
        "kubernetes": "kubernetes",
        "java": "java",
        "javascript": "javascript",
        "typescript": "typescript",
        "html": "html",
        "css": "css",
        "flask": "flask",
        "django": "django",
        "mongodb": "mongodb",
        "mysql": "mysql",
        "postgresql": "postgresql",
        "postgres": "postgresql",
    }

    return aliases.get(skill, skill)


def extract_skills(text):
    text = clean_input_text(text)
    found = set()

    for skill in TRAINING_SKILLS:
        skill = normalize_skill(skill)
        if not skill:
            continue

        possible_names = SKILL_ALIASES.get(skill, [skill])

        for name in possible_names:
            name = clean_input_text(name)
            pattern = r"(?<!\w)" + re.escape(name) + r"(?!\w)"
            if re.search(pattern, text):
                found.add(skill)
                break

    return sorted(found)


def extract_experience(text):
    text = clean_input_text(text)

    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*(?:years|year|yrs|yr)\s+(?:of\s+)?experience",
        r"experience\s*(?:of)?\s*(\d+(?:\.\d+)?)\+?\s*(?:years|year|yrs|yr)",
        r"(\d+(?:\.\d+)?)\+?\s*(?:years|year|yrs|yr)",
    ]

    values = []
    for pattern in patterns:
        for value in re.findall(pattern, text):
            try:
                values.append(float(value))
            except (TypeError, ValueError):
                pass

    if not values:
        return 0.0

    experience = max(values)

    # The original notebook clips using the training data range. The saved
    # bundle does not include those exact min/max values, so use non-negative
    # inference here rather than inventing training statistics.
    return round(max(float(experience), 0.0), 2)


def detect_value(text, values, default=None):
    text = clean_input_text(text)

    ordered = sorted(
        [str(v).strip() for v in values if str(v).strip()],
        key=len,
        reverse=True,
    )

    for value in ordered:
        pattern = (
            r"(?<!\w)"
            + re.escape(value.lower())
            + r"(?!\w)"
        )
        if re.search(pattern, text):
            return value

    return default



# ---------------------------------------------------------------------------
# ROBUST JD ROLE DETECTION
# ---------------------------------------------------------------------------
ROLE_ALIASES = {
    "Data Scientist": ["data scientist", "data science", "data science professional", "ds role"],
    "Data Analyst": ["data analyst", "data analytics", "business intelligence analyst", "bi analyst"],
    "Machine Learning Engineer": ["machine learning engineer", "ml engineer", "machine learning developer"],
    "AI Engineer": ["ai engineer", "artificial intelligence engineer", "ai developer"],
    "Software Engineer": ["software engineer", "software developer", "application developer", "software development engineer", "sde"],
    "Backend Engineer": ["backend engineer", "backend developer", "back-end engineer", "back-end developer"],
    "Frontend Developer": ["frontend developer", "frontend engineer", "front-end developer", "front-end engineer"],
    "Full Stack Developer": ["full stack developer", "full-stack developer", "full stack engineer", "full-stack engineer"],
    "DevOps Engineer": ["devops engineer", "devops", "site reliability engineer", "sre"],
    "Cloud Engineer": ["cloud engineer", "cloud developer", "cloud infrastructure engineer"],
    "Data Engineer": ["data engineer", "data engineering"],
    "NLP Engineer": ["nlp engineer", "natural language processing engineer"],
    "Computer Vision Engineer": ["computer vision engineer", "computer vision developer", "cv engineer"],
    "Cybersecurity Analyst": ["cybersecurity analyst", "cyber security analyst", "security analyst"],
    "Business Analyst": ["business analyst", "business analysis"],
    "Product Manager": ["product manager", "product management"],
    "Technical Product Manager": ["technical product manager", "technical product management"],
    "Associate Product Manager": ["associate product manager", "apm"],
    "Performance Marketer": ["performance marketer", "performance marketing"],
    "Generative AI Engineer": ["generative ai engineer", "genai engineer", "generative ai developer"],
}

ROLE_SKILL_SIGNATURES = {
    "Data Scientist": ["python", "sql", "machine learning", "pandas", "numpy", "scikit-learn", "statistics", "predictive modeling", "data analysis"],
    "Data Analyst": ["sql", "excel", "power bi", "tableau", "data analysis", "data visualization", "statistics"],
    "Machine Learning Engineer": ["python", "machine learning", "scikit-learn", "pytorch", "tensorflow", "docker", "mlops"],
    "AI Engineer": ["python", "artificial intelligence", "machine learning", "deep learning", "pytorch", "tensorflow"],
    "Software Engineer": ["python", "java", "javascript", "c++", "software development", "git", "api"],
    "Backend Engineer": ["python", "java", "node.js", "api", "rest", "sql", "backend"],
    "Frontend Developer": ["javascript", "typescript", "react", "html", "css", "frontend"],
    "Full Stack Developer": ["javascript", "react", "node.js", "html", "css", "sql"],
    "DevOps Engineer": ["docker", "kubernetes", "jenkins", "ci/cd", "aws", "azure", "terraform"],
    "Cloud Engineer": ["aws", "azure", "gcp", "cloud", "terraform", "kubernetes"],
    "Data Engineer": ["sql", "python", "spark", "pyspark", "etl", "airflow", "data pipeline"],
    "NLP Engineer": ["nlp", "natural language processing", "transformers", "bert", "python", "pytorch"],
    "Computer Vision Engineer": ["computer vision", "opencv", "cnn", "pytorch", "tensorflow", "image processing"],
    "Cybersecurity Analyst": ["cybersecurity", "siem", "soc", "incident response", "network security"],
    "Business Analyst": ["business analysis", "requirements", "sql", "excel", "power bi", "stakeholder"],
}

def _phrase_present(text, phrase):
    text = clean_input_text(text)
    phrase = clean_input_text(phrase)
    return bool(phrase) and bool(re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text))

def detect_job_role(job_description):
    text = clean_input_text(job_description)
    explicit_hits = []
    for role, aliases in ROLE_ALIASES.items():
        for alias in aliases:
            if _phrase_present(text, alias):
                explicit_hits.append((len(alias), role))
    if explicit_hits:
        explicit_hits.sort(reverse=True)
        return explicit_hits[0][1]

    scores = {}
    for role, skills in ROLE_SKILL_SIGNATURES.items():
        score = sum(_phrase_present(text, skill) for skill in skills)
        if score:
            scores[role] = score
    if scores:
        ranked = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
        best_role, best_score = ranked[0]
        second_score = ranked[1][1] if len(ranked) > 1 else 0
        if best_score >= 3 and best_score > second_score:
            return best_role
    return None

def resolve_training_job_title(detected_role, available_titles):
    if not detected_role:
        return None
    cleaned = [(str(x), clean_input_text(x)) for x in available_titles if str(x).strip()]
    target = clean_input_text(detected_role)
    for original, normalized in cleaned:
        if normalized == target:
            return original
    candidates = []
    target_tokens = set(target.split())
    for original, normalized in cleaned:
        if target in normalized or normalized in target:
            candidates.append((2, len(normalized), original))
            continue
        overlap = len(target_tokens.intersection(set(normalized.split())))
        if overlap >= 2:
            candidates.append((1, overlap, original))
    if candidates:
        candidates.sort(key=lambda x: (-x[0], -x[1], len(x[2]), x[2]))
        return candidates[0][2]
    return None

def detect_seniority(text):
    text = clean_input_text(text)

    if re.search(r"\b(senior|sr\.?|lead|principal|staff)\b", text):
        return "senior"

    if re.search(
        r"\b(mid[- ]?level|midlevel|intermediate)\b",
        text
    ):
        return "mid"

    if re.search(
        r"\b(junior|jr\.?|entry[- ]?level|fresher|graduate|trainee)\b",
        text
    ):
        return "junior"

    experience = extract_experience(text)

    if experience >= 5:
        return "senior"
    if experience >= 2:
        return "mid"

    return "junior"


def extract_resume_text(file):
    text_parts = []

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

    return "\n".join(text_parts)


def calculate_skill_match(resume_skills, job_skills):
    resume_set = {skill.lower() for skill in resume_skills}
    job_set = {skill.lower() for skill in job_skills}

    matched = sorted(resume_set.intersection(job_set))
    missing = sorted(job_set.difference(resume_set))

    ratio = len(matched) / len(job_set) if job_set else 0.0

    return matched, missing, ratio


def build_prediction_features(resume_text, job_description, selected_role):
    resume_text = clean_input_text(resume_text)
    job_description = clean_input_text(job_description)

    resume_skills = set(extract_skills(resume_text))
    required_skills = set(extract_skills(job_description))

    matched_skills = sorted(
        resume_skills.intersection(required_skills)
    )
    missing_skills = sorted(
        required_skills.difference(resume_skills)
    )
    extra_skills = sorted(
        resume_skills.difference(required_skills)
    )

    required_count = len(required_skills)
    match_count = len(matched_skills)
    match_ratio = (
        match_count / required_count
        if required_count
        else 0.0
    )

    resume_role = detect_value(
        resume_text,
        RESUME_ROLES,
        None
    )

    # FIX: the JD determines the target role when it contains clear evidence.
    # If the JD has no identifiable role, the UI selection is used only when it
    # is an actual training category. There is NEVER a job_titles[0] fallback.
    detected_job_role = detect_job_role(job_description)
    effective_job_role = detected_job_role or selected_role or None
    job_title = resolve_training_job_title(effective_job_role, JOB_TITLES)

    resume_industry = detect_value(
        resume_text,
        RESUME_INDUSTRIES,
        RESUME_INDUSTRIES[0] if RESUME_INDUSTRIES else ""
    )

    job_industry = detect_value(
        job_description,
        JOB_INDUSTRIES,
        JOB_INDUSTRIES[0] if JOB_INDUSTRIES else ""
    )

    education = detect_value(
        resume_text,
        EDUCATION_VALUES,
        "unknown"
    )

    resume_seniority = detect_seniority(resume_text)
    job_seniority = detect_seniority(job_description)
    experience = extract_experience(resume_text)

    try:
        resume_seniority_encoded = int(
            label_encoder.transform([resume_seniority])[0]
        )
    except Exception:
        resume_seniority_encoded = 0

    try:
        job_seniority_encoded = int(
            label_encoder.transform([job_seniority])[0]
        )
    except Exception:
        job_seniority_encoded = 0

    numeric_values = {
        "years_experience": experience,
        "skill_count": len(resume_skills),
        "required_skill_count": required_count,
        "seniority_resume_encoded": resume_seniority_encoded,
        "seniority_job_encoded": job_seniority_encoded,
    }

    # Avoid a pandas dependency in the web layer; construct the same column
    # order expected by the saved scaler.
    import pandas as pd

    numeric_df = pd.DataFrame([numeric_values])
    numeric_df = numeric_df.reindex(
        columns=NUMERIC_COLUMNS,
        fill_value=0
    )
    numeric_df[NUMERIC_COLUMNS] = scaler.transform(
        numeric_df[NUMERIC_COLUMNS]
    )

    encoded_df = pd.DataFrame(
        0,
        index=[0],
        columns=ENCODED_COLUMNS
    )

    categorical_values = {
        "role": resume_role,
        "industry_resume": resume_industry,
        "education": education,
        "job_title": job_title,
        "industry_job": job_industry,
    }

    for column, value in categorical_values.items():
        if value is None:
            continue
        encoded_column = f"{column}_{value}"
        if encoded_column in encoded_df.columns:
            encoded_df.loc[0, encoded_column] = 1

    prediction_features = pd.concat(
        [
            numeric_df.reset_index(drop=True),
            encoded_df.reset_index(drop=True),
        ],
        axis=1
    )

    prediction_features["skill_match_count"] = match_count
    prediction_features["skill_match_ratio"] = match_ratio
    prediction_features["seniority_match"] = int(
        resume_seniority == job_seniority
    )
    prediction_features["industry_match"] = int(
        clean_input_text(resume_industry)
        == clean_input_text(job_industry)
    )

    prediction_features = prediction_features.reindex(
        columns=ENGINEERED_COLUMNS,
        fill_value=0
    )

    selected = selector.transform(prediction_features)

    return {
        "selected_features": selected,
        "resume_skills": sorted(resume_skills),
        "job_skills": sorted(required_skills),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "extra_skills": extra_skills,
        "skill_match_ratio": match_ratio,
        "resume_role": resume_role,
        "job_role": detected_job_role or selected_role or "Unknown",
        "training_job_title": job_title,
        "selected_role": selected_role,
        "resume_seniority": resume_seniority,
        "job_seniority": job_seniority,
        "resume_industry": resume_industry,
        "job_industry": job_industry,
        "experience": experience,
    }


def create_summary(info):
    ratio = info["skill_match_ratio"] * 100
    matched_count = len(info["matched_skills"])
    missing_count = len(info["missing_skills"])

    if info["resume_role"] and info["selected_role"]:
        role_text = (
            f"The detected resume role is {info['resume_role']}, "
            f"while the selected target role is {info['selected_role']}."
        )
    else:
        role_text = ""

    if matched_count == 0:
        return (
            f"{role_text} "
            "No detected resume skills currently overlap with the "
            "skills found in the job description."
        ).strip()

    if ratio >= 75:
        return (
            f"{role_text} The resume shows strong detected skill "
            f"coverage, with {matched_count} matched skills."
        ).strip()

    if ratio >= 50:
        return (
            f"{role_text} The resume shows moderate detected skill "
            f"coverage, with {matched_count} matched skills and "
            f"{missing_count} potential gaps."
        ).strip()

    return (
        f"{role_text} The resume currently shows limited detected "
        f"skill coverage, with {missing_count} potential gaps."
    ).strip()


# ---------------------------------------------------------------------------
# MACHINE-LEARNING API
# ---------------------------------------------------------------------------

@app.route("/api/analyze", methods=["POST"])
def analyze():
    try:
        if "resume" not in request.files:
            return jsonify({
                "success": False,
                "message": "Resume PDF is required."
            }), 400

        resume_file = request.files["resume"]

        if not resume_file.filename:
            return jsonify({
                "success": False,
                "message": "Please select a resume."
            }), 400

        job_description = request.form.get(
            "job_description", ""
        ).strip()

        selected_role = request.form.get(
            "target_role", ""
        ).strip()

        if not job_description:
            return jsonify({
                "success": False,
                "message": "Job description is required."
            }), 400

        if selected_role and selected_role not in ROLES:
            return jsonify({
                "success": False,
                "message": "Invalid target role."
            }), 400

        resume_text = extract_resume_text(resume_file)

        if not resume_text.strip():
            return jsonify({
                "success": False,
                "message": "Could not extract text from the PDF."
            }), 400

        info = build_prediction_features(
            resume_text,
            job_description,
            selected_role
        )

        X = info["selected_features"]
        prediction = int(model.predict(X)[0])

        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(X)[0]
            classes = getattr(model, "classes_", None)

            if classes is not None and 1 in classes:
                positive_index = list(classes).index(1)
                match_probability = float(
                    probabilities[positive_index]
                ) * 100
            else:
                match_probability = float(max(probabilities)) * 100
        else:
            match_probability = float(prediction) * 100

        match_probability = max(
            0.0,
            min(100.0, match_probability)
        )

        if match_probability >= 70:
            status = "STRONG MATCH"
        elif match_probability >= 50:
            status = "MODERATE MATCH"
        else:
            status = "LOW MATCH"

        message = (
            "The trained ResuMatch model classified this resume "
            "as a positive match for the selected role."
            if prediction == 1
            else
            "The trained ResuMatch model classified this resume "
            "as a lower match for the selected role."
        )

        result = {
            "prediction": prediction,
            "match_probability": round(match_probability, 2),
            # UI-only score: mirrors Skill Coverage. This does NOT change
            # the trained model prediction/probability above.
            "display_match_score": round(info["skill_match_ratio"] * 100, 2),
            "status": status,
            "message": message,
            "summary": create_summary(info),
            "matched_skills": info["matched_skills"],
            "missing_skills": info["missing_skills"],
            "extra_skills": info["extra_skills"],
            "resume_skill_count": len(info["resume_skills"]),
            "required_skill_count": len(info["job_skills"]),
            "matched_skill_count": len(info["matched_skills"]),
            "skill_match_ratio": round(
                info["skill_match_ratio"], 4
            ),
            "resume_role": info["resume_role"],
            "job_role": info["job_role"],
            "selected_role": selected_role,
            "resume_seniority": info["resume_seniority"],
            "job_seniority": info["job_seniority"],
            "resume_industry": info["resume_industry"],
            "job_industry": info["job_industry"],
            "resume_experience": info["experience"],
            "model": type(model).__name__,
            "feature_count": int(X.shape[1]),
            # Returned so the browser can provide the exact same ML context
            # to the two GenAI functions without recalculating anything.
            "resume_text": resume_text,
        }

        return jsonify({
            "success": True,
            "result": result,
            "resume_text": resume_text,
            "job_description": job_description,
            "target_role": selected_role
        })

    except Exception as error:
        print("\nANALYSIS ERROR:", repr(error))
        return jsonify({
            "success": False,
            "message": "An error occurred while analyzing the resume.",
            "error": str(error)
        }), 500


# ---------------------------------------------------------------------------
# GENERATIVE AI — ONLY THE TWO FUNCTIONS FROM THE NOTEBOOK
# ---------------------------------------------------------------------------

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.8-flash"
)

# Load Gemini configuration from the process environment first.
# If the hosting environment does not provide environment variables,
# also support a local .env file next to app.py.
def load_local_env():
    env_path = os.path.join(BASE_DIR, ".env")
    if not os.path.exists(env_path):
        return

    try:
        with open(env_path, "r", encoding="utf-8") as env_file:
            for raw_line in env_file:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                if (
                    len(value) >= 2
                    and value[0] == value[-1]
                    and value[0] in ('"', "'")
                ):
                    value = value[1:-1]

                # Do not overwrite a real hosting environment variable.
                if key and key not in os.environ:
                    os.environ[key] = value
    except Exception as env_error:
        print(f"Warning: could not read .env file: {env_error}")


load_local_env()

# Read the key AFTER loading .env.
# GEMINI_API_KEY loaded above

gemini_client = None
if genai is not None and GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)


def get_gemini_client():
    """Return the SDK client when google-genai is installed."""
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. Set it as an environment "
            "variable before starting Flask."
        )

    if genai is None or gemini_client is None:
        return None

    return gemini_client


def generate_gemini_text(prompt):
    """
    Generate Gemini text using the google-genai SDK when available.
    If the SDK is missing, fall back to Gemini's HTTPS REST API so the
    website does not fail merely because google-genai is not installed.
    """
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. Set it as an environment "
            "variable before starting Flask."
        )

    client = get_gemini_client()

    # Preferred path: official google-genai Python SDK.
    if client is not None:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        text = getattr(response, "text", None)
        if text:
            return text
        raise RuntimeError("Gemini returned an empty response.")

    # Fallback path: direct Gemini GenerateContent REST API.
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    body = json.dumps(payload).encode("utf-8")
    http_request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(http_request, timeout=90) as response:
            raw = response.read().decode("utf-8")
            data = json.loads(raw)
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Gemini API error ({error.code}): {details}"
        ) from error
    except urllib.error.URLError as error:
        raise RuntimeError(
            f"Could not connect to Gemini API: {error.reason}"
        ) from error

    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError(
            "Gemini returned no candidates. "
            + json.dumps(data, default=str)[:1500]
        )

    parts = (
        candidates[0]
        .get("content", {})
        .get("parts", [])
    )

    text_parts = [
        str(part.get("text", ""))
        for part in parts
        if isinstance(part, dict) and part.get("text")
    ]

    text = "\n".join(text_parts).strip()

    if not text:
        raise RuntimeError("Gemini returned an empty response.")

    return text

def resumatch_genai_analysis(resume, job_description, result):
    """
    Web version of the exact GenAI analysis function from the notebook.
    It explains the existing ML result and does not replace/recalculate it.
    """
    prompt = f"""
You are an AI Resume and Job Matching Assistant called ResuMatch.

Your job is to explain the result produced by an existing machine learning
resume-job matching system.

IMPORTANT:
- Do NOT replace the machine learning prediction.
- Do NOT calculate a new match score.
- Use the ML results provided below as the source of truth.
- Explain WHY the result occurred.
- Clearly distinguish between matched skills and missing skills.
- Explain the candidate's strengths and gaps for this particular job.
- Give practical suggestions for improving the resume or preparing for the role.
- Do not invent skills, experience, projects, qualifications, or job requirements
  that are not present in the provided information.

RESUME
{resume}

JOB DESCRIPTION
{job_description}

RESUMATCH ML RESULT
{json.dumps(result, indent=2, default=str)}

TASK

Provide a clear analysis with the following sections:

1. Overall Result
Explain what the ML model predicted.

2. Match Score
Explain the existing AI Match Score.

3. Why This Result Was Given
Explain the important factors behind the result using the provided
matched and missing skills.

4. Matching Skills
List the important skills that match the job.

5. Missing Skills
List the important skills that are missing from the resume.

6. Candidate Strengths
Explain the candidate's strongest areas for this specific job.

7. Candidate Gaps
Explain the main areas that could be improved.

8. Recommendation
Give practical, job-focused suggestions for improving the resume or
preparing for this role.

Keep the explanation concise, professional and easy to understand.
"""

    return generate_gemini_text(prompt)


def resumatch_chat(resume, job_description, result, question):
    """
    Web-safe version of the notebook chat function.
    The notebook used input() in a loop; the website supplies one question
    per HTTP request instead.
    """
    context = f"""
You are ResuMatch, an AI Resume and Job Matching Assistant.

You are answering questions about a resume-job matching result.

IMPORTANT RULES:
- The ML result below was produced by the ResuMatch model.
- Treat the ML result as the source of truth.
- Do not change or recalculate the prediction.
- Do not invent information.
- Answer only using the resume, job description and model result.
- If something is not available in the provided information, say so.

RESUME
{resume}

JOB DESCRIPTION
{job_description}

RESUMATCH RESULT
{json.dumps(result, indent=2, default=str)}
"""

    prompt = f"""
{context}

USER QUESTION:
{question}

Answer the user's question clearly and specifically.

If the question is about:
- why the candidate matched → explain using matched skills and model result
- why the candidate did not match → explain using missing skills and model result
- the score → explain the existing score, do not calculate a new one
- missing skills → use the missing skills from the model result
- resume improvement → give practical suggestions based on the job
- job suitability → explain the evidence from the model output

Do not contradict the ResuMatch ML result.
"""

    return generate_gemini_text(prompt)


@app.route("/api/genai-analysis", methods=["POST"])
def genai_analysis_api():
    try:
        data = request.get_json(silent=True) or {}

        resume = str(data.get("resume", "")).strip()
        job_description = str(
            data.get("job_description", "")
        ).strip()
        result = data.get("result") or {}

        if not resume or not job_description or not result:
            return jsonify({
                "success": False,
                "message": (
                    "Resume, job description and completed ML result "
                    "are required before GenAI analysis."
                )
            }), 400

        response = resumatch_genai_analysis(
            resume,
            job_description,
            result
        )

        return jsonify({
            "success": True,
            "response": response
        })

    except Exception as error:
        print("\nGENAI ANALYSIS ERROR:", repr(error))
        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


@app.route("/api/chat", methods=["POST"])
def chat_api():
    try:
        data = request.get_json(silent=True) or {}

        resume = str(data.get("resume", "")).strip()
        job_description = str(
            data.get("job_description", "")
        ).strip()
        question = str(data.get("question", "")).strip()
        result = data.get("result") or {}

        if not resume or not job_description or not result:
            return jsonify({
                "success": False,
                "message": (
                    "Run the resume analysis first so the chat has "
                    "the ML result as context."
                )
            }), 400

        if not question:
            return jsonify({
                "success": False,
                "message": "Please enter a question."
            }), 400

        response = resumatch_chat(
            resume,
            job_description,
            result,
            question
        )

        return jsonify({
            "success": True,
            "response": response
        })

    except Exception as error:
        print("\nGENAI CHAT ERROR:", repr(error))
        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


@app.route("/api/health")
def health():
    return jsonify({
        "status": "healthy",
        "model": type(model).__name__,
        "model_features": getattr(model, "n_features_in_", None),
        "selected_features": len(SELECTED_COLUMNS),
        "genai_package": genai is not None,
        "genai_configured": bool(GEMINI_API_KEY),
        "genai_backend": (
            "google-genai SDK" if genai is not None
            else "Gemini REST API fallback"
        ),
        "genai_model": GEMINI_MODEL,
    })


if __name__ == "__main__":
    print("      ResumeMatch Flask Application")
    print(f"Model: {MODEL_PATH}")
    print(f"Model: {type(model).__name__}")
    print(f"Selected features: {len(SELECTED_COLUMNS)}")
    print(f"GenAI package installed: {genai is not None}")
    print(f"GenAI configured: {bool(GEMINI_API_KEY)}")
    print(f"GenAI key source: {GEMINI_KEY_SOURCE}")
    print(f"GenAI backend: {'google-genai SDK' if genai is not None else 'Gemini REST API fallback'}")
    print(f"GenAI model: {GEMINI_MODEL}")
    if not GEMINI_API_KEY:
        print("WARNING: Gemini API key not found.")
        print("Add GEMINI_API_KEY to a .env file beside app.py or set it in the hosting environment.")
    print("Server: http://127.0.0.1:5004")

    app.run(
        host="0.0.0.0",
        port=5006,
        debug=True,
        use_reloader=False
    )
