import axios from "axios";

import type {
  BrdAnalysisRequest,
  BrdAnalysisResponse,
} from "../types/brd";

export async function analyzeBrd(
  request: BrdAnalysisRequest
): Promise<BrdAnalysisResponse> {
  const response = await axios.post<BrdAnalysisResponse>(
    "/api/brd/analyze",
    request
  );

  return response.data;
}
