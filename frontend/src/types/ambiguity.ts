export type AmbiguityCategory =
  | "Vague Term"
  | "Undefined Actor"
  | "Undefined Object"
  | "Missing Condition"
  | "Missing Boundary"
  | "Missing Quantity"
  | "Missing Timing"
  | "Optionality"
  | "Subjective Language"
  | "Unclear Reference"
  | "Compound Requirement"
  | "Conflicting Interpretation"
  | "Undefined Outcome"
  | "Undefined Error Behavior";

export type Severity = "High" | "Medium" | "Low";

export type RequirementQualityStatus =
  | "Clear"
  | "Needs Clarification"
  | "Not Ready";

export interface AmbiguityAnalysisRequest {
  requirement_id: string;
  requirement_title: string;
  requirement_text: string;
  business_context: string;
  known_actors: string[];
  known_business_rules: string[];
  additional_instructions: string | null;
}

export interface PossibleInterpretation {
  interpretation_id: string;
  interpretation: string;
  supported_by_input: boolean;
  notes: string;
}

export interface AmbiguityFinding {
  finding_id: string;
  category: AmbiguityCategory;
  ambiguous_text: string;
  explanation: string;
  severity: Severity;
  interpretation_risk: string;
  possible_interpretations: PossibleInterpretation[];
  clarification_questions: string[];
  source_reference: string;
  requires_human_validation: boolean;
  validation_owner: string;
}

export interface SuggestedRewrite {
  rewrite_id: string;
  rewritten_requirement: string;
  status: "Ready" | "Conditional" | "Cannot Rewrite Safely";
  unresolved_placeholders: string[];
  assumptions_used: string[];
  source_finding_ids: string[];
}

export interface AmbiguityAnalysisResponse {
  requirement_summary: string;
  confirmed_information: string[];
  ambiguity_findings: AmbiguityFinding[];
  overall_status: RequirementQualityStatus;
  overall_score: number;
  score_explanation: string;
  suggested_rewrites: SuggestedRewrite[];
  assumptions: string[];
  missing_information: string[];
  risks: string[];
  human_validation_required: string[];
}
