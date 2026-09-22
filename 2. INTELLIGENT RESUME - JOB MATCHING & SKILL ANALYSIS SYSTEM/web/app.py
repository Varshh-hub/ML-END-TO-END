from flask import Flask, request, jsonify, render_template
import os
import re
import pickle
import pdfplumber
import numpy as np


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")


app = Flask(
    __name__,
    template_folder=BASE_DIR,
    static_folder=BASE_DIR,
    static_url_path=""
)


# ---------------------------------------------------------
# LOAD THE ACTUAL TRAINED MODEL
# ---------------------------------------------------------

with open(MODEL_PATH, "rb") as file:
    model = pickle.load(file)


# ---------------------------------------------------------
# MODEL FEATURES
# ---------------------------------------------------------

SELECTED_FEATURES = [

    "skill_count",

    "role_Associate Product Manager",
    "role_BI Analyst",
    "role_Business Analyst",
    "role_Computer Vision Engineer",
    "role_Cybersecurity Analyst",
    "role_Data Analyst",
    "role_Data Scientist",
    "role_DevOps Engineer",
    "role_Generative AI Engineer",
    "role_Machine Learning Engineer",
    "role_NLP Engineer",
    "role_Performance Marketer",
    "role_Product Manager",
    "role_Software Engineer",
    "role_Technical Product Manager",

    "skill_match_count",
    "skill_match_ratio",
    "seniority_match",
    "industry_match",
]


# ---------------------------------------------------------
# SUPPORTED ROLES
# ---------------------------------------------------------

ROLES = [

    "Associate Product Manager",

    "BI Analyst",

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


SUPPORTED_ROLE_SET = set(ROLES)


# ---------------------------------------------------------
# ROLE ALIASES
# ---------------------------------------------------------

ROLE_ALIASES = {

    "Associate Product Manager": [
        "associate product manager",
        "associate product",
        "apm",
    ],

    "BI Analyst": [
        "bi analyst",
        "business intelligence analyst",
        "business intelligence",
    ],

    "Business Analyst": [
        "business analyst",
        "business analysis",
    ],

    "Computer Vision Engineer": [
        "computer vision engineer",
        "computer vision",
        "cv engineer",
    ],

    "Cybersecurity Analyst": [
        "cybersecurity analyst",
        "cyber security analyst",
        "security analyst",
    ],

    "Data Analyst": [
        "data analyst",
        "data analytics",
        "analytics analyst",
    ],

    "Data Scientist": [
        "data scientist",
        "data science",
    ],

    "DevOps Engineer": [
        "devops engineer",
        "devops",
    ],

    "Generative AI Engineer": [
        "generative ai engineer",
        "generative ai",
        "genai engineer",
        "gen ai engineer",
    ],

    "Machine Learning Engineer": [
        "machine learning engineer",
        "ml engineer",
        "machine learning",
    ],

    "NLP Engineer": [
        "nlp engineer",
        "natural language processing engineer",
        "nlp",
    ],

    "Performance Marketer": [
        "performance marketer",
        "performance marketing",
    ],

    "Product Manager": [
        "product manager",
        "product management",
    ],

    "Software Engineer": [
        "software engineer",
        "software developer",
        "software development",
    ],

    "Technical Product Manager": [
        "technical product manager",
        "technical product",
    ],
}


# ---------------------------------------------------------
# SKILLS
# ---------------------------------------------------------

SKILLS = [

    "python",
    "sql",
    "java",
    "c++",
    "javascript",

    "machine learning",
    "deep learning",
    "artificial intelligence",

    "pandas",
    "numpy",
    "scikit-learn",

    "tensorflow",
    "pytorch",

    "flask",
    "django",

    "rest api",
    "api",

    "docker",
    "kubernetes",

    "git",
    "github",

    "aws",
    "azure",
    "gcp",

    "power bi",
    "tableau",
    "excel",

    "statistics",
    "data analysis",
    "data science",

    "nlp",
    "natural language processing",

    "computer vision",

    "hugging face",
    "transformers",

    "selenium",
    "beautifulsoup",

    "streamlit",
    "mlflow",

    "feature engineering",
    "model evaluation",
    "data preprocessing",
    "data cleaning",

    "object oriented programming",
    "oop",

    "data structures",
    "algorithms",
]


# ---------------------------------------------------------
# SENIORITY
# ---------------------------------------------------------

SENIORITY_TERMS = {

    "junior": [
        "junior",
        "entry level",
        "entry-level",
        "fresher",
        "graduate",
    ],

    "mid": [
        "mid level",
        "mid-level",
        "midlevel",
    ],

    "senior": [
        "senior",
        "lead",
        "principal",
    ],
}


# ---------------------------------------------------------
# INDUSTRIES
# ---------------------------------------------------------

INDUSTRIES = [

    "retail",
    "healthcare",
    "finance",
    "banking",
    "technology",
    "software",
    "education",
    "manufacturing",
    "marketing",
    "telecommunications",
    "telecom",
    "automotive",
    "e-commerce",
    "ecommerce",
    "insurance",
    "media",
    "consulting",
    "logistics",
    "travel",
    "hospitality",
]


# ---------------------------------------------------------
# TEXT NORMALIZATION
# ---------------------------------------------------------

def normalize(text):

    text = str(text).lower()

    text = text.replace(
        "&",
        " and "
    )

    text = re.sub(
        r"[^a-z0-9+#.\s-]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ---------------------------------------------------------
# PHRASE MATCHING
# ---------------------------------------------------------

def contains_phrase(
    text,
    phrase
):

    text = normalize(text)

    phrase = normalize(phrase)

    return bool(
        re.search(
            r"(?<!\w)"
            + re.escape(phrase)
            + r"(?!\w)",
            text
        )
    )


# ---------------------------------------------------------
# SKILL EXTRACTION
# ---------------------------------------------------------

def extract_skills(text):

    normalized = normalize(text)

    found = []


    # Longer phrases first
    for skill in sorted(
        SKILLS,
        key=len,
        reverse=True
    ):

        if re.search(
            r"(?<!\w)"
            + re.escape(
                normalize(skill)
            )
            + r"(?!\w)",
            normalized
        ):

            found.append(skill)


    return sorted(
        set(found)
    )


# ---------------------------------------------------------
# ROLE INFERENCE
# ---------------------------------------------------------

def infer_role(text):

    normalized = normalize(text)

    candidates = []


    for role, aliases in ROLE_ALIASES.items():

        for alias in aliases:

            if re.search(
                r"(?<!\w)"
                + re.escape(
                    normalize(alias)
                )
                + r"(?!\w)",
                normalized
            ):

                candidates.append(
                    (
                        len(
                            normalize(alias)
                        ),
                        role
                    )
                )


    if not candidates:

        return None


    # Prefer longest matching phrase
    candidates.sort(
        reverse=True
    )


    return candidates[0][1]


# ---------------------------------------------------------
# SENIORITY INFERENCE
# ---------------------------------------------------------

def infer_seniority(text):

    normalized = normalize(text)


    for level, terms in SENIORITY_TERMS.items():

        for term in terms:

            if re.search(
                r"(?<!\w)"
                + re.escape(
                    normalize(term)
                )
                + r"(?!\w)",
                normalized
            ):

                return level


    return None


# ---------------------------------------------------------
# INDUSTRY INFERENCE
# ---------------------------------------------------------

def infer_industry(text):

    normalized = normalize(text)


    for industry in INDUSTRIES:

        if re.search(
            r"(?<!\w)"
            + re.escape(
                normalize(industry)
            )
            + r"(?!\w)",
            normalized
        ):

            return industry


    return None


# ---------------------------------------------------------
# PDF TEXT EXTRACTION
# ---------------------------------------------------------

def extract_resume_text(file):

    pages = []


    with pdfplumber.open(file) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()


            if page_text:

                pages.append(
                    page_text
                )


    return "\n".join(
        pages
    ).strip()


# ---------------------------------------------------------
# BUILD MODEL FEATURES
# ---------------------------------------------------------

def build_model_features(
    resume_text,
    job_description,
):

    resume_skills = extract_skills(
            resume_text
        )

    job_skills = extract_skills(
            job_description
        )


    resume_skill_set = set(resume_skills)

    job_skill_set = set(job_skills)


    matched_skills = sorted(
            resume_skill_set
            &
            job_skill_set
        )


    missing_skills = sorted(
            job_skill_set
            -
            resume_skill_set
        )


    resume_role = infer_role(
            resume_text
        )


    job_role = infer_role(
            job_description
        )


    resume_seniority = infer_seniority(
            resume_text
        )


    job_seniority = infer_seniority(
            job_description
        )


    resume_industry = infer_industry(
            resume_text
        )


    job_industry = infer_industry(
            job_description
        )


    skill_match_count = len(
            matched_skills
        )


    skill_match_ratio = (

        skill_match_count
        /
        len(job_skills)

        if job_skills

        else 0.0
    )


    seniority_match = int(

        resume_seniority
        is not None

        and

        job_seniority
        is not None

        and

        resume_seniority == job_seniority
    )


    industry_match = int(

        resume_industry
        is not None

        and

        job_industry
        is not None

        and

        resume_industry == job_industry
    )


    features = {

        feature: 0.0

        for feature
        in SELECTED_FEATURES

    }


    features[
        "skill_count"
    ] = float(
        len(resume_skills)
    )


    if resume_role:

        role_feature = f"role_{resume_role}"


        if role_feature in features:

            features[
                role_feature
            ] = 1.0


    features[
        "skill_match_count"
    ] = float(
        skill_match_count
    )


    features[
        "skill_match_ratio"
    ] = float(
        skill_match_ratio
    )


    features[
        "seniority_match"
    ] = float(
        seniority_match
    )


    features[
        "industry_match"
    ] = float(
        industry_match
    )


    X = np.array(

        [
            [
                features[name]

                for name
                in SELECTED_FEATURES
            ]
        ],

        dtype=float
    )


    return (

        X,

        resume_skills,

        job_skills,

        matched_skills,

        missing_skills,

        resume_role,

        job_role,

        resume_seniority,

        job_seniority,

        resume_industry,

        job_industry,

    )


# ---------------------------------------------------------
# SCREENING MESSAGE
# ---------------------------------------------------------

def screening_message(
    probability
):

    """
    The model predicts resume-job relevance,
    not an actual recruiter decision.
    """

    if probability >= 80:

        return (

            "Strong model-estimated alignment",

            "This resume shows strong alignment "
            "with the job requirements detected "
            "by the model and is well positioned "
            "for initial screening."

        )


    if probability >= 60:

        return (

            "Good model-estimated alignment",

            "This resume shows several relevant "
            "matches and may have reasonable "
            "alignment for initial screening, "
            "with some areas to strengthen."

        )


    if probability >= 40:

        return (

            "Partial model-estimated alignment",

            "This resume matches some of the "
            "detected requirements, but "
            "strengthening the missing skills "
            "could improve alignment."

        )


    return (

        "Low model-estimated alignment",

        "The model found limited alignment "
        "with the detected job requirements. "
        "Tailoring the resume to the role "
        "may improve its match."

    )


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ---------------------------------------------------------
# HEALTH
# ---------------------------------------------------------

@app.route("/api/health")
def health():

    return jsonify(

        {
            "status": "healthy",

            "model":
                "HistGradientBoosting",

            "features":
                len(
                    SELECTED_FEATURES
                ),

            "supported_roles":
                ROLES,
        }

    )


# ---------------------------------------------------------
# ANALYZE
# ---------------------------------------------------------

@app.route(
    "/api/analyze",
    methods=["POST"]
)
def analyze():

    try:

        # ---------------------------------------------
        # RESUME
        # ---------------------------------------------

        if "resume" not in request.files:

            return jsonify(
                {
                    "error":
                        "Please upload a PDF resume."
                }
            ), 400


        resume_file = request.files["resume"]


        # ---------------------------------------------
        # JOB DESCRIPTION
        # ---------------------------------------------

        job_description = request.form.get(
                "job_description",
                ""
            ).strip()


        # ---------------------------------------------
        # SELECTED ROLE
        # ---------------------------------------------

        target_role = request.form.get(
                "target_role",
                ""
            ).strip()


        # ---------------------------------------------
        # ROLE VALIDATION
        # ---------------------------------------------

        if not target_role:

            return jsonify(
                {
                    "error":
                        "Please select the role you want to apply for."
                }
            ), 400


        if target_role not in SUPPORTED_ROLE_SET:

            return jsonify(
                {
                    "error":
                        (
                            "This role is not supported "
                            "by the trained model. "
                            "Please select one of the "
                            "available roles."
                        )
                }
            ), 400


        # ---------------------------------------------
        # JOB DESCRIPTION VALIDATION
        # ---------------------------------------------

        if not job_description:

            return jsonify(
                {
                    "error":
                        "Please paste the job description."
                }
            ), 400


        # ---------------------------------------------
        # PDF VALIDATION
        # ---------------------------------------------

        if not resume_file.filename.lower().endswith(
            ".pdf"
        ):

            return jsonify(
                {
                    "error":
                        "Only PDF resumes are supported."
                }
            ), 400


        # ---------------------------------------------
        # EXTRACT RESUME
        # ---------------------------------------------

        resume_text = extract_resume_text(
                resume_file
            )


        if not resume_text:

            return jsonify(
                {
                    "error":
                        (
                            "Could not extract text "
                            "from this PDF. Please use "
                            "a text-based PDF rather than "
                            "a scanned image PDF."
                        )
                }
            ), 400


        # ---------------------------------------------
        # BUILD FEATURES
        # ---------------------------------------------

        (
            X,

            resume_skills,

            job_skills,

            matched_skills,

            missing_skills,

            resume_role,

            job_role,

            resume_seniority,

            job_seniority,

            resume_industry,

            job_industry,

        ) = build_model_features(

            resume_text,

            job_description,

        )


        # ---------------------------------------------
        # ROLE CONSISTENCY CHECK
        # ---------------------------------------------

        if (
            job_role
            and
            job_role != target_role
        ):

            return jsonify(
                {
                    "error":
                        (
                            f"The selected role is "
                            f"'{target_role}', but the "
                            f"pasted job description "
                            f"appears to be for "
                            f"'{job_role}'. Please "
                            f"select the role that "
                            f"matches the job description."
                        )
                }
            ), 400


        # ---------------------------------------------
        # MODEL INPUT SAFETY CHECK
        # ---------------------------------------------

        if getattr(
            model,
            "n_features_in_",
            X.shape[1]
        ) != X.shape[1]:

            return jsonify(
                {
                    "error":
                        (
                            "Model input mismatch. "

                            f"The saved model expects "
                            f"{model.n_features_in_} "
                            f"features, but the "
                            f"application created "
                            f"{X.shape[1]}."
                        )
                }
            ), 500


        # ---------------------------------------------
        # PREDICTION
        # ---------------------------------------------

        prediction = int(
                model.predict(X)[0]
            )


        probability = float(
                model.predict_proba(X)[0][1]
            )


        percentage = round(
                probability * 100,
                2
            )


        # ---------------------------------------------
        # SCREENING MESSAGE
        # ---------------------------------------------

        status, message = screening_message(
                percentage
            )


        # ---------------------------------------------
        # RESPONSE
        # ---------------------------------------------

        return jsonify(

            {

                "match_probability":
                    percentage,

                "prediction":
                    prediction,

                "status":
                    status,

                "message":
                    message,

                "summary":
                    (
                        "Relevant"

                        if prediction == 1

                        else

                        "Not Relevant"
                    ),

                "matched_skills":
                    matched_skills,

                "missing_skills":
                    missing_skills,

                "resume_skill_count":
                    len(resume_skills),

                "required_skill_count":
                    len(job_skills),

                "matched_skill_count":
                    len(matched_skills),

                "skill_match_ratio":
                    round(

                        (
                            len(matched_skills)
                            /
                            len(job_skills)
                            *
                            100
                        )

                        if job_skills

                        else

                        0,

                        2
                    ),

                "resume_role":
                    resume_role
                    or
                    "Not detected",

                "job_role":
                    job_role
                    or
                    target_role,

                "selected_role":
                    target_role,

                "resume_seniority":
                    resume_seniority
                    or
                    "Not detected",

                "job_seniority":
                    job_seniority
                    or
                    "Not detected",

                "resume_industry":
                    resume_industry
                    or
                    "Not detected",

                "job_industry":
                    job_industry
                    or
                    "Not detected",

                "model":
                    "HistGradientBoosting",

                "feature_count":
                    len(
                        SELECTED_FEATURES
                    ),

            }

        )


    except Exception as exc:

        app.logger.exception(
            "Analysis failed"
        )


        return jsonify(

            {

                "error":
                    (
                        "Unable to analyze "
                        "the resume. "

                        f"Details: {str(exc)}"
                    )

            }

        ), 500


# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5002,

        debug=True

    )