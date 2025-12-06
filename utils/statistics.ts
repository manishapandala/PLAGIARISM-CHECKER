/**
 * Statistical Analysis Functions for COVID-19 Hypotheses
 * Implements various statistical tests including correlation, t-tests, ANOVA, regression, etc.
 */

import type { CovidDataRecord, HypothesisResult, CorrelationResult, RegressionResult } from '../types';

/**
 * Calculate mean of an array
 */
export function mean(values: number[]): number {
  if (values.length === 0) return 0;
  return values.reduce((sum, val) => sum + val, 0) / values.length;
}

/**
 * Calculate standard deviation
 */
export function standardDeviation(values: number[]): number {
  if (values.length === 0) return 0;
  const avg = mean(values);
  const squaredDiffs = values.map(val => Math.pow(val - avg, 2));
  return Math.sqrt(mean(squaredDiffs));
}

/**
 * Calculate median
 */
export function median(values: number[]): number {
  if (values.length === 0) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid];
}

/**
 * Pearson correlation coefficient
 */
export function pearsonCorrelation(x: number[], y: number[]): number {
  if (x.length !== y.length || x.length === 0) return 0;
  
  const n = x.length;
  const meanX = mean(x);
  const meanY = mean(y);
  
  let numerator = 0;
  let sumXSquared = 0;
  let sumYSquared = 0;
  
  for (let i = 0; i < n; i++) {
    const dx = x[i] - meanX;
    const dy = y[i] - meanY;
    numerator += dx * dy;
    sumXSquared += dx * dx;
    sumYSquared += dy * dy;
  }
  
  const denominator = Math.sqrt(sumXSquared * sumYSquared);
  return denominator === 0 ? 0 : numerator / denominator;
}

/**
 * Calculate t-statistic and p-value for correlation
 */
export function correlationTest(r: number, n: number): { t: number; p: number } {
  if (n <= 2) return { t: 0, p: 1 };
  const t = r * Math.sqrt((n - 2) / (1 - r * r));
  const df = n - 2;
  const p = 2 * (1 - tCDF(Math.abs(t), df));
  return { t, p };
}

/**
 * Independent samples t-test
 */
export function tTest(group1: number[], group2: number[]): { t: number; p: number; df: number } {
  const n1 = group1.length;
  const n2 = group2.length;
  
  if (n1 === 0 || n2 === 0) return { t: 0, p: 1, df: 0 };
  
  const mean1 = mean(group1);
  const mean2 = mean(group2);
  const std1 = standardDeviation(group1);
  const std2 = standardDeviation(group2);
  
  // Pooled standard deviation
  const pooledStd = Math.sqrt(((n1 - 1) * std1 * std1 + (n2 - 1) * std2 * std2) / (n1 + n2 - 2));
  const t = (mean1 - mean2) / (pooledStd * Math.sqrt(1 / n1 + 1 / n2));
  const df = n1 + n2 - 2;
  const p = 2 * (1 - tCDF(Math.abs(t), df));
  
  return { t, p, df };
}

/**
 * One-way ANOVA
 */
export function anova(groups: number[][]): { f: number; p: number; dfBetween: number; dfWithin: number } {
  const k = groups.length; // number of groups
  const n = groups.reduce((sum, g) => sum + g.length, 0); // total observations
  
  if (k < 2 || n === 0) return { f: 0, p: 1, dfBetween: 0, dfWithin: 0 };
  
  // Grand mean
  const allValues = groups.flat();
  const grandMean = mean(allValues);
  
  // Between-group sum of squares
  let ssb = 0;
  for (const group of groups) {
    const groupMean = mean(group);
    ssb += group.length * Math.pow(groupMean - grandMean, 2);
  }
  
  // Within-group sum of squares
  let ssw = 0;
  for (const group of groups) {
    const groupMean = mean(group);
    for (const value of group) {
      ssw += Math.pow(value - groupMean, 2);
    }
  }
  
  const dfBetween = k - 1;
  const dfWithin = n - k;
  
  const msb = ssb / dfBetween;
  const msw = ssw / dfWithin;
  
  const f = msw === 0 ? 0 : msb / msw;
  const p = 1 - fCDF(f, dfBetween, dfWithin);
  
  return { f, p, dfBetween, dfWithin };
}

/**
 * Chi-square test for independence (contingency table)
 */
export function chiSquareTest(observed: number[][]): { chiSquare: number; p: number; df: number } {
  const rows = observed.length;
  const cols = observed[0].length;
  
  // Calculate row and column totals
  const rowTotals = observed.map(row => row.reduce((sum, val) => sum + val, 0));
  const colTotals = observed[0].map((_, colIndex) => 
    observed.reduce((sum, row) => sum + row[colIndex], 0)
  );
  const total = rowTotals.reduce((sum, val) => sum + val, 0);
  
  // Calculate expected frequencies and chi-square statistic
  let chiSquare = 0;
  for (let i = 0; i < rows; i++) {
    for (let j = 0; j < cols; j++) {
      const expected = (rowTotals[i] * colTotals[j]) / total;
      if (expected > 0) {
        chiSquare += Math.pow(observed[i][j] - expected, 2) / expected;
      }
    }
  }
  
  const df = (rows - 1) * (cols - 1);
  const p = 1 - chiSquareCDF(chiSquare, df);
  
  return { chiSquare, p, df };
}

/**
 * Simple linear regression
 */
export function simpleLinearRegression(x: number[], y: number[]): RegressionResult {
  const n = x.length;
  const meanX = mean(x);
  const meanY = mean(y);
  
  let numerator = 0;
  let denominator = 0;
  
  for (let i = 0; i < n; i++) {
    numerator += (x[i] - meanX) * (y[i] - meanY);
    denominator += Math.pow(x[i] - meanX, 2);
  }
  
  const slope = denominator === 0 ? 0 : numerator / denominator;
  const intercept = meanY - slope * meanX;
  
  // Calculate R-squared
  const predictions = x.map(xi => intercept + slope * xi);
  const ssTotal = y.reduce((sum, yi) => sum + Math.pow(yi - meanY, 2), 0);
  const ssResidual = y.reduce((sum, yi, i) => sum + Math.pow(yi - predictions[i], 2), 0);
  const rSquared = ssTotal === 0 ? 0 : 1 - ssResidual / ssTotal;
  
  // Standard error and t-statistic for slope
  const residuals = y.map((yi, i) => yi - predictions[i]);
  const mse = ssResidual / (n - 2);
  const slopeStdError = Math.sqrt(mse / denominator);
  const tValue = slopeStdError === 0 ? 0 : slope / slopeStdError;
  const pValue = 2 * (1 - tCDF(Math.abs(tValue), n - 2));
  
  const fStatistic = rSquared === 1 ? Infinity : (rSquared / 1) / ((1 - rSquared) / (n - 2));
  
  return {
    predictors: ['X'],
    coefficients: [slope],
    standardErrors: [slopeStdError],
    tValues: [tValue],
    pValues: [pValue],
    rSquared,
    adjustedRSquared: 1 - (1 - rSquared) * (n - 1) / (n - 2),
    fStatistic,
    intercept
  };
}

/**
 * Approximate t-distribution CDF using normal approximation for large df
 */
function tCDF(t: number, df: number): number {
  if (df > 100) {
    // Use normal approximation for large df
    return normalCDF(t);
  }
  
  // Simplified approximation for smaller df
  const x = df / (df + t * t);
  return 1 - 0.5 * incompleteBeta(df / 2, 0.5, x);
}

/**
 * Normal distribution CDF (approximation)
 */
function normalCDF(z: number): number {
  const t = 1 / (1 + 0.2316419 * Math.abs(z));
  const d = 0.3989423 * Math.exp(-z * z / 2);
  const p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));
  return z > 0 ? 1 - p : p;
}

/**
 * Chi-square distribution CDF (approximation)
 */
function chiSquareCDF(x: number, df: number): number {
  if (x <= 0) return 0;
  if (df === 1) {
    return 2 * normalCDF(Math.sqrt(x)) - 1;
  }
  // Wilson-Hilferty approximation
  const z = Math.pow(x / df, 1 / 3) - (1 - 2 / (9 * df)) / Math.sqrt(2 / (9 * df));
  return normalCDF(z);
}

/**
 * F-distribution CDF (approximation)
 */
function fCDF(x: number, df1: number, df2: number): number {
  if (x <= 0) return 0;
  // Beta distribution relationship
  const t = df2 / (df2 + df1 * x);
  return 1 - incompleteBeta(df2 / 2, df1 / 2, t);
}

/**
 * Incomplete beta function (simplified approximation)
 */
function incompleteBeta(a: number, b: number, x: number): number {
  if (x <= 0) return 0;
  if (x >= 1) return 1;
  
  // Use continued fraction approximation
  const lbeta = logGamma(a) + logGamma(b) - logGamma(a + b);
  const front = Math.exp(Math.log(x) * a + Math.log(1 - x) * b - lbeta) / a;
  
  let f = 1.0;
  let c = 1.0;
  let d = 0.0;
  
  for (let i = 0; i <= 200; i++) {
    const m = i / 2;
    
    let numerator;
    if (i === 0) {
      numerator = 1.0;
    } else if (i % 2 === 0) {
      numerator = (m * (b - m) * x) / ((a + 2 * m - 1) * (a + 2 * m));
    } else {
      numerator = -((a + m) * (a + b + m) * x) / ((a + 2 * m) * (a + 2 * m + 1));
    }
    
    d = 1.0 + numerator * d;
    if (Math.abs(d) < 1e-30) d = 1e-30;
    d = 1.0 / d;
    
    c = 1.0 + numerator / c;
    if (Math.abs(c) < 1e-30) c = 1e-30;
    
    const cd = c * d;
    f *= cd;
    
    if (Math.abs(1.0 - cd) < 1e-8) break;
  }
  
  return front * f;
}

/**
 * Log gamma function (Stirling approximation)
 */
function logGamma(x: number): number {
  const coef = [
    76.18009172947146, -86.50532032941677,
    24.01409824083091, -1.231739572450155,
    0.001208650973866179, -0.000005395239384953
  ];
  
  let y = x;
  let tmp = x + 5.5;
  tmp -= (x + 0.5) * Math.log(tmp);
  let ser = 1.000000000190015;
  
  for (let j = 0; j < 6; j++) {
    ser += coef[j] / ++y;
  }
  
  return -tmp + Math.log(2.5066282746310005 * ser / x);
}

/**
 * Cohen's d effect size for t-test
 */
export function cohensD(group1: number[], group2: number[]): number {
  const mean1 = mean(group1);
  const mean2 = mean(group2);
  const n1 = group1.length;
  const n2 = group2.length;
  const std1 = standardDeviation(group1);
  const std2 = standardDeviation(group2);
  
  const pooledStd = Math.sqrt(((n1 - 1) * std1 * std1 + (n2 - 1) * std2 * std2) / (n1 + n2 - 2));
  return pooledStd === 0 ? 0 : (mean1 - mean2) / pooledStd;
}

/**
 * Eta-squared effect size for ANOVA
 */
export function etaSquared(groups: number[][]): number {
  const allValues = groups.flat();
  const grandMean = mean(allValues);
  
  let ssb = 0;
  for (const group of groups) {
    const groupMean = mean(group);
    ssb += group.length * Math.pow(groupMean - grandMean, 2);
  }
  
  let ssTotal = 0;
  for (const value of allValues) {
    ssTotal += Math.pow(value - grandMean, 2);
  }
  
  return ssTotal === 0 ? 0 : ssb / ssTotal;
}
