"""
Hypothesis Testing Module
Implements all 10 hypotheses for COVID-19 Work and Wellbeing Analysis
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import pearsonr, spearmanr, ttest_ind, f_oneway, chi2_contingency
from statsmodels.formula.api import ols, logit
from statsmodels.stats.anova import anova_lm
import statsmodels.api as sm
from typing import Dict, Any, Tuple


class HypothesisTester:
    """Class to conduct all 10 hypothesis tests"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize with encoded dataset
        
        Parameters:
        -----------
        df : pd.DataFrame
            Dataset with both categorical and numeric encoded variables
        """
        self.df = df
        self.results = {}
    
    def h1_stress_vs_productivity(self) -> Dict[str, Any]:
        """
        H1: Stress vs Productivity
        H0: Stress level has no effect on productivity
        H1: Higher stress levels reduce productivity
        Test: Correlation and Regression
        """
        print("\n" + "="*70)
        print("H1: STRESS vs PRODUCTIVITY")
        print("="*70)
        
        # Pearson correlation
        corr, p_value = pearsonr(
            self.df['StressLevel_Numeric'], 
            self.df['ProductivityChange_Numeric']
        )
        
        # Linear regression for more detail
        X = sm.add_constant(self.df['StressLevel_Numeric'])
        y = self.df['ProductivityChange_Numeric']
        model = sm.OLS(y, X).fit()
        
        result = {
            'hypothesis': 'H1',
            'title': 'Stress vs Productivity',
            'null_hypothesis': 'Stress level has no effect on productivity',
            'alternative_hypothesis': 'Higher stress levels reduce productivity',
            'test_used': 'Pearson Correlation + Linear Regression',
            'correlation': corr,
            'p_value': p_value,
            'regression_coefficient': model.params[1],
            'regression_p_value': model.pvalues[1],
            'r_squared': model.rsquared,
            'reject_null': p_value < 0.05 and corr < 0,
            'conclusion': self._generate_conclusion(
                p_value < 0.05, 
                f"Correlation = {corr:.4f}, p = {p_value:.4f}. " +
                (f"Higher stress is associated with {'lower' if corr < 0 else 'higher'} productivity." 
                 if p_value < 0.05 else "No significant relationship found.")
            )
        }
        
        self._print_result(result)
        self.results['H1'] = result
        return result
    
    def h2_sector_comparison(self) -> Dict[str, Any]:
        """
        H2: Sector Comparison
        H0: Average productivity change is equal across sectors
        H1: At least one sector differs in productivity change
        Test: ANOVA / Kruskal-Wallis
        """
        print("\n" + "="*70)
        print("H2: SECTOR COMPARISON (Productivity)")
        print("="*70)
        
        # Group by sector
        groups = [
            self.df[self.df['Sector'] == sector]['ProductivityChange_Numeric'].values
            for sector in self.df['Sector'].unique()
        ]
        
        # ANOVA
        f_stat, p_value = f_oneway(*groups)
        
        # Kruskal-Wallis (non-parametric alternative)
        h_stat, kw_p_value = stats.kruskal(*groups)
        
        # Calculate sector means
        sector_means = self.df.groupby('Sector')['ProductivityChange_Numeric'].mean().to_dict()
        
        result = {
            'hypothesis': 'H2',
            'title': 'Sector Comparison (Productivity)',
            'null_hypothesis': 'Average productivity change is equal across sectors',
            'alternative_hypothesis': 'At least one sector differs in productivity change',
            'test_used': 'One-Way ANOVA + Kruskal-Wallis',
            'f_statistic': f_stat,
            'p_value': p_value,
            'kruskal_wallis_h': h_stat,
            'kruskal_wallis_p': kw_p_value,
            'sector_means': sector_means,
            'reject_null': p_value < 0.05,
            'conclusion': self._generate_conclusion(
                p_value < 0.05,
                f"F = {f_stat:.4f}, p = {p_value:.4f}. " +
                ("Significant differences exist between sectors." if p_value < 0.05 
                 else "No significant differences between sectors.")
            )
        }
        
        self._print_result(result)
        self.results['H2'] = result
        return result
    
    def h3_technology_adaptation(self) -> Dict[str, Any]:
        """
        H3: Technology Adaptation
        H0: Technology adaptation is unrelated to productivity
        H1: Better technology adaptation improves productivity
        Test: Regression / Logistic Regression
        """
        print("\n" + "="*70)
        print("H3: TECHNOLOGY ADAPTATION vs PRODUCTIVITY")
        print("="*70)
        
        # Correlation
        corr, p_value = pearsonr(
            self.df['TechAdaptation_Numeric'],
            self.df['ProductivityChange_Numeric']
        )
        
        # Linear regression
        X = sm.add_constant(self.df['TechAdaptation_Numeric'])
        y = self.df['ProductivityChange_Numeric']
        model = sm.OLS(y, X).fit()
        
        result = {
            'hypothesis': 'H3',
            'title': 'Technology Adaptation vs Productivity',
            'null_hypothesis': 'Technology adaptation is unrelated to productivity',
            'alternative_hypothesis': 'Better technology adaptation improves productivity',
            'test_used': 'Linear Regression',
            'correlation': corr,
            'p_value': model.pvalues[1],
            'regression_coefficient': model.params[1],
            'r_squared': model.rsquared,
            'reject_null': model.pvalues[1] < 0.05 and model.params[1] > 0,
            'conclusion': self._generate_conclusion(
                model.pvalues[1] < 0.05,
                f"β = {model.params[1]:.4f}, p = {model.pvalues[1]:.4f}. " +
                ("Better tech adaptation is associated with higher productivity." 
                 if model.pvalues[1] < 0.05 and model.params[1] > 0
                 else "No significant relationship found.")
            )
        }
        
        self._print_result(result)
        self.results['H3'] = result
        return result
    
    def h4_work_mode_stress(self) -> Dict[str, Any]:
        """
        H4: Work-from-Home vs Stress
        H0: Work mode (remote/on-site) is not associated with stress
        H1: Stress levels differ between remote and on-site workers
        Test: t-test / Chi-square
        """
        print("\n" + "="*70)
        print("H4: WORK MODE vs STRESS")
        print("="*70)
        
        # Independent samples t-test
        remote = self.df[self.df['WorkFromHome']]['StressLevel_Numeric']
        onsite = self.df[~self.df['WorkFromHome']]['StressLevel_Numeric']
        
        t_stat, p_value = ttest_ind(remote, onsite)
        
        # Effect size (Cohen's d)
        cohens_d = (remote.mean() - onsite.mean()) / np.sqrt(
            ((len(remote) - 1) * remote.std()**2 + (len(onsite) - 1) * onsite.std()**2) / 
            (len(remote) + len(onsite) - 2)
        )
        
        # Chi-square test
        contingency = pd.crosstab(self.df['WorkFromHome'], self.df['StressLevel'])
        chi2, chi2_p, dof, expected = chi2_contingency(contingency)
        
        result = {
            'hypothesis': 'H4',
            'title': 'Work Mode vs Stress',
            'null_hypothesis': 'Work mode is not associated with stress',
            'alternative_hypothesis': 'Stress levels differ between remote and on-site workers',
            'test_used': 'Independent t-test + Chi-square',
            't_statistic': t_stat,
            'p_value': p_value,
            'cohens_d': cohens_d,
            'chi_square': chi2,
            'chi_square_p': chi2_p,
            'remote_mean_stress': remote.mean(),
            'onsite_mean_stress': onsite.mean(),
            'reject_null': p_value < 0.05,
            'conclusion': self._generate_conclusion(
                p_value < 0.05,
                f"t = {t_stat:.4f}, p = {p_value:.4f}, d = {cohens_d:.4f}. " +
                (f"Remote workers have {'higher' if remote.mean() > onsite.mean() else 'lower'} stress." 
                 if p_value < 0.05 else "No significant difference in stress levels.")
            )
        }
        
        self._print_result(result)
        self.results['H4'] = result
        return result
    
    def h5_work_hours_stress(self) -> Dict[str, Any]:
        """
        H5: Work Hours vs Stress
        H0: Hours worked per day are not correlated with stress
        H1: Longer work hours increase stress levels
        Test: Pearson/Spearman Correlation
        """
        print("\n" + "="*70)
        print("H5: WORK HOURS vs STRESS")
        print("="*70)
        
        # Pearson correlation
        pearson_corr, pearson_p = pearsonr(
            self.df['HoursWorkedPerDay'],
            self.df['StressLevel_Numeric']
        )
        
        # Spearman correlation (non-parametric)
        spearman_corr, spearman_p = spearmanr(
            self.df['HoursWorkedPerDay'],
            self.df['StressLevel_Numeric']
        )
        
        result = {
            'hypothesis': 'H5',
            'title': 'Work Hours vs Stress',
            'null_hypothesis': 'Hours worked per day are not correlated with stress',
            'alternative_hypothesis': 'Longer work hours increase stress levels',
            'test_used': 'Pearson + Spearman Correlation',
            'pearson_r': pearson_corr,
            'pearson_p': pearson_p,
            'spearman_r': spearman_corr,
            'spearman_p': spearman_p,
            'p_value': pearson_p,
            'reject_null': pearson_p < 0.05 and pearson_corr > 0,
            'conclusion': self._generate_conclusion(
                pearson_p < 0.05,
                f"r = {pearson_corr:.4f}, p = {pearson_p:.4f}. " +
                ("Longer work hours are associated with higher stress." 
                 if pearson_p < 0.05 and pearson_corr > 0
                 else "No significant correlation found.")
            )
        }
        
        self._print_result(result)
        self.results['H5'] = result
        return result
    
    def h6_collaboration_productivity(self) -> Dict[str, Any]:
        """
        H6: Collaboration Challenges vs Productivity
        H0: Collaboration challenges do not affect productivity
        H1: Collaboration challenges decrease productivity
        Test: ANOVA / Regression
        """
        print("\n" + "="*70)
        print("H6: COLLABORATION CHALLENGES vs PRODUCTIVITY")
        print("="*70)
        
        # ANOVA
        groups = [
            self.df[self.df['CollaborationChallenges'] == level]['ProductivityChange_Numeric'].values
            for level in ['None', 'Minor', 'Moderate', 'Severe']
        ]
        f_stat, p_value = f_oneway(*groups)
        
        # Linear regression
        X = sm.add_constant(self.df['CollaborationChallenges_Numeric'])
        y = self.df['ProductivityChange_Numeric']
        model = sm.OLS(y, X).fit()
        
        result = {
            'hypothesis': 'H6',
            'title': 'Collaboration Challenges vs Productivity',
            'null_hypothesis': 'Collaboration challenges do not affect productivity',
            'alternative_hypothesis': 'Collaboration challenges decrease productivity',
            'test_used': 'ANOVA + Linear Regression',
            'f_statistic': f_stat,
            'p_value': p_value,
            'regression_coefficient': model.params[1],
            'regression_p': model.pvalues[1],
            'reject_null': p_value < 0.05 and model.params[1] < 0,
            'conclusion': self._generate_conclusion(
                p_value < 0.05,
                f"F = {f_stat:.4f}, p = {p_value:.4f}. " +
                ("Greater collaboration challenges are associated with lower productivity." 
                 if p_value < 0.05 and model.params[1] < 0
                 else "No significant relationship found.")
            )
        }
        
        self._print_result(result)
        self.results['H6'] = result
        return result
    
    def h7_job_security_pri(self) -> Dict[str, Any]:
        """
        H7: Job Security vs PRI
        H0: Job security has no effect on productivity resilience (PRI)
        H1: Workers with secure jobs have higher PRI values
        Test: t-test / Regression
        """
        print("\n" + "="*70)
        print("H7: JOB SECURITY vs PRODUCTIVITY RESILIENCE INDEX")
        print("="*70)
        
        # Compare Secure vs Not Secure
        secure = self.df[self.df['JobSecurity'] == 'Secure']['ProductivityResilienceIndex']
        not_secure = self.df[self.df['JobSecurity'] != 'Secure']['ProductivityResilienceIndex']
        
        t_stat, p_value = ttest_ind(secure, not_secure)
        
        # Effect size
        cohens_d = (secure.mean() - not_secure.mean()) / np.sqrt(
            ((len(secure) - 1) * secure.std()**2 + (len(not_secure) - 1) * not_secure.std()**2) / 
            (len(secure) + len(not_secure) - 2)
        )
        
        # Regression with numeric encoding
        X = sm.add_constant(self.df['JobSecurity_Numeric'])
        y = self.df['ProductivityResilienceIndex']
        model = sm.OLS(y, X).fit()
        
        result = {
            'hypothesis': 'H7',
            'title': 'Job Security vs PRI',
            'null_hypothesis': 'Job security has no effect on PRI',
            'alternative_hypothesis': 'Workers with secure jobs have higher PRI',
            'test_used': 'Independent t-test + Regression',
            't_statistic': t_stat,
            'p_value': p_value,
            'cohens_d': cohens_d,
            'secure_mean_pri': secure.mean(),
            'not_secure_mean_pri': not_secure.mean(),
            'regression_coefficient': model.params[1],
            'reject_null': p_value < 0.05 and secure.mean() > not_secure.mean(),
            'conclusion': self._generate_conclusion(
                p_value < 0.05,
                f"t = {t_stat:.4f}, p = {p_value:.4f}, d = {cohens_d:.4f}. " +
                ("Workers with secure jobs have significantly higher PRI." 
                 if p_value < 0.05 and secure.mean() > not_secure.mean()
                 else "No significant difference in PRI.")
            )
        }
        
        self._print_result(result)
        self.results['H7'] = result
        return result
    
    def h8_childcare_productivity(self) -> Dict[str, Any]:
        """
        H8: Childcare Responsibilities vs Productivity
        H0: Childcare duties are unrelated to productivity
        H1: Childcare responsibilities lower productivity
        Test: Chi-square / t-test
        """
        print("\n" + "="*70)
        print("H8: CHILDCARE RESPONSIBILITIES vs PRODUCTIVITY")
        print("="*70)
        
        # t-test on numeric productivity
        with_childcare = self.df[self.df['ChildcareResponsibilities']]['ProductivityChange_Numeric']
        without_childcare = self.df[~self.df['ChildcareResponsibilities']]['ProductivityChange_Numeric']
        
        t_stat, p_value = ttest_ind(with_childcare, without_childcare)
        
        # Chi-square test
        contingency = pd.crosstab(
            self.df['ChildcareResponsibilities'],
            self.df['ProductivityChange']
        )
        chi2, chi2_p, dof, expected = chi2_contingency(contingency)
        
        result = {
            'hypothesis': 'H8',
            'title': 'Childcare Responsibilities vs Productivity',
            'null_hypothesis': 'Childcare duties are unrelated to productivity',
            'alternative_hypothesis': 'Childcare responsibilities lower productivity',
            'test_used': 'Independent t-test + Chi-square',
            't_statistic': t_stat,
            'p_value': p_value,
            'chi_square': chi2,
            'chi_square_p': chi2_p,
            'with_childcare_mean': with_childcare.mean(),
            'without_childcare_mean': without_childcare.mean(),
            'reject_null': p_value < 0.05 and with_childcare.mean() < without_childcare.mean(),
            'conclusion': self._generate_conclusion(
                p_value < 0.05,
                f"t = {t_stat:.4f}, p = {p_value:.4f}. " +
                ("Childcare responsibilities are associated with lower productivity." 
                 if p_value < 0.05 and with_childcare.mean() < without_childcare.mean()
                 else "No significant relationship found.")
            )
        }
        
        self._print_result(result)
        self.results['H8'] = result
        return result
    
    def h9_meetings_stress(self) -> Dict[str, Any]:
        """
        H9: Meetings vs Stress
        H0: Number of meetings per day is unrelated to stress
        H1: More meetings increase stress levels
        Test: Correlation
        """
        print("\n" + "="*70)
        print("H9: MEETINGS vs STRESS")
        print("="*70)
        
        # Pearson correlation
        pearson_corr, pearson_p = pearsonr(
            self.df['MeetingsPerDay'],
            self.df['StressLevel_Numeric']
        )
        
        # Spearman correlation
        spearman_corr, spearman_p = spearmanr(
            self.df['MeetingsPerDay'],
            self.df['StressLevel_Numeric']
        )
        
        result = {
            'hypothesis': 'H9',
            'title': 'Meetings vs Stress',
            'null_hypothesis': 'Number of meetings is unrelated to stress',
            'alternative_hypothesis': 'More meetings increase stress levels',
            'test_used': 'Pearson + Spearman Correlation',
            'pearson_r': pearson_corr,
            'pearson_p': pearson_p,
            'spearman_r': spearman_corr,
            'spearman_p': spearman_p,
            'p_value': pearson_p,
            'reject_null': pearson_p < 0.05 and pearson_corr > 0,
            'conclusion': self._generate_conclusion(
                pearson_p < 0.05,
                f"r = {pearson_corr:.4f}, p = {pearson_p:.4f}. " +
                ("More meetings are associated with higher stress." 
                 if pearson_p < 0.05 and pearson_corr > 0
                 else "No significant correlation found.")
            )
        }
        
        self._print_result(result)
        self.results['H9'] = result
        return result
    
    def h10_health_productivity(self) -> Dict[str, Any]:
        """
        H10: Health Issues vs Productivity
        H0: Health issues do not affect productivity
        H1: Health issues reduce productivity
        Test: t-test / ANOVA
        """
        print("\n" + "="*70)
        print("H10: HEALTH ISSUES vs PRODUCTIVITY")
        print("="*70)
        
        # t-test
        with_health_issues = self.df[self.df['HealthIssues']]['ProductivityChange_Numeric']
        without_health_issues = self.df[~self.df['HealthIssues']]['ProductivityChange_Numeric']
        
        t_stat, p_value = ttest_ind(with_health_issues, without_health_issues)
        
        # Effect size
        cohens_d = (with_health_issues.mean() - without_health_issues.mean()) / np.sqrt(
            ((len(with_health_issues) - 1) * with_health_issues.std()**2 + 
             (len(without_health_issues) - 1) * without_health_issues.std()**2) / 
            (len(with_health_issues) + len(without_health_issues) - 2)
        )
        
        result = {
            'hypothesis': 'H10',
            'title': 'Health Issues vs Productivity',
            'null_hypothesis': 'Health issues do not affect productivity',
            'alternative_hypothesis': 'Health issues reduce productivity',
            'test_used': 'Independent t-test',
            't_statistic': t_stat,
            'p_value': p_value,
            'cohens_d': cohens_d,
            'with_health_issues_mean': with_health_issues.mean(),
            'without_health_issues_mean': without_health_issues.mean(),
            'reject_null': p_value < 0.05 and with_health_issues.mean() < without_health_issues.mean(),
            'conclusion': self._generate_conclusion(
                p_value < 0.05,
                f"t = {t_stat:.4f}, p = {p_value:.4f}, d = {cohens_d:.4f}. " +
                ("Health issues are associated with lower productivity." 
                 if p_value < 0.05 and with_health_issues.mean() < without_health_issues.mean()
                 else "No significant relationship found.")
            )
        }
        
        self._print_result(result)
        self.results['H10'] = result
        return result
    
    def run_all_tests(self) -> Dict[str, Dict[str, Any]]:
        """Run all 10 hypothesis tests"""
        print("\n" + "="*70)
        print("COVID-19 WORK & WELLBEING ANALYSIS")
        print("HYPOTHESIS TESTING BATTERY")
        print("="*70)
        
        self.h1_stress_vs_productivity()
        self.h2_sector_comparison()
        self.h3_technology_adaptation()
        self.h4_work_mode_stress()
        self.h5_work_hours_stress()
        self.h6_collaboration_productivity()
        self.h7_job_security_pri()
        self.h8_childcare_productivity()
        self.h9_meetings_stress()
        self.h10_health_productivity()
        
        return self.results
    
    @staticmethod
    def _generate_conclusion(reject_null: bool, details: str) -> str:
        """Generate conclusion statement"""
        decision = "REJECT H₀" if reject_null else "FAIL TO REJECT H₀"
        return f"{decision}. {details}"
    
    @staticmethod
    def _print_result(result: Dict[str, Any]):
        """Pretty print a hypothesis result"""
        print(f"\nNull Hypothesis: {result['null_hypothesis']}")
        print(f"Alternative: {result['alternative_hypothesis']}")
        print(f"Test: {result['test_used']}")
        print(f"p-value: {result['p_value']:.6f}")
        print(f"Decision: {'REJECT H₀' if result['reject_null'] else 'FAIL TO REJECT H₀'}")
        print(f"Conclusion: {result['conclusion']}")


if __name__ == '__main__':
    # Load dataset
    print("Loading dataset...")
    df = pd.read_csv('covid19_work_wellbeing_data.csv')
    
    # Run all tests
    tester = HypothesisTester(df)
    results = tester.run_all_tests()
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY OF ALL HYPOTHESES")
    print("="*70)
    rejected_count = sum(1 for r in results.values() if r['reject_null'])
    print(f"\nTotal Hypotheses: 10")
    print(f"Rejected: {rejected_count}")
    print(f"Not Rejected: {10 - rejected_count}")
