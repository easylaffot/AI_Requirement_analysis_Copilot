import axios from "axios";

import type {
  ConflictAnalysisRequest,
  ConflictAnalysisResponse,
} from "../types/requirementConflict";

export async function analyzeRequirementConflicts(
  request: ConflictAnalysisRequest
): Promise<ConflictAnalysisResponse> {
  const response = await axios.post<ConflictAnalysisResponse>(
    "/api/requirement-conflicts/analyze",
    request
  );
  return response.data;
}
