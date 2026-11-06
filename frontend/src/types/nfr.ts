export type NfrCategory =
  | "Security"
  | "Performance"
  | "Availability"
  | "Reliability"
  | "Scalability"
  | "Privacy"
  | "Auditability"
  | "Accessibility"
  | "Usability"
  | "Maintainability"
  | "Observability"
  | "Recoverability"
  | "Compatibility"
  | "Compliance";

export type DataSensitivity =
  | "Public"
  | "Internal"
  | "Confidential"
  | "Restricted"
  | "Unknown";

export type Criticality = "Critical" | "High" | "Medium" | "Low" | "Unknown";

export type RecommendationStatus =
  | "Ready"
  | "Needs Target"
  | "Needs Clarification";

export interface NfrRecommendationRequest {
  requirement_id: string;
  requirement_title: string;
  requirement_text: string;
  business_context: string;
  business_domain: string;
  data_sensitivity?: DataSensitivity;
  criticality?: Criticality;
  known_constraints?: string[];
  existing_nfrs?: string[];
  additional_instructions?: string | null;
}

export interface RecommendedNfr {
  nfr_id: string;
  category: NfrCategory;
  title: string;
  requirement: string;
  rationale: string;
  source_references: string[];
  measurable: boolean;
  measurement_method: string;
  status: RecommendationStatus;
  missing_target: string | null;
  assumptions: string[];
  requires_human_validation: boolean;
  validation_reason: string | null;
}

export interface NfrCategoryAssessment {
  category: NfrCategory;
  relevant: boolean;
  rationale: string;
  recommendation_ids: string[];
}

export interface NfrRecommendationResponse {
  requirement_summary: string;
  relevant_categories: NfrCategoryAssessment[];
  recommendations: RecommendedNfr[];
  existing_nfr_coverage: string[];
  duplicate_existing_nfrs: string[];
  assumptions: string[];
  ambiguities: string[];
  missing_information: string[];
  risks: string[];
  human_validation_required: string[];
}
