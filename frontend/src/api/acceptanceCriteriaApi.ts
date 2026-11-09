import { apiClient } from "./apiClient";

import type {
  AcceptanceCriteriaRequest,
  AcceptanceCriteriaResponse,
} from "../types/acceptanceCriteria";

export async function generateAcceptanceCriteria(
  request: AcceptanceCriteriaRequest
): Promise<AcceptanceCriteriaResponse> {
  const response = await apiClient.post<AcceptanceCriteriaResponse>(
    "/api/acceptance-criteria/generate",
    request
  );

  return response.data;
}
