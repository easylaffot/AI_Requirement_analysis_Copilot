import { apiClient } from "./apiClient";

import type {
  DuplicateAnalysisRequest,
  DuplicateAnalysisResponse,
} from "../types/duplicateRequirement";

export async function analyzeDuplicateRequirements(
  request: DuplicateAnalysisRequest
): Promise<DuplicateAnalysisResponse> {
  const response = await apiClient.post<DuplicateAnalysisResponse>(
    "/api/duplicate-requirements/analyze",
    request
  );

  return response.data;
}
