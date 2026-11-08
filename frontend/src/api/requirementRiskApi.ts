import axios from "axios";

import type {
  RequirementRiskRequest,
  RequirementRiskResponse,
} from "../types/requirementRisk";

export async function analyzeRequirementRisks(
  request: RequirementRiskRequest
): Promise<RequirementRiskResponse> {
  const response = await axios.post<RequirementRiskResponse>(
    "/api/requirement-risks/analyze",
    request
  );
  return response.data;
}
