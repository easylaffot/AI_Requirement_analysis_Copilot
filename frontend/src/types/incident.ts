export interface IncidentFormData {
  incident_id: string;
  application: string;
  severity: string;
  description: string;
  impact: string;
  logs: string;
}

export interface IncidentAnalysis {
  incident_summary: string;
  business_impact: string;
  root_cause_hypothesis: string;
  functional_requirements: string[];
  user_story: string;
  acceptance_criteria: string[];
  risks: string[];
  priority: string;
}