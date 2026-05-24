

import os
import sys
import pickle
from datetime import datetime

import numpy as np
from scipy import sparse

# Machine learning
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve
)

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns


# ============================================================
# CONFIGURATION
# ============================================================
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
MODELS_DIR = os.path.join(PROJECT_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# ============================================================
# STEP 1: Load Preprocessed Data
# ============================================================
print("=" * 60)
print("STEP 1: Loading Preprocessed Data")
print("=" * 60)

def load_preprocessed_data():
    """Loads the preprocessed train/test data from the output folder."""
    try:
        X_train = sparse.load_npz(os.path.join(OUTPUT_DIR, "X_train.npz"))
        X_test = sparse.load_npz(os.path.join(OUTPUT_DIR, "X_test.npz"))
        y_train = np.load(os.path.join(OUTPUT_DIR, "y_train.npy"))
        y_test = np.load(os.path.join(OUTPUT_DIR, "y_test.npy"))

        # Load feature names for interpretation
        with open(os.path.join(OUTPUT_DIR, "feature_names.pkl"), 'rb') as f:
            feature_names = pickle.load(f)

        return X_train, X_test, y_train, y_test, feature_names

    except FileNotFoundError as e:
        print(f"[ERROR] Preprocessed data not found: {e}")
        print("[HINT] Please run 'spam_preprocessing.py' first to generate the data.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to load data: {e}")
        sys.exit(1)


X_train, X_test, y_train, y_test, feature_names = load_preprocessed_data()

print(f"[INFO] Training features shape: {X_train.shape}")
print(f"[INFO] Testing features shape:  {X_test.shape}")
print(f"[INFO] Training labels shape:   {y_train.shape}")
print(f"[INFO] Testing labels shape:    {y_test.shape}")
print(f"[INFO] Feature names loaded:    {len(feature_names)}")
print("[SUCCESS] Data loaded successfully.\n")


# ============================================================
# STEP 2: Train Multinomial Naive Bayes Model
# ============================================================
print("=" * 60)
print("STEP 2: Training Multinomial Naive Bayes Classifier")
print("=" * 60)

# MultinomialNB is ideal for text classification with discrete features
# like word counts or TF-IDF values.
# alpha=1.0 applies Laplace smoothing to handle unseen words.
model = MultinomialNB(alpha=1.0)

print("[INFO] Training model...")
model.fit(X_train, y_train)
print("[SUCCESS] Model training completed.\n")


# ============================================================
# STEP 3: Model Evaluation
# ============================================================
print("=" * 60)
print("STEP 3: Model Evaluation")
print("=" * 60)

# Predictions
y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)
y_test_proba = model.predict_proba(X_test)[:, 1]  # Probabilities for ROC-AUC

# --- Training Set Metrics ---
print("\n--- Training Set Performance ---")
train_acc = accuracy_score(y_train, y_train_pred)
print(f"Accuracy:  {train_acc:.4f}")

# --- Testing Set Metrics ---
print("\n--- Testing Set Performance ---")
test_acc = accuracy_score(y_test, y_test_pred)
test_precision = precision_score(y_test, y_test_pred, zero_division=0)
test_recall = recall_score(y_test, y_test_pred, zero_division=0)
test_f1 = f1_score(y_test, y_test_pred, zero_division=0)
test_auc = roc_auc_score(y_test, y_test_proba)

print(f"Accuracy:  {test_acc:.4f}")
print(f"Precision: {test_precision:.4f}")
print(f"Recall:    {test_recall:.4f}")
print(f"F1-Score:  {test_f1:.4f}")
print(f"ROC-AUC:   {test_auc:.4f}")

# --- Detailed Classification Report ---
print("\n--- Classification Report (Test Set) ---")
print(classification_report(
    y_test, y_test_pred,
    target_names=["Ham (0)", "Spam (1)"],
    digits=4
))


# ============================================================
# STEP 4: Confusion Matrix Visualization
# ============================================================
print("=" * 60)
print("STEP 4: Confusion Matrix")
print("=" * 60)

cm = confusion_matrix(y_test, y_test_pred)
print("Confusion Matrix:")
print(f"                 Predicted")
print(f"                 Ham    Spam")
print(f"Actual Ham   {cm[0,0]:5d}  {cm[0,1]:5d}  (TN={cm[0,0]}, FP={cm[0,1]})")
print(f"Actual Spam  {cm[1,0]:5d}  {cm[1,1]:5d}  (FN={cm[1,0]}, TP={cm[1,1]})")

# Plot confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(
    cm, annot=True, fmt='d', cmap='Blues',
    xticklabels=['Ham', 'Spam'],
    yticklabels=['Ham', 'Spam'],
    annot_kws={"size": 14, "weight": "bold"}
)
plt.title('Confusion Matrix - Naive Bayes Spam Detection', fontsize=14, fontweight='bold')
plt.xlabel('Predicted Label', fontsize=12)
plt.ylabel('True Label', fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(MODELS_DIR, 'confusion_matrix.png'), dpi=300)
plt.close()
print(f"[INFO] Saved confusion matrix plot to: {os.path.join(MODELS_DIR, 'confusion_matrix.png')}")


# ============================================================
# STEP 5: ROC Curve Visualization
# ============================================================
print("\n" + "=" * 60)
print("STEP 5: ROC Curve")
print("=" * 60)

fpr, tpr, thresholds = roc_curve(y_test, y_test_proba)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC Curve (AUC = {test_auc:.4f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Classifier')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate', fontsize=12)
plt.ylabel('True Positive Rate', fontsize=12)
plt.title('ROC Curve - Naive Bayes Spam Detection', fontsize=14, fontweight='bold')
plt.legend(loc='lower right', fontsize=11)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(MODELS_DIR, 'roc_curve.png'), dpi=300)
plt.close()
print(f"[INFO] Saved ROC curve plot to: {os.path.join(MODELS_DIR, 'roc_curve.png')}")


# ============================================================
# STEP 6: Feature Importance (Top Spam Indicators)
# ============================================================
print("\n" + "=" * 60)
print("STEP 6: Top Spam Indicator Words")
print("=" * 60)

# In MultinomialNB, feature_log_prob_ gives log probability of features given class
# We compute the difference to find words most indicative of spam vs ham
spam_log_prob = model.feature_log_prob_[1]  # spam class
ham_log_prob = model.feature_log_prob_[0]   # ham class
log_prob_diff = spam_log_prob - ham_log_prob

# Get top features that distinguish spam from ham
top_n = 20
top_indices = np.argsort(log_prob_diff)[-top_n:][::-1]

top_spam_words = [(feature_names[i], log_prob_diff[i]) for i in top_indices]

print(f"\nTop {top_n} words most indicative of SPAM:")
for rank, (word, score) in enumerate(top_spam_words, 1):
    print(f"  {rank:2d}. {word:<15s} (log-prob diff: {score:7.4f})")

# Plot top spam indicators
words, scores = zip(*top_spam_words)
plt.figure(figsize=(10, 6))
sns.barplot(x=list(scores), y=list(words), hue=list(words), palette='rocket', legend=False)
plt.title('Top 20 Words Most Indicative of Spam', fontsize=14, fontweight='bold')
plt.xlabel('Log Probability Difference (Spam - Ham)', fontsize=12)
plt.ylabel('Word', fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(MODELS_DIR, 'top_spam_indicators.png'), dpi=300)
plt.close()
print(f"[INFO] Saved spam indicators plot to: {os.path.join(MODELS_DIR, 'top_spam_indicators.png')}")


# ============================================================
# STEP 7: Save Trained Model
# ============================================================
print("\n" + "=" * 60)
print("STEP 7: Saving Trained Model")
print("=" * 60)

model_path = os.path.join(MODELS_DIR, 'naive_bayes_spam_model.pkl')
with open(model_path, 'wb') as f:
    pickle.dump(model, f)
print(f"[SAVED] Trained model: {model_path}")

# Save evaluation metrics for reference
metrics = {
    'accuracy': test_acc,
    'precision': test_precision,
    'recall': test_recall,
    'f1_score': test_f1,
    'roc_auc': test_auc,
    'training_samples': int(X_train.shape[0]),
    'testing_samples': int(X_test.shape[0]),
    'timestamp': datetime.now().isoformat()
}
metrics_path = os.path.join(MODELS_DIR, 'evaluation_metrics.pkl')
with open(metrics_path, 'wb') as f:
    pickle.dump(metrics, f)
print(f"[SAVED] Evaluation metrics: {metrics_path}")


# ============================================================
# STEP 8: Final Summary
# ============================================================
print("\n" + "=" * 60)
print("MODEL TRAINING COMPLETED SUCCESSFULLY")
print("=" * 60)
print(f"""
FINAL RESULTS:
--------------
Model:                Multinomial Naive Bayes
Training Samples:     {X_train.shape[0]:,}
Testing Samples:      {X_test.shape[0]:,}
Features:             {X_train.shape[1]:,}

TEST SET PERFORMANCE:
---------------------
Accuracy:             {test_acc:.4f} ({test_acc*100:.2f}%)
Precision:            {test_precision:.4f}
Recall:               {test_recall:.4f}
F1-Score:             {test_f1:.4f}
ROC-AUC:              {test_auc:.4f}

Confusion Matrix:
  True Negatives (Ham correctly classified):  {cm[0,0]}
  False Positives (Ham misclassified as Spam): {cm[0,1]}
  False Negatives (Spam misclassified as Ham): {cm[1,0]}
  True Positives (Spam correctly classified):  {cm[1,1]}

OUTPUT FILES:
-------------
Trained Model:        {model_path}
Evaluation Metrics:   {metrics_path}
Confusion Matrix:     {os.path.join(MODELS_DIR, 'confusion_matrix.png')}
ROC Curve:            {os.path.join(MODELS_DIR, 'roc_curve.png')}
Spam Indicators:      {os.path.join(MODELS_DIR, 'top_spam_indicators.png')}

The model is ready for inference!
""")
print("=" * 60)
