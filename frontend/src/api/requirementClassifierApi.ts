import { apiClient } from "./apiClient";

import type {
  RequirementClassificationRequest,
  RequirementClassificationResponse,
} from "../types/requirementClassifier";

export async function classifyRequirements(
  request: RequirementClassificationRequest
): Promise<RequirementClassificationResponse> {
  const response = await apiClient.post<RequirementClassificationResponse>(
    "/api/requirement-classifier/classify",
    request
  );
  return response.data;
}
