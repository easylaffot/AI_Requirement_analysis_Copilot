export type CriterionType =
  | "Positive"
  | "Negative"
  | "Boundary"
  | "Permission"
  | "Business Rule"
  | "Failure";

export type CoverageStatus =
  | "Covered"
  | "Partially Covered"
  | "Not Covered";

export interface AcceptanceCriteriaRequest {
  story_id: string;
  story_title: string;
  user_story: string;
  business_context: string;
  business_rules: string[];
  known_constraints: string[];
  existing_acceptance_criteria: string[];
  additional_instructions?: string | null;
}

export interface GeneratedAcceptanceCriterion {
  criterion_id: string;
  criterion_type: CriterionType;
  title: string;
  given: string;
  when: string;
  then: string;
  criterion: string;
  source_references: string[];
  business_rules_applied: string[];
  testable: boolean;
  testability_reason: string;
  requires_human_validation: boolean;
  validation_reason: string | null;
}

export interface CoverageEntry {
  coverage_area: string;
  status: CoverageStatus;
  criterion_ids: string[];
  notes: string;
}

export interface AcceptanceCriteriaResponse {
  story_summary: string;
  confirmed_actor: string;
  confirmed_goal: string;
  confirmed_business_value: string;
  preconditions: string[];
  generated_criteria: GeneratedAcceptanceCriterion[];
  coverage: CoverageEntry[];
  assumptions: string[];
  ambiguities: string[];
  missing_information: string[];
  risks: string[];
  duplicate_existing_criteria: string[];
  human_validation_required: string[];
}
