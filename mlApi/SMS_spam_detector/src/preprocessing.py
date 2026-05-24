import pandas as pd
import re

# Load dataset
df = pd.read_csv(r"data/raw/spam.csv")

# Text cleaning function
def clean_text(text):
    
    # Convert to lowercase
    text = text.lower()

    # Replace URLs with URL token
    text = re.sub(r'http\S+|www\S+|https\S+', ' URL ', text)

    # Remove special characters
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)

    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# Apply cleaning
df['cleaned_msg'] = df['msg'].apply(clean_text)

# Show original and cleaned text
print(df[['msg', 'cleaned_msg']].head())

df.to_csv(r"data/processed/cleaned_spam.csv", index=False)

print("\nCleaned dataset saved successfully.")