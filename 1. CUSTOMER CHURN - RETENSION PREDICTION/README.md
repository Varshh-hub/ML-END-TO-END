# Customer Churn & Retention Prediction

An end-to-end machine learning application that predicts whether a customer is at risk of churning and provides a probability-based risk assessment through an interactive web interface.

**Live Demo:** https://churn-retension-prediction-ml.onrender.com/

---

## Overview

Customer churn is a major business challenge, as retaining existing customers can often be more valuable than acquiring new ones.

This project implements an end-to-end **customer churn prediction system**, covering the complete machine learning workflow from data exploration and preprocessing to model training, evaluation, serialization, API development, containerization, and cloud deployment.

The trained **Logistic Regression** model is integrated with a **Flask backend** and connected to a web interface where users can enter customer information and receive a churn prediction, estimated probability, and corresponding risk level.

---

## Key Features

* Customer churn prediction
* Probability-based churn risk assessment
* Low Risk / High Risk classification
* Interactive web interface
* Flask backend
* REST-style prediction API
* Pre-trained machine learning model
* Model serialization using Joblib
* Dockerized application
* Cloud deployment using Render

---

## Machine Learning Development

### 1. Exploratory Data Analysis

The dataset was explored to understand the structure of the customer data and identify patterns associated with customer churn.

The analysis included:

* Understanding the dataset structure and features
* Examining numerical and categorical variables
* Analyzing the target variable distribution
* Identifying relationships between customer attributes and churn
* Visualizing relevant features and churn patterns

### 2. Data Cleaning

The dataset was cleaned and prepared before model training.

The cleaning process included:

* Checking for missing values
* Checking for duplicate records
* Examining data types
* Identifying unnecessary or inconsistent data
* Preparing the dataset for preprocessing

### 3. Data Preprocessing

The cleaned data was transformed into a format suitable for machine learning.

The preprocessing workflow included:

* Separating input features and the target variable
* Encoding categorical variables
* Processing numerical features
* Splitting the data into training and testing sets
* Applying the required feature transformations

### 4. Model Training

A **Logistic Regression** model was trained for the customer churn classification task.

Logistic Regression was selected because customer churn is a **binary classification problem**, where the model predicts whether a customer is likely to churn.

The model also provides a probability score, which is used by the application to determine the customer's churn risk level.

### 5. Model Evaluation

The trained model was evaluated using the test dataset.

The evaluation included:

* Accuracy
* Precision
* Recall
* F1-score
* Confusion Matrix

These metrics were used to assess the model's classification performance.

### 6. Model Tuning

The Logistic Regression model was tuned to identify suitable model parameters and improve its classification performance.

The final model was selected based on its evaluation results.

### 7. Model Serialization

After training and evaluation, the final Logistic Regression model was serialized using **Joblib**.

The trained model is stored as:

```text
final_churn_model.pkl
```

The serialized model is later loaded by the Flask application to generate predictions for new customer inputs.

---

## Machine Learning Workflow

```text
Raw Customer Data
       |
       v
Exploratory Data Analysis
       |
       v
Data Cleaning
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
Model Tuning
       |
       v
Model Serialization
       |
       v
Flask Application
       |
       v
Prediction API
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

* Python
* Pandas
* Scikit-learn
* Joblib
* Jupyter Notebook

### Backend

* Flask
* Flask-CORS
* Gunicorn

### Frontend

* HTML
* CSS
* JavaScript

### Deployment

* Docker
* Render

---

## Project Structure

```text
1. CUSTOMER CHURN - RETENSION PREDICTION/
│
├── web/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── app.py
├── Dockerfile
├── requirements.txt
│
├── churn_train.csv
├── churn_test.csv
├── final_churn_model.pkl
│
├── prediction.ipynb
└── README.md
```

---

## Live Application

The application is deployed and publicly accessible through Render.

**Live Demo:**
https://churn-retension-prediction-ml.onrender.com/

The web application allows users to enter customer information and receive a machine learning prediction without requiring the project to be run locally.

---

## Prediction API

The Flask application exposes a prediction endpoint for generating churn predictions.

### Endpoint

```text
POST /predict
```

The endpoint accepts customer information and returns:

* Churn prediction
* Estimated churn probability
* Risk classification

### Example Response

```json
{
    "prediction": 1,
    "probability": 95.35,
    "risk": "HIGH RISK"
}
```

### Response Explanation

| Field         | Description                             |
| ------------- | --------------------------------------- |
| `prediction`  | `1` indicates predicted churn           |
| `probability` | Estimated probability of customer churn |
| `risk`        | User-friendly churn risk classification |

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

The application will be available at:

```text
http://localhost:5000
```

---

## Run with Docker

### Build the Docker Image

```bash
docker build -t customer-churn-app .
```

### Run the Container

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

```text
churn_train.csv
churn_test.csv
```

The datasets are used during model development and evaluation.

---

## Trained Model

The final trained model is stored as:

```text
final_churn_model.pkl
```

The Flask backend loads this serialized model during runtime and uses it to generate predictions for new customer inputs.

---

## Jupyter Notebook

The machine learning development process is documented in:

```text
prediction.ipynb
```

The notebook contains the data exploration, preprocessing, model development, evaluation, tuning, and prediction workflow used during the project.

---

## Project Objective

The objective of this project is to demonstrate how a machine learning model can be developed and transformed into a usable end-to-end application.

Rather than stopping at model training, the project covers the complete pipeline:

```text
Data
  ↓
Machine Learning Model
  ↓
Model Serialization
  ↓
Flask API
  ↓
Web Interface
  ↓
Docker
  ↓
Cloud Deployment
```

This demonstrates practical exposure to both **machine learning development and application deployment**.

---

## Project Links

* **Live Application:** https://churn-retension-prediction-ml.onrender.com/
* **GitHub Repository:** https://github.com/Varshh-hub/MACHINE-LEARNING---END-TO-END--BEST-3-

---

## Author

**Varsha A.**

Machine Learning | Python | Data Science | AI

---

## License

This project is intended for **educational and portfolio purposes**.
