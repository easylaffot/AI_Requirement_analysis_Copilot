export type Priority = "Critical" | "High" | "Medium" | "Low";

export type RequirementCategory =
  | "Functional"
  | "Non-Functional"
  | "Business Rule"
  | "Data"
  | "Security"
  | "Compliance"
  | "Integration"
  | "Constraint";

export interface BrdAnalysisRequest {
  brd_title: string;
  project_name: string;
  business_domain: string;
  brd_content: string;
  additional_instructions?: string | null;
}

export interface ExtractedRequirement {
  requirement_id: string;
  requirement_text: string;
  category: RequirementCategory;
  source_reference: string;
  confidence: "High" | "Medium" | "Low";
}

export interface AcceptanceCriterion {
  criterion_id: string;
  criterion: string;
}

export interface UserStory {
  story_id: string;
  title: string;
  story: string;
  acceptance_criteria: AcceptanceCriterion[];
  source_requirement_ids: string[];
  priority: Priority;
  priority_justification: string;
  dependencies: string[];
  may_require_splitting: boolean;
  splitting_reason: string | null;
}

export interface Feature {
  feature_id: string;
  name: string;
  description: string;
  source_requirement_ids: string[];
  user_stories: UserStory[];
}

export interface Epic {
  epic_id: string;
  name: string;
  business_value: string;
  source_requirement_ids: string[];
  features: Feature[];
}

export interface TraceabilityEntry {
  requirement_id: string;
  backlog_item_ids: string[];
  coverage_status: "Covered" | "Partially Covered" | "Not Covered";
  notes: string;
}

export interface BrdAnalysisResponse {
  brd_summary: string;
  business_problem: string;
  business_goals: string[];
  stakeholders_and_actors: string[];
  confirmed_scope: string[];
  extracted_requirements: ExtractedRequirement[];
  epics: Epic[];
  assumptions: string[];
  ambiguities: string[];
  missing_information: string[];
  risks: string[];
  human_validation_required: string[];
  traceability: TraceabilityEntry[];
}
