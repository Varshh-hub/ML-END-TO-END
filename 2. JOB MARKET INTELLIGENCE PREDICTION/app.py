from flask import Flask, request, jsonify, send_from_directory
import joblib
import numpy as np
import os

app = Flask(__name__, static_folder="web", static_url_path="")

# --------------------------------------------------
# Load ML model
# --------------------------------------------------

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "job_market_model.pkl"
)

model = joblib.load(MODEL_PATH)


# --------------------------------------------------
# Home page
# --------------------------------------------------

@app.route("/")
def home():
    return send_from_directory("web", "index.html")


# --------------------------------------------------
# Prediction API
# --------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():

    try:
        data = request.get_json()

        description = data.get("description", "").strip()

        if not description:
            return jsonify({
                "error": "Please enter a job description."
            }), 400

        # Prediction
        prediction = model.predict([description])[0]

        # LinearSVC decision scores
        decision_scores = model.decision_function([description])[0]

        # Handle binary classification safely
        if np.ndim(decision_scores) == 0:
            decision_scores = np.array([decision_scores])

        classes = model.classes_

        # Sort highest scores first
        ranked_indices = np.argsort(decision_scores)[::-1]

        top_predictions = []

        for index in ranked_indices[:5]:
            top_predictions.append({
                "role": str(classes[index]),
                "score": round(float(decision_scores[index]), 4)
            })

        # --------------------------------------------------
        # Convert decision scores into a relative percentage
        # --------------------------------------------------
        scores = np.array(decision_scores, dtype=float)

        # Softmax-like transformation for UI visualization.
        # This is NOT a calibrated probability.
        exp_scores = np.exp(scores - np.max(scores))
        relative_scores = exp_scores / exp_scores.sum()

        prediction_index = np.where(classes == prediction)[0][0]

        confidence = float(relative_scores[prediction_index] * 100)

        # Keep UI confidence sensible
        confidence = min(max(confidence, 0), 100)

        return jsonify({
            "prediction": str(prediction),
            "confidence": round(confidence, 1),
            "top_predictions": top_predictions
        })

    except Exception as e:

        print("Prediction error:", e)

        return jsonify({
            "error": "Something went wrong while analyzing the description."
        }), 500


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.route("/health")
def health():
    return jsonify({
        "status": "online",
        "model": "Job Market Intelligence"
    })


# --------------------------------------------------
# Run Flask
# --------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)