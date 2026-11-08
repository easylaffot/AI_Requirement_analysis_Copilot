export type RequirementCategory =
  | "Functional"
  | "Non-Functional"
  | "Business Rule"
  | "Security"
  | "Compliance"
  | "Integration"
  | "Constraint"
  | "Unknown";

export type ConflictType =
  | "Direct Contradiction"
  | "Permission Conflict"
  | "Boundary Conflict"
  | "Timing Conflict"
  | "Workflow Conflict"
  | "Data Conflict"
  | "Channel Conflict"
  | "Priority Conflict"
  | "Scope Conflict"
  | "Terminology Conflict"
  | "Potential Conflict";

export type ConflictSeverity = "Critical" | "High" | "Medium" | "Low";

export type ResolutionStatus =
  | "Requires Decision"
  | "Requires Clarification"
  | "Can Coexist"
  | "No Conflict";

export type RecommendedAction =
  | "Select One Requirement"
  | "Rewrite Conflicting Requirements"
  | "Define Conditional Rules"
  | "Define Source Authority"
  | "Split Scope"
  | "Clarify Terminology"
  | "Keep Both"
  | "No Action";

export interface ConflictRequirementItem {
  requirement_id: string;
  title: string;
  requirement_text: string;
  category: RequirementCategory;
  source_document: string | null;
  source_section: string | null;
  source_authority: string | null;
}

export interface ConflictAnalysisRequest {
  analysis_title: string;
  business_context: string;
  requirements: ConflictRequirementItem[];
  known_business_rules: string[];
  additional_instructions: string | null;
}

export interface ConflictDifference {
  comparison_area: string;
  requirement_values: RequirementValue[];
  conflict_reason: string;
}

export interface RequirementValue {
  requirement_id: string;
  value: string;
}

export interface ConflictFinding {
  conflict_id: string;
  requirement_ids: string[];
  conflict_type: ConflictType;
  severity: ConflictSeverity;
  summary: string;
  explanation: string;
  conflicting_statements: RequirementValue[];
  differences: ConflictDifference[];
  business_impact: string;
  implementation_impact: string;
  testing_impact: string;
  resolution_status: ResolutionStatus;
  recommended_action: RecommendedAction;
  action_rationale: string;
  clarification_questions: string[];
  source_references: string[];
  requires_human_validation: boolean;
  suggested_owner: string;
}

export interface RequirementConflictRelationship {
  requirement_id: string;
  conflicting_requirement_ids: string[];
  conflict_ids: string[];
  conflict_free: boolean;
  notes: string;
}

export interface ConflictAnalysisResponse {
  analysis_summary: string;
  confirmed_information: string[];
  conflict_findings: ConflictFinding[];
  requirement_relationships: RequirementConflictRelationship[];
  critical_conflict_count: number;
  high_conflict_count: number;
  medium_conflict_count: number;
  low_conflict_count: number;
  conflict_free_requirement_count: number;
  unresolved_decisions: string[];
  assumptions: string[];
  missing_information: string[];
  risks: string[];
  recommended_next_actions: string[];
  human_validation_required: string[];
}
