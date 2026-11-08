import { useState } from "react";
import axios from "axios";

import { analyzeRequirementGaps } from "../api/gapAnalysisApi";
import GapAnalysisResult from "../components/GapAnalysisResult";
import type {
  GapAnalysisRequest,
  GapAnalysisResponse,
} from "../types/gapAnalysis";

interface FormData {
  requirement_id: string;
  requirement_title: string;
  requirement_text: string;
  business_context: string;
  known_actors: string;
  known_business_rules: string;
  known_constraints: string;
  existing_acceptance_criteria: string;
  additional_instructions: string;
}

const initialFormData: FormData = {
  requirement_id: "",
  requirement_title: "",
  requirement_text: "",
  business_context: "",
  known_actors: "",
  known_business_rules: "",
  known_constraints: "",
  existing_acceptance_criteria: "",
  additional_instructions: "",
};

function linesToList(value: string): string[] {
  return value
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0);
}

function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError<{ detail?: unknown }>(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") {
      return detail;
    }

    if (Array.isArray(detail)) {
      const messages = detail
        .map((item) => {
          if (
            typeof item === "object" &&
            item !== null &&
            "msg" in item &&
            typeof item.msg === "string"
          ) {
            return item.msg;
          }
          return null;
        })
        .filter((message): message is string => message !== null);
      if (messages.length > 0) {
        return messages.join(" ");
      }
    }

    if (!error.response) {
      return "Unable to reach the requirement gap analysis service. Check that the backend is running and try again.";
    }
  }

  if (error instanceof Error && error.message) {
    return `Unable to analyze requirement gaps: ${error.message}`;
  }

  return "Unable to analyze requirement gaps. Please try again.";
}

export default function GapAnalyzer() {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [result, setResult] = useState<GapAnalysisResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  function handleChange(
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) {
    const { name, value } = event.target;
    setFormData((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setResult(null);
    setError("");
    setIsLoading(true);

    const request: GapAnalysisRequest = {
      requirement_id: formData.requirement_id,
      requirement_title: formData.requirement_title,
      requirement_text: formData.requirement_text,
      business_context: formData.business_context,
      known_actors: linesToList(formData.known_actors),
      known_business_rules: linesToList(formData.known_business_rules),
      known_constraints: linesToList(formData.known_constraints),
      existing_acceptance_criteria: linesToList(
        formData.existing_acceptance_criteria
      ),
      additional_instructions: formData.additional_instructions.trim() || null,
    };

    try {
      setResult(await analyzeRequirementGaps(request));
    } catch (requestError: unknown) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main>
      <h1>Requirement Gap Analyzer</h1>
      <p>
        Assess requirement completeness, identify delivery and testing gaps,
        and review readiness.
      </p>

      <form className="gap-analysis-form" onSubmit={handleSubmit}>
        <div className="form-field">
          <label htmlFor="requirement_id">Requirement ID</label>
          <input
            id="requirement_id"
            name="requirement_id"
            value={formData.requirement_id}
            onChange={handleChange}
            minLength={2}
            maxLength={100}
            required
          />
        </div>

        <div className="form-field">
          <label htmlFor="requirement_title">Requirement title</label>
          <input
            id="requirement_title"
            name="requirement_title"
            value={formData.requirement_title}
            onChange={handleChange}
            minLength={3}
            maxLength={200}
            required
          />
        </div>

        <div className="form-field">
          <label htmlFor="requirement_text">Requirement text</label>
          <textarea
            id="requirement_text"
            name="requirement_text"
            value={formData.requirement_text}
            onChange={handleChange}
            minLength={20}
            maxLength={15000}
            rows={5}
            required
          />
        </div>

        <div className="form-field">
          <label htmlFor="business_context">Business context</label>
          <textarea
            id="business_context"
            name="business_context"
            value={formData.business_context}
            onChange={handleChange}
            minLength={10}
            maxLength={5000}
            rows={4}
            required
          />
        </div>

        <div className="form-field">
          <label htmlFor="known_actors">Known actors</label>
          <textarea
            id="known_actors"
            name="known_actors"
            value={formData.known_actors}
            onChange={handleChange}
            rows={3}
            placeholder="Enter one actor per line"
          />
        </div>

        <div className="form-field">
          <label htmlFor="known_business_rules">Known business rules</label>
          <textarea
            id="known_business_rules"
            name="known_business_rules"
            value={formData.known_business_rules}
            onChange={handleChange}
            rows={4}
            placeholder="Enter one business rule per line"
          />
        </div>

        <div className="form-field">
          <label htmlFor="known_constraints">Known constraints</label>
          <textarea
            id="known_constraints"
            name="known_constraints"
            value={formData.known_constraints}
            onChange={handleChange}
            rows={3}
            placeholder="Enter one constraint per line"
          />
        </div>

        <div className="form-field">
          <label htmlFor="existing_acceptance_criteria">
            Existing acceptance criteria
          </label>
          <textarea
            id="existing_acceptance_criteria"
            name="existing_acceptance_criteria"
            value={formData.existing_acceptance_criteria}
            onChange={handleChange}
            rows={4}
            placeholder="Enter one acceptance criterion per line"
          />
        </div>

        <div className="form-field">
          <label htmlFor="additional_instructions">
            Additional instructions
          </label>
          <textarea
            id="additional_instructions"
            name="additional_instructions"
            value={formData.additional_instructions}
            onChange={handleChange}
            maxLength={1000}
            rows={3}
          />
        </div>

        <button type="submit" disabled={isLoading}>
          {isLoading ? "Analyzing Requirement Gaps..." : "Analyze Gaps"}
        </button>
        {isLoading && (
          <p className="loading-state" role="status" aria-live="polite">
            Analyzing Requirement Gaps...
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
        <section
          className="result-container"
          aria-label="Requirement gap analysis results"
        >
          <GapAnalysisResult result={result} />
        </section>
      )}
    </main>
  );
}
