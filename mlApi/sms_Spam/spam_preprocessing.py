"""
SMS Spam Detection - Data Cleaning & NLP Preprocessing Pipeline
===============================================================
A production-ready script for preprocessing SMS spam data for NLP model training.

Author: Data Science Pipeline
Requirements: pandas, numpy, nltk, scikit-learn, matplotlib, seaborn
"""

import os
import sys
import re
import string
import pickle
import glob
from collections import Counter

# Core data libraries
import pandas as pd
import numpy as np

# NLP libraries
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer

# Machine learning libraries
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split

# Visualization libraries
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================================
# STEP 0: Download Required NLTK Data
# ============================================================
print("=" * 60)
print("STEP 0: Downloading NLTK Resources")
print("=" * 60)

try:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)
    print("[SUCCESS] All NLTK resources downloaded successfully.\n")
except Exception as e:
    print(f"[ERROR] Failed to download NLTK resources: {e}")
    sys.exit(1)


# ============================================================
# STEP 1: Auto-Detect and Load Dataset
# ============================================================
print("=" * 60)
print("STEP 1: Dataset Detection & Loading")
print("=" * 60)

def detect_dataset(project_dir):
    """
    Automatically detects CSV files in the project directory.
    Returns the path to the first CSV file found.
    """
    try:
        csv_files = glob.glob(os.path.join(project_dir, "*.csv"))
        if not csv_files:
            raise FileNotFoundError("No CSV files found in the project directory.")
        if len(csv_files) > 1:
            print(f"[INFO] Multiple CSV files found. Using: {os.path.basename(csv_files[0])}")
        return csv_files[0]
    except Exception as e:
        print(f"[ERROR] Dataset detection failed: {e}")
        sys.exit(1)


# Get current script directory as project folder
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = detect_dataset(PROJECT_DIR)
print(f"[INFO] Dataset detected: {DATASET_PATH}")

# Load the dataset
# The dataset has trailing empty columns, so we handle them
try:
    df = pd.read_csv(DATASET_PATH, encoding='utf-8')
    print("[INFO] Dataset loaded with UTF-8 encoding.")
except UnicodeDecodeError:
    try:
        df = pd.read_csv(DATASET_PATH, encoding='latin-1')
        print("[INFO] Dataset loaded with latin-1 encoding (fallback).")
    except Exception as e:
        print(f"[ERROR] Failed to load dataset: {e}")
        sys.exit(1)
except Exception as e:
    print(f"[ERROR] Failed to load dataset: {e}")
    sys.exit(1)

print("[SUCCESS] Dataset loaded successfully.\n")


# ============================================================
# STEP 2: Initial Dataset Exploration
# ============================================================
print("=" * 60)
print("STEP 2: Initial Dataset Exploration")
print("=" * 60)

print(f"Dataset Shape: {df.shape}")
print(f"Number of Rows: {df.shape[0]}")
print(f"Number of Columns: {df.shape[1]}")
print(f"\nColumn Names: {list(df.columns)}")
print(f"\nFirst 5 Rows:")
print(df.head())

print(f"\nMissing Values per Column:")
missing_values = df.isnull().sum()
print(missing_values)
print(f"Total Missing Values: {missing_values.sum()}")

print(f"\nDuplicate Rows: {df.duplicated().sum()}")
print("-" * 60)


# ============================================================
# STEP 3: Data Cleaning
# ============================================================
print("\n" + "=" * 60)
print("STEP 3: Data Cleaning")
print("=" * 60)

# 3a. Remove completely empty columns
df = df.dropna(axis=1, how='all')
print(f"[INFO] Removed empty columns. New shape: {df.shape}")

# 3b. Fix column names: rename v1 -> label, v2 -> message
if 'v1' in df.columns and 'v2' in df.columns:
    df = df.rename(columns={'v1': 'label', 'v2': 'message'})
    print("[INFO] Renamed columns: 'v1' -> 'label', 'v2' -> 'message'")
else:
    print("[WARNING] Expected columns 'v1' and 'v2' not found. Using existing columns.")
    df.columns = ['label', 'message'] + [f'extra_{i}' for i in range(len(df.columns) - 2)]
    df = df[['label', 'message']]

# 3c. Keep only necessary columns
df = df[['label', 'message']].copy()

# 3d. Remove rows with null values in critical columns
initial_rows = len(df)
df = df.dropna(subset=['label', 'message'])
print(f"[INFO] Removed {initial_rows - len(df)} rows with null values.")

# 3e. Remove duplicate rows
initial_rows = len(df)
df = df.drop_duplicates()
print(f"[INFO] Removed {initial_rows - len(df)} duplicate rows.")

# 3f. Convert labels to numeric: spam = 1, ham = 0
print("[INFO] Converting labels to numeric (spam=1, ham=0)...")
df['label_num'] = df['label'].map({'ham': 0, 'spam': 1})

# Check for any unmapped labels
unmapped = df['label_num'].isnull().sum()
if unmapped > 0:
    print(f"[WARNING] Found {unmapped} unmapped labels. Removing them.")
    df = df.dropna(subset=['label_num'])

df['label_num'] = df['label_num'].astype(int)
print("[SUCCESS] Label conversion completed.")

# 3g. Reset index
df = df.reset_index(drop=True)

print(f"\nCleaned Dataset Shape: {df.shape}")
print(f"Label Distribution:")
print(df['label'].value_counts())
print("-" * 60)


# ============================================================
# STEP 4: NLP Text Preprocessing
# ============================================================
print("\n" + "=" * 60)
print("STEP 4: NLP Text Preprocessing")
print("=" * 60)

# Initialize NLP tools
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))


def preprocess_text(text, use_stemming=True):
    """
    Comprehensive NLP preprocessing pipeline for SMS text.

    Steps performed:
    1. Lowercase conversion - standardizes text case
    2. Remove numbers - digits don't carry semantic meaning for spam detection
    3. Remove punctuation - reduces noise
    4. Remove special characters - cleans encoding artifacts
    5. Tokenize - split into individual words
    6. Remove stopwords - filter out common non-informative words
    7. Stemming/Lemmatization - reduce words to root form

    Args:
        text (str): Raw input text
        use_stemming (bool): If True, use stemming; else use lemmatization

    Returns:
        str: Cleaned and preprocessed text
    """
    # Handle non-string inputs
    if not isinstance(text, str):
        text = str(text)

    # Step 1: Lowercase conversion
    # Converts all characters to lowercase for uniformity
    text = text.lower()

    # Step 2: Remove numbers
    # Digits rarely contribute to spam/ham classification
    text = re.sub(r'\d+', '', text)

    # Step 3: Remove URLs
    # URLs are often present in spam but we handle them via regex
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)

    # Step 4: Remove punctuation
    # Punctuation marks don't add semantic value for bag-of-words models
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Step 5: Remove special characters and extra whitespace
    # Handles encoding artifacts and non-alphabetic symbols
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()

    # Step 6: Tokenization
    # Split text into individual word tokens
    tokens = word_tokenize(text)

    # Step 7: Remove stopwords
    # Filter out common words (the, and, is, etc.) that don't help classification
    tokens = [word for word in tokens if word not in stop_words and len(word) > 1]

    # Step 8: Stemming or Lemmatization
    # Reduce words to their root form to normalize variations
    if use_stemming:
        tokens = [stemmer.stem(word) for word in tokens]
    else:
        tokens = [lemmatizer.lemmatize(word) for word in tokens]

    return ' '.join(tokens)


# Apply preprocessing to all messages
print("[INFO] Applying NLP preprocessing to all messages...")
print("[INFO] This may take a moment depending on dataset size.")

df['cleaned_message'] = df['message'].apply(lambda x: preprocess_text(x, use_stemming=True))

# Remove any rows where cleaning resulted in empty text
df = df[df['cleaned_message'].str.strip() != ''].reset_index(drop=True)

print(f"[SUCCESS] Preprocessing completed. Final shape: {df.shape}")
print("-" * 60)


# ============================================================
# STEP 5: Before vs After Preprocessing Examples
# ============================================================
print("\n" + "=" * 60)
print("STEP 5: Before vs After Preprocessing Examples")
print("=" * 60)

# Show examples for both spam and ham
print("\n--- HAM EXAMPLES ---")
ham_samples = df[df['label'] == 'ham'].head(3)
for idx, row in ham_samples.iterrows():
    print(f"\nExample (Row {idx}):")
    print(f"  BEFORE: {row['message'][:120]}...")
    print(f"  AFTER:  {row['cleaned_message'][:120]}...")

print("\n--- SPAM EXAMPLES ---")
spam_samples = df[df['label'] == 'spam'].head(3)
for idx, row in spam_samples.iterrows():
    print(f"\nExample (Row {idx}):")
    print(f"  BEFORE: {row['message'][:120]}...")
    print(f"  AFTER:  {row['cleaned_message'][:120]}...")
print("-" * 60)


# ============================================================
# STEP 6: Exploratory Data Analysis (EDA)
# ============================================================
print("\n" + "=" * 60)
print("STEP 6: Exploratory Data Analysis (EDA)")
print("=" * 60)

# Create output directory for plots
PLOTS_DIR = os.path.join(PROJECT_DIR, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

# 6a. Spam vs Ham Count
print("\n--- Spam vs Ham Count ---")
label_counts = df['label'].value_counts()
print(label_counts)
print(f"Spam Percentage: {label_counts.get('spam', 0) / len(df) * 100:.2f}%")
print(f"Ham Percentage: {label_counts.get('ham', 0) / len(df) * 100:.2f}%")

plt.figure(figsize=(8, 5))
sns.countplot(data=df, x='label', hue='label', palette='Set2', order=['ham', 'spam'], legend=False)
plt.title('Spam vs Ham Distribution', fontsize=14, fontweight='bold')
plt.xlabel('Message Type', fontsize=12)
plt.ylabel('Count', fontsize=12)
for i, v in enumerate([label_counts.get('ham', 0), label_counts.get('spam', 0)]):
    plt.text(i, v + 20, str(v), ha='center', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, 'spam_vs_ham.png'), dpi=300)
plt.close()
print(f"[INFO] Saved plot: {os.path.join(PLOTS_DIR, 'spam_vs_ham.png')}")

# 6b. Message Length Distribution
print("\n--- Message Length Distribution ---")
df['message_length'] = df['message'].apply(len)
df['cleaned_length'] = df['cleaned_message'].apply(len)

print(f"Original Message Length - Mean: {df['message_length'].mean():.2f}, Std: {df['message_length'].std():.2f}")
print(f"Cleaned Message Length - Mean: {df['cleaned_length'].mean():.2f}, Std: {df['cleaned_length'].std():.2f}")

plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
sns.histplot(data=df, x='message_length', hue='label', bins=50, kde=True, palette='Set2')
plt.title('Original Message Length Distribution', fontsize=12, fontweight='bold')
plt.xlabel('Length (characters)')
plt.ylabel('Frequency')

plt.subplot(1, 2, 2)
sns.histplot(data=df, x='cleaned_length', hue='label', bins=50, kde=True, palette='Set2')
plt.title('Cleaned Message Length Distribution', fontsize=12, fontweight='bold')
plt.xlabel('Length (characters)')
plt.ylabel('Frequency')

plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, 'message_length_distribution.png'), dpi=300)
plt.close()
print(f"[INFO] Saved plot: {os.path.join(PLOTS_DIR, 'message_length_distribution.png')}")

# 6c. Most Common Words
print("\n--- Most Common Words ---")
all_words = ' '.join(df['cleaned_message']).split()
word_freq = Counter(all_words)
most_common = word_freq.most_common(20)
print("Top 20 Most Common Words:")
for word, count in most_common:
    print(f"  {word}: {count}")

# Plot most common words
words, counts = zip(*most_common)
plt.figure(figsize=(10, 6))
sns.barplot(x=list(counts), y=list(words), hue=list(words), palette='viridis', legend=False)
plt.title('Top 20 Most Common Words (After Preprocessing)', fontsize=14, fontweight='bold')
plt.xlabel('Frequency', fontsize=12)
plt.ylabel('Word', fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, 'most_common_words.png'), dpi=300)
plt.close()
print(f"[INFO] Saved plot: {os.path.join(PLOTS_DIR, 'most_common_words.png')}")

# Most common words by class
print("\n--- Most Common Words by Class ---")
ham_words = ' '.join(df[df['label'] == 'ham']['cleaned_message']).split()
spam_words = ' '.join(df[df['label'] == 'spam']['cleaned_message']).split()

print("Top 10 words in HAM messages:")
for word, count in Counter(ham_words).most_common(10):
    print(f"  {word}: {count}")

print("\nTop 10 words in SPAM messages:")
for word, count in Counter(spam_words).most_common(10):
    print(f"  {word}: {count}")
print("-" * 60)


# ============================================================
# STEP 7: TF-IDF Vectorization
# ============================================================
print("\n" + "=" * 60)
print("STEP 7: TF-IDF Vectorization")
print("=" * 60)

# Initialize TF-IDF Vectorizer
# max_features=5000 limits vocabulary to most informative terms
# min_df=2 ignores terms appearing in fewer than 2 documents
# max_df=0.8 ignores terms appearing in more than 80% of documents
print("[INFO] Initializing TF-IDF Vectorizer...")
tfidf = TfidfVectorizer(
    max_features=5000,      # Limit to top 5000 features
    min_df=2,               # Ignore terms in fewer than 2 documents
    max_df=0.8,             # Ignore terms in more than 80% of documents
    ngram_range=(1, 2)      # Use unigrams and bigrams
)

# Fit and transform the cleaned text
X = tfidf.fit_transform(df['cleaned_message'])
y = df['label_num'].values

print(f"[INFO] TF-IDF matrix shape: {X.shape}")
print(f"[INFO] Vocabulary size: {len(tfidf.vocabulary_)}")
print(f"[INFO] Non-zero entries: {X.nnz}")
print("[SUCCESS] TF-IDF vectorization completed.")
print("-" * 60)


# ============================================================
# STEP 8: Train/Test Split
# ============================================================
print("\n" + "=" * 60)
print("STEP 8: Train/Test Split")
print("=" * 60)

# Split with stratification to maintain class balance
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,          # 80% training, 20% testing
    random_state=42,        # Reproducible split
    stratify=y              # Maintain spam/ham ratio in both sets
)

print(f"[INFO] Training set size: {X_train.shape[0]} samples")
print(f"[INFO] Testing set size: {X_test.shape[0]} samples")
print(f"[INFO] Training set spam ratio: {np.mean(y_train)*100:.2f}%")
print(f"[INFO] Testing set spam ratio: {np.mean(y_test)*100:.2f}%")
print("[SUCCESS] Train/test split completed.")
print("-" * 60)


# ============================================================
# STEP 9: Save All Artifacts
# ============================================================
print("\n" + "=" * 60)
print("STEP 9: Saving Processed Data & Artifacts")
print("=" * 60)

OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

try:
    # 9a. Save cleaned dataset
    cleaned_csv_path = os.path.join(OUTPUT_DIR, "cleaned_dataset.csv")
    df.to_csv(cleaned_csv_path, index=False)
    print(f"[SAVED] Cleaned dataset: {cleaned_csv_path}")

    # 9b. Save TF-IDF vectorizer
    vectorizer_path = os.path.join(OUTPUT_DIR, "tfidf_vectorizer.pkl")
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(tfidf, f)
    print(f"[SAVED] TF-IDF vectorizer: {vectorizer_path}")

    # 9c. Save processed train/test data (using scipy sparse matrix format)
    from scipy import sparse

    train_data_path = os.path.join(OUTPUT_DIR, "X_train.npz")
    test_data_path = os.path.join(OUTPUT_DIR, "X_test.npz")
    sparse.save_npz(train_data_path, X_train)
    sparse.save_npz(test_data_path, X_test)
    print(f"[SAVED] Training features: {train_data_path}")
    print(f"[SAVED] Testing features: {test_data_path}")

    # 9d. Save labels
    np.save(os.path.join(OUTPUT_DIR, "y_train.npy"), y_train)
    np.save(os.path.join(OUTPUT_DIR, "y_test.npy"), y_test)
    print(f"[SAVED] Training labels: {os.path.join(OUTPUT_DIR, 'y_train.npy')}")
    print(f"[SAVED] Testing labels: {os.path.join(OUTPUT_DIR, 'y_test.npy')}")

    # 9e. Save feature names for reference
    feature_names_path = os.path.join(OUTPUT_DIR, "feature_names.pkl")
    with open(feature_names_path, 'wb') as f:
        pickle.dump(tfidf.get_feature_names_out(), f)
    print(f"[SAVED] Feature names: {feature_names_path}")

    print("\n[SUCCESS] All artifacts saved successfully.")

except Exception as e:
    print(f"[ERROR] Failed to save artifacts: {e}")
    sys.exit(1)


# ============================================================
# STEP 10: Summary
# ============================================================
print("\n" + "=" * 60)
print("PREPROCESSING PIPELINE COMPLETED SUCCESSFULLY")
print("=" * 60)
print(f"""
SUMMARY:
--------
Original Dataset:     {DATASET_PATH}
Cleaned Dataset:      {df.shape[0]} rows, {df.shape[1]} columns
Spam Count:           {label_counts.get('spam', 0)}
Ham Count:            {label_counts.get('ham', 0)}
TF-IDF Features:      {X.shape[1]}
Training Samples:     {X_train.shape[0]}
Testing Samples:      {X_test.shape[0]}

OUTPUT FILES:
-------------
Cleaned CSV:          {os.path.join(OUTPUT_DIR, 'cleaned_dataset.csv')}
TF-IDF Vectorizer:    {os.path.join(OUTPUT_DIR, 'tfidf_vectorizer.pkl')}
Training Features:    {os.path.join(OUTPUT_DIR, 'X_train.npz')}
Testing Features:     {os.path.join(OUTPUT_DIR, 'X_test.npz')}
Training Labels:      {os.path.join(OUTPUT_DIR, 'y_train.npy')}
Testing Labels:       {os.path.join(OUTPUT_DIR, 'y_test.npy')}
Feature Names:        {os.path.join(OUTPUT_DIR, 'feature_names.pkl')}
Plots Directory:      {PLOTS_DIR}

All preprocessing steps completed. Ready for model training!
""")
print("=" * 60)
