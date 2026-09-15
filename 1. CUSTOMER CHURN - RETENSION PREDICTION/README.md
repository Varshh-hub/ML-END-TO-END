# Customer Churn & Retention Prediction

An end-to-end machine learning application that predicts whether a customer is at risk of churning and provides a probability-based risk assessment through a web interface.

**Live Demo:** https://churn-retension-prediction-ml.onrender.com/

---

## Overview

Customer churn is a major business problem because retaining an existing customer is often more valuable than acquiring a new one.

This project builds a complete machine learning workflow for customer churn prediction, from data exploration and model development to deployment as an interactive web application.

The trained machine learning model is integrated with a Flask backend and served through a web interface where users can enter customer information and receive a churn prediction.

---

## Features

- Customer churn prediction
- Probability-based risk assessment
- Risk classification such as Low Risk / High Risk
- Interactive web interface
- Flask-based backend
- Pre-trained machine learning model
- Dockerized application
- Cloud deployment using Render
- Prediction API endpoint

---

## Machine Learning Workflow

The project follows an end-to-end machine learning workflow:

```text
Raw Customer Data
       |
       v
Data Exploration
       |
       v
Data Preprocessing
       |
       v
Model Training
       |
       v
Model Evaluation
       |
       v
Model Serialization
       |
       v
Flask Application
       |
       v
Docker Container
       |
       v
Render Deployment
       |
       v
Live Web Application
```

---

## Tech Stack

### Machine Learning

- Python
- Pandas
- Scikit-learn
- Joblib
- Jupyter Notebook

### Backend

- Flask
- Flask-CORS
- Gunicorn

### Frontend

- HTML
- CSS
- JavaScript

### Deployment

- Docker
- Render

---

## Project Structure

```text
1. CUSTOMER CHURN - RETENSION PREDICTION/
|
├── web/
│   ├── index.html
│   ├── style.css
│   └── script.js
|
├── app.py
├── Dockerfile
├── requirements.txt
|
├── churn_train.csv
├── churn_test.csv
├── final_churn_model.pkl
|
├── prediction.ipynb
└── README.md
```

---

## Live Application

The application is deployed and publicly accessible:

**https://churn-retension-prediction-ml.onrender.com/**

The deployed application allows users to enter customer information and receive a machine learning prediction without needing to run the project locally.

---

## Prediction API

The Flask application also exposes a prediction endpoint.

### Endpoint

```text
POST /predict
```

The endpoint accepts customer information and returns a prediction along with the estimated probability and risk level.

Example response:

```json
{
    "prediction": 1,
    "probability": 95.35,
    "risk": "HIGH RISK"
}
```

Where:

- `prediction = 1` indicates predicted churn
- `probability` represents the model's estimated churn probability
- `risk` provides an easier-to-understand risk classification

---

## Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/Varshh-hub/MACHINE-LEARNING---END-TO-END--BEST-3-.git
```

### 2. Navigate to the Project

```bash
cd "1. CUSTOMER CHURN - RETENSION PREDICTION"
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Flask Application

```bash
python app.py
```

The application will be available locally at:

```text
http://localhost:5000
```

---

## Run with Docker

Build the Docker image:

```bash
docker build -t customer-churn-app .
```

Run the container:

```bash
docker run -p 5001:5000 customer-churn-app
```

The application can then be accessed at:

```text
http://localhost:5001
```

---

## Dataset

The project contains separate training and testing datasets:

- `churn_train.csv`
- `churn_test.csv`

These datasets are used during the model development and evaluation process.

---

## Trained Model

The trained machine learning model is stored as:

```text
final_churn_model.pkl
```

The Flask application loads this serialized model during runtime and uses it to generate predictions for new customer inputs.

---

## Notebook

The machine learning development process is documented in:

```text
prediction.ipynb
```

The notebook contains the experimentation and prediction workflow used during development.

---

## Project Goal

The goal of this project is not only to train a machine learning model, but also to demonstrate how a machine learning model can be taken from experimentation to a usable production-style application.

The complete pipeline covers:

```text
Data → Model → API → Web Interface → Docker → Cloud Deployment
```

---

## Links

- Live Application: https://churn-retension-prediction-ml.onrender.com/
- GitHub Repository: https://github.com/Varshh-hub/MACHINE-LEARNING---END-TO-END--BEST-3-

---

## Author

**Varsha A.**

Machine Learning | Python | Data Science | AI

---

## License

This project is intended for educational and portfolio purposes.
