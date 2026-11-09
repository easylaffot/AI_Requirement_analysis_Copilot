import { useState } from "react";
import { axios } from "../api/apiClient";

import { analyzeRequirementConflicts } from "../api/requirementConflictApi";
import RequirementConflictResult from "../components/RequirementConflictResult";
import type {
  ConflictAnalysisRequest,
  ConflictAnalysisResponse,
  RequirementCategory,
} from "../types/requirementConflict";

interface RequirementForm {
  key: number;
  requirement_id: string;
  title: string;
  requirement_text: string;
  category: RequirementCategory;
  source_document: string;
  source_section: string;
  source_authority: string;
}

interface FormData {
  analysis_title: string;
  business_context: string;
  known_business_rules: string;
  additional_instructions: string;
}

const requirementCategories: RequirementCategory[] = [
  "Functional",
  "Non-Functional",
  "Business Rule",
  "Security",
  "Compliance",
  "Integration",
  "Constraint",
  "Unknown",
];

const initialFormData: FormData = {
  analysis_title: "",
  business_context: "",
  known_business_rules: "",
  additional_instructions: "",
};

function createRequirement(key: number): RequirementForm {
  return {
    key,
    requirement_id: "",
    title: "",
    requirement_text: "",
    category: "Unknown",
    source_document: "",
    source_section: "",
    source_authority: "",
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
      return "Unable to reach the requirement conflict analysis service. Check that the backend is running and try again.";
    }
  }

  if (error instanceof Error && error.message) {
    return `Unable to analyze requirement conflicts: ${error.message}`;
  }

  return "Unable to analyze requirement conflicts. Please try again.";
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
  if (requirements.length < 2) {
    return "Add at least two requirements.";
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

export default function RequirementConflictDetector() {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [requirements, setRequirements] = useState<RequirementForm[]>([
    createRequirement(1),
    createRequirement(2),
  ]);
  const [nextRequirementKey, setNextRequirementKey] = useState(3);
  const [result, setResult] = useState<ConflictAnalysisResponse | null>(null);
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
    event: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
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
      current.length > 2
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
    const request: ConflictAnalysisRequest = {
      analysis_title: formData.analysis_title.trim(),
      business_context: formData.business_context.trim(),
      requirements: requirements.map((requirement) => ({
        requirement_id: requirement.requirement_id.trim(),
        title: requirement.title.trim(),
        requirement_text: requirement.requirement_text.trim(),
        category: requirement.category,
        source_document: requirement.source_document.trim() || null,
        source_section: requirement.source_section.trim() || null,
        source_authority: requirement.source_authority.trim() || null,
      })),
      known_business_rules: formData.known_business_rules
        .split(/\r?\n/)
        .map((rule) => rule.trim())
        .filter((rule) => rule.length > 0),
      additional_instructions:
        formData.additional_instructions.trim() || null,
    };

    try {
      setResult(await analyzeRequirementConflicts(request));
    } catch (requestError: unknown) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main>
      <h1>Requirement Conflict Detector</h1>
      <p>
        Analyze requirements to identify conflicts, impacts, and decisions
        requiring human validation.
      </p>

      <form className="conflict-analysis-form" onSubmit={handleSubmit} noValidate>
        <div className="form-field">
          <label htmlFor="conflict-analysis-title">Analysis title</label>
          <input
            id="conflict-analysis-title"
            name="analysis_title"
            value={formData.analysis_title}
            onChange={handleFormChange}
            minLength={3}
            maxLength={200}
            required
          />
        </div>

        <div className="form-field">
          <label htmlFor="conflict-business-context">Business context</label>
          <textarea
            id="conflict-business-context"
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
          <label htmlFor="known-business-rules">Known business rules</label>
          <textarea
            id="known-business-rules"
            name="known_business_rules"
            value={formData.known_business_rules}
            onChange={handleFormChange}
            rows={4}
            placeholder="Enter one business rule per line"
          />
          <span className="field-hint">Enter one rule per line.</span>
        </div>

        <section className="requirement-cards-section">
          <div className="requirement-cards-heading">
            <h2>Requirements</h2>
            <button type="button" onClick={addRequirement}>
              Add Requirement
            </button>
          </div>

          <div className="conflict-requirement-list">
            {requirements.map((requirement, index) => (
              <article
                className="requirement-card conflict-requirement-card"
                key={requirement.key}
              >
                <div className="requirement-card-heading">
                  <h3>Requirement {index + 1}</h3>
                  <button
                    type="button"
                    onClick={() => removeRequirement(requirement.key)}
                    disabled={requirements.length <= 2}
                    aria-label={`Remove requirement ${index + 1}`}
                  >
                    Remove
                  </button>
                </div>

                <div className="form-field">
                  <label htmlFor={`conflict-requirement-id-${requirement.key}`}>
                    Requirement ID
                  </label>
                  <input
                    id={`conflict-requirement-id-${requirement.key}`}
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
                  <label htmlFor={`conflict-requirement-title-${requirement.key}`}>
                    Title
                  </label>
                  <input
                    id={`conflict-requirement-title-${requirement.key}`}
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
                  <label htmlFor={`conflict-requirement-text-${requirement.key}`}>
                    Requirement text
                  </label>
                  <textarea
                    id={`conflict-requirement-text-${requirement.key}`}
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
                  <label htmlFor={`conflict-category-${requirement.key}`}>
                    Category
                  </label>
                  <select
                    id={`conflict-category-${requirement.key}`}
                    name="category"
                    value={requirement.category}
                    onChange={(event) =>
                      handleRequirementChange(requirement.key, event)
                    }
                  >
                    {requirementCategories.map((category) => (
                      <option key={category} value={category}>
                        {category}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-field">
                  <label htmlFor={`conflict-source-document-${requirement.key}`}>
                    Source document
                  </label>
                  <input
                    id={`conflict-source-document-${requirement.key}`}
                    name="source_document"
                    value={requirement.source_document}
                    onChange={(event) =>
                      handleRequirementChange(requirement.key, event)
                    }
                    maxLength={300}
                  />
                </div>

                <div className="form-field">
                  <label htmlFor={`conflict-source-section-${requirement.key}`}>
                    Source section
                  </label>
                  <input
                    id={`conflict-source-section-${requirement.key}`}
                    name="source_section"
                    value={requirement.source_section}
                    onChange={(event) =>
                      handleRequirementChange(requirement.key, event)
                    }
                    maxLength={200}
                  />
                </div>

                <div className="form-field">
                  <label htmlFor={`conflict-source-authority-${requirement.key}`}>
                    Source authority
                  </label>
                  <input
                    id={`conflict-source-authority-${requirement.key}`}
                    name="source_authority"
                    value={requirement.source_authority}
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
          <label htmlFor="conflict-additional-instructions">
            Additional instructions
          </label>
          <textarea
            id="conflict-additional-instructions"
            name="additional_instructions"
            value={formData.additional_instructions}
            onChange={handleFormChange}
            maxLength={1000}
            rows={3}
          />
        </div>

        <button type="submit" disabled={isLoading}>
          {isLoading ? "Analyzing Conflicts..." : "Analyze Conflicts"}
        </button>
        {isLoading && (
          <p className="loading-state" role="status" aria-live="polite">
            Analyzing Conflicts...
          </p>
        )}
      </form>

      {error && (
        <section className="error-message" role="alert">
          <h2>Analysis failed</h2>
          <p>{error}</p>
        </section>
      )}

      {result && <RequirementConflictResult result={result} />}
    </main>
  );
}
