import pandas as pd
import re
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

print("Loading cleaned dataset...")

# Load cleaned dataset
df = pd.read_csv(r"data/processed/cleaned_spam.csv")

print("Dataset loaded successfully.")

print("\nDataset Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns)

# ============================================================
# FEATURES AND LABELS
# ============================================================

X = df['cleaned_msg']

y = df['label']

# ============================================================
# TRAIN TEST SPLIT
# ============================================================

print("\nSplitting dataset...")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("Dataset split completed.")

print("Training samples:", len(X_train))

print("Testing samples:", len(X_test))

# ============================================================
# TF-IDF VECTORIZATION
# ============================================================

print("\nCreating TF-IDF vectorizer...")

vectorizer = TfidfVectorizer(
    stop_words='english',
    ngram_range=(1,2),
    max_features=15000
)

print("Fitting TF-IDF on training data...")

X_train_vectorized = vectorizer.fit_transform(X_train)

print("Transforming testing data...")

X_test_vectorized = vectorizer.transform(X_test)

print("\nTF-IDF completed successfully.")

print("\nTraining Shape:")
print(X_train_vectorized.shape)

print("\nTesting Shape:")
print(X_test_vectorized.shape)



# ============================================================
# TRAIN MODEL
# ============================================================

print("\nTraining Logistic Regression model...")

model = LogisticRegression(
    max_iter=2000,
    class_weight='balanced'
)

model.fit(X_train_vectorized, y_train)

print("Model training completed.")

# ============================================================
# PREDICTIONS
# ============================================================

print("\nMaking predictions...")

predictions = model.predict(X_test_vectorized)

# ============================================================
# EVALUATION
# ============================================================

accuracy = accuracy_score(y_test, predictions)

print("\n================ RESULTS ================\n")

print("Accuracy:", accuracy)

print("\nClassification Report:\n")

print(classification_report(y_test, predictions))

print("\n=========================================\n")


# # ============================================================
# # CUSTOM MESSAGE TESTING
# # ============================================================

# while True:

#     message = input("\nEnter a message: ")

#     cleaned_message = message.lower()

#     cleaned_message = re.sub(r'http\S+|www\S+|https\S+', ' URL ', cleaned_message)

#     cleaned_message = re.sub(r'[^a-zA-Z0-9\s]', ' ', cleaned_message)

#     cleaned_message = re.sub(r'\s+', ' ', cleaned_message).strip()

#     # Vectorize
#     message_vectorized = vectorizer.transform([cleaned_message])

#     # Predict
#     prediction = model.predict(message_vectorized)[0]

#     # Probabilities
#     probabilities = model.predict_proba(message_vectorized)[0]

#     print("\nPrediction:", prediction)

#     print("Ham Probability:", probabilities[0])

#     print("Spam Probability:", probabilities[1])


# ============================================================
# SAVE MODEL AND VECTORIZER
# ============================================================

print("Saving model and vectorizer...")

joblib.dump(model, r"models/spam_model.pkl")

joblib.dump(vectorizer, r"models/tfidf_vectorizer.pkl")

print("Model saved successfully.")