import axios from "axios";

import type {
  RequirementDependencyRequest,
  RequirementDependencyResponse,
} from "../types/requirementDependency";

export async function analyzeRequirementDependencies(
  request: RequirementDependencyRequest
): Promise<RequirementDependencyResponse> {
  const response = await axios.post<RequirementDependencyResponse>(
    "/api/requirement-dependencies/analyze",
    request
  );
  return response.data;
}
