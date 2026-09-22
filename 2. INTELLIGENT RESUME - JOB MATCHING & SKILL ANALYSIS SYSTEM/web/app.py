from flask import (
    Flask,
    request,
    jsonify,
    render_template
)

import os
import pickle
import re

import pdfplumber


app = Flask(
    __name__,
    template_folder=".",
    static_folder=".",
    static_url_path=""
)


# =========================================================
# LOAD MODEL
# =========================================================

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "model.pkl"
)


with open(
    MODEL_PATH,
    "rb"
) as file:

    model = pickle.load(file)


# =========================================================
# SKILL LIST
# =========================================================

SKILLS = [

    "Python",
    "SQL",
    "Java",
    "C++",
    "JavaScript",

    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",

    "Pandas",
    "NumPy",
    "Scikit-learn",

    "TensorFlow",
    "PyTorch",

    "Flask",
    "Django",

    "REST API",
    "API",

    "Docker",
    "Kubernetes",

    "Git",
    "GitHub",

    "AWS",
    "Azure",
    "GCP",

    "Power BI",
    "Tableau",
    "Excel",

    "Statistics",
    "Data Analysis",
    "Data Science",

    "NLP",
    "Natural Language Processing",

    "Computer Vision",

    "Hugging Face",
    "Transformers",

    "Selenium",
    "BeautifulSoup",

    "Streamlit",

    "MLflow",

    "Feature Engineering",
    "Model Evaluation",

    "Data Preprocessing",
    "Data Cleaning",

    "OOP",
    "Data Structures",
    "Algorithms"

]


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/api/health")
def health():

    return jsonify({
        "status": "healthy",
        "model": "HistGradientBoosting"
    })


# =========================================================
# RESUME TEXT EXTRACTION
# =========================================================

def extract_resume_text(file):

    text = []

    with pdfplumber.open(
        file
    ) as pdf:

        for page in pdf.pages:

            page_text = (
                page.extract_text()
            )

            if page_text:

                text.append(
                    page_text
                )


    return "\n".join(text)



# =========================================================
# SKILL EXTRACTION
# =========================================================

def normalize(text):

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9+#.\s]",
        " ",
        text
    )

    return text



def extract_skills(text):

    normalized =
        normalize(text)

    found = []


    for skill in SKILLS:

        skill_normalized =
            normalize(skill)


        pattern = (
            r"(?<!\w)"
            +
            re.escape(
                skill_normalized
            )
            +
            r"(?!\w)"
        )


        if re.search(
            pattern,
            normalized
        ):

            found.append(
                skill
            )


    return sorted(
        set(found)
    )



# =========================================================
# COMPARE SKILLS
# =========================================================

def compare_skills(
    resume_skills,
    jd_skills
):

    resume_set = {
        skill.lower()
        for skill in resume_skills
    }


    matched = []

    missing = []


    for skill in jd_skills:

        if (
            skill.lower()
            in resume_set
        ):

            matched.append(
                skill
            )

        else:

            missing.append(
                skill
            )


    return matched, missing



# =========================================================
# MODEL FEATURE CREATION
# =========================================================

def build_features(
    resume_text,
    job_description,
    resume_skills,
    jd_skills
):

    # IMPORTANT:
    #
    # This section MUST eventually contain
    # the SAME 20 features used when your
    # model.pkl was trained.
    #
    # Do not randomly create 20 values here.
    #
    # This temporary section is only to show
    # the connection between frontend and model.

    skill_overlap = 0

    if len(jd_skills) > 0:

        skill_overlap = (
            len(
                set(resume_skills)
                &
                set(jd_skills)
            )
            /
            len(jd_skills)
        )


    resume_length =
        len(resume_text)

    jd_length =
        len(job_description)

    matched_count =
        len(
            set(resume_skills)
            &
            set(jd_skills)
        )

    missing_count =
        len(
            set(jd_skills)
            -
            set(resume_skills)
        )


    # -------------------------------------------------
    # DO NOT DEPLOY THIS ARRAY YET
    # -------------------------------------------------

    features = [

        skill_overlap,
        resume_length,
        jd_length,
        matched_count,
        missing_count

    ]


    return features



# =========================================================
# ANALYZE
# =========================================================

@app.route(
    "/api/analyze",
    methods=["POST"]
)

def analyze():

    try:

        # ---------------------------------------------
        # CHECK RESUME
        # ---------------------------------------------

        if "resume" not in request.files:

            return jsonify({
                "error":
                "Please upload a resume."
            }), 400


        resume_file =
            request.files["resume"]


        # ---------------------------------------------
        # CHECK JD
        # ---------------------------------------------

        job_description =
            request.form.get(
                "job_description",
                ""
            ).strip()


        if not job_description:

            return jsonify({
                "error":
                "Please enter the job description."
            }), 400


        # ---------------------------------------------
        # EXTRACT RESUME
        # ---------------------------------------------

        resume_text =
            extract_resume_text(
                resume_file
            )


        if not resume_text.strip():

            return jsonify({
                "error":
                "Could not extract text from the PDF."
            }), 400


        # ---------------------------------------------
        # EXTRACT SKILLS
        # ---------------------------------------------

        resume_skills =
            extract_skills(
                resume_text
            )


        jd_skills =
            extract_skills(
                job_description
            )


        # ---------------------------------------------
        # COMPARE
        # ---------------------------------------------

        matched_skills, missing_skills = \
            compare_skills(
                resume_skills,
                jd_skills
            )


        # ---------------------------------------------
        # MODEL
        # ---------------------------------------------

        features =
            build_features(
                resume_text,
                job_description,
                resume_skills,
                jd_skills
            )


        # ------------------------------------------------
        # IMPORTANT:
        #
        # YOUR ACTUAL MODEL EXPECTS 20 FEATURES.
        #
        # Until we connect the exact feature pipeline
        # from ResumeMatch.ipynb, do NOT call:
        #
        # model.predict(features)
        #
        # because it would be invalid.
        # ------------------------------------------------


        # TEMPORARY DEMO SCORE
        #
        # This is NOT the final ML prediction.

        if len(jd_skills) > 0:

            probability = (
                len(matched_skills)
                /
                len(jd_skills)
            ) * 100

        else:

            probability = 0


        probability =
            round(
                probability,
                2
            )


        prediction =
            1 if probability >= 50 else 0


        # ---------------------------------------------
        # MESSAGE
        # ---------------------------------------------

        if probability >= 80:

            status =
                "Strong Match"

            message =
                "Strong resume–job alignment."

            summary =
                "Your resume demonstrates strong alignment with the requirements detected in this job description."


        elif probability >= 60:

            status =
                "Moderate Match"

            message =
                "Your resume shows moderate alignment."

            summary =
                "Several relevant requirements are present, but some areas could be strengthened."


        elif probability >= 40:

            status =
                "Partial Match"

            message =
                "Your resume has partial alignment."

            summary =
                "Some relevant requirements are present, but several important skills are missing."


        else:

            status =
                "Low Match"

            message =
                "Low alignment with this job description."

            summary =
                "Consider tailoring your resume toward the skills and requirements listed in the role."


        # ---------------------------------------------
        # RETURN JSON
        # ---------------------------------------------

        return jsonify({

            "match_probability":
                probability,

            "prediction":
                prediction,

            "status":
                status,

            "message":
                message,

            "summary":
                summary,

            "matched_skills":
                matched_skills,

            "missing_skills":
                missing_skills,

            "model":
                "HistGradientBoosting"

        })


    except Exception as e:

        print(
            "ERROR:",
            str(e)
        )


        return jsonify({
            "error":
            "Unable to analyze the resume."
        }), 500



# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )