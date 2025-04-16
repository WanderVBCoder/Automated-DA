# 📊 Project 2 – Automated Data Analysis with LLMs

This project was completed as part of the **KaroStartup Internship Program**, where the goal was to build a fully automated data analysis pipeline using an LLM (GPT-4o-Mini via AI Proxy).

---

## 🚀 Objective

Build a single Python script, `autolysis.py`, that:

- Accepts a CSV file as input
- Performs **general-purpose analysis** without prior knowledge of the dataset
- Leverages an **LLM** to generate insights, suggest further analysis, and narrate a story
- Generates:
  - A structured `README.md` (story-style output)
  - 1–3 charts (`*.png`) to support the narrative

---

## 🛠️ Usage

1. **Install [uv](https://docs.astral.sh/uv/) (Python package manager)**  
   Follow: https://docs.astral.sh/uv/getting-started/installation/

2. **Set your AI Proxy Token** (DO NOT commit this key to GitHub)

```bash
export AIPROXY_TOKEN=your_token_here
# Automated-DA
