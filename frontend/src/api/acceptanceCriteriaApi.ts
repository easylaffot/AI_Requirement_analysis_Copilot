import axios from "axios";

import type {
  AcceptanceCriteriaRequest,
  AcceptanceCriteriaResponse,
} from "../types/acceptanceCriteria";

export async function generateAcceptanceCriteria(
  request: AcceptanceCriteriaRequest
): Promise<AcceptanceCriteriaResponse> {
  const response = await axios.post<AcceptanceCriteriaResponse>(
    "/api/acceptance-criteria/generate",
    request
  );

  return response.data;
}
