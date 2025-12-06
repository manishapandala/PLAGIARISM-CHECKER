import type { CovidDataRecord } from '../types';

/**
 * Generates synthetic COVID-19 work and wellbeing dataset
 * Based on the specifications provided in the research document
 */
export function generateCovidDataset(size: number = 10000): CovidDataRecord[] {
  const sectors = ['IT', 'Retail', 'Education', 'Healthcare', 'Finance'] as const;
  const stressLevels = ['Low', 'Medium', 'High'] as const;
  const productivityChanges = ['Increased', 'Decreased', 'No Change'] as const;
  const commuteChanges = ['Increased', 'Decreased', 'No Change'] as const;
  const salaryChanges = ['Increased', 'Decreased', 'No Change'] as const;
  const jobSecurityLevels = ['Secure', 'Uncertain', 'At Risk'] as const;
  const techAdaptationLevels = ['Poor', 'Fair', 'Good', 'Excellent'] as const;
  const collaborationLevels = ['None', 'Minor', 'Moderate', 'Severe'] as const;

  const data: CovidDataRecord[] = [];

  for (let i = 0; i < size; i++) {
    const sector = sectors[Math.floor(Math.random() * sectors.length)];
    
    // 80% work from home
    const workFromHome = Math.random() < 0.8;
    
    // Sector-specific adjustments
    let stressBonus = 0;
    let productivityBonus = 0;
    let hoursBonus = 0;
    
    if (sector === 'Healthcare' || sector === 'Retail') {
      stressBonus = 0.3; // Higher stress
      productivityBonus = -0.2; // Lower productivity
    } else if (sector === 'IT' || sector === 'Finance') {
      productivityBonus = 0.1; // Better productivity
    }
    
    // Work hours: 67% reported longer hours (6-10 hours typical)
    const baseHours = 8;
    const longerHours = Math.random() < 0.67;
    const hoursWorkedPerDay = longerHours 
      ? baseHours + Math.random() * 3 + hoursBonus
      : baseHours - Math.random() * 2;
    
    // Meetings (2-8 per day, more for remote workers)
    const meetingsPerDay = workFromHome 
      ? 3 + Math.floor(Math.random() * 5)
      : 2 + Math.floor(Math.random() * 3);
    
    // Stress (Medium most common, influenced by sector and hours)
    const stressRand = Math.random() + stressBonus + (hoursWorkedPerDay > 9 ? 0.2 : 0);
    let stressLevel: typeof stressLevels[number];
    if (stressRand < 0.3) stressLevel = 'Low';
    else if (stressRand < 0.7) stressLevel = 'Medium';
    else stressLevel = 'High';
    
    // Productivity change (60-70% noted changes)
    const productivityRand = Math.random() + productivityBonus;
    let productivityChange: typeof productivityChanges[number];
    if (productivityRand < 0.35) productivityChange = 'Decreased';
    else if (productivityRand < 0.65) productivityChange = 'No Change';
    else productivityChange = 'Increased';
    
    // Commute change (mostly decreased for remote workers)
    let commuteChange: typeof commuteChanges[number];
    if (workFromHome) {
      commuteChange = Math.random() < 0.85 ? 'Decreased' : 'No Change';
    } else {
      const rand = Math.random();
      if (rand < 0.4) commuteChange = 'Decreased';
      else if (rand < 0.7) commuteChange = 'No Change';
      else commuteChange = 'Increased';
    }
    
    // Health issues (20-30% affected)
    const healthIssues = Math.random() < 0.25;
    
    // Childcare responsibilities (30-40%)
    const childcareResponsibilities = Math.random() < 0.35;
    
    // Salary changes
    const salaryRand = Math.random();
    let salaryChange: typeof salaryChanges[number];
    if (salaryRand < 0.3) salaryChange = 'Decreased';
    else if (salaryRand < 0.8) salaryChange = 'No Change';
    else salaryChange = 'Increased';
    
    // Job security
    const jobSecRand = Math.random();
    let jobSecurity: typeof jobSecurityLevels[number];
    if (sector === 'Healthcare' || sector === 'IT') {
      // More secure in these sectors
      if (jobSecRand < 0.6) jobSecurity = 'Secure';
      else if (jobSecRand < 0.85) jobSecurity = 'Uncertain';
      else jobSecurity = 'At Risk';
    } else {
      if (jobSecRand < 0.4) jobSecurity = 'Secure';
      else if (jobSecRand < 0.75) jobSecurity = 'Uncertain';
      else jobSecurity = 'At Risk';
    }
    
    // Technology adaptation (better in IT sector)
    const techRand = Math.random();
    let technologyAdaptation: typeof techAdaptationLevels[number];
    if (sector === 'IT') {
      if (techRand < 0.5) technologyAdaptation = 'Excellent';
      else if (techRand < 0.8) technologyAdaptation = 'Good';
      else technologyAdaptation = 'Fair';
    } else {
      if (techRand < 0.15) technologyAdaptation = 'Poor';
      else if (techRand < 0.4) technologyAdaptation = 'Fair';
      else if (techRand < 0.75) technologyAdaptation = 'Good';
      else technologyAdaptation = 'Excellent';
    }
    
    // Collaboration challenges (more for remote workers)
    const collabRand = Math.random();
    let collaborationChallenges: typeof collaborationLevels[number];
    if (workFromHome) {
      if (collabRand < 0.15) collaborationChallenges = 'None';
      else if (collabRand < 0.4) collaborationChallenges = 'Minor';
      else if (collabRand < 0.75) collaborationChallenges = 'Moderate';
      else collaborationChallenges = 'Severe';
    } else {
      if (collabRand < 0.4) collaborationChallenges = 'None';
      else if (collabRand < 0.75) collaborationChallenges = 'Minor';
      else if (collabRand < 0.9) collaborationChallenges = 'Moderate';
      else collaborationChallenges = 'Severe';
    }
    
    // Productivity Resilience Index (0-100)
    // Higher for: secure jobs, good tech adaptation, lower stress
    let pri = 50;
    pri += jobSecurity === 'Secure' ? 20 : jobSecurity === 'Uncertain' ? 0 : -20;
    pri += technologyAdaptation === 'Excellent' ? 15 : technologyAdaptation === 'Good' ? 10 : technologyAdaptation === 'Fair' ? 0 : -10;
    pri += stressLevel === 'Low' ? 15 : stressLevel === 'Medium' ? 0 : -15;
    pri += healthIssues ? -10 : 5;
    pri += childcareResponsibilities ? -5 : 0;
    pri += Math.random() * 20 - 10; // Random variation
    pri = Math.max(0, Math.min(100, pri)); // Clamp to 0-100
    
    // Age and experience
    const age = 22 + Math.floor(Math.random() * 40); // 22-62
    const yearsExperience = Math.min(age - 20, Math.floor(Math.random() * 30)); // 0-30 years
    
    data.push({
      id: i + 1,
      sector,
      workFromHome,
      hoursWorkedPerDay: Math.round(hoursWorkedPerDay * 10) / 10,
      meetingsPerDay,
      commuteChange,
      stressLevel,
      productivityChange,
      healthIssues,
      childcareResponsibilities,
      salaryChange,
      jobSecurity,
      technologyAdaptation,
      collaborationChallenges,
      productivityResilienceIndex: Math.round(pri * 10) / 10,
      age,
      yearsExperience
    });
  }

  return data;
}

/**
 * Convert categorical variables to numerical for statistical analysis
 */
export function encodeVariables(data: CovidDataRecord[]) {
  return data.map(record => ({
    ...record,
    stressLevelNumeric: record.stressLevel === 'Low' ? 1 : record.stressLevel === 'Medium' ? 2 : 3,
    productivityChangeNumeric: record.productivityChange === 'Decreased' ? -1 : record.productivityChange === 'No Change' ? 0 : 1,
    techAdaptationNumeric: record.technologyAdaptation === 'Poor' ? 1 : record.technologyAdaptation === 'Fair' ? 2 : record.technologyAdaptation === 'Good' ? 3 : 4,
    collaborationChallengesNumeric: record.collaborationChallenges === 'None' ? 0 : record.collaborationChallenges === 'Minor' ? 1 : record.collaborationChallenges === 'Moderate' ? 2 : 3,
    jobSecurityNumeric: record.jobSecurity === 'Secure' ? 2 : record.jobSecurity === 'Uncertain' ? 1 : 0,
  }));
}
