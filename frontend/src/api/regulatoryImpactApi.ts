import axios from "axios";

import type {
  RegulatoryImpactRequest,
  RegulatoryImpactResponse,
} from "../types/regulatoryImpact";

export async function analyzeRegulatoryImpact(
  request: RegulatoryImpactRequest
): Promise<RegulatoryImpactResponse> {
  const response = await axios.post<RegulatoryImpactResponse>(
    "/api/regulatory-impact/analyze",
    request
  );
  return response.data;
}
