import { useState } from "react";

import { analyzeIncident } from "./api/incidentApi";
import type {
  IncidentAnalysis,
  IncidentFormData,
} from "./types/incident";

const initialFormData: IncidentFormData = {
  incident_id: "",
  application: "",
  severity: "High",
  description: "",
  impact: "",
  logs: "",
};

function App() {
  const [formData, setFormData] =
    useState<IncidentFormData>(initialFormData);

  const [result, setResult] =
    useState<IncidentAnalysis | null>(null);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  function handleChange(
    event: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) {
    const { name, value } = event.target;

    setFormData((currentData) => ({
      ...currentData,
      [name]: value,
    }));
  }

  async function handleSubmit(
    event: React.FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    setError("");
    setResult(null);
    setIsLoading(true);

    try {
      const analysis = await analyzeIncident(formData);
      setResult(analysis);
    } catch (requestError) {
      console.error("Incident analysis failed:", requestError);

      setError(
        "Unable to analyze the incident. Check whether the FastAPI backend is running on port 8000."
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main>
      <h1>Requirement Analysis Copilot</h1>
      <h2>Production Incident Requirement Analyzer</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="incident_id">Incident ID</label>
          <br />

          <input
            id="incident_id"
            name="incident_id"
            value={formData.incident_id}
            onChange={handleChange}
            placeholder="INC-1001"
            required
          />
        </div>

        <br />

        <div>
          <label htmlFor="application">Application</label>
          <br />

          <input
            id="application"
            name="application"
            value={formData.application}
            onChange={handleChange}
            placeholder="Mobile Banking"
            required
          />
        </div>

        <br />

        <div>
          <label htmlFor="severity">Severity</label>
          <br />

          <select
            id="severity"
            name="severity"
            value={formData.severity}
            onChange={handleChange}
          >
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </div>

        <br />

        <div>
          <label htmlFor="description">Incident Description</label>
          <br />

          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Describe what happened in production"
            rows={5}
            cols={60}
            required
          />
        </div>

        <br />

        <div>
          <label htmlFor="impact">Business Impact</label>
          <br />

          <textarea
            id="impact"
            name="impact"
            value={formData.impact}
            onChange={handleChange}
            placeholder="Describe customer, financial or operational impact"
            rows={4}
            cols={60}
            required
          />
        </div>

        <br />

        <div>
          <label htmlFor="logs">Relevant Logs</label>
          <br />

          <textarea
            id="logs"
            name="logs"
            value={formData.logs}
            onChange={handleChange}
            placeholder="Paste relevant application logs"
            rows={4}
            cols={60}
          />
        </div>

        <br />

        <button type="submit" disabled={isLoading}>
          {isLoading ? "Analyzing..." : "Analyze Incident"}
        </button>
      </form>

      {error && (
        <section>
          <h2>Error</h2>
          <p>{error}</p>
        </section>
      )}

      {result && (
        <section>
          <hr />

          <h2>Requirement Analysis Result</h2>

          <h3>Incident Summary</h3>
          <p>{result.incident_summary}</p>

          <h3>Business Impact</h3>
          <p>{result.business_impact}</p>

          <h3>Root-Cause Hypothesis</h3>
          <p>{result.root_cause_hypothesis}</p>

          <h3>Functional Requirements</h3>
          <ul>
            {result.functional_requirements.map(
              (requirement, index) => (
                <li key={`${index}-${requirement}`}>
                  {requirement}
                </li>
              )
            )}
          </ul>

          <h3>User Story</h3>
          <p>{result.user_story}</p>

          <h3>Acceptance Criteria</h3>
          <ul>
            {result.acceptance_criteria.map(
              (criterion, index) => (
                <li key={`${index}-${criterion}`}>
                  {criterion}
                </li>
              )
            )}
          </ul>

          <h3>Risks</h3>
          <ul>
            {result.risks.map((risk, index) => (
              <li key={`${index}-${risk}`}>{risk}</li>
            ))}
          </ul>

          <h3>Recommended Priority</h3>
          <p>{result.priority}</p>
        </section>
      )}
    </main>
  );
}

export default App;