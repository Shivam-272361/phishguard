"""
SMS Spam Detection - Production-Ready Flask API
================================================
A RESTful API for real-time spam detection using the trained
Multinomial Naive Bayes model and TF-IDF vectorizer.

Endpoints:
    POST /predict        - Predict single SMS message
    POST /predict/batch  - Predict multiple SMS messages
    GET  /health         - Health check
    GET  /               - API info

Usage:
    Development: python app.py
    Production:  waitress-serve --port=5000 app:app

Dependencies:
    pip install flask waitress numpy scipy
"""

import os
import sys
import re
import string
import pickle
import logging
from datetime import datetime
from functools import wraps

import numpy as np
from scipy import sparse

from flask import Flask, request, jsonify

# ============================================================
# Logging Configuration
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('spam_api')

# ============================================================
# App Initialization
# ============================================================
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# ============================================================
# Configuration
# ============================================================
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(PROJECT_DIR, "models")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")

MODEL_PATH = os.path.join(MODELS_DIR, "naive_bayes_spam_model.pkl")
VECTORIZER_PATH = os.path.join(OUTPUT_DIR, "tfidf_vectorizer.pkl")

# ============================================================
# NLTK Setup (Lazy import to avoid startup overhead)
# ============================================================
_nltk_ready = False
_stemmer = None
_stop_words = None


def _ensure_nltk():
    """Lazily initialize NLTK resources on first use."""
    global _nltk_ready, _stemmer, _stop_words
    if _nltk_ready:
        return

    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import PorterStemmer

    # Download if missing
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab', quiet=True)
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)

    _stemmer = PorterStemmer()
    _stop_words = set(stopwords.words('english'))
    _nltk_ready = True


# ============================================================
# Model Loading
# ============================================================
model = None
vectorizer = None
model_loaded_at = None


def load_model():
    """Loads the trained model and vectorizer into memory."""
    global model, vectorizer, model_loaded_at

    logger.info("Loading model and vectorizer...")

    if not os.path.exists(MODEL_PATH):
        logger.error(f"Model file not found: {MODEL_PATH}")
        raise FileNotFoundError(f"Model not found. Train the model first.")
    if not os.path.exists(VECTORIZER_PATH):
        logger.error(f"Vectorizer file not found: {VECTORIZER_PATH}")
        raise FileNotFoundError(f"Vectorizer not found. Run preprocessing first.")

    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    with open(VECTORIZER_PATH, 'rb') as f:
        vectorizer = pickle.load(f)

    model_loaded_at = datetime.utcnow().isoformat()
    logger.info(f"Model loaded successfully at {model_loaded_at}")


def preprocess_text(text):
    """
    Applies the same NLP preprocessing pipeline used during training.
    """
    _ensure_nltk()

    if not isinstance(text, str):
        text = str(text) if text is not None else ""

    # Lowercase
    text = text.lower()
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Remove special characters and normalize whitespace
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()

    # Tokenize, remove stopwords, and stem
    tokens = text.split()
    tokens = [w for w in tokens if w not in _stop_words and len(w) > 1]
    tokens = [_stemmer.stem(w) for w in tokens]

    return ' '.join(tokens)


def predict_message(raw_text):
    """
    Preprocesses a raw message and returns prediction results.
    """
    cleaned = preprocess_text(raw_text)
    if not cleaned.strip():
        return {
            "label": "unknown",
            "label_num": -1,
            "confidence": 0.0,
            "is_spam": None,
            "cleaned_text": cleaned,
            "error": "Message is empty after preprocessing"
        }

    X = vectorizer.transform([cleaned])
    pred = model.predict(X)[0]
    proba = model.predict_proba(X)[0]

    label = "spam" if pred == 1 else "ham"
    confidence = float(proba[pred])

    return {
        "label": label,
        "label_num": int(pred),
        "confidence": round(confidence, 6),
        "is_spam": bool(pred == 1),
        "cleaned_text": cleaned,
        "spam_probability": round(float(proba[1]), 6),
        "ham_probability": round(float(proba[0]), 6)
    }


# ============================================================
# Error Handlers
# ============================================================
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": "Bad request",
        "message": str(error.description)
    }), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Not found",
        "message": "The requested endpoint does not exist."
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": "Method not allowed",
        "message": "This endpoint does not support the requested HTTP method."
    }), 405


@app.errorhandler(500)
def internal_error(error):
    logger.exception("Internal server error")
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "message": "An unexpected error occurred. Please try again later."
    }), 500


# ============================================================
# Middleware: Request Logging
# ============================================================
@app.before_request
def log_request():
    logger.info(f"{request.method} {request.path} - {request.remote_addr}")


# ============================================================
# Routes
# ============================================================

@app.route('/', methods=['GET'])
def index():
    """API root — returns service information."""
    return jsonify({
        "success": True,
        "service": "SMS Spam Detection API",
        "version": "1.0.0",
        "model": "Multinomial Naive Bayes",
        "model_loaded_at": model_loaded_at,
        "endpoints": {
            "GET /health": "Health check",
            "POST /predict": "Predict a single SMS message",
            "POST /predict/batch": "Predict multiple SMS messages"
        }
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    healthy = model is not None and vectorizer is not None
    status_code = 200 if healthy else 503

    return jsonify({
        "success": healthy,
        "status": "healthy" if healthy else "unhealthy",
        "model_loaded": healthy,
        "model_loaded_at": model_loaded_at,
        "timestamp": datetime.utcnow().isoformat()
    }), status_code


@app.route('/predict', methods=['POST'])
def predict_single():
    """
    Predict whether a single SMS message is spam or ham.

    Request Body (JSON):
        {
            "message": "Your SMS text here"
        }

    Response (JSON):
        {
            "success": true,
            "prediction": {
                "label": "spam",
                "label_num": 1,
                "confidence": 0.8862,
                "is_spam": true,
                "cleaned_text": "congratul youv gift card call claim prize",
                "spam_probability": 0.8862,
                "ham_probability": 0.1138
            },
            "input": "Congratulations! You've won a $1000 gift card...",
            "timestamp": "2026-05-08T12:00:00"
        }
    """
    if not request.is_json:
        return jsonify({
            "success": False,
            "error": "Invalid request",
            "message": "Content-Type must be application/json"
        }), 400

    data = request.get_json()
    if data is None:
        return jsonify({
            "success": False,
            "error": "Invalid request",
            "message": "Request body is empty or invalid JSON"
        }), 400

    message = data.get('message')
    if message is None:
        return jsonify({
            "success": False,
            "error": "Missing field",
            "message": "Required field 'message' is missing"
        }), 400

    if not isinstance(message, str) or not message.strip():
        return jsonify({
            "success": False,
            "error": "Invalid input",
            "message": "Field 'message' must be a non-empty string"
        }), 400

    if len(message) > 5000:
        return jsonify({
            "success": False,
            "error": "Input too long",
            "message": "Message exceeds maximum length of 5000 characters"
        }), 400

    try:
        result = predict_message(message)
        return jsonify({
            "success": True,
            "prediction": result,
            "input": message,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.exception("Prediction failed")
        return jsonify({
            "success": False,
            "error": "Prediction failed",
            "message": str(e)
        }), 500


@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """
    Predict spam/ham for multiple SMS messages in a single request.

    Request Body (JSON):
        {
            "messages": [
                "Hey, are we still on for lunch?",
                "Congratulations! You've won a prize!",
                ...
            ]
        }

    Response (JSON):
        {
            "success": true,
            "predictions": [...],
            "summary": {
                "total": 3,
                "spam_count": 1,
                "ham_count": 2
            },
            "timestamp": "2026-05-08T12:00:00"
        }
    """
    if not request.is_json:
        return jsonify({
            "success": False,
            "error": "Invalid request",
            "message": "Content-Type must be application/json"
        }), 400

    data = request.get_json()
    if data is None:
        return jsonify({
            "success": False,
            "error": "Invalid request",
            "message": "Request body is empty or invalid JSON"
        }), 400

    messages = data.get('messages')
    if messages is None:
        return jsonify({
            "success": False,
            "error": "Missing field",
            "message": "Required field 'messages' is missing"
        }), 400

    if not isinstance(messages, list):
        return jsonify({
            "success": False,
            "error": "Invalid input",
            "message": "Field 'messages' must be a list"
        }), 400

    if len(messages) == 0:
        return jsonify({
            "success": False,
            "error": "Invalid input",
            "message": "Field 'messages' must not be empty"
        }), 400

    if len(messages) > 100:
        return jsonify({
            "success": False,
            "error": "Batch too large",
            "message": "Maximum batch size is 100 messages"
        }), 400

    # Validate each message
    for i, msg in enumerate(messages):
        if not isinstance(msg, str):
            return jsonify({
                "success": False,
                "error": "Invalid input",
                "message": f"Message at index {i} is not a string"
            }), 400
        if len(msg) > 5000:
            return jsonify({
                "success": False,
                "error": "Input too long",
                "message": f"Message at index {i} exceeds maximum length of 5000 characters"
            }), 400

    try:
        predictions = []
        spam_count = 0
        ham_count = 0

        for msg in messages:
            pred = predict_message(msg)
            predictions.append({
                "input": msg,
                "prediction": pred
            })
            if pred.get('is_spam') is True:
                spam_count += 1
            elif pred.get('is_spam') is False:
                ham_count += 1

        return jsonify({
            "success": True,
            "predictions": predictions,
            "summary": {
                "total": len(messages),
                "spam_count": spam_count,
                "ham_count": ham_count
            },
            "timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.exception("Batch prediction failed")
        return jsonify({
            "success": False,
            "error": "Prediction failed",
            "message": str(e)
        }), 500


# ============================================================
# Application Startup
# ============================================================
if __name__ == '__main__':
    try:
        load_model()
    except Exception as e:
        logger.error(f"Failed to start API: {e}")
        sys.exit(1)

    # Development server
    logger.info("Starting Flask development server on http://127.0.0.1:5002")
    app.run(host='127.0.0.1', port=5002, debug=False)
