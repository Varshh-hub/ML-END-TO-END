from flask import Flask, jsonify, request, send_from_directory
import pickle
import pandas as pd
import os

app = Flask(
    __name__,
    static_folder="web",
    static_url_path=""
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_DIR = os.path.join(BASE_DIR, "models")
WEB_DIR = os.path.join(BASE_DIR, "web")

recommendation_model_path = os.path.join(
    MODEL_DIR,
    "food_recommendation_model.pkl"
)

with open(recommendation_model_path, "rb") as file:
    recommendation_model = pickle.load(file)

rules = recommendation_model["rules"]

print("Recommendation model loaded successfully.")
print("Association rules:", len(rules))

forecast_model_path = os.path.join(
    MODEL_DIR,
    "food_forecasting_models.pkl"
)

with open(forecast_model_path, "rb") as file:
    forecast_models = pickle.load(file)

order_model = forecast_models["order_model"]
sales_model = forecast_models["sales_model"]

order_forecast_df = forecast_models.get(
    "order_forecast",
    pd.DataFrame()
)

sales_forecast_df = forecast_models.get(
    "sales_forecast",
    pd.DataFrame()
)

print("Forecasting models loaded successfully.")

def recommend_food(item, top_n=5):

    if rules.empty:
        return []

    item = str(item).strip()

    recommendations = []

    for _, rule in rules.iterrows():

        antecedents = set(rule["antecedents"])
        consequents = set(rule["consequents"])

        if item.lower() in {
            str(x).lower() for x in antecedents
        }:

            for food in consequents:

                recommendations.append({
                    "FoodItem": str(food),
                    "Confidence": round(
                        float(rule["confidence"]) * 100,
                        2
                    ),
                    "Lift": round(
                        float(rule["lift"]),
                        2
                    ),
                    "Support": round(
                        float(rule["support"]) * 100,
                        2
                    )
                })

    if not recommendations:
        return []

    result = pd.DataFrame(recommendations)

    result = (
        result
        .sort_values(
            by=[
                "Lift",
                "Confidence",
                "Support"
            ],
            ascending=False
        )
        .drop_duplicates(
            subset=["FoodItem"]
        )
        .head(top_n)
        .reset_index(drop=True)
    )

    return result.to_dict(
        orient="records"
    )

@app.route("/")
def home():

    return send_from_directory(
        WEB_DIR,
        "index.html"
    )

@app.route("/api/recommend", methods=["GET"])
def recommendation_api():

    item = request.args.get(
        "item",
        ""
    ).strip()

    if not item:

        return jsonify({
            "success": False,
            "message": "Please enter a food item."
        }), 400

    recommendations = recommend_food(
        item,
        top_n=5
    )

    return jsonify({
        "success": True,
        "item": item,
        "recommendations": recommendations
    })

@app.route("/api/forecast", methods=["GET"])
def forecast_api():

    forecasts = []

    if not order_forecast_df.empty:

        for _, row in order_forecast_df.iterrows():

            month = pd.to_datetime(
                row["Month"]
            ).strftime("%b %Y")

            order_value = int(
                row["ForecastedOrders"]
            )

            sales_value = 0

            if not sales_forecast_df.empty:

                matching = sales_forecast_df[
                    pd.to_datetime(
                        sales_forecast_df["Month"]
                    ) == pd.to_datetime(
                        row["Month"]
                    )
                ]

                if not matching.empty:

                    sales_value = float(
                        matching.iloc[0][
                            "ForecastedSales"
                        ]
                    )

            forecasts.append({
                "month": month,
                "orders": order_value,
                "sales": round(
                    sales_value,
                    2
                )
            })

    return jsonify({
        "success": True,
        "forecast": forecasts
    })

@app.route("/api/status")
def status_api():

    return jsonify({
        "success": True,
        "recommendation_model": True,
        "forecast_model": True,
        "association_rules": len(rules)
    })

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5007,
        debug=True
    )