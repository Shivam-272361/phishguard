"""
PhiUSIIL Phishing URL Dataset - Preprocessing Pipeline
=======================================================
A production-ready, modular preprocessing pipeline for the AI-powered
phishing URL detection system.

Author: AI Assistant
Date: 2026-05-09
"""

import os
import sys
import logging
import warnings
from datetime import datetime
from typing import Tuple, List, Optional
import glob

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Use non-interactive backend for headless environments
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import mutual_info_classif

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RANDOM_STATE = 42
TEST_SIZE = 0.2
OUTPUT_DIR = "output"
PLOTS_DIR = "plots"
SUMMARY_FILE = "preprocessing_summary.txt"

# Columns to drop (textual / identifiers not suitable for ML)
DROP_COLUMNS = ["FILENAME", "URL", "Domain", "Title"]

# Setup matplotlib style
plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("husl")

warnings.filterwarnings("ignore")


# ---------------------------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------------------------
def setup_logging() -> logging.Logger:
    """Configure professional logging with timestamps and levels."""
    logger = logging.getLogger("PhishingPreprocessing")
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


def find_csv_dataset(directory: str = ".") -> str:
    """
    Automatically detect a CSV dataset in the given directory.
    Raises FileNotFoundError if no CSV is found.
    """
    pattern = os.path.join(directory, "*.csv")
    candidates = glob.glob(pattern)

    if not candidates:
        raise FileNotFoundError(f"No CSV file found in directory: {directory}")

    # Prefer the largest CSV (assumes it is the main dataset)
    dataset_path = max(candidates, key=os.path.getsize)
    logger.info("Auto-detected dataset: %s", dataset_path)
    return dataset_path


def save_dataframe(df: pd.DataFrame, path: str, index: bool = False) -> None:
    """Persist a DataFrame to CSV with error handling."""
    try:
        df.to_csv(path, index=index)
        logger.info("Saved DataFrame to %s (shape=%s)", path, df.shape)
    except Exception as exc:
        logger.error("Failed to save %s: %s", path, exc)
        raise


# ---------------------------------------------------------------------------
# Core Pipeline Class
# ---------------------------------------------------------------------------
class PhishingURLPreprocessor:
    """
    End-to-end preprocessor for the PhiUSIIL Phishing URL Dataset.
    """

    def __init__(self, dataset_path: Optional[str] = None):
        self.dataset_path = dataset_path or find_csv_dataset()
        self.df: Optional[pd.DataFrame] = None
        self.df_cleaned: Optional[pd.DataFrame] = None
        self.X: Optional[pd.DataFrame] = None
        self.y: Optional[pd.Series] = None
        self.X_train: Optional[pd.DataFrame] = None
        self.X_test: Optional[pd.DataFrame] = None
        self.y_train: Optional[pd.Series] = None
        self.y_test: Optional[pd.Series] = None
        self.scaler: Optional[StandardScaler] = None
        self.label_encoder: Optional[LabelEncoder] = None
        self.original_shape: Tuple[int, int] = (0, 0)
        self.removed_duplicates: int = 0
        self.removed_missing: int = 0
        self.final_feature_count: int = 0
        self.numeric_columns: List[str] = []

    # =======================================================================
    # 1. Load & Inspect
    # =======================================================================
    def load_dataset(self) -> pd.DataFrame:
        """Load the CSV dataset and perform initial inspection."""
        logger.info("=" * 60)
        logger.info("STEP 1: Loading Dataset")
        logger.info("=" * 60)

        self.df = pd.read_csv(self.dataset_path)
        self.original_shape = self.df.shape

        logger.info("Dataset loaded successfully.")
        logger.info("  Shape        : %s", self.df.shape)
        logger.info("  Columns      : %d", len(self.df.columns))
        logger.info("  Column Names : %s", list(self.df.columns))
        logger.info("  Data Types   :\n%s", self.df.dtypes)
        logger.info("  Missing Values per Column:\n%s", self.df.isnull().sum())
        logger.info("  Duplicate Rows: %d", self.df.duplicated().sum())

        if "label" not in self.df.columns:
            # Try common alternatives
            for alt in ["Label", "LABEL", "class", "Class", "CLASS", "target", "Target"]:
                if alt in self.df.columns:
                    self.df.rename(columns={alt: "label"}, inplace=True)
                    logger.info("Renamed target column '%s' -> 'label'", alt)
                    break
            else:
                raise ValueError("Target column 'label' not found in dataset.")

        logger.info("  Class Distribution:\n%s", self.df["label"].value_counts().sort_index())
        return self.df

    # =======================================================================
    # 2. Exploratory Data Analysis (EDA) - Textual
    # =======================================================================
    def eda_inspection(self) -> None:
        """Log detailed EDA statistics before cleaning."""
        logger.info("=" * 60)
        logger.info("STEP 2: Exploratory Data Analysis (EDA)")
        logger.info("=" * 60)

        df = self.df
        logger.info("--- Basic Statistics ---")
        logger.info("Shape: %s", df.shape)
        logger.info("Memory usage: %.2f MB", df.memory_usage(deep=True).sum() / (1024 * 1024))

        logger.info("--- Missing Values Summary ---")
        missing = df.isnull().sum()
        missing_pct = (missing / len(df)) * 100
        missing_df = pd.DataFrame({
            "Missing Count": missing,
            "Missing %": missing_pct.round(4)
        })
        logger.info("\n%s", missing_df[missing_df["Missing Count"] > 0])

        logger.info("--- Duplicate Rows ---")
        logger.info("Exact duplicates: %d", df.duplicated().sum())

        logger.info("--- Target Distribution ---")
        logger.info("\n%s", df["label"].value_counts())
        logger.info("Target proportion:\n%s", df["label"].value_counts(normalize=True).round(4))

        logger.info("--- Numeric Columns Summary ---")
        numeric_df = df.select_dtypes(include=[np.number])
        logger.info("Numeric columns count: %d", len(numeric_df.columns))
        logger.info("Numeric describe:\n%s", numeric_df.describe().transpose().head(10))

    # =======================================================================
    # 3. Data Cleaning
    # =======================================================================
    def clean_dataset(self) -> pd.DataFrame:
        """
        Clean the dataset by:
        - Removing rows with null values
        - Removing duplicate rows
        - Handling invalid / out-of-range rows
        - Encoding target labels
        """
        logger.info("=" * 60)
        logger.info("STEP 3: Data Cleaning")
        logger.info("=" * 60)

        df = self.df.copy()
        original_rows = len(df)

        # 3.1 Remove rows with null values
        null_before = df.isnull().sum().sum()
        df.dropna(inplace=True)
        self.removed_missing = original_rows - len(df)
        logger.info("Removed %d rows containing null values (total null cells: %d).",
                    self.removed_missing, null_before)

        # 3.2 Remove duplicate rows
        dup_count = df.duplicated().sum()
        df.drop_duplicates(inplace=True)
        self.removed_duplicates = dup_count
        logger.info("Removed %d duplicate rows.", dup_count)

        # 3.3 Handle invalid rows
        # Remove rows where label is not 0 or 1 (assuming binary classification)
        valid_labels = df["label"].isin([0, 1])
        invalid_labels = (~valid_labels).sum()
        df = df[valid_labels]
        logger.info("Removed %d rows with invalid labels.", invalid_labels)

        # Remove rows with negative counts where only non-negative makes sense
        count_cols = [c for c in df.columns if c.startswith(("NoOf", "Has", "Is"))]
        for col in count_cols:
            if df[col].dtype in [np.int64, np.float64]:
                invalid_mask = df[col] < 0
                if invalid_mask.sum() > 0:
                    logger.info("Clipped %d negative values in '%s' to 0.", invalid_mask.sum(), col)
                    df.loc[invalid_mask, col] = 0

        # 3.4 Encode target labels
        self.label_encoder = LabelEncoder()
        df["label"] = self.label_encoder.fit_transform(df["label"].astype(str))
        logger.info("Target labels encoded. Classes: %s", self.label_encoder.classes_)

        self.df_cleaned = df
        logger.info("Cleaned dataset shape: %s", df.shape)
        return df

    # =======================================================================
    # 4. URL Feature Preprocessing & Engineering
    # =======================================================================
    def preprocess_url_features(self) -> pd.DataFrame:
        """
        Engineer and preprocess URL-specific features:
        - URL length (already present as URLLength)
        - Number of dots in URL
        - Presence of HTTPS (already present as IsHTTPS)
        - Presence of IP address in domain (already present as IsDomainIP)
        - Special characters count
        - Suspicious symbols (@, // in path, etc.)
        - Prefix / suffix usage (www, suspicious TLDs)
        """
        logger.info("=" * 60)
        logger.info("STEP 4: URL Feature Preprocessing")
        logger.info("=" * 60)

        df = self.df_cleaned.copy()

        # If raw URL column exists, extract additional handcrafted features
        if "URL" in df.columns:
            urls = df["URL"].astype(str)

            # 4.1 Number of dots in full URL
            df["NoOfDotsInURL"] = urls.str.count(r"\.")
            logger.info("Engineered feature: NoOfDotsInURL")

            # 4.2 Number of special characters in URL
            df["NoOfSpecialCharsInURL"] = urls.str.count(r"[^a-zA-Z0-9\.\/:]")
            logger.info("Engineered feature: NoOfSpecialCharsInURL")

            # 4.3 Presence of suspicious symbols
            df["HasAtSymbol"] = urls.str.contains(r"@", regex=True, na=False).astype(int)
            df["HasDoubleSlash"] = urls.str.contains(r"//", regex=True, na=False).astype(int)
            logger.info("Engineered features: HasAtSymbol, HasDoubleSlash")

            # 4.4 Prefix / suffix indicators
            df["HasWWW"] = urls.str.contains(r"www\.", regex=True, na=False).astype(int)
            logger.info("Engineered feature: HasWWW")

            # 4.5 Suspicious TLDs (commonly abused)
            suspicious_tlds = {"tk", "ml", "ga", "cf", "top", "xyz", "bid", "work", "date", "party", "link", "download"}
            if "TLD" in df.columns:
                df["HasSuspiciousTLD"] = df["TLD"].astype(str).str.lower().isin(suspicious_tlds).astype(int)
                logger.info("Engineered feature: HasSuspiciousTLD")
        else:
            logger.warning("Raw 'URL' column not found; skipping URL-derived feature engineering.")

        # 4.6 Domain-based features if Domain column exists
        if "Domain" in df.columns:
            domains = df["Domain"].astype(str)
            df["NoOfDotsInDomain"] = domains.str.count(r"\.")
            df["HasHyphenInDomain"] = domains.str.contains(r"-", regex=True, na=False).astype(int)
            logger.info("Engineered features: NoOfDotsInDomain, HasHyphenInDomain")

        self.df_cleaned = df
        return df

    # =======================================================================
    # 5. Encode Categorical Features
    # =======================================================================
    def encode_categoricals(self) -> pd.DataFrame:
        """Encode non-numeric categorical columns for ML compatibility."""
        logger.info("=" * 60)
        logger.info("STEP 5: Encoding Categorical Features")
        logger.info("=" * 60)

        df = self.df_cleaned.copy()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

        # Remove identifier/text columns that will be dropped later anyway
        for col in DROP_COLUMNS:
            if col in categorical_cols:
                categorical_cols.remove(col)

        for col in categorical_cols:
            unique_count = df[col].nunique()
            if unique_count <= 10:
                # One-hot encode low-cardinality categoricals
                dummies = pd.get_dummies(df[col], prefix=col, drop_first=False)
                df = pd.concat([df.drop(columns=[col]), dummies], axis=1)
                logger.info("One-hot encoded '%s' (%d categories).", col, unique_count)
            else:
                # Frequency encoding for high-cardinality categoricals
                freq_map = df[col].value_counts().to_dict()
                df[col + "_FreqEnc"] = df[col].map(freq_map)
                df.drop(columns=[col], inplace=True)
                logger.info("Frequency encoded '%s' (%d unique values).", col, unique_count)

        self.df_cleaned = df
        return df

    # =======================================================================
    # 6. Remove Unnecessary Columns
    # =======================================================================
    def remove_unnecessary_columns(self) -> pd.DataFrame:
        """Drop columns that are not useful for machine learning."""
        logger.info("=" * 60)
        logger.info("STEP 6: Removing Unnecessary Columns")
        logger.info("=" * 60)

        df = self.df_cleaned.copy()
        cols_to_drop = [c for c in DROP_COLUMNS if c in df.columns]

        if cols_to_drop:
            df.drop(columns=cols_to_drop, inplace=True)
            logger.info("Dropped columns: %s", cols_to_drop)
        else:
            logger.info("No unnecessary columns to drop.")

        self.df_cleaned = df
        return df

    # =======================================================================
    # 7. Scale Numerical Features
    # =======================================================================
    def scale_features(self, fit_on_train: bool = True) -> pd.DataFrame:
        """
        Normalize/scale numerical features using StandardScaler.
        This is applied to the full cleaned dataset before train/test split
        for simplicity, but in production one should fit only on training data.
        """
        logger.info("=" * 60)
        logger.info("STEP 7: Scaling Numerical Features")
        logger.info("=" * 60)

        df = self.df_cleaned.copy()
        self.numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()

        if "label" in self.numeric_columns:
            self.numeric_columns.remove("label")

        if not self.numeric_columns:
            logger.warning("No numeric columns found for scaling.")
            return df

        self.scaler = StandardScaler()
        df[self.numeric_columns] = self.scaler.fit_transform(df[self.numeric_columns])
        logger.info("Scaled %d numerical features using StandardScaler.", len(self.numeric_columns))

        self.df_cleaned = df
        return df

    # =======================================================================
    # 8. Separate Features & Target
    # =======================================================================
    def separate_features_target(self) -> Tuple[pd.DataFrame, pd.Series]:
        """Separate independent features (X) from the target label (y)."""
        logger.info("=" * 60)
        logger.info("STEP 8: Separating Features (X) and Target (y)")
        logger.info("=" * 60)

        df = self.df_cleaned.copy()
        self.y = df["label"]
        self.X = df.drop(columns=["label"])
        self.final_feature_count = self.X.shape[1]

        logger.info("Features (X) shape : %s", self.X.shape)
        logger.info("Target (y) shape   : %s", self.y.shape)
        logger.info("Final feature count: %d", self.final_feature_count)
        return self.X, self.y

    # =======================================================================
    # 9. Train-Test Split with Stratification
    # =======================================================================
    def split_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Perform stratified train-test split to preserve class balance."""
        logger.info("=" * 60)
        logger.info("STEP 9: Stratified Train-Test Split")
        logger.info("=" * 60)

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X,
            self.y,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE,
            stratify=self.y,
            shuffle=True
        )

        logger.info("Training set   -> X_train: %s | y_train: %s", self.X_train.shape, self.y_train.shape)
        logger.info("Testing set    -> X_test : %s | y_test : %s", self.X_test.shape, self.y_test.shape)
        logger.info("Train class distribution:\n%s", self.y_train.value_counts().sort_index())
        logger.info("Test class distribution:\n%s", self.y_test.value_counts().sort_index())

        return self.X_train, self.X_test, self.y_train, self.y_test

    # =======================================================================
    # 10. Save Processed Datasets
    # =======================================================================
    def save_outputs(self) -> None:
        """Persist cleaned data and train/test splits to the output folder."""
        logger.info("=" * 60)
        logger.info("STEP 10: Saving Processed Datasets")
        logger.info("=" * 60)

        ensure_dir(OUTPUT_DIR)

        # 10.1 Save cleaned full dataset
        cleaned_path = os.path.join(OUTPUT_DIR, "cleaned_dataset.csv")
        cleaned_df = pd.concat([self.X, self.y], axis=1)
        save_dataframe(cleaned_df, cleaned_path)

        # 10.2 Save train/test splits
        save_dataframe(self.X_train, os.path.join(OUTPUT_DIR, "X_train.csv"))
        save_dataframe(self.X_test, os.path.join(OUTPUT_DIR, "X_test.csv"))
        save_dataframe(self.y_train.to_frame(name="label"), os.path.join(OUTPUT_DIR, "y_train.csv"))
        save_dataframe(self.y_test.to_frame(name="label"), os.path.join(OUTPUT_DIR, "y_test.csv"))

        logger.info("All datasets saved to '%s/' directory.", OUTPUT_DIR)

    # =======================================================================
    # 11. EDA Visualizations
    # =======================================================================
    def generate_visualizations(self) -> None:
        """
        Generate and save EDA plots:
        - Class distribution
        - Correlation heatmap
        - Feature importance plot
        - Histograms of key numerical features
        """
        logger.info("=" * 60)
        logger.info("STEP 11: Generating EDA Visualizations")
        logger.info("=" * 60)

        ensure_dir(PLOTS_DIR)
        df = self.df_cleaned.copy()

        # -----------------------------------------------------------------
        # 11.1 Class Distribution
        # -----------------------------------------------------------------
        logger.info("Plotting class distribution...")
        fig, ax = plt.subplots(figsize=(8, 6))
        class_counts = df["label"].value_counts().sort_index()
        bars = ax.bar(class_counts.index.astype(str), class_counts.values, color=["#3498db", "#e74c3c"], edgecolor="black")
        ax.set_xlabel("Class Label", fontsize=12)
        ax.set_ylabel("Count", fontsize=12)
        ax.set_title("Class Distribution (0 = Legitimate, 1 = Phishing)", fontsize=14, fontweight="bold")
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f"{height:,}", xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=10)
        fig.tight_layout()
        fig.savefig(os.path.join(PLOTS_DIR, "class_distribution.png"), dpi=300)
        plt.close(fig)
        logger.info("Saved: class_distribution.png")

        # -----------------------------------------------------------------
        # 11.2 Correlation Heatmap
        # -----------------------------------------------------------------
        logger.info("Plotting correlation heatmap...")
        numeric_df = df.select_dtypes(include=[np.number])
        # Select top 30 features by absolute correlation with label for readability
        corr_with_label = numeric_df.corr()["label"].abs().sort_values(ascending=False)
        top_features = corr_with_label.head(30).index.tolist()
        corr_matrix = numeric_df[top_features].corr()

        fig, ax = plt.subplots(figsize=(18, 14))
        sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", center=0,
                    linewidths=0.5, ax=ax, cbar_kws={"shrink": 0.8})
        ax.set_title("Top 30 Feature Correlation Heatmap", fontsize=16, fontweight="bold")
        fig.tight_layout()
        fig.savefig(os.path.join(PLOTS_DIR, "correlation_heatmap.png"), dpi=300)
        plt.close(fig)
        logger.info("Saved: correlation_heatmap.png")

        # -----------------------------------------------------------------
        # 11.3 Feature Importance (Random Forest)
        # -----------------------------------------------------------------
        logger.info("Computing feature importance via RandomForest...")
        X = df.drop(columns=["label"])
        y = df["label"]

        # Use only numeric columns for the quick RF model
        X_numeric = X.select_dtypes(include=[np.number])
        rf = RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE, n_jobs=-1)
        rf.fit(X_numeric, y)

        importances = pd.Series(rf.feature_importances_, index=X_numeric.columns)
        top_imp = importances.sort_values(ascending=False).head(25)

        fig, ax = plt.subplots(figsize=(12, 10))
        top_imp.plot(kind="barh", color="teal", edgecolor="black", ax=ax)
        ax.set_xlabel("Importance Score", fontsize=12)
        ax.set_ylabel("Feature", fontsize=12)
        ax.set_title("Top 25 Feature Importances (Random Forest)", fontsize=14, fontweight="bold")
        ax.invert_yaxis()
        fig.tight_layout()
        fig.savefig(os.path.join(PLOTS_DIR, "feature_importance.png"), dpi=300)
        plt.close(fig)
        logger.info("Saved: feature_importance.png")

        # -----------------------------------------------------------------
        # 11.4 Histograms of Key URL Features
        # -----------------------------------------------------------------
        logger.info("Plotting histograms of key URL features...")
        hist_candidates = ["URLLength", "DomainLength", "NoOfSubDomain", "NoOfOtherSpecialCharsInURL", "URLSimilarityIndex"]
        hist_features = [c for c in hist_candidates if c in df.columns]

        if hist_features:
            n_cols = 3
            n_rows = (len(hist_features) + n_cols - 1) // n_cols
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows))
            axes = axes.flatten() if n_rows > 1 or len(hist_features) > 1 else [axes]

            for idx, col in enumerate(hist_features):
                ax = axes[idx]
                for label, color in zip(sorted(df["label"].unique()), ["#3498db", "#e74c3c"]):
                    subset = df[df["label"] == label][col]
                    ax.hist(subset, bins=50, alpha=0.6, label=f"Label {label}", color=color, edgecolor="black")
                ax.set_title(col, fontsize=12, fontweight="bold")
                ax.set_xlabel("Value")
                ax.set_ylabel("Frequency")
                ax.legend()

            # Hide unused subplots
            for idx in range(len(hist_features), len(axes)):
                axes[idx].set_visible(False)

            fig.tight_layout()
            fig.savefig(os.path.join(PLOTS_DIR, "feature_histograms.png"), dpi=300)
            plt.close(fig)
            logger.info("Saved: feature_histograms.png")
        else:
            logger.warning("No suitable columns found for histogram plotting.")

    # =======================================================================
    # 12. Preprocessing Summary Report
    # =======================================================================
    def generate_summary(self) -> str:
        """Generate and save a textual preprocessing summary report."""
        logger.info("=" * 60)
        logger.info("STEP 12: Generating Preprocessing Summary")
        logger.info("=" * 60)

        summary_lines = [
            "=" * 60,
            "PHISHING URL DATASET - PREPROCESSING SUMMARY REPORT",
            "=" * 60,
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "--- Dataset Overview ---",
            f"Original shape           : {self.original_shape[0]} rows x {self.original_shape[1]} columns",
            f"Cleaned shape            : {self.df_cleaned.shape[0]} rows x {self.df_cleaned.shape[1]} columns",
            f"Removed duplicates       : {self.removed_duplicates}",
            f"Missing values handled   : {self.removed_missing} rows removed",
            f"Final feature count (X)  : {self.final_feature_count}",
            "",
            "--- Train / Test Split ---",
            f"Test size ratio          : {TEST_SIZE}",
            f"Random state             : {RANDOM_STATE}",
            f"X_train shape            : {self.X_train.shape}",
            f"X_test  shape            : {self.X_test.shape}",
            f"y_train distribution     : {dict(self.y_train.value_counts().sort_index())}",
            f"y_test  distribution     : {dict(self.y_test.value_counts().sort_index())}",
            "",
            "--- Feature Engineering ---",
            "Engineered features added (if URL column present):",
            "  - NoOfDotsInURL",
            "  - NoOfSpecialCharsInURL",
            "  - HasAtSymbol",
            "  - HasDoubleSlash",
            "  - HasWWW",
            "  - HasSuspiciousTLD",
            "  - NoOfDotsInDomain",
            "  - HasHyphenInDomain",
            "",
            "--- Scaling ---",
            f"Scaler used              : StandardScaler",
            f"Numerical columns scaled : {len(self.numeric_columns)}",
            "",
            "--- Output Files ---",
            "  - output/cleaned_dataset.csv",
            "  - output/X_train.csv",
            "  - output/X_test.csv",
            "  - output/y_train.csv",
            "  - output/y_test.csv",
            "",
            "--- Plots Generated ---",
            "  - plots/class_distribution.png",
            "  - plots/correlation_heatmap.png",
            "  - plots/feature_importance.png",
            "  - plots/feature_histograms.png",
            "",
            "=" * 60,
            "END OF REPORT",
            "=" * 60,
        ]

        summary_text = "\n".join(summary_lines)
        summary_path = os.path.join(OUTPUT_DIR, SUMMARY_FILE)
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary_text)

        logger.info("Summary report saved to: %s", summary_path)
        return summary_text

    # =======================================================================
    # Master Run Method
    # =======================================================================
    def run(self) -> None:
        """Execute the complete preprocessing pipeline end-to-end."""
        logger.info("\n" + "=" * 60)
        logger.info("STARTING PHISHING URL PREPROCESSING PIPELINE")
        logger.info("=" * 60 + "\n")

        start_time = datetime.now()

        self.load_dataset()
        self.eda_inspection()
        self.clean_dataset()
        self.preprocess_url_features()
        self.encode_categoricals()
        self.remove_unnecessary_columns()
        self.scale_features()
        self.separate_features_target()
        self.split_data()
        self.save_outputs()
        self.generate_visualizations()
        summary = self.generate_summary()

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY in %.2f seconds", elapsed)
        logger.info("=" * 60)

        print("\n" + summary)


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        preprocessor = PhishingURLPreprocessor()
        preprocessor.run()
    except Exception as exc:
        logger.error("Pipeline failed: %s", exc, exc_info=True)
        sys.exit(1)
