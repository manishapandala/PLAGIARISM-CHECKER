"""
Descriptive Statistics and Exploratory Data Analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


class DescriptiveAnalyzer:
    """Perform comprehensive descriptive statistics"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
    
    def dataset_overview(self) -> Dict[str, Any]:
        """Get basic dataset information"""
        print("\n" + "="*70)
        print("DATASET OVERVIEW")
        print("="*70)
        
        overview = {
            'total_records': len(self.df),
            'total_variables': len(self.df.columns),
            'missing_values': self.df.isnull().sum().sum(),
            'complete_records': len(self.df.dropna())
        }
        
        print(f"Total Records: {overview['total_records']:,}")
        print(f"Total Variables: {overview['total_variables']}")
        print(f"Missing Values: {overview['missing_values']}")
        print(f"Complete Records: {overview['complete_records']:,}")
        
        return overview
    
    def demographic_summary(self):
        """Summarize demographics"""
        print("\n" + "="*70)
        print("DEMOGRAPHIC SUMMARY")
        print("="*70)
        
        print(f"\nAge Statistics:")
        print(f"  Mean: {self.df['Age'].mean():.1f} years")
        print(f"  Median: {self.df['Age'].median():.1f} years")
        print(f"  Range: {self.df['Age'].min()}-{self.df['Age'].max()} years")
        
        print(f"\nYears of Experience:")
        print(f"  Mean: {self.df['YearsExperience'].mean():.1f} years")
        print(f"  Median: {self.df['YearsExperience'].median():.1f} years")
        print(f"  Range: {self.df['YearsExperience'].min()}-{self.df['YearsExperience'].max()} years")
        
        print(f"\nSector Distribution:")
        sector_counts = self.df['Sector'].value_counts()
        for sector, count in sector_counts.items():
            pct = (count / len(self.df)) * 100
            print(f"  {sector}: {count:,} ({pct:.1f}%)")
    
    def work_patterns_summary(self):
        """Summarize work patterns"""
        print("\n" + "="*70)
        print("WORK PATTERNS SUMMARY")
        print("="*70)
        
        remote_pct = (self.df['WorkFromHome'].sum() / len(self.df)) * 100
        print(f"\nWork From Home: {remote_pct:.1f}%")
        
        print(f"\nHours Worked Per Day:")
        print(f"  Mean: {self.df['HoursWorkedPerDay'].mean():.1f} hours")
        print(f"  Median: {self.df['HoursWorkedPerDay'].median():.1f} hours")
        print(f"  Range: {self.df['HoursWorkedPerDay'].min():.1f}-{self.df['HoursWorkedPerDay'].max():.1f} hours")
        
        long_hours = (self.df['HoursWorkedPerDay'] > 8).sum()
        long_hours_pct = (long_hours / len(self.df)) * 100
        print(f"  Working >8 hours: {long_hours:,} ({long_hours_pct:.1f}%)")
        
        print(f"\nMeetings Per Day:")
        print(f"  Mean: {self.df['MeetingsPerDay'].mean():.1f} meetings")
        print(f"  Median: {self.df['MeetingsPerDay'].median():.1f} meetings")
        print(f"  Range: {self.df['MeetingsPerDay'].min()}-{self.df['MeetingsPerDay'].max()} meetings")
    
    def wellbeing_summary(self):
        """Summarize wellbeing indicators"""
        print("\n" + "="*70)
        print("WELLBEING INDICATORS")
        print("="*70)
        
        print(f"\nStress Level Distribution:")
        stress_counts = self.df['StressLevel'].value_counts()
        for level in ['Low', 'Medium', 'High']:
            count = stress_counts.get(level, 0)
            pct = (count / len(self.df)) * 100
            print(f"  {level}: {count:,} ({pct:.1f}%)")
        
        health_issues_pct = (self.df['HealthIssues'].sum() / len(self.df)) * 100
        print(f"\nHealth Issues: {health_issues_pct:.1f}%")
        
        childcare_pct = (self.df['ChildcareResponsibilities'].sum() / len(self.df)) * 100
        print(f"Childcare Responsibilities: {childcare_pct:.1f}%")
        
        print(f"\nProductivity Resilience Index (PRI):")
        print(f"  Mean: {self.df['ProductivityResilienceIndex'].mean():.1f}")
        print(f"  Median: {self.df['ProductivityResilienceIndex'].median():.1f}")
        print(f"  Range: {self.df['ProductivityResilienceIndex'].min():.1f}-{self.df['ProductivityResilienceIndex'].max():.1f}")
    
    def productivity_summary(self):
        """Summarize productivity outcomes"""
        print("\n" + "="*70)
        print("PRODUCTIVITY OUTCOMES")
        print("="*70)
        
        print(f"\nProductivity Change Distribution:")
        prod_counts = self.df['ProductivityChange'].value_counts()
        for change in ['Increased', 'No Change', 'Decreased']:
            count = prod_counts.get(change, 0)
            pct = (count / len(self.df)) * 100
            print(f"  {change}: {count:,} ({pct:.1f}%)")
        
        print(f"\nTechnology Adaptation:")
        tech_counts = self.df['TechnologyAdaptation'].value_counts()
        for level in ['Poor', 'Fair', 'Good', 'Excellent']:
            count = tech_counts.get(level, 0)
            pct = (count / len(self.df)) * 100
            print(f"  {level}: {count:,} ({pct:.1f}%)")
        
        print(f"\nCollaboration Challenges:")
        collab_counts = self.df['CollaborationChallenges'].value_counts()
        for level in ['None', 'Minor', 'Moderate', 'Severe']:
            count = collab_counts.get(level, 0)
            pct = (count / len(self.df)) * 100
            print(f"  {level}: {count:,} ({pct:.1f}%)")
    
    def job_conditions_summary(self):
        """Summarize job conditions"""
        print("\n" + "="*70)
        print("JOB CONDITIONS")
        print("="*70)
        
        print(f"\nJob Security:")
        security_counts = self.df['JobSecurity'].value_counts()
        for level in ['Secure', 'Uncertain', 'At Risk']:
            count = security_counts.get(level, 0)
            pct = (count / len(self.df)) * 100
            print(f"  {level}: {count:,} ({pct:.1f}%)")
        
        print(f"\nSalary Change:")
        salary_counts = self.df['SalaryChange'].value_counts()
        for change in ['Increased', 'No Change', 'Decreased']:
            count = salary_counts.get(change, 0)
            pct = (count / len(self.df)) * 100
            print(f"  {change}: {count:,} ({pct:.1f}%)")
    
    def sector_breakdown(self):
        """Detailed breakdown by sector"""
        print("\n" + "="*70)
        print("SECTOR-WISE BREAKDOWN")
        print("="*70)
        
        for sector in self.df['Sector'].unique():
            sector_df = self.df[self.df['Sector'] == sector]
            print(f"\n{sector} (n={len(sector_df):,}):")
            print(f"  Remote Work: {(sector_df['WorkFromHome'].sum()/len(sector_df)*100):.1f}%")
            print(f"  Avg Hours: {sector_df['HoursWorkedPerDay'].mean():.1f}")
            print(f"  Avg Stress: {sector_df['StressLevel_Numeric'].mean():.2f}")
            print(f"  Avg Productivity: {sector_df['ProductivityChange_Numeric'].mean():.2f}")
            print(f"  Avg PRI: {sector_df['ProductivityResilienceIndex'].mean():.1f}")
    
    def run_full_analysis(self):
        """Run complete descriptive analysis"""
        self.dataset_overview()
        self.demographic_summary()
        self.work_patterns_summary()
        self.wellbeing_summary()
        self.productivity_summary()
        self.job_conditions_summary()
        self.sector_breakdown()


if __name__ == '__main__':
    # Load dataset
    df = pd.read_csv('covid19_work_wellbeing_data.csv')
    
    # Run analysis
    analyzer = DescriptiveAnalyzer(df)
    analyzer.run_full_analysis()
