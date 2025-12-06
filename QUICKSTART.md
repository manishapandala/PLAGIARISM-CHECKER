# 🚀 Quick Start Guide

## Where to Execute

**Execute in your terminal/command line:**

### Step 1: Navigate to the workspace directory
```bash
cd /workspace
```

### Step 2: Install dependencies (first time only)
```bash
pip install -r requirements.txt
```

Or if you have Python 3 specifically:
```bash
pip3 install -r requirements.txt
```

### Step 3: Run the complete analysis
```bash
python3 main_analysis.py
```

That's it! The analysis will:
- ✅ Generate 10,000 synthetic records
- ✅ Run all 10 hypothesis tests
- ✅ Create 10 visualization charts
- ✅ Generate comprehensive reports

## ⏱️ Expected Runtime
**30-60 seconds** for the complete analysis

## 📂 What You'll Get

After running, check these files:

### 1. Raw Data
- `covid19_work_wellbeing_data.csv` - The complete dataset (10,000 records)

### 2. Reports
- `output/analysis_report.txt` - Detailed findings for all hypotheses
- `output/hypothesis_results_summary.csv` - Quick summary table

### 3. Visualizations
- `output/h1_stress_productivity.png`
- `output/h2_sector_comparison.png`
- `output/h3_technology_adaptation.png`
- `output/h4_work_mode_stress.png`
- `output/h5_work_hours_stress.png`
- `output/h6_collaboration_productivity.png`
- `output/h7_job_security_pri.png`
- `output/h8_childcare_productivity.png`
- `output/h9_meetings_stress.png`
- `output/h10_health_productivity.png`

## 🎯 Quick Results Summary

From the latest run:

**✅ 6 Hypotheses Rejected (Significant Findings):**
- H1: Stress reduces productivity (p < 0.0001)
- H2: Sectors differ significantly (p < 0.0001)
- H3: Tech adaptation improves productivity (p < 0.0001)
- H4: Remote workers have higher stress (p = 0.0120)
- H5: Longer hours increase stress (p < 0.0001)
- H7: Job security increases resilience (p < 0.0001)

**❌ 4 Hypotheses Not Rejected:**
- H6: Collaboration challenges (p = 0.0519)
- H8: Childcare responsibilities (p = 0.6504)
- H9: Meeting frequency (p = 0.0635)
- H10: Health issues (p = 0.0958)

## 🔧 Individual Components

If you want to run specific parts:

### Generate dataset only
```bash
python3 data_generator.py
```

### Run descriptive statistics only
```bash
python3 descriptive_stats.py
```

### Run hypothesis tests only
```bash
python3 hypothesis_tests.py
```

### Generate visualizations only
```bash
python3 visualizations.py
```

## 📊 View Results

### In Terminal
```bash
cat output/analysis_report.txt
```

### Open CSV in Python
```bash
python3 -c "import pandas as pd; df = pd.read_csv('covid19_work_wellbeing_data.csv'); print(df.head())"
```

### View Images
Open the PNG files in `output/` directory with any image viewer

## 🐍 Python Requirements

- Python 3.8 or higher
- All packages in `requirements.txt` (installed automatically)

## ❓ Troubleshooting

### If you see "python: command not found"
Use `python3` instead of `python`

### If packages fail to install
Try:
```bash
python3 -m pip install -r requirements.txt
```

### If you get "Permission denied"
Add sudo (Linux/Mac):
```bash
sudo pip3 install -r requirements.txt
```

## 📖 Full Documentation
See `README.md` for complete details about:
- Dataset structure
- Statistical methods
- Hypothesis details
- Interpretation guidelines

---

**Ready? Just run:**
```bash
python3 main_analysis.py
```
