import axios from "axios";

import type {
  NfrRecommendationRequest,
  NfrRecommendationResponse,
} from "../types/nfr";

export async function recommendNfrs(
  request: NfrRecommendationRequest
): Promise<NfrRecommendationResponse> {
  const response = await axios.post<NfrRecommendationResponse>(
    "/api/nfr/recommend",
    request
  );

  return response.data;
}
