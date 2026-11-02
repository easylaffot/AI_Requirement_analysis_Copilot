import axios from "axios";

import type {
  IncidentAnalysis,
  IncidentFormData,
} from "../types/incident";

export async function analyzeIncident(
  incident: IncidentFormData
): Promise<IncidentAnalysis> {
  const response = await axios.post<IncidentAnalysis>(
    "/api/incidents/analyze",
    incident
  );

  return response.data;
}