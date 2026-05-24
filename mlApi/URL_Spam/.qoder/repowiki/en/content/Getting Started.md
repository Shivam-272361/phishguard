# Getting Started

<cite>
**Referenced Files in This Document**
- [preprocessing.py](file://preprocessing.py)
- [requirements.txt](file://requirements.txt)
- [PhiUSIIL_Phishing_URL_Dataset.csv](file://PhiUSIIL_Phishing_URL_Dataset.csv)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Dataset Preparation](#dataset-preparation)
5. [Quick Start](#quick-start)
6. [Basic Usage Examples](#basic-usage-examples)
7. [Understanding the Output](#understanding-the-output)
8. [Common Setup Issues](#common-setup-issues)
9. [Verification and First Run](#verification-and-first-run)
10. [Troubleshooting Guide](#troubleshooting-guide)
11. [Next Steps](#next-steps)

## Introduction

The URL_Spam project is a comprehensive phishing URL detection preprocessing pipeline designed to transform raw URL datasets into machine learning-ready formats. This project focuses on the PhiUSIIL Phishing URL Dataset, providing automated data cleaning, feature engineering, and dataset preparation for machine learning models.

The preprocessing pipeline handles the complete workflow from raw CSV data to standardized train/test splits, complete with exploratory data analysis, visualizations, and detailed processing summaries. Whether you're building phishing detection systems or learning about URL analysis techniques, this project provides a robust foundation for URL dataset preprocessing.

## Prerequisites

Before using the URL_Spam project, you should have familiarity with the following concepts:

### Python Fundamentals
- Basic Python syntax and data structures
- Working with command-line interfaces
- Understanding of virtual environments
- File system navigation and permissions

### Pandas DataFrame Operations
- Loading CSV files into DataFrames
- Basic data exploration and inspection
- Data filtering and selection operations
- Handling missing data and data types
- Column manipulation and data transformation
- Grouping and aggregation operations

### Basic Machine Learning Concepts
- Understanding supervised learning tasks
- Training and testing data splits
- Feature engineering and preprocessing
- Binary classification concepts
- Data validation and quality assessment

## Installation

Follow these step-by-step instructions to set up your environment:

### Step 1: Create a Virtual Environment
```bash
# Create a new virtual environment
python -m venv url_spam_env

# Activate the environment (Windows)
url_spam_env\Scripts\activate

# Activate the environment (macOS/Linux)
source url_spam_env/bin/activate
```

### Step 2: Upgrade pip
```bash
python -m pip install --upgrade pip
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

The requirements.txt file specifies the following dependencies:
- pandas >= 2.0.0 (data manipulation and analysis)
- numpy >= 1.24.0 (numerical computing)
- scikit-learn >= 1.3.0 (machine learning algorithms)
- matplotlib >= 3.7.0 (data visualization)
- seaborn >= 0.12.0 (statistical data visualization)

### Step 4: Verify Installation
```bash
python -c "import pandas, numpy, sklearn, matplotlib, seaborn; print('All dependencies installed successfully')"
```

## Dataset Preparation

The preprocessing pipeline expects a CSV dataset with specific column requirements. Here's how to prepare your dataset:

### Required Dataset Structure
Your dataset should contain the following essential columns:
- **label**: Target variable (binary classification: 0 for legitimate, 1 for phishing)
- **URL**: Complete URL string (optional but enables advanced feature engineering)
- **Domain**: Domain portion of the URL (optional)
- Additional numerical features for URL analysis

### Automatic Dataset Detection
The pipeline automatically detects CSV files in your working directory:
- Searches for files with `.csv` extension
- Selects the largest CSV file as the primary dataset
- Raises an error if no CSV files are found

### Manual Dataset Specification
If you need to specify a different dataset path:
```python
from preprocessing import PhishingURLPreprocessor

# Initialize with custom dataset path
preprocessor = PhishingURLPreprocessor(dataset_path="path/to/your/dataset.csv")
```

### Dataset Example Structure
The PhiUSIIL dataset includes features like:
- URL characteristics (length, special characters)
- Domain analysis (length, suspicious TLDs)
- Content analysis metrics
- Binary flags for obfuscation techniques

## Quick Start

Complete the following steps to run your first preprocessing job:

### Step 1: Prepare Your Dataset
Place your CSV dataset in the project root directory. The pipeline will automatically detect it.

### Step 2: Run the Preprocessing Pipeline
```bash
python preprocessing.py
```

### Step 3: Monitor Progress
The pipeline logs detailed progress information including:
- Dataset loading and inspection
- Data cleaning operations
- Feature engineering steps
- Model preparation and splitting
- Output generation

### Expected Runtime
Processing typically takes 1-3 minutes depending on dataset size and system performance.

## Basic Usage Examples

### Running with Default Settings
```bash
python preprocessing.py
```

This executes the complete pipeline with default configurations:
- Automatic dataset detection
- Standard train/test split (80/20 ratio)
- Default random state for reproducibility
- All preprocessing steps enabled

### Customizing Dataset Path
```python
from preprocessing import PhishingURLPreprocessor

# Specify custom dataset path
custom_preprocessor = PhishingURLPreprocessor(
    dataset_path="/path/to/your/custom_dataset.csv"
)
custom_preprocessor.run()
```

### Running Specific Pipeline Steps
```python
from preprocessing import PhishingURLPreprocessor

preprocessor = PhishingURLPreprocessor()

# Load and inspect dataset
preprocessor.load_dataset()
preprocessor.eda_inspection()

# Clean and process
preprocessor.clean_dataset()
preprocessor.preprocess_url_features()

# Continue with remaining steps...
```

## Understanding the Output

The preprocessing pipeline generates several types of output files:

### Processed Datasets
All outputs are saved in the `output/` directory:

- **cleaned_dataset.csv**: Complete cleaned dataset with all preprocessing applied
- **X_train.csv**: Training features (without labels)
- **X_test.csv**: Testing features (without labels)
- **y_train.csv**: Training labels
- **y_test.csv**: Testing labels

### Visualizations
Generated plots are saved in the `plots/` directory:

- **class_distribution.png**: Distribution of legitimate vs phishing URLs
- **correlation_heatmap.png**: Top 30 feature correlations
- **feature_importance.png**: Random Forest feature importance scores
- **feature_histograms.png**: Key URL feature distributions

### Processing Summary
- **preprocessing_summary.txt**: Complete processing log and statistics

### Output Directory Structure
```
output/
├── cleaned_dataset.csv
├── X_train.csv
├── X_test.csv
├── y_train.csv
├── y_test.csv
└── preprocessing_summary.txt

plots/
├── class_distribution.png
├── correlation_heatmap.png
├── feature_importance.png
└── feature_histograms.png
```

## Common Setup Issues

### Issue 1: Python Version Compatibility
**Problem**: Unsupported Python version
**Solution**: Use Python 3.8 or higher
```bash
python --version
# Ensure version is 3.8+
```

### Issue 2: Missing Dependencies
**Problem**: ImportError during execution
**Solution**: Reinstall dependencies
```bash
pip uninstall pandas numpy scikit-learn matplotlib seaborn
pip install -r requirements.txt
```

### Issue 3: Permission Errors
**Problem**: Cannot create output directories
**Solution**: Check write permissions
```bash
# Verify current directory permissions
dir  # Windows
ls -la  # Unix/Linux/macOS
```

### Issue 4: Memory Issues
**Problem**: Out of memory errors with large datasets
**Solution**: Process smaller subsets or increase system RAM
- Consider sampling your dataset for initial testing
- Monitor memory usage during processing

### Issue 5: Matplotlib Backend Issues
**Problem**: Display backend errors in headless environments
**Solution**: The pipeline automatically uses non-interactive backend
```python
# This is handled internally by the pipeline
matplotlib.use("Agg")
```

## Verification and First Run

### Step 1: Confirm Dependencies
```bash
python -c "
import pandas as pd
import numpy as np
import sklearn
import matplotlib
import seaborn
print('Dependencies verified:')
print(f'pandas: {pd.__version__}')
print(f'numpy: {np.__version__}')
print(f'scikit-learn: {sklearn.__version__}')
print(f'matplotlib: {matplotlib.__version__}')
print(f'seaborn: {seaborn.__version__}')
"
```

### Step 2: Test Dataset Loading
```python
from preprocessing import PhishingURLPreprocessor

# Test automatic dataset detection
try:
    preprocessor = PhishingURLPreprocessor()
    print('Dataset detected successfully')
    print(f'Dataset path: {preprocessor.dataset_path}')
except FileNotFoundError as e:
    print(f'Dataset detection failed: {e}')
```

### Step 3: Run Minimal Pipeline
```bash
# Test with minimal dataset
python preprocessing.py
```

### Step 4: Verify Output Files
After successful completion, check for:
- `output/cleaned_dataset.csv` (non-empty)
- `output/preprocessing_summary.txt` (contains processing details)
- `plots/` directory with generated visualizations

## Troubleshooting Guide

### Dependency Conflicts
**Symptom**: Package installation failures
**Diagnosis**: Check for conflicting package versions
```bash
pip list | grep -E "(pandas|numpy|scikit-learn|matplotlib|seaborn)"
```

**Resolution**: 
1. Create a fresh virtual environment
2. Install requirements in order
3. Use compatible versions as specified in requirements.txt

### Environment Configuration Problems
**Symptom**: Module not found errors
**Cause**: Incorrect Python interpreter selection
**Solution**:
```bash
# Verify Python path
which python
# Ensure it points to your virtual environment

# Reactivate virtual environment
deactivate
source url_spam_env/bin/activate  # Linux/macOS
# or
url_spam_env\Scripts\activate  # Windows
```

### Dataset Issues
**Symptom**: Target column not found
**Cause**: Missing or differently named label column
**Solution**:
```python
# The pipeline accepts various label column names:
# 'label', 'Label', 'LABEL', 'class', 'Class', 'CLASS', 'target', 'Target'
```

**Symptom**: Empty or corrupted CSV
**Solution**:
```bash
# Validate CSV structure
head -n 5 your_dataset.csv
wc -l your_dataset.csv  # Check row count
```

### Performance Issues
**Symptom**: Slow processing
**Cause**: Large dataset or insufficient system resources
**Optimization Strategies**:
1. Use smaller sample datasets for testing
2. Close other applications during processing
3. Consider chunked processing for very large files

### Output Generation Failures
**Symptom**: Missing output files
**Cause**: Permission or path issues
**Solution**:
```bash
# Check directory permissions
ls -la output/
ls -la plots/

# Create directories manually if needed
mkdir output plots
chmod 755 output plots
```

## Next Steps

### Data Analysis
Explore the processed datasets:
```python
import pandas as pd

# Load processed data
df = pd.read_csv('output/cleaned_dataset.csv')
print(df.info())
print(df.describe())
```

### Model Training
Use the prepared datasets for machine learning:
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Load features and labels
X = pd.read_csv('output/X_train.csv')
y = pd.read_csv('output/y_train.csv')

# Train model
model = RandomForestClassifier(random_state=42)
model.fit(X, y)
```

### Further Customization
Extend the preprocessing pipeline:
- Add custom feature engineering
- Implement additional data cleaning steps
- Modify visualization parameters
- Integrate with different machine learning frameworks

### Contributing
Enhance the project by:
- Adding support for additional dataset formats
- Implementing new feature extraction techniques
- Improving error handling and logging
- Creating additional visualization types