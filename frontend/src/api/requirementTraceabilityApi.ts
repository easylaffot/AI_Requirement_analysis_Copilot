import axios from "axios";

import type {
  RequirementTraceabilityRequest,
  RequirementTraceabilityResponse,
} from "../types/requirementTraceability";

export async function analyzeRequirementTraceability(
  request: RequirementTraceabilityRequest
): Promise<RequirementTraceabilityResponse> {
  const response = await axios.post<RequirementTraceabilityResponse>(
    "/api/requirement-traceability/analyze",
    request
  );
  return response.data;
}
