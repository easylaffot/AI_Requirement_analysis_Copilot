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

export type DependencyType =
  | "Prerequisite"
  | "Sequence"
  | "Data"
  | "Business Rule"
  | "Permission"
  | "Integration"
  | "Technical"
  | "External"
  | "Shared Resource"
  | "Potential Dependency";

export type DependencyStrength = "Hard" | "Soft" | "Potential";
export type DependencyConfidence = "High" | "Medium" | "Low";
export type DependencyStatus = "Confirmed" | "Inferred" | "Needs Clarification";
export type ReadinessStatus = "Ready" | "Needs Clarification" | "Blocked";

export interface DependencyRequirementItem {
  requirement_id: string;
  title: string;
  requirement_text: string;
  category: RequirementCategory;
  source_document: string | null;
  source_section: string | null;
}

export interface RequirementDependencyRequest {
  analysis_title: string;
  business_context: string;
  requirements: DependencyRequirementItem[];
  known_dependencies: string[];
  known_constraints: string[];
  additional_instructions: string | null;
}

export interface DependencyEvidence {
  source_reference: string;
  evidence_text: string;
  explanation: string;
}

export interface RequirementDependencyFinding {
  dependency_id: string;
  source_requirement_id: string;
  target_requirement_id: string;
  dependency_type: DependencyType;
  dependency_strength: DependencyStrength;
  status: DependencyStatus;
  confidence: DependencyConfidence;
  description: string;
  rationale: string;
  evidence: DependencyEvidence[];
  delivery_impact: string;
  testing_impact: string;
  blocks_target: boolean;
  missing_information: string[];
  clarification_questions: string[];
  requires_human_validation: boolean;
  suggested_owner: string;
}

export interface RequirementDependencyRelationship {
  requirement_id: string;
  depends_on_requirement_ids: string[];
  required_by_requirement_ids: string[];
  dependency_ids: string[];
  blocked: boolean;
  blocking_reasons: string[];
  standalone: boolean;
  notes: string;
}

export interface DeliveryStage {
  stage_number: number;
  stage_name: string;
  requirement_ids: string[];
  rationale: string;
}

export interface DependencySummaryEntry {
  dependency_type: DependencyType;
  count: number;
  dependency_ids: string[];
}

export interface RequirementDependencyResponse {
  analysis_summary: string;
  confirmed_information: string[];
  dependency_findings: RequirementDependencyFinding[];
  requirement_relationships: RequirementDependencyRelationship[];
  dependency_summary: DependencySummaryEntry[];
  recommended_delivery_stages: DeliveryStage[];
  blocking_requirement_ids: string[];
  circular_dependency_detected: boolean;
  circular_dependency_paths: string[];
  readiness_status: ReadinessStatus;
  assumptions: string[];
  missing_information: string[];
  risks: string[];
  recommended_next_actions: string[];
  human_validation_required: string[];
}
