import { useState } from "react";
import axios from "axios";

import { generateUserStories } from "../api/userStoryApi";
import UserStoryResult from "../components/UserStoryResult";
import type {
  UserStoryGenerationRequest,
  UserStoryGenerationResponse,
} from "../types/userStory";

interface UserStoryFormData {
  requirement_title: string;
  requirement_text: string;
  business_context: string;
  known_actors: string;
  business_rules: string;
  additional_instructions: string;
}

const initialFormData: UserStoryFormData = {
  requirement_title: "",
  requirement_text: "",
  business_context: "",
  known_actors: "",
  business_rules: "",
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
      return "Unable to reach the user story generation service. Check that the backend is running and try again.";
    }
  }

  if (error instanceof Error && error.message) {
    return `Unable to generate user stories: ${error.message}`;
  }

  return "Unable to generate user stories. Please try again.";
}

function linesToList(value: string): string[] {
  return value
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0);
}

export default function UserStoryGenerator() {
  const [formData, setFormData] =
    useState<UserStoryFormData>(initialFormData);
  const [result, setResult] =
    useState<UserStoryGenerationResponse | null>(null);
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

    const request: UserStoryGenerationRequest = {
      requirement_title: formData.requirement_title,
      requirement_text: formData.requirement_text,
      business_context: formData.business_context,
      known_actors: linesToList(formData.known_actors),
      business_rules: linesToList(formData.business_rules),
      additional_instructions:
        formData.additional_instructions.trim() || null,
    };

    try {
      const generatedStories = await generateUserStories(request);
      setResult(generatedStories);
    } catch (requestError: unknown) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main>
      <h1>User Story Generator</h1>
      <p>
        Turn a requirement and its business context into structured user
        stories with acceptance criteria and an INVEST assessment.
      </p>

      <form className="user-story-form" onSubmit={handleSubmit}>
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
            rows={6}
            minLength={20}
            maxLength={10000}
            required
          />
          <span className="field-hint">
            At least 20 characters. {formData.requirement_text.length} entered.
          </span>
        </div>

        <div className="form-field">
          <label htmlFor="business_context">Business context</label>
          <textarea
            id="business_context"
            name="business_context"
            value={formData.business_context}
            onChange={handleChange}
            rows={5}
            minLength={10}
            maxLength={5000}
            required
          />
          <span className="field-hint">
            At least 10 characters. {formData.business_context.length} entered.
          </span>
        </div>

        <div className="form-field">
          <label htmlFor="known_actors">Known actors</label>
          <textarea
            id="known_actors"
            name="known_actors"
            value={formData.known_actors}
            onChange={handleChange}
            rows={4}
            placeholder={"Enter one actor per line"}
          />
          <span className="field-hint">Enter one actor per line.</span>
        </div>

        <div className="form-field">
          <label htmlFor="business_rules">Business rules</label>
          <textarea
            id="business_rules"
            name="business_rules"
            value={formData.business_rules}
            onChange={handleChange}
            rows={4}
            placeholder={"Enter one business rule per line"}
          />
          <span className="field-hint">Enter one business rule per line.</span>
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
            rows={4}
            maxLength={1000}
          />
        </div>

        <button type="submit" disabled={isLoading}>
          {isLoading ? "Generating Stories..." : "Generate User Stories"}
        </button>
        {isLoading && (
          <p className="loading-state" role="status" aria-live="polite">
            Generating Stories...
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
        <section
          className="result-container"
          aria-label="User story generation results"
        >
          <UserStoryResult result={result} />
        </section>
      )}
    </main>
  );
}
