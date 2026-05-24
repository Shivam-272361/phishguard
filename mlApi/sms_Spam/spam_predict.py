"""
SMS Spam Detection - Inference Script
======================================
Predict whether new SMS messages are spam or ham using the
trained Naive Bayes model and TF-IDF vectorizer.

Author: Data Science Pipeline
"""

import os
import sys
import pickle
import re
import string

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

# Ensure NLTK resources are available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)


# ============================================================
# CONFIGURATION
# ============================================================
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(PROJECT_DIR, "models")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")

# ============================================================
# STEP 1: Load Model and Vectorizer
# ============================================================
print("=" * 60)
print("STEP 1: Loading Model and Vectorizer")
print("=" * 60)

def load_artifacts():
    """Loads the trained model and TF-IDF vectorizer."""
    model_path = os.path.join(MODELS_DIR, "naive_bayes_spam_model.pkl")
    vectorizer_path = os.path.join(OUTPUT_DIR, "tfidf_vectorizer.pkl")

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"[ERROR] Model not found at {model_path}\n"
            "[HINT] Please run 'spam_naive_bayes_model.py' first to train the model."
        )
    if not os.path.exists(vectorizer_path):
        raise FileNotFoundError(
            f"[ERROR] Vectorizer not found at {vectorizer_path}\n"
            "[HINT] Please run 'spam_preprocessing.py' first to generate the vectorizer."
        )

    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    with open(vectorizer_path, 'rb') as f:
        vectorizer = pickle.load(f)

    return model, vectorizer


try:
    model, vectorizer = load_artifacts()
    print("[SUCCESS] Model and vectorizer loaded successfully.\n")
except Exception as e:
    print(e)
    sys.exit(1)


# ============================================================
# STEP 2: Preprocessing Function (Same as Training)
# ============================================================
print("=" * 60)
print("STEP 2: Preparing Preprocessing Pipeline")
print("=" * 60)

stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))


def preprocess_text(text):
    """
    Applies the same NLP preprocessing used during training.
    """
    if not isinstance(text, str):
        text = str(text)

    # Lowercase
    text = text.lower()
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Remove special characters
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Tokenize
    tokens = word_tokenize(text)
    # Remove stopwords
    tokens = [w for w in tokens if w not in stop_words and len(w) > 1]
    # Stem
    tokens = [stemmer.stem(w) for w in tokens]

    return ' '.join(tokens)


print("[SUCCESS] Preprocessing pipeline ready.\n")


# ============================================================
# STEP 3: Define Test Messages
# ============================================================
print("=" * 60)
print("STEP 3: Defining Test SMS Messages")
print("=" * 60)

test_messages = [
    # Ham messages
    ("Hey, are we still meeting for lunch tomorrow at 1pm?", "ham"),
    ("Thanks for the ride home last night! Really appreciate it.", "ham"),
    ("Can you pick up some milk on your way back from work?", "ham"),
    ("Happy birthday! Hope you have an amazing day!", "ham"),
    ("The package has been delivered. Let me know when you get it.", "ham"),

    # Spam messages
    ("Congratulations! You've won a $1000 gift card. Call now to claim your prize!", "spam"),
    ("URGENT: You have won a free iPhone. Click here to claim within 24 hours.", "spam"),
    ("Free entry to win a brand new car! Text WIN to 88888 now. T&C apply.", "spam"),
    ("You are selected for a cash reward of $5000. Call 09061701461 to claim immediately.", "spam"),
    ("Buy cheap viagra pills now! 80% discount for limited time only!!!", "spam"),

    # Edge cases / ambiguous
    ("Call me back when you get a chance, it's urgent but not an emergency.", "ham"),
    ("You have a package waiting. Claim your free gift by calling this number now!", "spam"),
]

print(f"[INFO] Loaded {len(test_messages)} test messages ({sum(1 for _, l in test_messages if l=='ham')} ham, {sum(1 for _, l in test_messages if l=='spam')} spam).\n")


# ============================================================
# STEP 4: Predict and Display Results
# ============================================================
print("=" * 60)
print("STEP 4: Running Predictions")
print("=" * 60)

def predict_message(raw_text):
    """
    Preprocesses a raw message and returns prediction + probability.
    """
    cleaned = preprocess_text(raw_text)
    if not cleaned.strip():
        return "unknown", 0.0, cleaned

    X = vectorizer.transform([cleaned])
    pred = model.predict(X)[0]
    proba = model.predict_proba(X)[0]

    label = "spam" if pred == 1 else "ham"
    confidence = proba[pred]

    return label, confidence, cleaned


results = []
correct = 0

for idx, (message, true_label) in enumerate(test_messages, 1):
    pred_label, confidence, cleaned = predict_message(message)
    is_correct = pred_label == true_label
    if is_correct:
        correct += 1

    results.append({
        'id': idx,
        'message': message,
        'true_label': true_label,
        'pred_label': pred_label,
        'confidence': confidence,
        'cleaned': cleaned,
        'correct': is_correct
    })

    status = "✓ CORRECT" if is_correct else "✗ WRONG"
    print(f"\n[{idx}] {status}")
    print(f"    Original:  {message[:70]}{'...' if len(message) > 70 else ''}")
    print(f"    Cleaned:   {cleaned[:70]}{'...' if len(cleaned) > 70 else ''}")
    print(f"    True:      {true_label.upper()}")
    print(f"    Predicted: {pred_label.upper()} (confidence: {confidence:.4f})")


# ============================================================
# STEP 5: Summary Statistics
# ============================================================
print("\n" + "=" * 60)
print("STEP 5: Prediction Summary")
print("=" * 60)

total = len(results)
ham_messages = [r for r in results if r['true_label'] == 'ham']
spam_messages = [r for r in results if r['true_label'] == 'spam']

print(f"\nTotal Messages Tested: {total}")
print(f"Overall Accuracy:      {correct}/{total} ({correct/total*100:.1f}%)")

print(f"\n--- Ham Messages ({len(ham_messages)}) ---")
ham_correct = sum(1 for r in ham_messages if r['correct'])
print(f"Correctly Predicted:   {ham_correct}/{len(ham_messages)}")
for r in ham_messages:
    mark = "✓" if r['correct'] else "✗"
    print(f"  [{mark}] Msg {r['id']}: {r['pred_label'].upper()} ({r['confidence']:.2%})")

print(f"\n--- Spam Messages ({len(spam_messages)}) ---")
spam_correct = sum(1 for r in spam_messages if r['correct'])
print(f"Correctly Predicted:   {spam_correct}/{len(spam_messages)}")
for r in spam_messages:
    mark = "✓" if r['correct'] else "✗"
    print(f"  [{mark}] Msg {r['id']}: {r['pred_label'].upper()} ({r['confidence']:.2%})")

print("\n" + "=" * 60)
print("INFERENCE COMPLETED SUCCESSFULLY")
print("=" * 60)
