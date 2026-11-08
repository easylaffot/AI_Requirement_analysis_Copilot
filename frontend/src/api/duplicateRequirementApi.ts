import axios from "axios";

import type {
  DuplicateAnalysisRequest,
  DuplicateAnalysisResponse,
} from "../types/duplicateRequirement";

export async function analyzeDuplicateRequirements(
  request: DuplicateAnalysisRequest
): Promise<DuplicateAnalysisResponse> {
  const response = await axios.post<DuplicateAnalysisResponse>(
    "/api/duplicate-requirements/analyze",
    request
  );

  return response.data;
}
