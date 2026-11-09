export type RequirementCategory =
  | "Functional"
  | "Non-Functional"
  | "Business Rule"
  | "Data"
  | "Security"
  | "Privacy"
  | "Compliance"
  | "Integration"
  | "Constraint"
  | "Unknown";

export type ObligationCategory =
  | "Access Control"
  | "Data Protection"
  | "Data Retention"
  | "Consent"
  | "Customer Communication"
  | "Auditability"
  | "Reporting"
  | "Record Keeping"
  | "Security"
  | "Privacy"
  | "Operational Control"
  | "Business Process"
  | "Other";

export type ImpactType =
  | "New Requirement"
  | "Requirement Update"
  | "Requirement Removal"
  | "Control Update"
  | "Process Update"
  | "Testing Update"
  | "Documentation Update"
  | "Potential Impact"
  | "No Impact";

export type CoverageStatus =
  | "Covered"
  | "Partially Covered"
  | "Not Covered"
  | "Potentially Covered"
  | "Not Applicable";

export type ImpactSeverity = "Critical" | "High" | "Medium" | "Low";
export type Confidence = "High" | "Medium" | "Low";
export type ReadinessStatus = "Ready for Review" | "Needs Clarification" | "Not Ready";

export interface RegulatoryObligationItem {
  obligation_id: string;
  title: string;
  obligation_text: string;
  category: ObligationCategory;
  source_name: string;
  source_section: string | null;
  effective_date: string | null;
  jurisdiction: string | null;
}

export interface RegulatoryRequirementItem {
  requirement_id: string;
  title: string;
  requirement_text: string;
  category: RequirementCategory;
  source_document: string | null;
  source_section: string | null;
}

export interface RegulatoryImpactRequest {
  analysis_title: string;
  business_context: string;
  business_domain: string;
  obligations: RegulatoryObligationItem[];
  requirements: RegulatoryRequirementItem[];
  known_controls: string[];
  additional_instructions: string | null;
}

export type RegulatoryEvidenceSource =
  | "Regulatory Obligation"
  | "Requirement"
  | "Known Control";

export interface RegulatoryEvidence {
  source_type: RegulatoryEvidenceSource;
  source_reference: string;
  evidence_text: string;
  explanation: string;
}

export interface RegulatoryImpactFinding {
  impact_id: string;
  obligation_ids: string[];
  affected_requirement_ids: string[];
  impact_type: ImpactType;
  coverage_status: CoverageStatus;
  severity: ImpactSeverity;
  confidence: Confidence;
  title: string;
  explanation: string;
  current_coverage: string;
  coverage_gap: string;
  business_impact: string;
  implementation_impact: string;
  testing_impact: string;
  operational_impact: string;
  evidence: RegulatoryEvidence[];
  recommended_requirement_action: string;
  proposed_requirement_text: string | null;
  validation_questions: string[];
  requires_human_validation: boolean;
  suggested_owner: string;
}

export interface ObligationCoverageEntry {
  obligation_id: string;
  coverage_status: CoverageStatus;
  requirement_ids: string[];
  impact_ids: string[];
  coverage_explanation: string;
  missing_coverage: string[];
  requires_human_validation: boolean;
}

export interface RequirementImpactEntry {
  requirement_id: string;
  impacted: boolean;
  obligation_ids: string[];
  impact_ids: string[];
  highest_severity: ImpactSeverity | null;
  recommended_action: string;
  notes: string;
}

export interface ImpactSummaryEntry {
  severity: ImpactSeverity;
  count: number;
  impact_ids: string[];
}

export interface RegulatoryImpactResponse {
  analysis_summary: string;
  confirmed_information: string[];
  impact_findings: RegulatoryImpactFinding[];
  obligation_coverage: ObligationCoverageEntry[];
  requirement_impacts: RequirementImpactEntry[];
  impact_summary: ImpactSummaryEntry[];
  impacted_requirement_ids: string[];
  uncovered_obligation_ids: string[];
  potential_conflicts: string[];
  readiness_status: ReadinessStatus;
  assumptions: string[];
  missing_information: string[];
  risks: string[];
  recommended_next_actions: string[];
  human_validation_required: string[];
}
