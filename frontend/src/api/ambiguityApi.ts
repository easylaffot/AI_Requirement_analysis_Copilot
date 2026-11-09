import { apiClient } from "./apiClient";

import type {
  AmbiguityAnalysisRequest,
  AmbiguityAnalysisResponse,
} from "../types/ambiguity";

export async function analyzeAmbiguity(
  request: AmbiguityAnalysisRequest
): Promise<AmbiguityAnalysisResponse> {
  const response = await apiClient.post<AmbiguityAnalysisResponse>(
    "/api/ambiguity/analyze",
    request
  );

  return response.data;
}
