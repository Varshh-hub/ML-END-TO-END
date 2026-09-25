# ResuMatch — Intelligent Resume & Job Matching System

**ResuMatch** is an end-to-end **Machine Learning application for intelligent resume–job matching**, enhanced with Generative AI for result interpretation and career insights.

The system analyzes a candidate's resume against a target job description to determine their level of relevance, identify matched and missing skills, and provide actionable insights for improving their profile.

## Live Demo

**[View ResuMatch](https://YOUR-RESUMATCH-APP.onrender.com)**

*Live deployment coming soon.*

## Project Overview

ResuMatch addresses the challenge of manually evaluating resumes against job requirements. Users can upload a resume in PDF format, select a target role, and provide a job description. The application extracts relevant information and evaluates the compatibility between the candidate and the role using a trained classification model.

The system considers factors such as **skills, experience, seniority, industry, education, and job requirements** rather than relying solely on keyword matching.

## Key Features

* PDF resume upload and text extraction
* Resume–job relevance prediction
* Skill match and skill-gap analysis
* Seniority and industry compatibility analysis
* Target role-based evaluation
* ML-based match scoring
* AI-powered explanation and recommendations
* Resume improvement and learning suggestions
* Interview preparation support
* Interactive web interface

## Machine Learning

The problem is formulated as a **supervised binary classification task**:

```text
1 → Relevant Resume–Job Pair
0 → Non-Relevant Resume–Job Pair
```

The project combines **13,200 resume records, 3,400 job records, and 3,400 matched relationships** to construct **204,000 resume–job pairs** for model development.

### Feature Engineering

Key compatibility features include:

* **Skill Match Count**
* **Skill Match Ratio**
* **Seniority Match**
* **Industry Match**

The preprocessing pipeline includes data cleaning, categorical encoding, feature scaling, correlation analysis, and `SelectKBest` feature selection.

### Models Evaluated

* Logistic Regression
* Decision Tree
* Random Forest
* Extra Trees
* HistGradientBoosting

Models were evaluated using **Accuracy, Precision, Recall, F1 Score, and ROC-AUC**. The final model was selected based on **F1 Score**.

## Model Performance

| Model                | Accuracy | F1 Score | ROC-AUC |
| -------------------- | -------: | -------: | ------: |
| Logistic Regression  |   96.29% |   96.40% |  97.63% |
| Decision Tree        |   97.50% |   97.56% |  98.28% |
| Random Forest        |   97.51% |   97.57% |  98.29% |
| Extra Trees          |   97.50% |   97.56% |  98.28% |
| HistGradientBoosting |   97.51% |   97.57% |  98.33% |

*Evaluation results are based on the constructed dataset and its resume–job pair generation strategy.*

## Generative AI

The application includes a **Google Gemini-powered intelligence layer** that works alongside the ML model.

It uses the resume, job description, and ML result to provide:

* Match-result explanations
* Resume strengths and skill gaps
* Improvement recommendations
* Learning suggestions
* Interview questions
* Interactive career assistance

The **ML model remains responsible for the prediction**, while Generative AI is used to explain and extend the result.

## Technology Stack

**Machine Learning:** Python, Pandas, NumPy, Scikit-learn
**NLP & Processing:** Skill extraction, skill normalization, pdfplumber
**Backend:** Flask, REST APIs
**Frontend:** HTML, CSS, JavaScript
**Model Persistence:** Joblib
**Generative AI:** Google Gemini
**Deployment:** Render
**Development:** Jupyter Notebook, VS Code, Git, GitHub

## Project Structure

```text
ResuMatch/
├── app.py
├── index.html
├── styles.css
├── script.js
├── resumatch_model.pkl
├── Resume.csv
├── Jobs.csv
├── matches.csv
├── requirements.txt
├── notebook/
│   └── ResuMatch_Model.ipynb
└── README.md
```

## Running Locally

```bash
git clone YOUR-GITHUB-REPOSITORY-URL
cd ResuMatch
pip install -r requirements.txt
python app.py
```

The application can then be accessed locally through the Flask server.

## Deployment

The application is deployment-ready for **Render**.

**Build Command**

```bash
pip install -r requirements.txt
```

**Start Command**

```bash
gunicorn app:app
```

## Author

**Varsha**
B.Sc. Artificial Intelligence & Machine Learning
Aspiring Machine Learning Engineer
