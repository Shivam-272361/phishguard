import joblib
import re

# ============================================================
# LOAD MODEL AND VECTORIZER
# ============================================================

print("Loading model...")

model = joblib.load(r"models/spam_model.pkl")

vectorizer = joblib.load(r"models/tfidf_vectorizer.pkl")

print("Model loaded successfully.")

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
# PREDICTION LOOP
# ============================================================

while True:

    message = input("\nEnter a message: ")

    # Clean message
    cleaned_message = clean_text(message)

    # Convert into vector
    message_vectorized = vectorizer.transform([cleaned_message])

    # Predict
    prediction = model.predict(message_vectorized)[0]

    # Probabilities
    probabilities = model.predict_proba(message_vectorized)[0]

    ham_probability = probabilities[0]

    spam_probability = probabilities[1]

    print("\n========== RESULT ==========")

    print("Cleaned Message:", cleaned_message)

    print("Prediction:", prediction)

    print("Ham Probability:", ham_probability)

    print("Spam Probability:", spam_probability)

    print("============================")