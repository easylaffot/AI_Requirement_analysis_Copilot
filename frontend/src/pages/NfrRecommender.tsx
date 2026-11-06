import { useState } from "react";
import axios from "axios";

import { recommendNfrs } from "../api/nfrApi";
import NfrResult from "../components/NfrResult";
import type {
  Criticality,
  DataSensitivity,
  NfrRecommendationRequest,
  NfrRecommendationResponse,
} from "../types/nfr";

interface FormData {
  requirement_id: string;
  requirement_title: string;
  requirement_text: string;
  business_context: string;
  business_domain: string;
  data_sensitivity: DataSensitivity;
  criticality: Criticality;
  known_constraints: string;
  existing_nfrs: string;
  additional_instructions: string;
}

const initialFormData: FormData = {
  requirement_id: "",
  requirement_title: "",
  requirement_text: "",
  business_context: "",
  business_domain: "",
  data_sensitivity: "Unknown",
  criticality: "Unknown",
  known_constraints: "",
  existing_nfrs: "",
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
      return "Unable to reach the NFR recommendation service. Check that the backend is running and try again.";
    }
  }

  if (error instanceof Error && error.message) {
    return `Unable to generate NFR recommendations: ${error.message}`;
  }

  return "Unable to generate NFR recommendations. Please try again.";
}

export default function NfrRecommender() {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [result, setResult] = useState<NfrRecommendationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  function handleChange(
    event: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) {
    const { name, value } = event.target;
    setFormData((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setResult(null);
    setError("");
    setIsLoading(true);

    const request: NfrRecommendationRequest = {
      requirement_id: formData.requirement_id,
      requirement_title: formData.requirement_title,
      requirement_text: formData.requirement_text,
      business_context: formData.business_context,
      business_domain: formData.business_domain,
      data_sensitivity: formData.data_sensitivity,
      criticality: formData.criticality,
      known_constraints: linesToList(formData.known_constraints),
      existing_nfrs: linesToList(formData.existing_nfrs),
      additional_instructions:
        formData.additional_instructions.trim() || null,
    };

    try {
      setResult(await recommendNfrs(request));
    } catch (requestError: unknown) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main>
      <h1>NFR Recommender</h1>
      <p>
        Analyze a functional requirement and create traceable, measurable
        non-functional requirement recommendations.
      </p>

      <form className="nfr-form" onSubmit={handleSubmit}>
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
          <label htmlFor="data_sensitivity">Data sensitivity</label>
          <select
            id="data_sensitivity"
            name="data_sensitivity"
            value={formData.data_sensitivity}
            onChange={handleChange}
          >
            <option>Public</option>
            <option>Internal</option>
            <option>Confidential</option>
            <option>Restricted</option>
            <option>Unknown</option>
          </select>
        </div>

        <div className="form-field">
          <label htmlFor="criticality">Criticality</label>
          <select
            id="criticality"
            name="criticality"
            value={formData.criticality}
            onChange={handleChange}
          >
            <option>Critical</option>
            <option>High</option>
            <option>Medium</option>
            <option>Low</option>
            <option>Unknown</option>
          </select>
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
          <label htmlFor="existing_nfrs">Existing NFRs</label>
          <textarea
            id="existing_nfrs"
            name="existing_nfrs"
            value={formData.existing_nfrs}
            onChange={handleChange}
            rows={4}
            placeholder="Enter one existing NFR per line"
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
          {isLoading ? "Generating NFR Recommendations..." : "Recommend NFRs"}
        </button>
        {isLoading && (
          <p className="loading-state" role="status" aria-live="polite">
            Generating NFR Recommendations...
          </p>
        )}
      </form>

      {error && (
        <section className="error-message" role="alert">
          <h2>Recommendation failed</h2>
          <p>{error}</p>
        </section>
      )}

      {result && (
        <section className="result-container" aria-label="NFR recommendations">
          <NfrResult result={result} />
        </section>
      )}
    </main>
  );
}
