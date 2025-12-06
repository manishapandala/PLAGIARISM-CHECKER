# COVID-19 Work and Wellbeing Analysis

A comprehensive statistical analysis tool examining the impact of the COVID-19 pandemic on work patterns, productivity, and wellbeing across different sectors.

## 📋 Overview

This project analyzes how COVID-19 affected employees across IT, Retail, Education, Healthcare, and Finance sectors. It includes:

- **10,000 synthetic records** simulating realistic pandemic-era work patterns
- **10 hypothesis tests** examining relationships between work conditions, stress, and productivity
- **Statistical analysis** using correlation, t-tests, ANOVA, regression, and chi-square tests
- **Comprehensive visualizations** for each hypothesis
- **Detailed reporting** with conclusions and recommendations

## 🎯 Research Objectives

Examine how COVID-19 influenced:
- Work patterns (remote work, hours, meetings)
- Productivity outcomes
- Employee wellbeing (stress, health)
- Sector-specific impacts
- Technology adaptation
- Work-life balance factors

## 📊 Hypotheses Tested

| # | Focus | Test |
|---|-------|------|
| H1 | Stress vs Productivity | Correlation + Regression |
| H2 | Sector Comparison | ANOVA + Kruskal-Wallis |
| H3 | Technology Adaptation vs Productivity | Regression |
| H4 | Work Mode vs Stress | t-test + Chi-square |
| H5 | Work Hours vs Stress | Correlation |
| H6 | Collaboration Challenges vs Productivity | ANOVA + Regression |
| H7 | Job Security vs PRI | t-test + Regression |
| H8 | Childcare vs Productivity | t-test + Chi-square |
| H9 | Meetings vs Stress | Correlation |
| H10 | Health Issues vs Productivity | t-test |

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Install required packages:**

```bash
pip install -r requirements.txt
```

### Execution

**Run the complete analysis:**

```bash
python main_analysis.py
```

This single command will:
1. ✅ Generate the synthetic dataset (10,000 records)
2. ✅ Perform descriptive statistics
3. ✅ Run all 10 hypothesis tests
4. ✅ Create 10 visualization charts
5. ✅ Generate comprehensive reports

## 📁 Output Files

After running the analysis, you'll find:

```
workspace/
├── covid19_work_wellbeing_data.csv          # Raw dataset
└── output/
    ├── hypothesis_results_summary.csv       # Test results summary
    ├── analysis_report.txt                  # Detailed report
    ├── h1_stress_productivity.png           # Hypothesis 1 chart
    ├── h2_sector_comparison.png             # Hypothesis 2 chart
    ├── h3_technology_adaptation.png         # Hypothesis 3 chart
    ├── h4_work_mode_stress.png              # Hypothesis 4 chart
    ├── h5_work_hours_stress.png             # Hypothesis 5 chart
    ├── h6_collaboration_productivity.png    # Hypothesis 6 chart
    ├── h7_job_security_pri.png              # Hypothesis 7 chart
    ├── h8_childcare_productivity.png        # Hypothesis 8 chart
    ├── h9_meetings_stress.png               # Hypothesis 9 chart
    └── h10_health_productivity.png          # Hypothesis 10 chart
```

## 🔧 Individual Module Usage

### Generate Dataset Only

```bash
python data_generator.py
```

### Run Descriptive Statistics Only

```bash
python descriptive_stats.py
```

### Run Hypothesis Tests Only

```bash
python hypothesis_tests.py
```

### Generate Visualizations Only

```bash
python visualizations.py
```

## 📊 Dataset Variables

### Demographic
- **ID**: Unique identifier
- **Sector**: IT, Retail, Education, Healthcare, Finance
- **Age**: 22-62 years
- **YearsExperience**: 0-30 years

### Work Patterns
- **WorkFromHome**: Boolean
- **HoursWorkedPerDay**: 4-14 hours
- **MeetingsPerDay**: 2-8 meetings
- **CommuteChange**: Increased/Decreased/No Change

### Wellbeing
- **StressLevel**: Low/Medium/High
- **HealthIssues**: Boolean
- **ProductivityResilienceIndex (PRI)**: 0-100 scale

### Productivity
- **ProductivityChange**: Increased/Decreased/No Change
- **TechnologyAdaptation**: Poor/Fair/Good/Excellent
- **CollaborationChallenges**: None/Minor/Moderate/Severe

### Job Conditions
- **JobSecurity**: Secure/Uncertain/At Risk
- **SalaryChange**: Increased/Decreased/No Change
- **ChildcareResponsibilities**: Boolean

## 📈 Statistical Methods

- **Correlation Analysis**: Pearson & Spearman
- **t-tests**: Independent samples
- **ANOVA**: One-way analysis of variance
- **Chi-square**: Tests of independence
- **Linear Regression**: OLS regression
- **Effect Sizes**: Cohen's d, Eta-squared

## 🎨 Visualization Types

- Bar charts
- Box plots
- Violin plots
- Scatter plots with trend lines
- Heatmaps
- Stacked bar charts
- Distribution plots

## 📝 Example Output

```
==========================================================================
HYPOTHESIS TESTING SUMMARY
==========================================================================

Total Hypotheses: 10
Null Hypotheses Rejected: 8
Null Hypotheses Not Rejected: 2

Key Findings:
  H1: ✓ REJECT (p=0.0000)
  H2: ✓ REJECT (p=0.0000)
  H3: ✓ REJECT (p=0.0000)
  H4: ✓ REJECT (p=0.0000)
  H5: ✓ REJECT (p=0.0000)
  H6: ✓ REJECT (p=0.0000)
  H7: ✓ REJECT (p=0.0000)
  H8: ✗ FAIL TO REJECT (p=0.1234)
  H9: ✓ REJECT (p=0.0000)
  H10: ✗ FAIL TO REJECT (p=0.0876)
```

## 🔬 Research Context

This dataset simulates realistic patterns based on observed trends during the 2020 COVID-19 pandemic:
- 80% of workers transitioned to remote work
- 67% reported longer work hours
- Mixed productivity outcomes across sectors
- Healthcare and Retail faced higher stress
- IT and Finance maintained stable productivity
- Technology adaptation was crucial for success

## 📚 Dependencies

- **numpy**: Numerical computations
- **pandas**: Data manipulation
- **scipy**: Statistical tests
- **matplotlib**: Basic plotting
- **seaborn**: Advanced visualizations
- **statsmodels**: Regression and ANOVA

## 🤝 Contributing

This is a research analysis tool. For modifications:
1. Adjust parameters in `data_generator.py` to change dataset characteristics
2. Add new hypotheses in `hypothesis_tests.py`
3. Create new visualizations in `visualizations.py`

## 📄 License

This project is for educational and research purposes.

## 👥 Author

COVID-19 Work and Wellbeing Research Team

## 📞 Support

For questions or issues:
1. Check the output files in the `output/` directory
2. Review `analysis_report.txt` for detailed findings
3. Examine individual visualization files

## 🎯 Next Steps After Running Analysis

1. **Review the report**: Open `output/analysis_report.txt`
2. **Examine visualizations**: View all PNG files in `output/` directory
3. **Analyze results**: Open `output/hypothesis_results_summary.csv` in Excel
4. **Explore data**: Load `covid19_work_wellbeing_data.csv` for custom analysis

---

**Ready to start?** Simply run:

```bash
python main_analysis.py
```

The analysis will complete in approximately 30-60 seconds and generate all outputs automatically! 🚀
