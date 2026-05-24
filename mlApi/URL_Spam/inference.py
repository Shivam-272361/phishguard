"""
Phishing URL Detection - Model Inference / Prediction
=======================================================
A production-ready inference script for testing the trained
Random Forest model with new preprocessed inputs.

Usage:
    python inference.py                          -> Demo mode using X_test
    python inference.py --input custom.csv       -> Batch prediction on custom CSV
    python inference.py --input custom.csv --output results.csv

Author: AI Assistant
Date: 2026-05-09
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd
import joblib

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MODEL_PATH = os.path.join("models", "random_forest_phishing_model.pkl")
DEFAULT_INPUT_DIR = "output"
DEFAULT_INPUT_FILE = "X_test.csv"
DEFAULT_OUTPUT_DIR = "output"
DEFAULT_OUTPUT_FILE = "predictions.csv"

# ---------------------------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------------------------
def setup_logging() -> logging.Logger:
    """Configure professional logging."""
    logger = logging.getLogger("PhishingInference")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger


logger = setup_logging()


# ---------------------------------------------------------------------------
# Core Inference Class
# ---------------------------------------------------------------------------
class PhishingPredictor:
    """
    Inference wrapper for the trained Random Forest phishing detector.
    """

    def __init__(self, model_path: str = MODEL_PATH):
        self.model = None
        self.model_path = model_path
        self.feature_names: list = []
        self._load_model()

    def _load_model(self) -> None:
        """Load the serialized Random Forest model from disk."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Model file not found: {self.model_path}. "
                "Please run train_model.py first."
            )

        logger.info("Loading model from: %s", self.model_path)
        self.model = joblib.load(self.model_path)
        logger.info("Model loaded successfully. Type: %s", type(self.model).__name__)

    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Run batch prediction on a preprocessed feature DataFrame.

        Parameters
        ----------
        X : pd.DataFrame
            Preprocessed features matching the training schema.

        Returns
        -------
        pd.DataFrame
            DataFrame with 'Predicted_Label', 'Predicted_Class',
            and 'Phishing_Probability' columns.
        """
        if self.model is None:
            raise RuntimeError("Model is not loaded.")

        # Align columns with model expectations
        if hasattr(self.model, "feature_names_in_"):
            expected = list(self.model.feature_names_in_)
            missing = set(expected) - set(X.columns)
            extra = set(X.columns) - set(expected)

            if missing:
                raise ValueError(f"Input is missing expected columns: {sorted(missing)}")
            if extra:
                logger.warning("Ignoring extra columns in input: %s", sorted(extra))
                X = X[expected]
            else:
                X = X[expected]

        # Predict class labels and probabilities
        # NOTE: PhiUSIIL dataset uses inverted labels:
        #       label 1 = Legitimate, label 0 = Phishing
        logger.info("Running inference on %d samples...", len(X))
        labels = self.model.predict(X)
        probas = self.model.predict_proba(X)
        phishing_probabilities = probas[:, 0]  # class 0 = phishing

        results = pd.DataFrame({
            "Predicted_Label": labels,
            "Predicted_Class": np.where(labels == 1, "Legitimate", "Phishing"),
            "Phishing_Probability": phishing_probabilities.round(6),
            "Confidence_Score": np.where(
                labels == 0,
                phishing_probabilities.round(6),
                (1 - phishing_probabilities).round(6)
            )
        })

        logger.info("Inference complete.")
        return results

    def predict_single(self, features: dict) -> dict:
        """
        Run prediction on a single sample provided as a dictionary.

        Parameters
        ----------
        features : dict
            Dictionary of feature names and values.

        Returns
        -------
        dict
            Prediction result with label, class name, and probability.
        """
        X = pd.DataFrame([features])
        result = self.predict(X).iloc[0].to_dict()
        return result


# ---------------------------------------------------------------------------
# Demo / Utility Functions
# ---------------------------------------------------------------------------
def run_demo_mode(predictor: PhishingPredictor, n_samples: int = 10) -> None:
    """
    Run inference in demo mode using a random subset of the test set.
    Loads the corresponding true labels to show comparison.
    """
    logger.info("=" * 60)
    logger.info("INFERENCE DEMO MODE")
    logger.info("=" * 60)

    # Load test features and labels
    x_path = os.path.join(DEFAULT_INPUT_DIR, DEFAULT_INPUT_FILE)
    y_path = os.path.join(DEFAULT_INPUT_DIR, "y_test.csv")

    if not os.path.exists(x_path) or not os.path.exists(y_path):
        raise FileNotFoundError(
            "Demo mode requires output/X_test.csv and output/y_test.csv. "
            "Please run preprocessing.py and train_model.py first."
        )

    X_test = pd.read_csv(x_path)
    y_test = pd.read_csv(y_path).iloc[:, 0]

    # Drop index column if present
    if "Unnamed: 0" in X_test.columns:
        X_test = X_test.drop(columns=["Unnamed: 0"])

    # Random sample for display
    sample_idx = np.random.choice(X_test.index, size=min(n_samples, len(X_test)), replace=False)
    X_sample = X_test.loc[sample_idx].reset_index(drop=True)
    y_sample = y_test.loc[sample_idx].reset_index(drop=True)

    # Predict
    predictions = predictor.predict(X_sample)

    # Combine with true labels
    output_df = X_sample.copy()
    output_df["True_Label"] = y_sample.values
    output_df["True_Class"] = np.where(y_sample.values == 1, "Legitimate", "Phishing")
    output_df = pd.concat([output_df, predictions], axis=1)

    # Show summary
    logger.info("Demo sample size: %d", len(output_df))
    logger.info("Predicted class distribution:\n%s", predictions["Predicted_Class"].value_counts())

    correct = (predictions["Predicted_Label"] == y_sample.values).sum()
    logger.info("Correct predictions in sample: %d / %d (%.2f%%)",
                correct, len(output_df), 100 * correct / len(output_df))

    # Pretty-print sample results
    print("\n" + "=" * 80)
    print("SAMPLE PREDICTIONS")
    print("=" * 80)
    display_cols = ["True_Class", "Predicted_Class", "Phishing_Probability", "Confidence_Score"]
    print(output_df[display_cols].to_string(index=True))
    print("=" * 80 + "\n")

    # Save full demo predictions
    demo_path = os.path.join(DEFAULT_OUTPUT_DIR, "demo_predictions.csv")
    os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
    output_df.to_csv(demo_path, index=False)
    logger.info("Full demo predictions saved to: %s", demo_path)


def run_batch_mode(predictor: PhishingPredictor, input_path: str, output_path: str) -> None:
    """Run batch inference on a user-provided CSV file."""
    logger.info("=" * 60)
    logger.info("BATCH INFERENCE MODE")
    logger.info("=" * 60)

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    logger.info("Loading input data from: %s", input_path)
    X = pd.read_csv(input_path)

    if "Unnamed: 0" in X.columns:
        X = X.drop(columns=["Unnamed: 0"])

    predictions = predictor.predict(X)

    # Combine and save
    combined = pd.concat([X, predictions], axis=1)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    combined.to_csv(output_path, index=False)

    logger.info("Predictions saved to: %s", output_path)
    logger.info("Total predictions: %d", len(combined))
    logger.info("Class distribution:\n%s", predictions["Predicted_Class"].value_counts())

    # Print summary
    print("\n" + "=" * 60)
    print("BATCH PREDICTION SUMMARY")
    print("=" * 60)
    print(f"Input file  : {input_path}")
    print(f"Output file : {output_path}")
    print(f"Samples     : {len(combined)}")
    print(f"Phishing    : {(predictions['Predicted_Label'] == 1).sum()}")
    print(f"Legitimate  : {(predictions['Predicted_Label'] == 0).sum()}")
    print(f"Avg Confidence: {predictions['Confidence_Score'].mean():.4f}")
    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Phishing URL Detection Inference",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python inference.py                          # Demo mode (random samples from X_test)
  python inference.py -n 20                    # Demo with 20 samples
  python inference.py -i my_data.csv           # Batch prediction
  python inference.py -i my_data.csv -o out.csv # Custom output path
        """
    )
    parser.add_argument(
        "-i", "--input",
        type=str,
        default=None,
        help="Path to preprocessed feature CSV for batch prediction."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=DEFAULT_OUTPUT_FILE,
        help="Path to save prediction results (default: output/predictions.csv)."
    )
    parser.add_argument(
        "-n", "--samples",
        type=int,
        default=10,
        help="Number of demo samples to display (default: 10)."
    )
    parser.add_argument(
        "-m", "--model",
        type=str,
        default=MODEL_PATH,
        help="Path to trained model pickle file."
    )

    args = parser.parse_args()

    # Initialize predictor
    predictor = PhishingPredictor(model_path=args.model)

    if args.input is None:
        # Demo mode
        run_demo_mode(predictor, n_samples=args.samples)
    else:
        # Batch mode
        output_path = args.output
        if not os.path.isabs(output_path):
            output_path = os.path.join(DEFAULT_OUTPUT_DIR, output_path)
        run_batch_mode(predictor, args.input, output_path)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logger.error("Inference failed: %s", exc, exc_info=True)
        sys.exit(1)
