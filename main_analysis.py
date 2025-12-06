#!/usr/bin/env python3
"""
COVID-19 WORK AND WELLBEING ANALYSIS
Main Analysis Script

This script performs comprehensive statistical analysis on COVID-19's impact
on work patterns, productivity, and wellbeing across different sectors.

Usage:
    python main_analysis.py
"""

import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime

# Import analysis modules
from data_generator import generate_covid_dataset, encode_categorical_variables
from descriptive_stats import DescriptiveAnalyzer
from hypothesis_tests import HypothesisTester
from visualizations import Visualizer


def print_header():
    """Print analysis header"""
    print("\n" + "="*70)
    print("COVID-19 WORK AND WELLBEING ANALYSIS")
    print("Statistical Analysis of Pandemic Impact on Employees")
    print("="*70)
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")


def generate_or_load_data(force_generate=False):
    """Generate new dataset or load existing"""
    data_file = 'covid19_work_wellbeing_data.csv'
    
    if os.path.exists(data_file) and not force_generate:
        print(f"✓ Loading existing dataset: {data_file}")
        df = pd.read_csv(data_file)
        print(f"  Records loaded: {len(df):,}")
    else:
        print("✓ Generating new synthetic dataset...")
        df = generate_covid_dataset(n_records=10000)
        df = encode_categorical_variables(df)
        df.to_csv(data_file, index=False)
        print(f"  Dataset generated: {len(df):,} records")
        print(f"  Saved to: {data_file}")
    
    return df


def save_results_summary(results: dict, output_dir: str = 'output'):
    """Save hypothesis testing results to CSV"""
    os.makedirs(output_dir, exist_ok=True)
    
    summary_data = []
    for key, result in results.items():
        summary_data.append({
            'Hypothesis': result['hypothesis'],
            'Title': result['title'],
            'Test_Used': result['test_used'],
            'P_Value': result['p_value'],
            'Reject_Null': result['reject_null'],
            'Conclusion': result['conclusion']
        })
    
    summary_df = pd.DataFrame(summary_data)
    output_file = f'{output_dir}/hypothesis_results_summary.csv'
    summary_df.to_csv(output_file, index=False)
    print(f"\n✓ Results summary saved to: {output_file}")
    
    return summary_df


def generate_report(df: pd.DataFrame, results: dict, output_dir: str = 'output'):
    """Generate comprehensive text report"""
    os.makedirs(output_dir, exist_ok=True)
    report_file = f'{output_dir}/analysis_report.txt'
    
    with open(report_file, 'w') as f:
        f.write("="*70 + "\n")
        f.write("COVID-19 WORK AND WELLBEING ANALYSIS - COMPREHENSIVE REPORT\n")
        f.write("="*70 + "\n")
        f.write(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Dataset Size: {len(df):,} records\n")
        
        f.write("\n\n" + "="*70 + "\n")
        f.write("HYPOTHESIS TESTING RESULTS\n")
        f.write("="*70 + "\n\n")
        
        for key, result in results.items():
            f.write(f"\n{result['hypothesis']}: {result['title']}\n")
            f.write("-" * 70 + "\n")
            f.write(f"Null Hypothesis: {result['null_hypothesis']}\n")
            f.write(f"Alternative Hypothesis: {result['alternative_hypothesis']}\n")
            f.write(f"Test Used: {result['test_used']}\n")
            f.write(f"P-value: {result['p_value']:.6f}\n")
            f.write(f"Decision: {'REJECT H₀' if result['reject_null'] else 'FAIL TO REJECT H₀'}\n")
            f.write(f"Conclusion: {result['conclusion']}\n\n")
        
        # Summary statistics
        rejected_count = sum(1 for r in results.values() if r['reject_null'])
        f.write("\n" + "="*70 + "\n")
        f.write("SUMMARY\n")
        f.write("="*70 + "\n")
        f.write(f"Total Hypotheses Tested: 10\n")
        f.write(f"Null Hypotheses Rejected: {rejected_count}\n")
        f.write(f"Null Hypotheses Not Rejected: {10 - rejected_count}\n")
        f.write(f"Significance Level (α): 0.05\n")
    
    print(f"✓ Detailed report saved to: {report_file}")


def main():
    """Main analysis workflow"""
    try:
        # Print header
        print_header()
        
        # Step 1: Generate or load data
        print("STEP 1: DATA PREPARATION")
        print("-" * 70)
        df = generate_or_load_data(force_generate=False)
        
        # Step 2: Descriptive Statistics
        print("\n\nSTEP 2: DESCRIPTIVE STATISTICS & EDA")
        print("-" * 70)
        analyzer = DescriptiveAnalyzer(df)
        analyzer.run_full_analysis()
        
        # Step 3: Hypothesis Testing
        print("\n\nSTEP 3: HYPOTHESIS TESTING")
        print("-" * 70)
        tester = HypothesisTester(df)
        results = tester.run_all_tests()
        
        # Step 4: Visualizations
        print("\n\nSTEP 4: GENERATING VISUALIZATIONS")
        print("-" * 70)
        viz = Visualizer(df)
        viz.create_all_visualizations(output_dir='output')
        
        # Step 5: Save Results
        print("\n\nSTEP 5: SAVING RESULTS")
        print("-" * 70)
        summary_df = save_results_summary(results, output_dir='output')
        generate_report(df, results, output_dir='output')
        
        # Final Summary
        print("\n\n" + "="*70)
        print("ANALYSIS COMPLETE!")
        print("="*70)
        print("\nGenerated Files:")
        print("  📊 covid19_work_wellbeing_data.csv - Raw dataset")
        print("  📋 output/hypothesis_results_summary.csv - Results summary")
        print("  📝 output/analysis_report.txt - Detailed report")
        print("  📈 output/*.png - 10 visualization files")
        
        print("\n" + "="*70)
        print("HYPOTHESIS TESTING SUMMARY")
        print("="*70)
        rejected_count = sum(1 for r in results.values() if r['reject_null'])
        print(f"\nTotal Hypotheses: 10")
        print(f"Null Hypotheses Rejected: {rejected_count}")
        print(f"Null Hypotheses Not Rejected: {10 - rejected_count}")
        
        print("\nKey Findings:")
        for key, result in results.items():
            status = "✓ REJECT" if result['reject_null'] else "✗ FAIL TO REJECT"
            print(f"  {result['hypothesis']}: {status} (p={result['p_value']:.4f})")
        
        print("\n" + "="*70)
        print("Thank you for using COVID-19 Work & Wellbeing Analysis!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
