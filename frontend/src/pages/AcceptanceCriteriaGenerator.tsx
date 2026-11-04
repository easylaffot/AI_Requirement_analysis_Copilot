import { useState } from "react";
import axios from "axios";

import { generateAcceptanceCriteria } from "../api/acceptanceCriteriaApi";
import AcceptanceCriteriaResult from "../components/AcceptanceCriteriaResult";
import type {
  AcceptanceCriteriaRequest,
  AcceptanceCriteriaResponse,
} from "../types/acceptanceCriteria";

interface FormData {
  story_id: string;
  story_title: string;
  user_story: string;
  business_context: string;
  business_rules: string;
  known_constraints: string;
  existing_acceptance_criteria: string;
  additional_instructions: string;
}

const initialFormData: FormData = {
  story_id: "",
  story_title: "",
  user_story: "",
  business_context: "",
  business_rules: "",
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

    if (!error.response) {
      return "Unable to reach the acceptance criteria service. Check that the backend is running and try again.";
    }
  }

  if (error instanceof Error && error.message) {
    return `Unable to generate acceptance criteria: ${error.message}`;
  }

  return "Unable to generate acceptance criteria. Please try again.";
}

export default function AcceptanceCriteriaGenerator() {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [result, setResult] = useState<AcceptanceCriteriaResponse | null>(null);
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

    const request: AcceptanceCriteriaRequest = {
      story_id: formData.story_id,
      story_title: formData.story_title,
      user_story: formData.user_story,
      business_context: formData.business_context,
      business_rules: linesToList(formData.business_rules),
      known_constraints: linesToList(formData.known_constraints),
      existing_acceptance_criteria: linesToList(
        formData.existing_acceptance_criteria
      ),
      additional_instructions:
        formData.additional_instructions.trim() || null,
    };

    try {
      setResult(await generateAcceptanceCriteria(request));
    } catch (requestError: unknown) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main>
      <h1>Acceptance Criteria Generator</h1>
      <p>Generate testable, traceable criteria for a user story.</p>

      <form className="acceptance-criteria-form" onSubmit={handleSubmit}>
        <div className="form-field">
          <label htmlFor="story_id">Story ID</label>
          <input
            id="story_id"
            name="story_id"
            value={formData.story_id}
            onChange={handleChange}
            minLength={2}
            maxLength={100}
            required
          />
        </div>

        <div className="form-field">
          <label htmlFor="story_title">Story title</label>
          <input
            id="story_title"
            name="story_title"
            value={formData.story_title}
            onChange={handleChange}
            minLength={3}
            maxLength={200}
            required
          />
        </div>

        <div className="form-field">
          <label htmlFor="user_story">User story</label>
          <textarea
            id="user_story"
            name="user_story"
            value={formData.user_story}
            onChange={handleChange}
            minLength={20}
            maxLength={5000}
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
          <label htmlFor="business_rules">Business rules</label>
          <textarea
            id="business_rules"
            name="business_rules"
            value={formData.business_rules}
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
            rows={4}
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
            placeholder="Enter one criterion per line"
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
          {isLoading ? "Generating Criteria..." : "Generate Criteria"}
        </button>
        {isLoading && (
          <p className="loading-state" role="status" aria-live="polite">
            Generating Criteria...
          </p>
        )}
      </form>

      {error && (
        <section className="error-message" role="alert">
          <h2>Generation failed</h2>
          <p>{error}</p>
        </section>
      )}

      {result && (
        <section className="result-container" aria-label="Generated criteria">
          <AcceptanceCriteriaResult result={result} />
        </section>
      )}
    </main>
  );
}
