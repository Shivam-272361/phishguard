

import os
import sys
import json
import logging
from datetime import datetime

import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from preprocessing import PhishingURLPreprocessor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("TrainURLOnly")

MODELS_DIR = "models"
RANDOM_STATE = 42
TEST_SIZE = 0.2

# Features that feature_extractor.py can compute from a URL alone
URL_ONLY_FEATURES = [
    "URLLength", "DomainLength", "IsDomainIP", "URLSimilarityIndex",
    "CharContinuationRate", "TLDLegitimateProb", "URLCharProb", "TLDLength",
    "NoOfSubDomain", "HasObfuscation", "NoOfObfuscatedChar", "ObfuscationRatio",
    "NoOfLettersInURL", "LetterRatioInURL", "NoOfDegitsInURL", "DegitRatioInURL",
    "NoOfEqualsInURL", "NoOfQMarkInURL", "NoOfAmpersandInURL",
    "NoOfOtherSpecialCharsInURL", "SpacialCharRatioInURL", "IsHTTPS",
    "NoOfDotsInURL", "NoOfSpecialCharsInURL", "HasAtSymbol", "HasDoubleSlash",
    "HasWWW", "HasSuspiciousTLD", "NoOfDotsInDomain", "HasHyphenInDomain",
    "Bank", "Pay", "Crypto", "TLD_FreqEnc",
]


def main():
    logger.info("=" * 60)
    logger.info("TRAINING URL-ONLY PHISHING DETECTION MODEL")
    logger.info("=" * 60)

    # -----------------------------------------------------------------
    # 1. Run preprocessing up to scaling (same as full pipeline)
    # -----------------------------------------------------------------
    logger.info("Running preprocessing pipeline...")
    preprocessor = PhishingURLPreprocessor()
    preprocessor.load_dataset()
    preprocessor.clean_dataset()
    preprocessor.preprocess_url_features()
    preprocessor.encode_categoricals()
    preprocessor.remove_unnecessary_columns()

    df = preprocessor.df_cleaned.copy()

    # -----------------------------------------------------------------
    # 2. Save TLD frequency map for the API
    # -----------------------------------------------------------------
    tld_freq_path = os.path.join(MODELS_DIR, "tld_frequency_map.json")
    os.makedirs(MODELS_DIR, exist_ok=True)

    # Reconstruct TLD frequency from original dataset
    original_df = preprocessor.df.copy()
    if "TLD" in original_df.columns:
        tld_freq = original_df["TLD"].value_counts().to_dict()
        with open(tld_freq_path, "w", encoding="utf-8") as f:
            json.dump(tld_freq, f, ensure_ascii=False, indent=2)
        logger.info("Saved TLD frequency map (%d unique TLDs) to %s", len(tld_freq), tld_freq_path)
    else:
        logger.warning("TLD column not found; skipping TLD frequency map.")
        tld_freq = {}

    # -----------------------------------------------------------------
    # 3. Select URL-only features
    # -----------------------------------------------------------------
    available = [f for f in URL_ONLY_FEATURES if f in df.columns]
    missing = [f for f in URL_ONLY_FEATURES if f not in df.columns]
    if missing:
        logger.warning("Missing URL-only features (will be skipped): %s", missing)

    X = df[available].copy()
    y = df["label"].copy()

    logger.info("URL-only feature matrix: %s | Features: %d", X.shape, len(available))
    logger.info("Feature list: %s", available)

    # -----------------------------------------------------------------
    # 4. Scale features
    # -----------------------------------------------------------------
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=available)

    scaler_path = os.path.join(MODELS_DIR, "scaler_url_only.pkl")
    joblib.dump(scaler, scaler_path)
    logger.info("Saved URL-only scaler to %s", scaler_path)

    # -----------------------------------------------------------------
    # 5. Train-test split
    # -----------------------------------------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    logger.info("Train: %s | Test: %s", X_train.shape, X_test.shape)

    # -----------------------------------------------------------------
    # 6. Train Random Forest
    # -----------------------------------------------------------------
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        class_weight="balanced",
        bootstrap=True,
    )

    logger.info("Training URL-only Random Forest...")
    start = datetime.now()
    model.fit(X_train, y_train)
    elapsed = (datetime.now() - start).total_seconds()
    logger.info("Training completed in %.2f seconds", elapsed)

    # -----------------------------------------------------------------
    # 7. Evaluate
    # -----------------------------------------------------------------
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1": f1_score(y_test, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_test, y_prob),
    }

    logger.info("--- URL-Only Model Performance ---")
    for k, v in metrics.items():
        logger.info("  %-12s : %.4f", k, v)

    # -----------------------------------------------------------------
    # 8. Save model + metadata
    # -----------------------------------------------------------------
    model_path = os.path.join(MODELS_DIR, "random_forest_url_only.pkl")
    joblib.dump(model, model_path)
    logger.info("Saved URL-only model to %s", model_path)

    meta = {
        "feature_names": available,
        "feature_count": len(available),
        "metrics": {k: float(v) for k, v in metrics.items()},
        "trained_at": datetime.now().isoformat(),
        "training_samples": len(X_train),
        "test_samples": len(X_test),
    }
    meta_path = os.path.join(MODELS_DIR, "url_only_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    logger.info("Saved URL-only metadata to %s", meta_path)

    logger.info("=" * 60)
    logger.info("URL-ONLY MODEL TRAINING COMPLETE")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
