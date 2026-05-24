"""
Fit StandardScaler on Raw Preprocessed Features
=================================================
Re-runs the preprocessing pipeline up to (but not including) scaling,
then fits a StandardScaler on the raw features and saves it.
This allows the API to properly scale newly extracted features.

Usage:
    python fit_scaler_on_raw.py
"""

import os
import sys
import logging

import joblib
from sklearn.preprocessing import StandardScaler

# Add current directory to path so we can import preprocessing
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from preprocessing import PhishingURLPreprocessor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("FitScaler")

MODELS_DIR = "models"


def main():
    logger.info("Running preprocessing pipeline up to scaling...")

    preprocessor = PhishingURLPreprocessor()
    preprocessor.load_dataset()
    preprocessor.eda_inspection()
    preprocessor.clean_dataset()
    preprocessor.preprocess_url_features()
    preprocessor.encode_categoricals()
    preprocessor.remove_unnecessary_columns()

    df = preprocessor.df_cleaned.copy()
    X = df.drop(columns=["label"])
    feature_names = list(X.columns)

    logger.info("Raw feature matrix shape: %s", X.shape)

    scaler = StandardScaler()
    scaler.fit(X)
    logger.info("Fitted StandardScaler on %d raw features.", len(feature_names))

    os.makedirs(MODELS_DIR, exist_ok=True)
    scaler_path = os.path.join(MODELS_DIR, "scaler_raw.pkl")
    joblib.dump(scaler, scaler_path)
    logger.info("Saved raw scaler to: %s", scaler_path)

    # Also update feature_metadata.json with raw medians
    import json
    meta_path = os.path.join(MODELS_DIR, "feature_metadata.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
    else:
        meta = {}

    meta["feature_names"] = feature_names
    meta["feature_count"] = len(feature_names)
    meta["raw_medians"] = {k: float(v) for k, v in X.median().to_dict().items()}
    meta["raw_means"] = {k: float(v) for k, v in X.mean().to_dict().items()}
    meta["raw_stds"] = {k: float(v) for k, v in X.std().to_dict().items()}

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    logger.info("Updated feature_metadata.json with raw statistics.")


if __name__ == "__main__":
    main()
