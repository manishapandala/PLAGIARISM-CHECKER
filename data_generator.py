"""
COVID-19 Work and Wellbeing Dataset Generator
Generates synthetic dataset of 10,000 records matching research specifications
"""

import numpy as np
import pandas as pd
from typing import List


def generate_covid_dataset(n_records: int = 10000, random_seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic COVID-19 work and wellbeing dataset
    
    Parameters:
    -----------
    n_records : int
        Number of records to generate (default: 10000)
    random_seed : int
        Random seed for reproducibility (default: 42)
    
    Returns:
    --------
    pd.DataFrame
        Generated dataset with all variables
    """
    np.random.seed(random_seed)
    
    # Define categorical options
    sectors = ['IT', 'Retail', 'Education', 'Healthcare', 'Finance']
    stress_levels = ['Low', 'Medium', 'High']
    productivity_changes = ['Increased', 'Decreased', 'No Change']
    commute_changes = ['Increased', 'Decreased', 'No Change']
    salary_changes = ['Increased', 'Decreased', 'No Change']
    job_security_levels = ['Secure', 'Uncertain', 'At Risk']
    tech_adaptation_levels = ['Poor', 'Fair', 'Good', 'Excellent']
    collaboration_levels = ['None', 'Minor', 'Moderate', 'Severe']
    
    data = []
    
    for i in range(n_records):
        # Sector selection (equal distribution)
        sector = np.random.choice(sectors)
        
        # Work from home: 80% remote
        work_from_home = np.random.random() < 0.8
        
        # Sector-specific adjustments
        stress_bonus = 0
        productivity_bonus = 0
        
        if sector in ['Healthcare', 'Retail']:
            stress_bonus = 0.3  # Higher stress
            productivity_bonus = -0.2  # Lower productivity
        elif sector in ['IT', 'Finance']:
            productivity_bonus = 0.1  # Better productivity
        
        # Work hours: 67% reported longer hours
        base_hours = 8
        longer_hours = np.random.random() < 0.67
        if longer_hours:
            hours_worked = base_hours + np.random.uniform(0, 3)
        else:
            hours_worked = base_hours - np.random.uniform(0, 2)
        hours_worked = round(max(4, min(14, hours_worked)), 1)
        
        # Meetings per day (more for remote workers)
        if work_from_home:
            meetings = np.random.randint(3, 9)
        else:
            meetings = np.random.randint(2, 6)
        
        # Stress level (Medium most common)
        stress_rand = np.random.random() + stress_bonus + (0.2 if hours_worked > 9 else 0)
        if stress_rand < 0.3:
            stress_level = 'Low'
        elif stress_rand < 0.7:
            stress_level = 'Medium'
        else:
            stress_level = 'High'
        
        # Productivity change (60-70% noted changes)
        productivity_rand = np.random.random() + productivity_bonus
        if productivity_rand < 0.35:
            productivity_change = 'Decreased'
        elif productivity_rand < 0.65:
            productivity_change = 'No Change'
        else:
            productivity_change = 'Increased'
        
        # Commute change
        if work_from_home:
            commute_change = 'Decreased' if np.random.random() < 0.85 else 'No Change'
        else:
            rand = np.random.random()
            if rand < 0.4:
                commute_change = 'Decreased'
            elif rand < 0.7:
                commute_change = 'No Change'
            else:
                commute_change = 'Increased'
        
        # Health issues: 20-30% affected
        health_issues = np.random.random() < 0.25
        
        # Childcare responsibilities: 30-40%
        childcare = np.random.random() < 0.35
        
        # Salary change
        salary_rand = np.random.random()
        if salary_rand < 0.3:
            salary_change = 'Decreased'
        elif salary_rand < 0.8:
            salary_change = 'No Change'
        else:
            salary_change = 'Increased'
        
        # Job security (more secure in Healthcare/IT)
        if sector in ['Healthcare', 'IT']:
            sec_rand = np.random.random()
            if sec_rand < 0.6:
                job_security = 'Secure'
            elif sec_rand < 0.85:
                job_security = 'Uncertain'
            else:
                job_security = 'At Risk'
        else:
            sec_rand = np.random.random()
            if sec_rand < 0.4:
                job_security = 'Secure'
            elif sec_rand < 0.75:
                job_security = 'Uncertain'
            else:
                job_security = 'At Risk'
        
        # Technology adaptation (better in IT)
        tech_rand = np.random.random()
        if sector == 'IT':
            if tech_rand < 0.5:
                tech_adaptation = 'Excellent'
            elif tech_rand < 0.8:
                tech_adaptation = 'Good'
            else:
                tech_adaptation = 'Fair'
        else:
            if tech_rand < 0.15:
                tech_adaptation = 'Poor'
            elif tech_rand < 0.4:
                tech_adaptation = 'Fair'
            elif tech_rand < 0.75:
                tech_adaptation = 'Good'
            else:
                tech_adaptation = 'Excellent'
        
        # Collaboration challenges (more for remote)
        collab_rand = np.random.random()
        if work_from_home:
            if collab_rand < 0.15:
                collab_challenges = 'None'
            elif collab_rand < 0.4:
                collab_challenges = 'Minor'
            elif collab_rand < 0.75:
                collab_challenges = 'Moderate'
            else:
                collab_challenges = 'Severe'
        else:
            if collab_rand < 0.4:
                collab_challenges = 'None'
            elif collab_rand < 0.75:
                collab_challenges = 'Minor'
            elif collab_rand < 0.9:
                collab_challenges = 'Moderate'
            else:
                collab_challenges = 'Severe'
        
        # Productivity Resilience Index (0-100)
        pri = 50
        pri += 20 if job_security == 'Secure' else (0 if job_security == 'Uncertain' else -20)
        pri += {'Excellent': 15, 'Good': 10, 'Fair': 0, 'Poor': -10}[tech_adaptation]
        pri += {'Low': 15, 'Medium': 0, 'High': -15}[stress_level]
        pri += -10 if health_issues else 5
        pri += -5 if childcare else 0
        pri += np.random.uniform(-10, 10)
        pri = round(max(0, min(100, pri)), 1)
        
        # Demographics
        age = np.random.randint(22, 63)
        years_experience = min(age - 20, np.random.randint(0, 31))
        
        data.append({
            'ID': i + 1,
            'Sector': sector,
            'WorkFromHome': work_from_home,
            'HoursWorkedPerDay': hours_worked,
            'MeetingsPerDay': meetings,
            'CommuteChange': commute_change,
            'StressLevel': stress_level,
            'ProductivityChange': productivity_change,
            'HealthIssues': health_issues,
            'ChildcareResponsibilities': childcare,
            'SalaryChange': salary_change,
            'JobSecurity': job_security,
            'TechnologyAdaptation': tech_adaptation,
            'CollaborationChallenges': collab_challenges,
            'ProductivityResilienceIndex': pri,
            'Age': age,
            'YearsExperience': years_experience
        })
    
    df = pd.DataFrame(data)
    return df


def encode_categorical_variables(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add numeric encodings for categorical variables to enable statistical analysis
    
    Parameters:
    -----------
    df : pd.DataFrame
        Original dataset
    
    Returns:
    --------
    pd.DataFrame
        Dataset with additional numeric columns
    """
    df_encoded = df.copy()
    
    # Encode stress level
    stress_map = {'Low': 1, 'Medium': 2, 'High': 3}
    df_encoded['StressLevel_Numeric'] = df_encoded['StressLevel'].map(stress_map)
    
    # Encode productivity change
    productivity_map = {'Decreased': -1, 'No Change': 0, 'Increased': 1}
    df_encoded['ProductivityChange_Numeric'] = df_encoded['ProductivityChange'].map(productivity_map)
    
    # Encode technology adaptation
    tech_map = {'Poor': 1, 'Fair': 2, 'Good': 3, 'Excellent': 4}
    df_encoded['TechAdaptation_Numeric'] = df_encoded['TechnologyAdaptation'].map(tech_map)
    
    # Encode collaboration challenges
    collab_map = {'None': 0, 'Minor': 1, 'Moderate': 2, 'Severe': 3}
    df_encoded['CollaborationChallenges_Numeric'] = df_encoded['CollaborationChallenges'].map(collab_map)
    
    # Encode job security
    security_map = {'At Risk': 0, 'Uncertain': 1, 'Secure': 2}
    df_encoded['JobSecurity_Numeric'] = df_encoded['JobSecurity'].map(security_map)
    
    # Binary encodings
    df_encoded['WorkFromHome_Numeric'] = df_encoded['WorkFromHome'].astype(int)
    df_encoded['HealthIssues_Numeric'] = df_encoded['HealthIssues'].astype(int)
    df_encoded['ChildcareResponsibilities_Numeric'] = df_encoded['ChildcareResponsibilities'].astype(int)
    
    return df_encoded


if __name__ == '__main__':
    # Generate dataset
    print("Generating COVID-19 Work and Wellbeing Dataset...")
    df = generate_covid_dataset(n_records=10000)
    
    # Add numeric encodings
    df = encode_categorical_variables(df)
    
    # Save to CSV
    df.to_csv('covid19_work_wellbeing_data.csv', index=False)
    print(f"✓ Dataset generated: {len(df)} records")
    print(f"✓ Saved to: covid19_work_wellbeing_data.csv")
    
    # Display basic info
    print("\n" + "="*60)
    print("DATASET SUMMARY")
    print("="*60)
    print(f"\nShape: {df.shape}")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nFirst few rows:")
    print(df.head())
    print(f"\nBasic statistics:")
    print(df.describe())
