// COVID-19 Work and Wellbeing Dataset Types

export interface CovidDataRecord {
  id: number;
  sector: 'IT' | 'Retail' | 'Education' | 'Healthcare' | 'Finance';
  workFromHome: boolean;
  hoursWorkedPerDay: number;
  meetingsPerDay: number;
  commuteChange: 'Increased' | 'Decreased' | 'No Change';
  stressLevel: 'Low' | 'Medium' | 'High';
  productivityChange: 'Increased' | 'Decreased' | 'No Change';
  healthIssues: boolean;
  childcareResponsibilities: boolean;
  salaryChange: 'Increased' | 'Decreased' | 'No Change';
  jobSecurity: 'Secure' | 'Uncertain' | 'At Risk';
  technologyAdaptation: 'Poor' | 'Fair' | 'Good' | 'Excellent';
  collaborationChallenges: 'None' | 'Minor' | 'Moderate' | 'Severe';
  productivityResilienceIndex: number; // PRI: 0-100 scale
  age: number;
  yearsExperience: number;
}

export interface HypothesisResult {
  hypothesisNumber: number;
  title: string;
  nullHypothesis: string;
  alternativeHypothesis: string;
  testUsed: string;
  testStatistic: number;
  pValue: number;
  degreesOfFreedom?: number;
  effectSize?: number;
  conclusion: string;
  reject: boolean;
  additionalMetrics?: Record<string, number>;
}

export interface DescriptiveStats {
  variable: string;
  mean?: number;
  median?: number;
  std?: number;
  min?: number;
  max?: number;
  count?: number;
  frequencies?: Record<string, number>;
}

export interface SectorComparison {
  sector: string;
  avgProductivity: number;
  avgStress: number;
  remoteWorkPercentage: number;
  avgHours: number;
  count: number;
}

export interface CorrelationResult {
  variable1: string;
  variable2: string;
  correlation: number;
  pValue: number;
  significant: boolean;
}

export interface RegressionResult {
  predictors: string[];
  coefficients: number[];
  standardErrors: number[];
  tValues: number[];
  pValues: number[];
  rSquared: number;
  adjustedRSquared: number;
  fStatistic: number;
  intercept: number;
}

export interface ChartDataPoint {
  name: string;
  value: number;
  category?: string;
  [key: string]: any;
}
