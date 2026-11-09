import { apiClient } from "./apiClient";

import type {
  GapAnalysisRequest,
  GapAnalysisResponse,
} from "../types/gapAnalysis";

export async function analyzeRequirementGaps(
  request: GapAnalysisRequest
): Promise<GapAnalysisResponse> {
  const response = await apiClient.post<GapAnalysisResponse>(
    "/api/gap-analysis/analyze",
    request
  );

  return response.data;
}
