export type RequirementCategory =
  | "Functional"
  | "Non-Functional"
  | "Business Rule"
  | "Security"
  | "Compliance"
  | "Integration"
  | "Constraint"
  | "Unknown";

export type DuplicateClassification =
  | "Exact Duplicate"
  | "Semantic Duplicate"
  | "Near Duplicate"
  | "Partial Overlap"
  | "Related but Distinct"
  | "Not Duplicate";

export type RecommendedAction =
  | "Keep Both"
  | "Merge"
  | "Remove One After Validation"
  | "Rewrite Both"
  | "Establish Parent-Child Relationship"
  | "Clarify Before Deciding";

export type Confidence = "High" | "Medium" | "Low";

export interface RequirementItem {
  requirement_id: string;
  title: string;
  requirement_text: string;
  category: RequirementCategory;
  source_document: string | null;
  source_section: string | null;
}

export interface DuplicateAnalysisRequest {
  analysis_title: string;
  business_context: string;
  requirements: RequirementItem[];
  additional_instructions: string | null;
}

export interface RequirementDifference {
  requirement_id: string;
  unique_information: string[];
}

export interface DuplicateFinding {
  finding_id: string;
  requirement_ids: string[];
  classification: DuplicateClassification;
  confidence: Confidence;
  explanation: string;
  shared_meaning: string[];
  differences: RequirementDifference[];
  conflict_detected: boolean;
  conflict_description: string | null;
  recommended_action: RecommendedAction;
  action_rationale: string;
  consolidated_requirement: string | null;
  source_references: string[];
  requires_human_validation: boolean;
  validation_questions: string[];
}

export interface RequirementRelationship {
  requirement_id: string;
  related_requirement_ids: string[];
  covered_by_finding_ids: string[];
  standalone: boolean;
  notes: string;
}

export interface DuplicateAnalysisResponse {
  analysis_summary: string;
  findings: DuplicateFinding[];
  requirement_relationships: RequirementRelationship[];
  exact_duplicate_count: number;
  semantic_duplicate_count: number;
  partial_overlap_count: number;
  distinct_requirement_count: number;
  conflicts: string[];
  assumptions: string[];
  missing_information: string[];
  risks: string[];
  human_validation_required: string[];
}
