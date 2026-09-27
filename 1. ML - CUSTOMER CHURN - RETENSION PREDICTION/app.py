from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd


# --------------------------------------------------
# Flask App Configuration
# --------------------------------------------------

app = Flask(
    __name__,
    template_folder="web",
    static_folder="web"
)

CORS(app)


# --------------------------------------------------
# Load Trained ML Model
# --------------------------------------------------

model = joblib.load("final_churn_model.pkl")


# --------------------------------------------------
# Home Page
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# Prediction API
# --------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json()

    try:

        customer = pd.DataFrame([{
            "Age": float(data["Age"]),
            "Gender": data["Gender"],
            "Tenure": float(data["Tenure"]),
            "Usage Frequency": float(data["Usage Frequency"]),
            "Support Calls": float(data["Support Calls"]),
            "Payment Delay": float(data["Payment Delay"]),
            "Subscription Type": data["Subscription Type"],
            "Contract Length": data["Contract Length"],
            "Total Spend": float(data["Total Spend"]),
            "Last Interaction": float(data["Last Interaction"])
        }])


        # Model prediction
        prediction = model.predict(customer)[0]

        # Probability of churn
        probability = model.predict_proba(customer)[0][1]

        probability_percent = round(probability * 100, 2)


        # --------------------------------------------------
        # Risk Level + Retention Recommendation
        # --------------------------------------------------

        if probability >= 0.70:

            risk = "HIGH RISK"

            recommendation = [
                "Prioritize this customer for retention outreach.",
                "Consider a personalized retention offer.",
                "Review recent support and payment issues."
            ]

        elif probability >= 0.40:

            risk = "MEDIUM RISK"

            recommendation = [
                "Monitor customer engagement closely.",
                "Consider a proactive support message.",
                "Offer a relevant loyalty incentive."
            ]

        else:

            risk = "LOW RISK"

            recommendation = [
                "Continue normal customer engagement.",
                "Maintain service quality.",
                "Monitor for changes in usage behaviour."
            ]


        # --------------------------------------------------
        # Send Result Back to Frontend
        # --------------------------------------------------

        return jsonify({
            "prediction": int(prediction),
            "probability": probability_percent,
            "risk": risk,
            "recommendation": recommendation
        })


    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 400


# --------------------------------------------------
# Run Flask Application
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)