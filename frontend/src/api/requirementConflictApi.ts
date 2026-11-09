import { apiClient } from "./apiClient";

import type {
  ConflictAnalysisRequest,
  ConflictAnalysisResponse,
} from "../types/requirementConflict";

export async function analyzeRequirementConflicts(
  request: ConflictAnalysisRequest
): Promise<ConflictAnalysisResponse> {
  const response = await apiClient.post<ConflictAnalysisResponse>(
    "/api/requirement-conflicts/analyze",
    request
  );
  return response.data;
}
