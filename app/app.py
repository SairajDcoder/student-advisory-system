"""
Stage 8b - Flask Demo Application
===================================
A web-based demo where users enter student data and receive a
predicted career recommendation along with model confidence scores.
"""
from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import pandas as pd
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import MODELS_DIR
from src.preprocessing import NUMERIC_FEATURES, CATEGORICAL_FEATURES

app = Flask(__name__, template_folder="templates", static_folder="static")

# Load model artefacts
preprocessor = joblib.load(os.path.join(MODELS_DIR, "preprocessor.pkl"))
model = joblib.load(os.path.join(MODELS_DIR, "best_model_rf.pkl"))
label_encoder = joblib.load(os.path.join(MODELS_DIR, "label_encoder.pkl"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Collect form data
        data = {
            "study_hours_per_week": float(request.form["study_hours_per_week"]),
            "attendance_pct": float(request.form["attendance_pct"]),
            "previous_gpa": float(request.form["previous_gpa"]),
            "math_score": int(request.form["math_score"]),
            "science_score": int(request.form["science_score"]),
            "english_score": int(request.form["english_score"]),
            "programming_score": int(request.form["programming_score"]),
            "creativity_score": int(request.form["creativity_score"]),
            "communication_score": int(request.form["communication_score"]),
            "leadership_score": int(request.form["leadership_score"]),
            "extracurricular_activities": int(request.form["extracurricular_activities"]),
            "internship_experience": int(request.form["internship_experience"]),
            "projects_completed": int(request.form["projects_completed"]),
            "gender": request.form["gender"],
            "parental_education": request.form["parental_education"],
            "part_time_job": int(request.form["part_time_job"]),
        }

        df_input = pd.DataFrame([data])
        X_transformed = preprocessor.transform(df_input)

        # Predict
        prediction = model.predict(X_transformed)[0]
        career = label_encoder.inverse_transform([prediction])[0]

        # Confidence scores
        probas = model.predict_proba(X_transformed)[0]
        confidence = {
            label_encoder.inverse_transform([i])[0]: round(float(p) * 100, 1)
            for i, p in enumerate(probas)
        }
        # Sort by confidence descending
        confidence = dict(sorted(confidence.items(), key=lambda x: x[1], reverse=True))

        return render_template("result.html",
                               career=career,
                               confidence=confidence,
                               input_data=data)
    except Exception as e:
        return render_template("result.html", error=str(e))


@app.route("/api/predict", methods=["POST"])
def api_predict():
    """REST API endpoint for programmatic access."""
    try:
        data = request.get_json()
        df_input = pd.DataFrame([data])
        X_transformed = preprocessor.transform(df_input)

        prediction = model.predict(X_transformed)[0]
        career = label_encoder.inverse_transform([prediction])[0]
        probas = model.predict_proba(X_transformed)[0]
        confidence = {
            label_encoder.inverse_transform([i])[0]: round(float(p) * 100, 1)
            for i, p in enumerate(probas)
        }
        return jsonify({"career_recommendation": career, "confidence": confidence})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5000)
