import axios from "axios";

import type {
  RequirementClassificationRequest,
  RequirementClassificationResponse,
} from "../types/requirementClassifier";

export async function classifyRequirements(
  request: RequirementClassificationRequest
): Promise<RequirementClassificationResponse> {
  const response = await axios.post<RequirementClassificationResponse>(
    "/api/requirement-classifier/classify",
    request
  );
  return response.data;
}
