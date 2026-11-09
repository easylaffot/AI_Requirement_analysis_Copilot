import { apiClient } from "./apiClient";

import type {
  RegulatoryImpactRequest,
  RegulatoryImpactResponse,
} from "../types/regulatoryImpact";

export async function analyzeRegulatoryImpact(
  request: RegulatoryImpactRequest
): Promise<RegulatoryImpactResponse> {
  const response = await apiClient.post<RegulatoryImpactResponse>(
    "/api/regulatory-impact/analyze",
    request
  );
  return response.data;
}
