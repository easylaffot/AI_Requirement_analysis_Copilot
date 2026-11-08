export type GapCategory =
  | "Missing Actor"
  | "Missing Business Rule"
  | "Missing Data Definition"
  | "Missing Condition"
  | "Missing Boundary"
  | "Missing Permission"
  | "Missing Exception Handling"
  | "Missing Failure Behavior"
  | "Missing Dependency"
  | "Missing Integration Detail"
  | "Missing Security Requirement"
  | "Missing Privacy Requirement"
  | "Missing Audit Requirement"
  | "Missing Performance Target"
  | "Missing Availability Target"
  | "Missing Recovery Target"
  | "Missing Acceptance Information"
  | "Missing Scope Decision"
  | "Missing Priority"
  | "Missing Ownership";

export type GapSeverity = "High" | "Medium" | "Low";

export type GapStatus = "Confirmed Gap" | "Potential Gap" | "Not Applicable";

export type ReadinessStatus = "Ready" | "Needs Clarification" | "Not Ready";

export interface GapAnalysisRequest {
  requirement_id: string;
  requirement_title: string;
  requirement_text: string;
  business_context: string;
  known_actors: string[];
  known_business_rules: string[];
  known_constraints: string[];
  existing_acceptance_criteria: string[];
  additional_instructions?: string | null;
}

export interface GapFinding {
  gap_id: string;
  category: GapCategory;
  title: string;
  description: string;
  severity: GapSeverity;
  status: GapStatus;
  evidence_from_input: string[];
  missing_information: string;
  impact: string;
  clarification_questions: string[];
  suggested_owner: string;
  blocks_implementation: boolean;
  blocks_testing: boolean;
  requires_human_validation: boolean;
}

export interface CoverageArea {
  area: string;
  covered: boolean;
  evidence: string[];
  gap_ids: string[];
  notes: string;
}

export interface GapAnalysisResponse {
  requirement_summary: string;
  confirmed_information: string[];
  gap_findings: GapFinding[];
  coverage_assessment: CoverageArea[];
  readiness_status: ReadinessStatus;
  readiness_score: number;
  score_explanation: string;
  assumptions: string[];
  risks: string[];
  recommended_next_actions: string[];
  human_validation_required: string[];
}
