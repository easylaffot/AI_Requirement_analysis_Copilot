export type RequirementType =
  | "Functional"
  | "Non-Functional"
  | "Business Rule"
  | "Data"
  | "Security"
  | "Privacy"
  | "Compliance"
  | "Integration"
  | "Constraint"
  | "Assumption"
  | "Business Goal"
  | "Scope"
  | "Unknown";

export type RequirementSubtype =
  | "User Interaction"
  | "Workflow"
  | "Validation"
  | "Calculation"
  | "Notification"
  | "Authorization"
  | "Authentication"
  | "Data Capture"
  | "Data Retrieval"
  | "Data Retention"
  | "Auditability"
  | "Performance"
  | "Availability"
  | "Reliability"
  | "Scalability"
  | "Recoverability"
  | "Accessibility"
  | "Usability"
  | "Maintainability"
  | "Observability"
  | "External Integration"
  | "Policy"
  | "Eligibility"
  | "Restriction"
  | "Business Objective"
  | "Project Boundary"
  | "Unclassified";

export type Confidence = "High" | "Medium" | "Low";

export type ClassificationStatus =
  | "Classified"
  | "Needs Clarification"
  | "Mixed Requirement";

export type RequirementQuality =
  | "Clear"
  | "Partially Clear"
  | "Ambiguous"
  | "Incomplete";

export type Priority = "Critical" | "High" | "Medium" | "Low" | "Unknown";

export interface RequirementClassificationItem {
  requirement_id: string;
  title: string;
  requirement_text: string;
  source_document: string | null;
  source_section: string | null;
}

export interface RequirementClassificationRequest {
  analysis_title: string;
  business_context: string;
  business_domain: string;
  requirements: RequirementClassificationItem[];
  additional_instructions: string | null;
}

export interface ClassificationEvidence {
  evidence_text: string;
  explanation: string;
}

export interface ClassificationLabel {
  requirement_type: RequirementType;
  requirement_subtype: RequirementSubtype;
  confidence: Confidence;
  rationale: string;
  evidence: ClassificationEvidence[];
}

export interface ClassifiedRequirement {
  requirement_id: string;
  original_title: string;
  original_text: string;
  primary_classification: ClassificationLabel;
  secondary_classifications: ClassificationLabel[];
  classification_status: ClassificationStatus;
  requirement_quality: RequirementQuality;
  quality_explanation: string;
  suggested_priority: Priority;
  priority_rationale: string;
  contains_multiple_requirements: boolean;
  splitting_recommended: boolean;
  splitting_reason: string | null;
  missing_information: string[];
  clarification_questions: string[];
  requires_human_validation: boolean;
  validation_owner: string;
}

export interface ClassificationSummaryEntry {
  requirement_type: RequirementType;
  count: number;
  requirement_ids: string[];
}

export interface RequirementClassificationResponse {
  analysis_summary: string;
  classified_requirements: ClassifiedRequirement[];
  classification_summary: ClassificationSummaryEntry[];
  mixed_requirement_ids: string[];
  unclear_requirement_ids: string[];
  assumptions: string[];
  risks: string[];
  recommended_next_actions: string[];
  human_validation_required: string[];
}
