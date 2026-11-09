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

export type CoverageStatus =
  | "Covered"
  | "Partially Covered"
  | "Not Covered"
  | "Not Applicable";

export type TraceabilityStatus = "Valid" | "Broken" | "Missing" | "Ambiguous";

export type ArtifactType =
  | "Requirement"
  | "User Story"
  | "Acceptance Criterion"
  | "Test Case";

export type RiskLevel = "High" | "Medium" | "Low";
export type ReadinessStatus = "Ready" | "Needs Traceability Work" | "Not Ready";

export interface TraceRequirementItem {
  requirement_id: string;
  title: string;
  requirement_text: string;
  category: RequirementCategory;
}

export interface TraceUserStoryItem {
  story_id: string;
  title: string;
  story_text: string;
  source_requirement_ids: string[];
}

export interface TraceAcceptanceCriterionItem {
  criterion_id: string;
  criterion_text: string;
  source_story_ids: string[];
  source_requirement_ids: string[];
}

export interface TraceTestCaseItem {
  test_case_id: string;
  title: string;
  test_description: string;
  source_criterion_ids: string[];
  source_story_ids: string[];
  source_requirement_ids: string[];
}

export interface RequirementTraceabilityRequest {
  analysis_title: string;
  business_context: string;
  requirements: TraceRequirementItem[];
  user_stories: TraceUserStoryItem[];
  acceptance_criteria: TraceAcceptanceCriterionItem[];
  test_cases: TraceTestCaseItem[];
  additional_instructions: string | null;
}

export interface TraceLink {
  link_id: string;
  source_artifact_type: ArtifactType;
  source_artifact_id: string;
  target_artifact_type: ArtifactType;
  target_artifact_id: string;
  status: TraceabilityStatus;
  explanation: string;
  supported_by_explicit_reference: boolean;
  requires_human_validation: boolean;
}

export interface RequirementCoverageEntry {
  requirement_id: string;
  coverage_status: CoverageStatus;
  story_ids: string[];
  criterion_ids: string[];
  test_case_ids: string[];
  coverage_explanation: string;
  missing_coverage: string[];
  requires_human_validation: boolean;
}

export interface OrphanArtifact {
  artifact_type: ArtifactType;
  artifact_id: string;
  reason: string;
  suggested_action: string;
  requires_human_validation: boolean;
}

export interface BrokenReference {
  source_artifact_type: ArtifactType;
  source_artifact_id: string;
  missing_target_type: ArtifactType;
  missing_target_id: string;
  impact: string;
  suggested_action: string;
}

export interface TraceabilityRisk {
  risk_id: string;
  level: RiskLevel;
  title: string;
  description: string;
  affected_artifact_ids: string[];
  mitigation: string;
  suggested_owner: string;
}

export interface CoverageSummaryEntry {
  coverage_status: CoverageStatus;
  count: number;
  requirement_ids: string[];
}

export interface RequirementTraceabilityResponse {
  analysis_summary: string;
  trace_links: TraceLink[];
  requirement_coverage: RequirementCoverageEntry[];
  orphan_artifacts: OrphanArtifact[];
  broken_references: BrokenReference[];
  coverage_summary: CoverageSummaryEntry[];
  traceability_risks: TraceabilityRisk[];
  overall_coverage_percentage: number;
  readiness_status: ReadinessStatus;
  score_explanation: string;
  assumptions: string[];
  missing_information: string[];
  recommended_next_actions: string[];
  human_validation_required: string[];
}
