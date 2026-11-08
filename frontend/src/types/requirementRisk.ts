export type RequirementCategory =
  | "Functional"
  | "Non-Functional"
  | "Business Rule"
  | "Security"
  | "Compliance"
  | "Integration"
  | "Constraint"
  | "Unknown";

export type RiskCategory =
  | "Business"
  | "Scope"
  | "Requirement Quality"
  | "Delivery"
  | "Dependency"
  | "Integration"
  | "Data"
  | "Security"
  | "Privacy"
  | "Compliance"
  | "Operational"
  | "Performance"
  | "Availability"
  | "Recoverability"
  | "Testing"
  | "Stakeholder";

export type RiskLikelihood = "High" | "Medium" | "Low" | "Unknown";
export type RiskImpact = "Critical" | "High" | "Medium" | "Low";
export type RiskSeverity = "Critical" | "High" | "Medium" | "Low";
export type RiskStatus =
  | "Confirmed Risk"
  | "Potential Risk"
  | "Needs Clarification";
export type MitigationStatus =
  | "Ready"
  | "Needs Decision"
  | "Needs Specialist Review";
export type ReadinessStatus =
  | "Ready"
  | "Proceed with Caution"
  | "Not Ready";

export interface RiskRequirementItem {
  requirement_id: string;
  title: string;
  requirement_text: string;
  category: RequirementCategory;
  source_document: string | null;
  source_section: string | null;
}

export interface RequirementRiskRequest {
  analysis_title: string;
  business_context: string;
  business_domain: string;
  requirements: RiskRequirementItem[];
  known_dependencies: string[];
  known_constraints: string[];
  additional_instructions: string | null;
}

export interface RiskEvidence {
  requirement_id: string;
  evidence_text: string;
  explanation: string;
}

export interface RiskMitigation {
  mitigation_id: string;
  action: string;
  rationale: string;
  owner: string;
  status: MitigationStatus;
  validation_required: boolean;
}

export interface RequirementRiskFinding {
  risk_id: string;
  title: string;
  category: RiskCategory;
  status: RiskStatus;
  likelihood: RiskLikelihood;
  impact: RiskImpact;
  severity: RiskSeverity;
  risk_statement: string;
  cause: string;
  consequence: string;
  affected_requirement_ids: string[];
  evidence: RiskEvidence[];
  assumptions: string[];
  mitigation_actions: RiskMitigation[];
  monitoring_indicators: string[];
  blocks_implementation: boolean;
  blocks_testing: boolean;
  requires_human_validation: boolean;
  validation_questions: string[];
  suggested_owner: string;
}

export interface RequirementRiskRelationship {
  requirement_id: string;
  risk_ids: string[];
  highest_severity: RiskSeverity | null;
  risk_free: boolean;
  notes: string;
}

export interface RiskSummaryEntry {
  severity: RiskSeverity;
  count: number;
  risk_ids: string[];
}

export interface RequirementRiskResponse {
  analysis_summary: string;
  confirmed_information: string[];
  risk_findings: RequirementRiskFinding[];
  risk_summary: RiskSummaryEntry[];
  requirement_relationships: RequirementRiskRelationship[];
  overall_readiness: ReadinessStatus;
  overall_risk_score: number;
  score_explanation: string;
  assumptions: string[];
  missing_information: string[];
  recommended_next_actions: string[];
  human_validation_required: string[];
}
