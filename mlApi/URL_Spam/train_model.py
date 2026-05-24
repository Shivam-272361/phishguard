

import os
import sys
import logging
import warnings
from datetime import datetime
from typing import Dict, Any, Tuple

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    roc_curve, precision_recall_curve, average_precision_score
)
from sklearn.model_selection import cross_val_score, StratifiedKFold
import joblib

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RANDOM_STATE = 42
N_ESTIMATORS = 200
MAX_DEPTH = None
MIN_SAMPLES_SPLIT = 5
MIN_SAMPLES_LEAF = 2
N_JOBS = -1
CV_FOLDS = 5

INPUT_DIR = "output"
MODELS_DIR = "models"
PLOTS_DIR = "plots"
REPORTS_DIR = "reports"
MODEL_FILE = "random_forest_phishing_model.pkl"
METRICS_FILE = "model_evaluation_report.txt"

warnings.filterwarnings("ignore")
plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("husl")


# ---------------------------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------------------------
def setup_logging() -> logging.Logger:
    """Configure professional logging with timestamps and levels."""
    logger = logging.getLogger("PhishingModelTraining")
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
# Utility Functions
# ---------------------------------------------------------------------------
def ensure_dir(path: str) -> None:
    """Create directory if it does not already exist."""
    os.makedirs(path, exist_ok=True)
    logger.info("Ensured directory exists: %s", path)


def load_dataset(filename: str) -> pd.DataFrame:
    """Load a CSV dataset from the input directory."""
    path = os.path.join(INPUT_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Required file not found: {path}")
    df = pd.read_csv(path)
    logger.info("Loaded '%s' -> shape: %s", filename, df.shape)
    return df


# ---------------------------------------------------------------------------
# Core Training Pipeline Class
# ---------------------------------------------------------------------------
class PhishingModelTrainer:
    """
    End-to-end Random Forest training and evaluation pipeline
    for phishing URL detection.
    """

    def __init__(self):
        self.X_train: pd.DataFrame = None
        self.X_test: pd.DataFrame = None
        self.y_train: pd.Series = None
        self.y_test: pd.Series = None
        self.model: RandomForestClassifier = None
        self.y_pred: np.ndarray = None
        self.y_prob: np.ndarray = None
        self.metrics: Dict[str, float] = {}
        self.cv_scores: np.ndarray = None
        self.feature_names: list = []

    # =======================================================================
    # 1. Load Preprocessed Data
    # =======================================================================
    def load_data(self) -> None:
        """Load preprocessed train and test datasets from the output folder."""
        logger.info("=" * 60)
        logger.info("STEP 1: Loading Preprocessed Datasets")
        logger.info("=" * 60)

        self.X_train = load_dataset("X_train.csv")
        self.X_test = load_dataset("X_test.csv")
        self.y_train = load_dataset("y_train.csv").iloc[:, 0]
        self.y_test = load_dataset("y_test.csv").iloc[:, 0]

        # Drop index column if accidentally saved
        for df_name, df in [("X_train", self.X_train), ("X_test", self.X_test)]:
            if "Unnamed: 0" in df.columns:
                df.drop(columns=["Unnamed: 0"], inplace=True)
                logger.info("Dropped 'Unnamed: 0' index column from %s.", df_name)

        self.feature_names = list(self.X_train.columns)
        logger.info("Feature count: %d", len(self.feature_names))
        logger.info("Training samples: %d | Testing samples: %d", len(self.X_train), len(self.X_test))

    # =======================================================================
    # 2. Train Random Forest Classifier
    # =======================================================================
    def train_model(self) -> RandomForestClassifier:
        """
        Initialize and train a Random Forest classifier with tuned
        hyperparameters suitable for the phishing detection task.
        """
        logger.info("=" * 60)
        logger.info("STEP 2: Training Random Forest Classifier")
        logger.info("=" * 60)

        self.model = RandomForestClassifier(
            n_estimators=N_ESTIMATORS,
            max_depth=MAX_DEPTH,
            min_samples_split=MIN_SAMPLES_SPLIT,
            min_samples_leaf=MIN_SAMPLES_LEAF,
            random_state=RANDOM_STATE,
            n_jobs=N_JOBS,
            class_weight="balanced",  # Handle potential imbalance
            bootstrap=True,
            oob_score=True
        )

        logger.info("Model hyperparameters:")
        logger.info("  n_estimators      : %d", N_ESTIMATORS)
        logger.info("  max_depth         : %s", MAX_DEPTH)
        logger.info("  min_samples_split : %d", MIN_SAMPLES_SPLIT)
        logger.info("  min_samples_leaf  : %d", MIN_SAMPLES_LEAF)
        logger.info("  class_weight      : balanced")
        logger.info("  oob_score         : True")

        logger.info("Training started...")
        self.model.fit(self.X_train, self.y_train)
        logger.info("Training completed.")
        logger.info("Out-of-bag (OOB) Score: %.4f", self.model.oob_score_)

        return self.model

    # =======================================================================
    # 3. Cross-Validation
    # =======================================================================
    def cross_validate(self) -> None:
        """Perform stratified k-fold cross-validation on the training set."""
        logger.info("=" * 60)
        logger.info("STEP 3: Stratified Cross-Validation")
        logger.info("=" * 60)

        cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
        self.cv_scores = cross_val_score(
            self.model, self.X_train, self.y_train,
            cv=cv, scoring="roc_auc", n_jobs=N_JOBS
        )

        logger.info("CV ROC-AUC scores (%d-fold): %s", CV_FOLDS, self.cv_scores)
        logger.info("CV Mean ROC-AUC : %.4f (+/- %.4f)",
                    self.cv_scores.mean(), self.cv_scores.std())

    # =======================================================================
    # 4. Model Evaluation
    # =======================================================================
    def evaluate(self) -> Dict[str, float]:
        """
        Evaluate the trained model on the held-out test set.
        Computes accuracy, precision, recall, F1, and ROC-AUC.
        """
        logger.info("=" * 60)
        logger.info("STEP 4: Model Evaluation on Test Set")
        logger.info("=" * 60)

        self.y_pred = self.model.predict(self.X_test)
        self.y_prob = self.model.predict_proba(self.X_test)[:, 1]

        self.metrics = {
            "accuracy": accuracy_score(self.y_test, self.y_pred),
            "precision": precision_score(self.y_test, self.y_pred, zero_division=0),
            "recall": recall_score(self.y_test, self.y_pred, zero_division=0),
            "f1_score": f1_score(self.y_test, self.y_pred, zero_division=0),
            "roc_auc": roc_auc_score(self.y_test, self.y_prob),
            "average_precision": average_precision_score(self.y_test, self.y_prob),
        }

        logger.info("--- Classification Metrics ---")
        for metric, value in self.metrics.items():
            logger.info("  %-20s : %.4f", metric.replace("_", " ").title(), value)

        logger.info("\n--- Detailed Classification Report ---")
        report = classification_report(self.y_test, self.y_pred, target_names=["Legitimate", "Phishing"])
        logger.info("\n%s", report)

        return self.metrics

    # =======================================================================
    # 5. Save Trained Model
    # =======================================================================
    def save_model(self) -> None:
        """Persist the trained Random Forest model to disk using joblib."""
        logger.info("=" * 60)
        logger.info("STEP 5: Saving Trained Model")
        logger.info("=" * 60)

        ensure_dir(MODELS_DIR)
        model_path = os.path.join(MODELS_DIR, MODEL_FILE)
        joblib.dump(self.model, model_path)
        logger.info("Model saved to: %s", model_path)

    # =======================================================================
    # 6. Generate Evaluation Visualizations
    # =======================================================================
    def generate_plots(self) -> None:
        """
        Generate and save evaluation plots:
        - Confusion Matrix
        - ROC Curve
        - Precision-Recall Curve
        - Top Feature Importances
        """
        logger.info("=" * 60)
        logger.info("STEP 6: Generating Evaluation Plots")
        logger.info("=" * 60)

        ensure_dir(PLOTS_DIR)

        # -----------------------------------------------------------------
        # 6.1 Confusion Matrix
        # -----------------------------------------------------------------
        logger.info("Plotting confusion matrix...")
        cm = confusion_matrix(self.y_test, self.y_pred)
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", square=True,
                    xticklabels=["Legitimate", "Phishing"],
                    yticklabels=["Legitimate", "Phishing"],
                    linewidths=1, linecolor="black", ax=ax)
        ax.set_xlabel("Predicted Label", fontsize=12)
        ax.set_ylabel("True Label", fontsize=12)
        ax.set_title("Confusion Matrix", fontsize=14, fontweight="bold")
        fig.tight_layout()
        fig.savefig(os.path.join(PLOTS_DIR, "confusion_matrix.png"), dpi=300)
        plt.close(fig)
        logger.info("Saved: confusion_matrix.png")

        # -----------------------------------------------------------------
        # 6.2 ROC Curve
        # -----------------------------------------------------------------
        logger.info("Plotting ROC curve...")
        fpr, tpr, _ = roc_curve(self.y_test, self.y_prob)
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(fpr, tpr, color="darkorange", lw=2,
                label=f"ROC Curve (AUC = {self.metrics['roc_auc']:.4f})")
        ax.plot([0, 1], [0, 1], color="navy", lw=2, linestyle="--", label="Random Classifier")
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel("False Positive Rate", fontsize=12)
        ax.set_ylabel("True Positive Rate", fontsize=12)
        ax.set_title("Receiver Operating Characteristic (ROC)", fontsize=14, fontweight="bold")
        ax.legend(loc="lower right", fontsize=11)
        fig.tight_layout()
        fig.savefig(os.path.join(PLOTS_DIR, "roc_curve.png"), dpi=300)
        plt.close(fig)
        logger.info("Saved: roc_curve.png")

        # -----------------------------------------------------------------
        # 6.3 Precision-Recall Curve
        # -----------------------------------------------------------------
        logger.info("Plotting precision-recall curve...")
        precision_vals, recall_vals, _ = precision_recall_curve(self.y_test, self.y_prob)
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(recall_vals, precision_vals, color="teal", lw=2,
                label=f"PR Curve (AP = {self.metrics['average_precision']:.4f})")
        ax.set_xlabel("Recall", fontsize=12)
        ax.set_ylabel("Precision", fontsize=12)
        ax.set_title("Precision-Recall Curve", fontsize=14, fontweight="bold")
        ax.legend(loc="lower left", fontsize=11)
        fig.tight_layout()
        fig.savefig(os.path.join(PLOTS_DIR, "precision_recall_curve.png"), dpi=300)
        plt.close(fig)
        logger.info("Saved: precision_recall_curve.png")

        # -----------------------------------------------------------------
        # 6.4 Feature Importance
        # -----------------------------------------------------------------
        logger.info("Plotting feature importances...")
        importances = pd.Series(self.model.feature_importances_, index=self.feature_names)
        top_imp = importances.sort_values(ascending=False).head(25)

        fig, ax = plt.subplots(figsize=(12, 10))
        top_imp.plot(kind="barh", color="mediumseagreen", edgecolor="black", ax=ax)
        ax.set_xlabel("Importance Score", fontsize=12)
        ax.set_ylabel("Feature", fontsize=12)
        ax.set_title("Top 25 Random Forest Feature Importances", fontsize=14, fontweight="bold")
        ax.invert_yaxis()
        fig.tight_layout()
        fig.savefig(os.path.join(PLOTS_DIR, "model_feature_importance.png"), dpi=300)
        plt.close(fig)
        logger.info("Saved: model_feature_importance.png")

    # =======================================================================
    # 7. Generate Evaluation Report
    # =======================================================================
    def generate_report(self) -> str:
        """Generate and save a comprehensive evaluation report."""
        logger.info("=" * 60)
        logger.info("STEP 7: Generating Evaluation Report")
        logger.info("=" * 60)

        ensure_dir(REPORTS_DIR)

        cm = confusion_matrix(self.y_test, self.y_pred)
        tn, fp, fn, tp = cm.ravel()

        lines = [
            "=" * 60,
            "PHISHING URL DETECTION - MODEL EVALUATION REPORT",
            "=" * 60,
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "--- Model Configuration ---",
            f"Algorithm              : Random Forest Classifier",
            f"N Estimators           : {N_ESTIMATORS}",
            f"Max Depth              : {MAX_DEPTH}",
            f"Min Samples Split      : {MIN_SAMPLES_SPLIT}",
            f"Min Samples Leaf       : {MIN_SAMPLES_LEAF}",
            f"Class Weight           : balanced",
            f"Random State           : {RANDOM_STATE}",
            "",
            "--- Dataset Split ---",
            f"Training samples       : {len(self.X_train):,}",
            f"Testing samples        : {len(self.X_test):,}",
            f"Feature count          : {len(self.feature_names)}",
            "",
            "--- Cross-Validation (Stratified 5-Fold) ---",
            f"CV ROC-AUC Scores      : {self.cv_scores.round(4).tolist()}",
            f"CV Mean ROC-AUC        : {self.cv_scores.mean():.4f} (+/- {self.cv_scores.std():.4f})",
            f"OOB Score              : {self.model.oob_score_:.4f}",
            "",
            "--- Test Set Performance ---",
            f"Accuracy               : {self.metrics['accuracy']:.4f}",
            f"Precision              : {self.metrics['precision']:.4f}",
            f"Recall (Sensitivity)   : {self.metrics['recall']:.4f}",
            f"F1-Score               : {self.metrics['f1_score']:.4f}",
            f"ROC-AUC                : {self.metrics['roc_auc']:.4f}",
            f"Average Precision      : {self.metrics['average_precision']:.4f}",
            "",
            "--- Confusion Matrix ---",
            f"True Negatives (TN)    : {tn:,}",
            f"False Positives (FP)   : {fp:,}",
            f"False Negatives (FN)   : {fn:,}",
            f"True Positives (TP)    : {tp:,}",
            "",
            "--- Classification Report ---",
            classification_report(self.y_test, self.y_pred, target_names=["Legitimate", "Phishing"]),
            "",
            "--- Top 10 Important Features ---",
        ]

        importances = pd.Series(self.model.feature_importances_, index=self.feature_names)
        for feat, score in importances.sort_values(ascending=False).head(10).items():
            lines.append(f"  {feat:<35s} : {score:.4f}")

        lines.extend([
            "",
            "--- Output Files ---",
            f"  Model                : {MODELS_DIR}/{MODEL_FILE}",
            f"  Confusion Matrix     : {PLOTS_DIR}/confusion_matrix.png",
            f"  ROC Curve            : {PLOTS_DIR}/roc_curve.png",
            f"  Precision-Recall     : {PLOTS_DIR}/precision_recall_curve.png",
            f"  Feature Importance   : {PLOTS_DIR}/model_feature_importance.png",
            "",
            "=" * 60,
            "END OF REPORT",
            "=" * 60,
        ])

        report_text = "\n".join(lines)
        report_path = os.path.join(REPORTS_DIR, METRICS_FILE)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_text)

        logger.info("Evaluation report saved to: %s", report_path)
        return report_text

    # =======================================================================
    # Master Run Method
    # =======================================================================
    def run(self) -> None:
        """Execute the complete training and evaluation pipeline."""
        logger.info("\n" + "=" * 60)
        logger.info("STARTING RANDOM FOREST TRAINING PIPELINE")
        logger.info("=" * 60 + "\n")

        start_time = datetime.now()

        self.load_data()
        self.train_model()
        self.cross_validate()
        self.evaluate()
        self.save_model()
        self.generate_plots()
        report = self.generate_report()

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info("\n" + "=" * 60)
        logger.info("TRAINING PIPELINE COMPLETED SUCCESSFULLY in %.2f seconds", elapsed)
        logger.info("=" * 60)

        print("\n" + report)


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        trainer = PhishingModelTrainer()
        trainer.run()
    except Exception as exc:
        logger.error("Training pipeline failed: %s", exc, exc_info=True)
        sys.exit(1)
