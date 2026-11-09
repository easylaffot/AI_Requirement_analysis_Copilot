import { apiClient } from "./apiClient";

import type {
  RequirementDependencyRequest,
  RequirementDependencyResponse,
} from "../types/requirementDependency";

export async function analyzeRequirementDependencies(
  request: RequirementDependencyRequest
): Promise<RequirementDependencyResponse> {
  const response = await apiClient.post<RequirementDependencyResponse>(
    "/api/requirement-dependencies/analyze",
    request
  );
  return response.data;
}
