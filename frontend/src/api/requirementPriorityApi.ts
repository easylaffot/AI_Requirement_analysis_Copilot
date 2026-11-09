import { apiClient } from "./apiClient";

import type {
  RequirementPriorityRequest,
  RequirementPriorityResponse,
} from "../types/requirementPriority";

export async function analyzeRequirementPriorities(
  request: RequirementPriorityRequest
): Promise<RequirementPriorityResponse> {
  const response = await apiClient.post<RequirementPriorityResponse>(
    "/api/requirement-priorities/analyze",
    request
  );
  return response.data;
}
