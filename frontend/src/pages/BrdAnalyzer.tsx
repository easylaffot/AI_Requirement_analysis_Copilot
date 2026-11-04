import { useState } from "react";
import axios from "axios";

import { analyzeBrd } from "../api/brdApi";
import BrdBacklogResult from "../components/BrdBacklogResult";
import type {
  BrdAnalysisRequest,
  BrdAnalysisResponse,
} from "../types/brd";

type BrdFormData = BrdAnalysisRequest;

const initialFormData: BrdFormData = {
  brd_title: "",
  project_name: "",
  business_domain: "Banking",
  brd_content: "",
  additional_instructions: "",
};

function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError<{ detail?: unknown }>(error)) {
    const responseData = error.response?.data;
    if (
      responseData &&
      typeof responseData === "object" &&
      "detail" in responseData &&
      typeof responseData.detail === "string"
    ) {
      return responseData.detail;
    }

    if (!error.response) {
      return "Unable to reach the BRD analysis service. Check that the backend is running and try again.";
    }
  }

  if (error instanceof Error && error.message) {
    return `Unable to analyze the BRD: ${error.message}`;
  }

  return "Unable to analyze the BRD. Please try again.";
}

export default function BrdAnalyzer() {
  const [formData, setFormData] = useState<BrdFormData>(initialFormData);
  const [result, setResult] = useState<BrdAnalysisResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  function handleChange(
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) {
    const { name, value } = event.target;

    setFormData((currentData) => ({
      ...currentData,
      [name]: value,
    }));
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setResult(null);
    setError("");
    setIsLoading(true);

    try {
      const analysis = await analyzeBrd(formData);
      setResult(analysis);
    } catch (requestError: unknown) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main>
      <h1>BRD to Agile Backlog Generator</h1>
      <p>
        Provide a business requirements document to create a structured,
        traceable draft backlog.
      </p>

      <form className="brd-form" onSubmit={handleSubmit}>
        <div className="form-field">
          <label htmlFor="brd_title">BRD title</label>
          <input
            id="brd_title"
            name="brd_title"
            value={formData.brd_title}
            onChange={handleChange}
            minLength={3}
            maxLength={200}
            required
          />
        </div>

        <div className="form-field">
          <label htmlFor="project_name">Project name</label>
          <input
            id="project_name"
            name="project_name"
            value={formData.project_name}
            onChange={handleChange}
            minLength={3}
            maxLength={200}
            required
          />
        </div>

        <div className="form-field">
          <label htmlFor="business_domain">Business domain</label>
          <input
            id="business_domain"
            name="business_domain"
            value={formData.business_domain}
            onChange={handleChange}
            minLength={2}
            maxLength={100}
            required
          />
        </div>

        <div className="form-field">
          <label htmlFor="brd_content">BRD content</label>
          <textarea
            id="brd_content"
            name="brd_content"
            value={formData.brd_content}
            onChange={handleChange}
            rows={12}
            minLength={100}
            required
          />
          <span className="field-hint">
            Enter at least 100 characters. {formData.brd_content.length}{" "}
            characters entered.
          </span>
        </div>

        <div className="form-field">
          <label htmlFor="additional_instructions">
            Additional instructions
          </label>
          <textarea
            id="additional_instructions"
            name="additional_instructions"
            value={formData.additional_instructions ?? ""}
            onChange={handleChange}
            rows={4}
            maxLength={1000}
          />
        </div>

        <button type="submit" disabled={isLoading}>
          {isLoading ? "Analyzing BRD..." : "Analyze BRD"}
        </button>
        {isLoading && (
          <p className="loading-state" role="status" aria-live="polite">
            Analyzing BRD...
          </p>
        )}
      </form>

      {error && (
        <section className="error-message" role="alert">
          <h2>Analysis failed</h2>
          <p>{error}</p>
        </section>
      )}

      {result && (
        <section className="result-container" aria-label="BRD analysis results">
          <BrdBacklogResult result={result} />
        </section>
      )}
    </main>
  );
}
