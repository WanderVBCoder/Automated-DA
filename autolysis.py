# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pandas",
#   "numpy",
#   "matplotlib",
#   "seaborn",
#   "requests",
#   "tenacity",
#   "tabulate"
# ]
# ///

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from tenacity import retry, stop_after_attempt, wait_fixed

# 1. Load CSV
def load_data(filename):
    try:
        df = pd.read_csv(filename, encoding='ISO-8859-1')
        print(f"Loaded dataset with {df.shape[0]} rows and {df.shape[1]} columns.")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)

# 2. Analyze Data
def analyze_data(df):
    summary = df.describe(include='all')
    missing_values = df.isnull().sum()
    correlation_matrix = df.corr(numeric_only=True)
    return summary, missing_values, correlation_matrix

# 3. Generate Visuals
def generate_visualizations(df, folder):
    # Chart 1: Correlation Heatmap
    corr = df.corr(numeric_only=True)
    if not corr.empty:
        plt.figure(figsize=(10, 6))
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f')
        plt.title("Feature Correlation Heatmap")
        plt.tight_layout()
        plt.savefig(f"{folder}/chart1.png", dpi=300)
        plt.close()

    # Chart 2: Average Rating Distribution (if exists)
    if 'average_rating' in df.columns:
        plt.figure(figsize=(8, 5))
        sns.histplot(df['average_rating'].dropna(), bins=20, kde=True, color='green')
        plt.title("Distribution of Average Ratings")
        plt.xlabel("Average Rating")
        plt.ylabel("Frequency")
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.tight_layout()
        plt.savefig(f"{folder}/chart2.png", dpi=300)
        plt.close()

# 4. Get Insights from OpenAI
def get_openai_response(prompt):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not set.")
        sys.exit(1)

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-3.5-turbo",  # or "gpt-4" if you have access
        "messages": [
            {"role": "system", "content": "You are a data analyst."},
            {"role": "user", "content": prompt}
        ]
    }

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def chat():
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")

    return chat()

# 5. Write README
def generate_report(folder, filename, summary, missing_values, correlation_matrix, insights):
    readme_path = os.path.join(folder, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(f"# Automated Data Analysis Report\n\n")
        f.write(f"## Dataset: `{filename}`\n\n")

        f.write("### Summary Statistics\n\n")
        f.write(summary.to_markdown() + "\n\n")

        f.write("### Missing Values\n\n")
        f.write(missing_values.to_frame(name='missing_count').to_markdown() + "\n\n")

        f.write("### Correlation Matrix\n\n")
        f.write(correlation_matrix.to_markdown() + "\n\n")

        f.write("### AI-Generated Insights\n\n")
        f.write(insights + "\n\n")

        f.write("### Visualizations\n\n")
        if os.path.exists(f"{folder}/chart1.png"):
            f.write("![Correlation Heatmap](chart1.png)\n\n")
        if os.path.exists(f"{folder}/chart2.png"):
            f.write("![Rating Distribution](chart2.png)\n")

# 6. Main Entry Point
def main():
    if len(sys.argv) != 2:
        print("Usage: uv run autolysis.py <dataset.csv>")
        sys.exit(1)

    filename = sys.argv[1]
    df = load_data(filename)
    summary, missing_values, correlation_matrix = analyze_data(df)

    # Derive output folder from dataset name
    folder = os.path.splitext(os.path.basename(filename))[0]
    os.makedirs(folder, exist_ok=True)

    generate_visualizations(df, folder)

    # Trim prompt to avoid sending too much text
    prompt = (
        f"Here is a dataset summary:\n\n"
        f"Columns and types:\n{df.dtypes.to_string()}\n\n"
        f"Top summary:\n{summary.head().to_string()}\n\n"
        f"Missing values:\n{missing_values.head().to_string()}\n\n"
        f"Correlation matrix:\n{correlation_matrix.head().to_string()}\n\n"
        f"Write a narrative-style story with insights, trends, and what actions could be taken based on this data."
    )

    insights = get_openai_response(prompt)
    generate_report(folder, filename, summary, missing_values, correlation_matrix, insights)
    print(f"✅ Analysis complete. Output saved in `{folder}/README.md` and PNG files.")

if __name__ == "__main__":
    main()

