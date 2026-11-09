import { useState } from "react";
import { axios } from "../api/apiClient";

import { classifyRequirements } from "../api/requirementClassifierApi";
import RequirementClassifierResult from "../components/RequirementClassifierResult";
import type {
  RequirementClassificationRequest,
  RequirementClassificationResponse,
} from "../types/requirementClassifier";

interface RequirementForm {
  key: number;
  requirement_id: string;
  title: string;
  requirement_text: string;
  source_document: string;
  source_section: string;
}

interface FormData {
  analysis_title: string;
  business_context: string;
  business_domain: string;
  additional_instructions: string;
}

const initialFormData: FormData = {
  analysis_title: "",
  business_context: "",
  business_domain: "",
  additional_instructions: "",
};

function createRequirement(key: number): RequirementForm {
  return {
    key,
    requirement_id: "",
    title: "",
    requirement_text: "",
    source_document: "",
    source_section: "",
  };
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
      return "Unable to reach the requirement classification service. Check that the backend is running and try again.";
    }
  }

  if (error instanceof Error && error.message) {
    return `Unable to classify requirements: ${error.message}`;
  }

  return "Unable to classify requirements. Please try again.";
}

function getValidationError(
  formData: FormData,
  requirements: RequirementForm[]
): string {
  if (formData.analysis_title.trim().length < 3) {
    return "Analysis title must be at least 3 characters.";
  }
  if (formData.business_context.trim().length < 10) {
    return "Business context must be at least 10 characters.";
  }
  if (formData.business_domain.trim().length < 2) {
    return "Business domain must be at least 2 characters.";
  }
  if (requirements.length < 1) {
    return "Add at least one requirement.";
  }

  for (const [index, requirement] of requirements.entries()) {
    if (requirement.requirement_id.trim().length < 2) {
      return `Requirement ${index + 1} ID must be at least 2 characters.`;
    }
    if (requirement.title.trim().length < 3) {
      return `Requirement ${index + 1} title must be at least 3 characters.`;
    }
    if (requirement.requirement_text.trim().length < 10) {
      return `Requirement ${index + 1} text must be at least 10 characters.`;
    }
  }

  const normalizedIds = requirements.map((requirement) =>
    requirement.requirement_id.trim().toLocaleLowerCase()
  );
  if (new Set(normalizedIds).size !== normalizedIds.length) {
    return "Requirement IDs must be unique.";
  }

  return "";
}

export default function RequirementClassifier() {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [requirements, setRequirements] = useState<RequirementForm[]>([
    createRequirement(1),
  ]);
  const [nextRequirementKey, setNextRequirementKey] = useState(2);
  const [result, setResult] =
    useState<RequirementClassificationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  function handleFormChange(
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) {
    const { name, value } = event.target;
    setFormData((current) => ({ ...current, [name]: value }));
  }

  function handleRequirementChange(
    key: number,
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) {
    const { name, value } = event.target;
    setRequirements((current) =>
      current.map((requirement) =>
        requirement.key === key
          ? { ...requirement, [name]: value }
          : requirement
      )
    );
  }

  function addRequirement() {
    setRequirements((current) => [
      ...current,
      createRequirement(nextRequirementKey),
    ]);
    setNextRequirementKey((current) => current + 1);
  }

  function removeRequirement(key: number) {
    setRequirements((current) =>
      current.length > 1
        ? current.filter((requirement) => requirement.key !== key)
        : current
    );
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setResult(null);
    setError("");

    const validationError = getValidationError(formData, requirements);
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsLoading(true);
    const request: RequirementClassificationRequest = {
      analysis_title: formData.analysis_title.trim(),
      business_context: formData.business_context.trim(),
      business_domain: formData.business_domain.trim(),
      requirements: requirements.map((requirement) => ({
        requirement_id: requirement.requirement_id.trim(),
        title: requirement.title.trim(),
        requirement_text: requirement.requirement_text.trim(),
        source_document: requirement.source_document.trim() || null,
        source_section: requirement.source_section.trim() || null,
      })),
      additional_instructions:
        formData.additional_instructions.trim() || null,
    };

    try {
      setResult(await classifyRequirements(request));
    } catch (requestError: unknown) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main>
      <h1>Requirement Classifier</h1>
      <p>
        Classify requirements by type and quality, and identify areas that need
        clarification or validation.
      </p>

      <form className="classifier-analysis-form" onSubmit={handleSubmit} noValidate>
        <div className="form-field">
          <label htmlFor="classifier-analysis-title">Analysis title</label>
          <input
            id="classifier-analysis-title"
            name="analysis_title"
            value={formData.analysis_title}
            onChange={handleFormChange}
            minLength={3}
            maxLength={200}
            required
          />
        </div>

        <div className="form-field">
          <label htmlFor="classifier-business-context">Business context</label>
          <textarea
            id="classifier-business-context"
            name="business_context"
            value={formData.business_context}
            onChange={handleFormChange}
            minLength={10}
            maxLength={5000}
            rows={4}
            required
          />
        </div>

        <div className="form-field">
          <label htmlFor="classifier-business-domain">Business domain</label>
          <input
            id="classifier-business-domain"
            name="business_domain"
            value={formData.business_domain}
            onChange={handleFormChange}
            minLength={2}
            maxLength={100}
            required
          />
        </div>

        <section className="requirement-cards-section">
          <div className="requirement-cards-heading">
            <h2>Requirements</h2>
            <button type="button" onClick={addRequirement}>
              Add Requirement
            </button>
          </div>

          <div className="classifier-requirement-list">
            {requirements.map((requirement, index) => (
              <article
                className="requirement-card classifier-requirement-card"
                key={requirement.key}
              >
                <div className="requirement-card-heading">
                  <h3>Requirement {index + 1}</h3>
                  <button
                    type="button"
                    onClick={() => removeRequirement(requirement.key)}
                    disabled={requirements.length <= 1}
                    aria-label={`Remove requirement ${index + 1}`}
                  >
                    Remove
                  </button>
                </div>

                <div className="form-field">
                  <label htmlFor={`classifier-requirement-id-${requirement.key}`}>
                    Requirement ID
                  </label>
                  <input
                    id={`classifier-requirement-id-${requirement.key}`}
                    name="requirement_id"
                    value={requirement.requirement_id}
                    onChange={(event) =>
                      handleRequirementChange(requirement.key, event)
                    }
                    minLength={2}
                    maxLength={100}
                    required
                  />
                </div>

                <div className="form-field">
                  <label htmlFor={`classifier-requirement-title-${requirement.key}`}>
                    Title
                  </label>
                  <input
                    id={`classifier-requirement-title-${requirement.key}`}
                    name="title"
                    value={requirement.title}
                    onChange={(event) =>
                      handleRequirementChange(requirement.key, event)
                    }
                    minLength={3}
                    maxLength={200}
                    required
                  />
                </div>

                <div className="form-field">
                  <label htmlFor={`classifier-requirement-text-${requirement.key}`}>
                    Requirement text
                  </label>
                  <textarea
                    id={`classifier-requirement-text-${requirement.key}`}
                    name="requirement_text"
                    value={requirement.requirement_text}
                    onChange={(event) =>
                      handleRequirementChange(requirement.key, event)
                    }
                    minLength={10}
                    maxLength={10000}
                    rows={4}
                    required
                  />
                </div>

                <div className="form-field">
                  <label htmlFor={`classifier-source-document-${requirement.key}`}>
                    Source document
                  </label>
                  <input
                    id={`classifier-source-document-${requirement.key}`}
                    name="source_document"
                    value={requirement.source_document}
                    onChange={(event) =>
                      handleRequirementChange(requirement.key, event)
                    }
                    maxLength={300}
                  />
                </div>

                <div className="form-field">
                  <label htmlFor={`classifier-source-section-${requirement.key}`}>
                    Source section
                  </label>
                  <input
                    id={`classifier-source-section-${requirement.key}`}
                    name="source_section"
                    value={requirement.source_section}
                    onChange={(event) =>
                      handleRequirementChange(requirement.key, event)
                    }
                    maxLength={200}
                  />
                </div>
              </article>
            ))}
          </div>
        </section>

        <div className="form-field">
          <label htmlFor="classifier-additional-instructions">
            Additional instructions
          </label>
          <textarea
            id="classifier-additional-instructions"
            name="additional_instructions"
            value={formData.additional_instructions}
            onChange={handleFormChange}
            maxLength={1000}
            rows={3}
          />
        </div>

        <button type="submit" disabled={isLoading}>
          {isLoading ? "Classifying Requirements..." : "Classify Requirements"}
        </button>
        {isLoading && (
          <p className="loading-state" role="status" aria-live="polite">
            Classifying Requirements...
          </p>
        )}
      </form>

      {error && (
        <section className="error-message" role="alert">
          <h2>Classification failed</h2>
          <p>{error}</p>
        </section>
      )}

      {result && <RequirementClassifierResult result={result} />}
    </main>
  );
}
