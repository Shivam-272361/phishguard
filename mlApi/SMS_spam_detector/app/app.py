from flask import Flask, request, jsonify

import joblib
import re
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# LOAD MODEL AND VECTORIZER
# ============================================================

print("Loading model...")

model = joblib.load(r"models/spam_model.pkl")

vectorizer = joblib.load(r"models/tfidf_vectorizer.pkl")

print("Model loaded successfully.")

# ============================================================
# CREATE FLASK APP
# ============================================================

app = Flask(__name__)

# ============================================================
# CLEANING FUNCTION
# ============================================================

def clean_text(text):

    text = str(text)

    text = text.lower()

    text = re.sub(r'http\S+|www\S+|https\S+', ' URL ', text)

    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)

    text = re.sub(r'\s+', ' ', text).strip()

    return text

# ============================================================
# PREDICT ROUTE
# ============================================================

@app.route('/predict', methods=['POST'])

def predict():

    try:

        # Get JSON data
        data = request.get_json()

        # Extract message
        message = data.get('message', '')

        # Clean text
        cleaned_message = clean_text(message)

        # Vectorize
        message_vectorized = vectorizer.transform([cleaned_message])

        # Predict
        prediction = model.predict(message_vectorized)[0]

        # Probabilities
        probabilities = model.predict_proba(message_vectorized)[0]

        ham_probability = float(probabilities[0])

        spam_probability = float(probabilities[1])

        # Build response
        response = {

            "success": True,

            "input": message,

            "prediction": {

                "cleaned_text": cleaned_message,

                "label": prediction,

                "is_spam": prediction == "spam",

                "ham_probability": ham_probability,

                "spam_probability": spam_probability

            }

        }

        return jsonify(response)

    except Exception as e:

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500

# ============================================================
# RUN SERVER
# ============================================================

@app.route("/")
def home():
    return "PhishGuard API Running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)