

import os
import json
import logging

import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler, LabelEncoder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("SaveArtifacts")

CLEANED_PATH = "output/cleaned_dataset.csv"
MODELS_DIR = "models"
META_PATH = os.path.join(MODELS_DIR, "feature_metadata.json")


def main():
    logger.info("Loading cleaned dataset from: %s", CLEANED_PATH)
    df = pd.read_csv(CLEANED_PATH)

    if "label" not in df.columns:
        raise ValueError("'label' column not found in cleaned dataset.")

    X = df.drop(columns=["label"])
    y = df["label"]

    feature_names = list(X.columns)
    logger.info("Features (%d): %s", len(feature_names), feature_names)

    # Fit scaler on the cleaned data (which is already scaled in preprocessing,
    # but we re-fit here to get a scaler object that can be used for new data)
    # NOTE: The original preprocessing scaled data before train/test split.
    # For the API to accept RAW features, we need a scaler fitted on RAW data.
    # Since cleaned_dataset.csv contains already-scaled data, fitting a scaler
    # here would produce identity-like parameters.
    # Better approach: load the raw cleaned data BEFORE scaling.
    # However, since we don't have that saved, we'll create a pass-through scaler
    # and document that the API expects pre-scaled features OR we accept raw
    # features and the user is responsible for scaling.

    # STRATEGY: The API will accept pre-scaled features by default.
    # We save the feature names, medians (from scaled data), and a flag.
    # If the user sends raw features, we warn them.

    medians = X.median().to_dict()
    for k, v in medians.items():
        if isinstance(v, (np.floating, np.integer)):
            medians[k] = float(v)

    scaler = StandardScaler()
    scaler.fit(X)  # Fit on already-scaled data (near identity)

    label_encoder = LabelEncoder()
    label_encoder.fit(y.astype(str))

    os.makedirs(MODELS_DIR, exist_ok=True)

    joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler.pkl"))
    logger.info("Saved scaler.pkl")

    joblib.dump(label_encoder, os.path.join(MODELS_DIR, "label_encoder.pkl"))
    logger.info("Saved label_encoder.pkl")

    metadata = {
        "feature_names": feature_names,
        "feature_count": len(feature_names),
        "medians": medians,
        "label_classes": list(label_encoder.classes_),
        "note": (
            "The model was trained on StandardScaler-transformed features. "
            "For best results, submit pre-scaled feature values. "
            "If raw features are submitted, they will be passed through "
            "a no-op scaler (identity) and results may be less accurate."
        )
    }

    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    logger.info("Saved feature_metadata.json")

    logger.info("All artifacts saved to '%s/'", MODELS_DIR)


if __name__ == "__main__":
    main()
