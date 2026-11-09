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

export type Priority = "Critical" | "High" | "Medium" | "Low" | "Unknown";

export type PriorityMethod =
  | "MoSCoW"
  | "Value and Risk"
  | "Evidence-Based Recommendation";

export type MoSCoWCategory =
  | "Must Have"
  | "Should Have"
  | "Could Have"
  | "Won't Have This Release"
  | "Unclassified";

export type EvidenceStrength =
  | "Strong"
  | "Moderate"
  | "Weak"
  | "Insufficient";

export type ReadinessStatus =
  | "Ready for Prioritization"
  | "Needs Clarification"
  | "Not Ready";

export type PriorityFactorName =
  | "Business Value"
  | "Customer Impact"
  | "Urgency"
  | "Risk Reduction"
  | "Compliance Need"
  | "Security Need"
  | "Dependency Importance"
  | "Operational Impact"
  | "Implementation Readiness";

export type PriorityFactorAssessment = "High" | "Medium" | "Low" | "Unknown";

export interface PriorityRequirementItem {
  requirement_id: string;
  title: string;
  requirement_text: string;
  category: RequirementCategory;
  stated_priority: Priority;
  source_document: string | null;
  source_section: string | null;
}

export interface RequirementPriorityRequest {
  analysis_title: string;
  business_context: string;
  release_objective: string;
  prioritization_method: PriorityMethod;
  requirements: PriorityRequirementItem[];
  known_dependencies: string[];
  known_constraints: string[];
  additional_instructions: string | null;
}

export interface PriorityEvidence {
  evidence_id: string;
  source_reference: string;
  evidence_text: string;
  explanation: string;
}

export interface PriorityFactor {
  factor: PriorityFactorName;
  assessment: PriorityFactorAssessment;
  rationale: string;
  evidence_ids: string[];
}

export interface PrioritizedRequirement {
  requirement_id: string;
  title: string;
  recommended_priority: Priority;
  moscow_category: MoSCoWCategory;
  evidence_strength: EvidenceStrength;
  priority_rationale: string;
  factors: PriorityFactor[];
  evidence: PriorityEvidence[];
  dependency_ids: string[];
  priority_conflict_detected: boolean;
  priority_conflict_explanation: string | null;
  implementation_ready: boolean;
  readiness_explanation: string;
  missing_information: string[];
  clarification_questions: string[];
  requires_human_validation: boolean;
  suggested_owner: string;
}

export interface PrioritySummaryEntry {
  priority: Priority;
  count: number;
  requirement_ids: string[];
}

export interface RequirementPriorityResponse {
  analysis_summary: string;
  release_objective_summary: string;
  prioritized_requirements: PrioritizedRequirement[];
  priority_summary: PrioritySummaryEntry[];
  recommended_delivery_order: string[];
  blocking_requirement_ids: string[];
  readiness_status: ReadinessStatus;
  assumptions: string[];
  missing_information: string[];
  risks: string[];
  recommended_next_actions: string[];
  human_validation_required: string[];
}
