import { useState } from "react";
import axios from "axios";

import { analyzeAmbiguity } from "../api/ambiguityApi";
import AmbiguityResult from "../components/AmbiguityResult";
import type {
  AmbiguityAnalysisRequest,
  AmbiguityAnalysisResponse,
} from "../types/ambiguity";

interface FormData {
  requirement_id: string;
  requirement_title: string;
  requirement_text: string;
  business_context: string;
  known_actors: string;
  known_business_rules: string;
  additional_instructions: string;
}

const initialFormData: FormData = {
  requirement_id: "",
  requirement_title: "",
  requirement_text: "",
  business_context: "",
  known_actors: "",
  known_business_rules: "",
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
      return "Unable to reach the ambiguity analysis service. Check that the backend is running and try again.";
    }
  }

  if (error instanceof Error && error.message) {
    return `Unable to analyze ambiguity: ${error.message}`;
  }

  return "Unable to analyze ambiguity. Please try again.";
}

export default function AmbiguityDetector() {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [result, setResult] = useState<AmbiguityAnalysisResponse | null>(null);
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

    const request: AmbiguityAnalysisRequest = {
      requirement_id: formData.requirement_id,
      requirement_title: formData.requirement_title,
      requirement_text: formData.requirement_text,
      business_context: formData.business_context,
      known_actors: linesToList(formData.known_actors),
      known_business_rules: linesToList(formData.known_business_rules),
      additional_instructions: formData.additional_instructions.trim() || null,
    };

    try {
      setResult(await analyzeAmbiguity(request));
    } catch (requestError: unknown) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main>
      <h1>Ambiguity Detector</h1>
      <p>
        Identify unclear requirement language, evaluate interpretation risks,
        and review safe rewrite suggestions.
      </p>

      <form className="ambiguity-form" onSubmit={handleSubmit}>
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
            minLength={10}
            maxLength={10000}
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
          {isLoading ? "Analyzing Ambiguity..." : "Analyze Ambiguity"}
        </button>
        {isLoading && (
          <p className="loading-state" role="status" aria-live="polite">
            Analyzing Ambiguity...
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
          aria-label="Ambiguity analysis results"
        >
          <AmbiguityResult result={result} />
        </section>
      )}
    </main>
  );
}
