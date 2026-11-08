import axios from "axios";

import type {
  AmbiguityAnalysisRequest,
  AmbiguityAnalysisResponse,
} from "../types/ambiguity";

export async function analyzeAmbiguity(
  request: AmbiguityAnalysisRequest
): Promise<AmbiguityAnalysisResponse> {
  const response = await axios.post<AmbiguityAnalysisResponse>(
    "/api/ambiguity/analyze",
    request
  );

  return response.data;
}
