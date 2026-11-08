import axios from "axios";

import type {
  GapAnalysisRequest,
  GapAnalysisResponse,
} from "../types/gapAnalysis";

export async function analyzeRequirementGaps(
  request: GapAnalysisRequest
): Promise<GapAnalysisResponse> {
  const response = await axios.post<GapAnalysisResponse>(
    "/api/gap-analysis/analyze",
    request
  );

  return response.data;
}
