export type Priority = "Critical" | "High" | "Medium" | "Low";

export type CriterionType =
  | "Positive"
  | "Negative"
  | "Boundary"
  | "Business Rule";

export interface UserStoryGenerationRequest {
  requirement_title: string;
  requirement_text: string;
  business_context: string;
  known_actors: string[];
  business_rules: string[];
  additional_instructions?: string | null;
}

export interface AcceptanceCriterion {
  criterion_id: string;
  criterion: string;
  criterion_type: CriterionType;
}

export interface InvestAssessment {
  independent: boolean;
  independent_reason: string;
  negotiable: boolean;
  negotiable_reason: string;
  valuable: boolean;
  valuable_reason: string;
  estimable: boolean;
  estimable_reason: string;
  small: boolean;
  small_reason: string;
  testable: boolean;
  testable_reason: string;
}

export interface GeneratedUserStory {
  story_id: string;
  title: string;
  actor: string;
  goal: string;
  business_value: string;
  story: string;
  acceptance_criteria: AcceptanceCriterion[];
  source_requirement_references: string[];
  business_rules_applied: string[];
  dependencies: string[];
  priority: Priority;
  priority_justification: string;
  invest_assessment: InvestAssessment;
  may_require_further_splitting: boolean;
  splitting_reason: string | null;
}

export interface UserStoryGenerationResponse {
  requirement_summary: string;
  confirmed_actors: string[];
  identified_user_goals: string[];
  generated_stories: GeneratedUserStory[];
  splitting_summary: string;
  assumptions: string[];
  ambiguities: string[];
  missing_information: string[];
  risks: string[];
  human_validation_required: string[];
}
