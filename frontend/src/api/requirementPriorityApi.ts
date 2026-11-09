import axios from "axios";

import type {
  RequirementPriorityRequest,
  RequirementPriorityResponse,
} from "../types/requirementPriority";

export async function analyzeRequirementPriorities(
  request: RequirementPriorityRequest
): Promise<RequirementPriorityResponse> {
  const response = await axios.post<RequirementPriorityResponse>(
    "/api/requirement-priorities/analyze",
    request
  );
  return response.data;
}
