# Getting Started

<cite>
**Referenced Files in This Document**
- [spam_preprocessing.py](file://spam_preprocessing.py)
- [spam_sms_dataset.csv](file://spam_sms_dataset.csv)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [First Run Tutorial](#first-run-tutorial)
6. [Output Artifacts](#output-artifacts)
7. [Troubleshooting](#troubleshooting)
8. [Next Steps](#next-steps)

## Introduction
This guide helps you quickly set up and run the SMS Spam Detection preprocessing pipeline. The project automatically downloads required NLTK datasets, loads a CSV dataset, performs data cleaning and NLP preprocessing, generates exploratory visualizations, converts text to numerical features using TF-IDF, splits the data into train/test sets, and saves processed artifacts for downstream machine learning model training.

## Prerequisites
Before running the preprocessing pipeline, install the following Python packages. The script requires:
- pandas
- numpy
- nltk
- scikit-learn
- matplotlib
- seaborn

These are declared at the top of the preprocessing script and are used throughout the pipeline.

**Section sources**
- [spam_preprocessing.py:7](file://spam_preprocessing.py#L7)

## Installation
Follow these platform-agnostic steps to prepare your environment.

- Install Python 3.7 or newer if you haven't already.
- Create and activate a virtual environment:
  - Linux/macOS: python3 -m venv .venv && source .venv/bin/activate
  - Windows: py -m venv .venv && .venv\Scripts\Activate.ps1
- Install required packages:
  - pip install pandas numpy nltk scikit-learn matplotlib seaborn

Notes:
- The script automatically downloads NLTK corpora during the first run. If you prefer to download them manually, run the NLTK downloader before executing the script.

**Section sources**
- [spam_preprocessing.py:19-34](file://spam_preprocessing.py#L19-L34)

## Quick Start
Follow these steps to run the preprocessing pipeline:

1. Place the CSV dataset in the project root directory. The script expects a single CSV file in the same folder as the preprocessing script. The dataset must contain at least two columns: one for labels (e.g., ham/spam) and one for SMS messages.
2. Run the preprocessing script:
   - python spam_preprocessing.py
3. Review the console output and generated artifacts in the output directory.

Expected outcome:
- The script prints progress for each step and summarizes the preprocessing results.
- Output artifacts are saved under an output directory created in the project root.

**Section sources**
- [spam_preprocessing.py:62-100](file://spam_preprocessing.py#L62-L100)
- [spam_preprocessing.py:447-489](file://spam_preprocessing.py#L447-L489)

## First Run Tutorial
This tutorial walks you through the initial execution and what to expect.

- Execution flow:
  - Step 0: NLTK resources are downloaded automatically.
  - Step 1: The script auto-detects the CSV dataset in the project root and loads it.
  - Step 2: Initial dataset exploration prints shape, columns, missing values, duplicates, and a preview.
  - Step 3: Data cleaning removes empty columns, standardizes column names, drops nulls, removes duplicates, converts labels to numeric, and resets the index.
  - Step 4: NLP preprocessing applies tokenization, stopword removal, stemming, and cleans URLs and special characters.
  - Step 5: Before/after examples show transformations on sample messages.
  - Step 6: EDA creates plots (spam distribution, message length distributions, top words) and saves them to a plots directory.
  - Step 7: TF-IDF vectorization transforms cleaned messages into a sparse matrix with configurable parameters.
  - Step 8: Stratified train/test split ensures balanced classes.
  - Step 9: All artifacts are saved to the output directory.
  - Step 10: A summary prints the final statistics and saved file paths.

Verification steps:
- Confirm the dataset is detected and loaded without errors.
- Check that the plots directory contains PNG images.
- Verify that the output directory contains the saved artifacts.

**Section sources**
- [spam_preprocessing.py:37-52](file://spam_preprocessing.py#L37-L52)
- [spam_preprocessing.py:84-98](file://spam_preprocessing.py#L84-L98)
- [spam_preprocessing.py:103-178](file://spam_preprocessing.py#L103-L178)
- [spam_preprocessing.py:181-267](file://spam_preprocessing.py#L181-L267)
- [spam_preprocessing.py:270-291](file://spam_preprocessing.py#L270-L291)
- [spam_preprocessing.py:294-384](file://spam_preprocessing.py#L294-L384)
- [spam_preprocessing.py:387-414](file://spam_preprocessing.py#L387-L414)
- [spam_preprocessing.py:417-437](file://spam_preprocessing.py#L417-L437)
- [spam_preprocessing.py:440-489](file://spam_preprocessing.py#L440-L489)
- [spam_preprocessing.py:491-522](file://spam_preprocessing.py#L491-L522)

## Output Artifacts
After successful execution, the pipeline produces the following artifacts in the output directory:

- cleaned_dataset.csv: The cleaned DataFrame with standardized columns and numeric labels.
- tfidf_vectorizer.pkl: The fitted TF-IDF vectorizer for transforming new messages.
- X_train.npz: Sparse matrix containing training features.
- X_test.npz: Sparse matrix containing testing features.
- y_train.npy: Training labels array.
- y_test.npy: Testing labels array.
- feature_names.pkl: Pickled feature names from the vectorizer vocabulary.

Additionally, plots are saved in a plots directory:
- spam_vs_ham.png
- message_length_distribution.png
- most_common_words.png

**Section sources**
- [spam_preprocessing.py:447-489](file://spam_preprocessing.py#L447-L489)
- [spam_preprocessing.py:301-370](file://spam_preprocessing.py#L301-L370)

## Troubleshooting
Common issues and resolutions:

- NLTK resource download fails:
  - Symptom: An error occurs during NLTK resource download.
  - Resolution: Manually download required corpora using the NLTK downloader before running the script. Alternatively, run the script again; it attempts to download resources automatically.

- Encoding errors when loading the dataset:
  - Symptom: UnicodeDecodeError or failure to load the CSV.
  - Resolution: The script tries UTF-8 first, then falls back to latin-1. If neither works, verify the dataset encoding and ensure the CSV is valid.

- Missing CSV file:
  - Symptom: The script reports no CSV files found in the project directory.
  - Resolution: Place exactly one CSV file in the project root and rerun the script.

- Dependency conflicts:
  - Symptom: Import errors for pandas, numpy, nltk, scikit-learn, matplotlib, or seaborn.
  - Resolution: Reinstall the packages in a fresh virtual environment. Ensure versions are compatible with the script’s imports.

- Disk space or permissions:
  - Symptom: Failure to save artifacts or plots.
  - Resolution: Ensure write permissions in the project directory and sufficient disk space.

**Section sources**
- [spam_preprocessing.py:43-52](file://spam_preprocessing.py#L43-L52)
- [spam_preprocessing.py:84-98](file://spam_preprocessing.py#L84-L98)
- [spam_preprocessing.py:62-76](file://spam_preprocessing.py#L62-L76)
- [spam_preprocessing.py:486-488](file://spam_preprocessing.py#L486-L488)

## Next Steps
With the preprocessing pipeline successfully executed, you now have:
- A cleaned dataset ready for modeling.
- TF-IDF vectorizer and transformed features for training and testing.
- Labels and feature names for reproducible experiments.
- EDA visualizations to understand data characteristics.

Use the saved artifacts to train and evaluate machine learning models for SMS spam classification. The vectorizer and feature names enable consistent preprocessing of new messages.