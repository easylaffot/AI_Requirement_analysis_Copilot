import { apiClient } from "./apiClient";

import type {
  RequirementRiskRequest,
  RequirementRiskResponse,
} from "../types/requirementRisk";

export async function analyzeRequirementRisks(
  request: RequirementRiskRequest
): Promise<RequirementRiskResponse> {
  const response = await apiClient.post<RequirementRiskResponse>(
    "/api/requirement-risks/analyze",
    request
  );
  return response.data;
}
