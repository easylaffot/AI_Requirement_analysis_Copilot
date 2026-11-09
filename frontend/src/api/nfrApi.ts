import { apiClient } from "./apiClient";

import type {
  NfrRecommendationRequest,
  NfrRecommendationResponse,
} from "../types/nfr";

export async function recommendNfrs(
  request: NfrRecommendationRequest
): Promise<NfrRecommendationResponse> {
  const response = await apiClient.post<NfrRecommendationResponse>(
    "/api/nfr/recommend",
    request
  );

  return response.data;
}
