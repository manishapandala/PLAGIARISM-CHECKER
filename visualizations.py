"""
Visualization Module for COVID-19 Work and Wellbeing Analysis
Creates comprehensive charts and plots for all hypotheses
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, Any
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10


class Visualizer:
    """Create visualizations for hypothesis tests and descriptive analysis"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize with dataset
        
        Parameters:
        -----------
        df : pd.DataFrame
            Dataset with all variables
        """
        self.df = df
        self.colors = sns.color_palette("husl", 8)
    
    def plot_stress_productivity(self, save_path: str = None):
        """H1: Stress vs Productivity"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Box plot
        self.df.boxplot(column='ProductivityChange_Numeric', by='StressLevel', ax=axes[0])
        axes[0].set_title('Productivity Change by Stress Level')
        axes[0].set_xlabel('Stress Level')
        axes[0].set_ylabel('Productivity Change')
        plt.sca(axes[0])
        plt.xticks([1, 2, 3], ['Low', 'Medium', 'High'])
        
        # Heatmap of counts
        cross_tab = pd.crosstab(self.df['StressLevel'], self.df['ProductivityChange'])
        sns.heatmap(cross_tab, annot=True, fmt='d', cmap='YlOrRd', ax=axes[1])
        axes[1].set_title('Stress Level vs Productivity Change (Counts)')
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_sector_comparison(self, save_path: str = None):
        """H2: Sector Comparison"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Productivity by sector
        sector_prod = self.df.groupby('Sector')['ProductivityChange_Numeric'].mean().sort_values()
        axes[0, 0].barh(sector_prod.index, sector_prod.values, color=self.colors)
        axes[0, 0].set_title('Average Productivity Change by Sector')
        axes[0, 0].set_xlabel('Avg Productivity Change')
        axes[0, 0].axvline(0, color='black', linestyle='--', alpha=0.5)
        
        # Stress by sector
        sector_stress = self.df.groupby('Sector')['StressLevel_Numeric'].mean().sort_values()
        axes[0, 1].barh(sector_stress.index, sector_stress.values, color=self.colors)
        axes[0, 1].set_title('Average Stress Level by Sector')
        axes[0, 1].set_xlabel('Avg Stress (1=Low, 3=High)')
        
        # Remote work percentage by sector
        remote_pct = self.df.groupby('Sector')['WorkFromHome'].mean() * 100
        axes[1, 0].bar(remote_pct.index, remote_pct.values, color=self.colors)
        axes[1, 0].set_title('Remote Work Percentage by Sector')
        axes[1, 0].set_ylabel('Percentage (%)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Box plot: Productivity by sector
        self.df.boxplot(column='ProductivityChange_Numeric', by='Sector', ax=axes[1, 1])
        axes[1, 1].set_title('Productivity Distribution by Sector')
        axes[1, 1].set_xlabel('Sector')
        axes[1, 1].set_ylabel('Productivity Change')
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_technology_adaptation(self, save_path: str = None):
        """H3: Technology Adaptation vs Productivity"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Bar chart
        tech_prod = self.df.groupby('TechnologyAdaptation')['ProductivityChange_Numeric'].mean()
        tech_order = ['Poor', 'Fair', 'Good', 'Excellent']
        tech_prod = tech_prod.reindex(tech_order)
        axes[0].bar(tech_prod.index, tech_prod.values, color=self.colors[:4])
        axes[0].set_title('Productivity by Technology Adaptation')
        axes[0].set_ylabel('Avg Productivity Change')
        axes[0].axhline(0, color='black', linestyle='--', alpha=0.5)
        axes[0].tick_params(axis='x', rotation=45)
        
        # Scatter plot
        axes[1].scatter(self.df['TechAdaptation_Numeric'], 
                       self.df['ProductivityChange_Numeric'],
                       alpha=0.3, s=10)
        axes[1].set_title('Technology Adaptation vs Productivity (Scatter)')
        axes[1].set_xlabel('Tech Adaptation (1=Poor, 4=Excellent)')
        axes[1].set_ylabel('Productivity Change')
        
        # Add trend line
        z = np.polyfit(self.df['TechAdaptation_Numeric'], 
                      self.df['ProductivityChange_Numeric'], 1)
        p = np.poly1d(z)
        axes[1].plot(self.df['TechAdaptation_Numeric'].sort_values(), 
                    p(self.df['TechAdaptation_Numeric'].sort_values()),
                    "r--", alpha=0.8, linewidth=2)
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_work_mode_stress(self, save_path: str = None):
        """H4: Work Mode vs Stress"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Bar chart of mean stress
        work_mode_stress = self.df.groupby('WorkFromHome')['StressLevel_Numeric'].mean()
        labels = ['On-Site', 'Remote']
        axes[0].bar(labels, work_mode_stress.values, color=[self.colors[0], self.colors[2]])
        axes[0].set_title('Average Stress by Work Mode')
        axes[0].set_ylabel('Avg Stress Level')
        
        # Stacked bar chart
        cross_tab = pd.crosstab(self.df['WorkFromHome'], self.df['StressLevel'], normalize='index') * 100
        cross_tab.index = ['On-Site', 'Remote']
        cross_tab.plot(kind='bar', stacked=True, ax=axes[1], 
                      color=sns.color_palette("RdYlGn_r", 3))
        axes[1].set_title('Stress Distribution by Work Mode')
        axes[1].set_ylabel('Percentage (%)')
        axes[1].set_xlabel('Work Mode')
        axes[1].legend(title='Stress Level')
        axes[1].tick_params(axis='x', rotation=0)
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_work_hours_stress(self, save_path: str = None):
        """H5: Work Hours vs Stress"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Scatter plot with color coding
        for stress_level, color in zip(['Low', 'Medium', 'High'], sns.color_palette("RdYlGn_r", 3)):
            subset = self.df[self.df['StressLevel'] == stress_level]
            axes[0].scatter(subset['HoursWorkedPerDay'], 
                          subset['StressLevel_Numeric'],
                          label=stress_level, alpha=0.4, s=20, color=color)
        axes[0].set_title('Work Hours vs Stress Level')
        axes[0].set_xlabel('Hours Worked Per Day')
        axes[0].set_ylabel('Stress Level')
        axes[0].legend()
        
        # Box plot
        hours_binned = pd.cut(self.df['HoursWorkedPerDay'], bins=[0, 6, 8, 10, 15])
        temp_df = self.df.copy()
        temp_df['HoursBinned'] = hours_binned
        temp_df.boxplot(column='StressLevel_Numeric', by='HoursBinned', ax=axes[1])
        axes[1].set_title('Stress by Work Hours (Binned)')
        axes[1].set_xlabel('Hours Worked Per Day')
        axes[1].set_ylabel('Stress Level')
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_collaboration_productivity(self, save_path: str = None):
        """H6: Collaboration Challenges vs Productivity"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Bar chart
        collab_order = ['None', 'Minor', 'Moderate', 'Severe']
        collab_prod = self.df.groupby('CollaborationChallenges')['ProductivityChange_Numeric'].mean()
        collab_prod = collab_prod.reindex(collab_order)
        axes[0].bar(collab_prod.index, collab_prod.values, 
                   color=sns.color_palette("Reds", 4))
        axes[0].set_title('Productivity by Collaboration Challenges')
        axes[0].set_ylabel('Avg Productivity Change')
        axes[0].axhline(0, color='black', linestyle='--', alpha=0.5)
        axes[0].tick_params(axis='x', rotation=45)
        
        # Violin plot
        sns.violinplot(data=self.df, x='CollaborationChallenges', 
                      y='ProductivityChange_Numeric',
                      order=collab_order, ax=axes[1],
                      palette="Reds")
        axes[1].set_title('Productivity Distribution by Collaboration Challenges')
        axes[1].set_ylabel('Productivity Change')
        axes[1].set_xlabel('Collaboration Challenges')
        axes[1].axhline(0, color='black', linestyle='--', alpha=0.5)
        axes[1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_job_security_pri(self, save_path: str = None):
        """H7: Job Security vs PRI"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Bar chart
        job_order = ['At Risk', 'Uncertain', 'Secure']
        job_pri = self.df.groupby('JobSecurity')['ProductivityResilienceIndex'].mean()
        job_pri = job_pri.reindex(job_order)
        axes[0].bar(job_pri.index, job_pri.values, 
                   color=sns.color_palette("RdYlGn", 3))
        axes[0].set_title('PRI by Job Security')
        axes[0].set_ylabel('Avg Productivity Resilience Index')
        axes[0].tick_params(axis='x', rotation=45)
        
        # Box plot
        sns.boxplot(data=self.df, x='JobSecurity', y='ProductivityResilienceIndex',
                   order=job_order, ax=axes[1],
                   palette="RdYlGn")
        axes[1].set_title('PRI Distribution by Job Security')
        axes[1].set_ylabel('Productivity Resilience Index')
        axes[1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_childcare_productivity(self, save_path: str = None):
        """H8: Childcare vs Productivity"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Bar chart
        childcare_prod = self.df.groupby('ChildcareResponsibilities')['ProductivityChange_Numeric'].mean()
        labels = ['No Childcare', 'With Childcare']
        axes[0].bar(labels, childcare_prod.values, color=[self.colors[1], self.colors[3]])
        axes[0].set_title('Productivity by Childcare Responsibilities')
        axes[0].set_ylabel('Avg Productivity Change')
        axes[0].axhline(0, color='black', linestyle='--', alpha=0.5)
        
        # Stacked bar
        cross_tab = pd.crosstab(self.df['ChildcareResponsibilities'], 
                               self.df['ProductivityChange'], 
                               normalize='index') * 100
        cross_tab.index = ['No Childcare', 'With Childcare']
        cross_tab[['Decreased', 'No Change', 'Increased']].plot(kind='bar', 
                                                                  stacked=True, 
                                                                  ax=axes[1],
                                                                  color=sns.color_palette("RdYlGn", 3))
        axes[1].set_title('Productivity Distribution by Childcare Status')
        axes[1].set_ylabel('Percentage (%)')
        axes[1].set_xlabel('')
        axes[1].legend(title='Productivity')
        axes[1].tick_params(axis='x', rotation=0)
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_meetings_stress(self, save_path: str = None):
        """H9: Meetings vs Stress"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Scatter plot
        for stress_level, color in zip(['Low', 'Medium', 'High'], sns.color_palette("RdYlGn_r", 3)):
            subset = self.df[self.df['StressLevel'] == stress_level]
            axes[0].scatter(subset['MeetingsPerDay'], 
                          subset['StressLevel_Numeric'],
                          label=stress_level, alpha=0.4, s=20, color=color)
        axes[0].set_title('Meetings Per Day vs Stress Level')
        axes[0].set_xlabel('Meetings Per Day')
        axes[0].set_ylabel('Stress Level')
        axes[0].legend()
        
        # Box plot
        meetings_binned = pd.cut(self.df['MeetingsPerDay'], bins=[0, 3, 5, 10])
        temp_df = self.df.copy()
        temp_df['MeetingsBinned'] = meetings_binned
        temp_df.boxplot(column='StressLevel_Numeric', by='MeetingsBinned', ax=axes[1])
        axes[1].set_title('Stress by Meeting Frequency (Binned)')
        axes[1].set_xlabel('Meetings Per Day')
        axes[1].set_ylabel('Stress Level')
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_health_productivity(self, save_path: str = None):
        """H10: Health Issues vs Productivity"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Bar chart
        health_prod = self.df.groupby('HealthIssues')['ProductivityChange_Numeric'].mean()
        labels = ['No Health Issues', 'With Health Issues']
        axes[0].bar(labels, health_prod.values, color=[self.colors[2], self.colors[5]])
        axes[0].set_title('Productivity by Health Status')
        axes[0].set_ylabel('Avg Productivity Change')
        axes[0].axhline(0, color='black', linestyle='--', alpha=0.5)
        
        # Violin plot
        sns.violinplot(data=self.df, x='HealthIssues', y='ProductivityChange_Numeric',
                      ax=axes[1], palette=[self.colors[2], self.colors[5]])
        axes[1].set_title('Productivity Distribution by Health Status')
        axes[1].set_ylabel('Productivity Change')
        axes[1].set_xticklabels(['No Health Issues', 'With Health Issues'])
        axes[1].axhline(0, color='black', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_all_visualizations(self, output_dir: str = 'output'):
        """Generate all visualizations"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print("Generating visualizations...")
        self.plot_stress_productivity(f'{output_dir}/h1_stress_productivity.png')
        self.plot_sector_comparison(f'{output_dir}/h2_sector_comparison.png')
        self.plot_technology_adaptation(f'{output_dir}/h3_technology_adaptation.png')
        self.plot_work_mode_stress(f'{output_dir}/h4_work_mode_stress.png')
        self.plot_work_hours_stress(f'{output_dir}/h5_work_hours_stress.png')
        self.plot_collaboration_productivity(f'{output_dir}/h6_collaboration_productivity.png')
        self.plot_job_security_pri(f'{output_dir}/h7_job_security_pri.png')
        self.plot_childcare_productivity(f'{output_dir}/h8_childcare_productivity.png')
        self.plot_meetings_stress(f'{output_dir}/h9_meetings_stress.png')
        self.plot_health_productivity(f'{output_dir}/h10_health_productivity.png')
        print(f"✓ All visualizations saved to '{output_dir}/' directory")


if __name__ == '__main__':
    # Load dataset
    df = pd.read_csv('covid19_work_wellbeing_data.csv')
    
    # Create visualizer
    viz = Visualizer(df)
    viz.create_all_visualizations()
