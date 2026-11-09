import { useState } from "react";
import { axios } from "../api/apiClient";

import { analyzeRequirementDependencies } from "../api/requirementDependencyApi";
import RequirementDependencyResult from "../components/RequirementDependencyResult";
import type {
  RequirementCategory,
  RequirementDependencyRequest,
  RequirementDependencyResponse,
} from "../types/requirementDependency";

interface RequirementForm {
  key: number;
  requirement_id: string;
  title: string;
  requirement_text: string;
  category: RequirementCategory;
  source_document: string;
  source_section: string;
}

interface FormData {
  analysis_title: string;
  business_context: string;
  known_dependencies: string;
  known_constraints: string;
  additional_instructions: string;
}

const requirementCategories: RequirementCategory[] = [
  "Functional",
  "Non-Functional",
  "Business Rule",
  "Data",
  "Security",
  "Privacy",
  "Compliance",
  "Integration",
  "Constraint",
  "Unknown",
];

const initialFormData: FormData = {
  analysis_title: "",
  business_context: "",
  known_dependencies: "",
  known_constraints: "",
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
        .map((item) =>
          typeof item === "object" &&
          item !== null &&
          "msg" in item &&
          typeof item.msg === "string"
            ? item.msg
            : null
        )
        .filter((message): message is string => message !== null);
      if (messages.length > 0) {
        return messages.join(" ");
      }
    }

    if (!error.response) {
      return "Unable to reach the requirement dependency service. Check that the backend is running and try again.";
    }
  }

  if (error instanceof Error && error.message) {
    return `Unable to analyze dependencies: ${error.message}`;
  }

  return "Unable to analyze dependencies. Please try again.";
}

function getValidationError(
  formData: FormData,
  requirements: RequirementForm[]
): string {
  if (formData.analysis_title.trim().length < 3) {
    return "Analysis title must be at least 3 characters.";
  }
  if (formData.analysis_title.trim().length > 200) {
    return "Analysis title must be no more than 200 characters.";
  }
  if (formData.business_context.trim().length < 10) {
    return "Business context must be at least 10 characters.";
  }
  if (formData.business_context.trim().length > 5000) {
    return "Business context must be no more than 5000 characters.";
  }
  if (requirements.length < 2) {
    return "Add at least two requirements.";
  }
  if (requirements.length > 100) {
    return "A maximum of 100 requirements can be analyzed.";
  }

  for (const [index, requirement] of requirements.entries()) {
    if (requirement.requirement_id.trim().length < 2) {
      return `Requirement ${index + 1} ID must be at least 2 characters.`;
    }
    if (requirement.requirement_id.trim().length > 100) {
      return `Requirement ${index + 1} ID must be no more than 100 characters.`;
    }
    if (requirement.title.trim().length < 3) {
      return `Requirement ${index + 1} title must be at least 3 characters.`;
    }
    if (requirement.title.trim().length > 200) {
      return `Requirement ${index + 1} title must be no more than 200 characters.`;
    }
    if (requirement.requirement_text.trim().length < 10) {
      return `Requirement ${index + 1} text must be at least 10 characters.`;
    }
    if (requirement.requirement_text.trim().length > 10000) {
      return `Requirement ${index + 1} text must be no more than 10000 characters.`;
    }
    if (requirement.source_document.trim().length > 300) {
      return `Requirement ${index + 1} source document must be no more than 300 characters.`;
    }
    if (requirement.source_section.trim().length > 200) {
      return `Requirement ${index + 1} source section must be no more than 200 characters.`;
    }
  }

  const normalizedIds = requirements.map((requirement) =>
    requirement.requirement_id.trim().toLocaleLowerCase()
  );
  if (new Set(normalizedIds).size !== normalizedIds.length) {
    return "Requirement IDs must be unique.";
  }

  if (formData.additional_instructions.trim().length > 1000) {
    return "Additional instructions must be no more than 1000 characters.";
  }

  return "";
}

function linesToList(value: string): string[] {
  return value
    .split(/\r?\n/)
    .map((item) => item.trim())
    .filter((item) => item.length > 0);
}

export default function RequirementDependencyMapper() {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [requirements, setRequirements] = useState<RequirementForm[]>([
    createRequirement(1),
    createRequirement(2),
  ]);
  const [nextRequirementKey, setNextRequirementKey] = useState(3);
  const [result, setResult] = useState<RequirementDependencyResponse | null>(
    null
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  function handleFormChange(
    event: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
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
    const request: RequirementDependencyRequest = {
      analysis_title: formData.analysis_title.trim(),
      business_context: formData.business_context.trim(),
      requirements: requirements.map((requirement) => ({
        requirement_id: requirement.requirement_id.trim(),
        title: requirement.title.trim(),
        requirement_text: requirement.requirement_text.trim(),
        category: requirement.category,
        source_document: requirement.source_document.trim() || null,
        source_section: requirement.source_section.trim() || null,
      })),
      known_dependencies: linesToList(formData.known_dependencies),
      known_constraints: linesToList(formData.known_constraints),
      additional_instructions:
        formData.additional_instructions.trim() || null,
    };

    try {
      setResult(await analyzeRequirementDependencies(request));
    } catch (requestError: unknown) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main>
      <h1>Requirement Dependency Mapper</h1>
      <p>
        Map prerequisite relationships, blockers, and recommended delivery
        stages across your requirements.
      </p>

      <form className="dependency-analysis-form" onSubmit={handleSubmit} noValidate>
        <div className="form-field">
          <label htmlFor="dependency-analysis-title">Analysis title</label>
          <input
            id="dependency-analysis-title"
            name="analysis_title"
            value={formData.analysis_title}
            onChange={handleFormChange}
            minLength={3}
            maxLength={200}
            required
          />
        </div>

        <div className="form-field">
          <label htmlFor="dependency-business-context">Business context</label>
          <textarea
            id="dependency-business-context"
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
          <label htmlFor="dependency-known-dependencies">
            Known dependencies
          </label>
          <textarea
            id="dependency-known-dependencies"
            name="known_dependencies"
            value={formData.known_dependencies}
            onChange={handleFormChange}
            rows={3}
            placeholder="Enter one dependency per line"
          />
          <span className="field-hint">Enter one dependency per line.</span>
        </div>

        <div className="form-field">
          <label htmlFor="dependency-known-constraints">
            Known constraints
          </label>
          <textarea
            id="dependency-known-constraints"
            name="known_constraints"
            value={formData.known_constraints}
            onChange={handleFormChange}
            rows={3}
            placeholder="Enter one constraint per line"
          />
          <span className="field-hint">Enter one constraint per line.</span>
        </div>

        <section className="requirement-cards-section">
          <div className="requirement-cards-heading">
            <h2>Requirements</h2>
            <button
              type="button"
              onClick={addRequirement}
              disabled={requirements.length >= 100}
            >
              Add Requirement
            </button>
          </div>

          <div className="dependency-requirement-list">
            {requirements.map((requirement, index) => (
              <article
                className="requirement-card dependency-requirement-card"
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
                  <label htmlFor={`dependency-requirement-id-${requirement.key}`}>
                    ID
                  </label>
                  <input
                    id={`dependency-requirement-id-${requirement.key}`}
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
                  <label htmlFor={`dependency-requirement-title-${requirement.key}`}>
                    Title
                  </label>
                  <input
                    id={`dependency-requirement-title-${requirement.key}`}
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
                  <label htmlFor={`dependency-requirement-text-${requirement.key}`}>
                    Requirement text
                  </label>
                  <textarea
                    id={`dependency-requirement-text-${requirement.key}`}
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
                  <label htmlFor={`dependency-category-${requirement.key}`}>
                    Category
                  </label>
                  <select
                    id={`dependency-category-${requirement.key}`}
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
                  <label htmlFor={`dependency-source-document-${requirement.key}`}>
                    Source document
                  </label>
                  <input
                    id={`dependency-source-document-${requirement.key}`}
                    name="source_document"
                    value={requirement.source_document}
                    onChange={(event) =>
                      handleRequirementChange(requirement.key, event)
                    }
                    maxLength={300}
                  />
                </div>
                <div className="form-field">
                  <label htmlFor={`dependency-source-section-${requirement.key}`}>
                    Source section
                  </label>
                  <input
                    id={`dependency-source-section-${requirement.key}`}
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
          <label htmlFor="dependency-additional-instructions">
            Additional instructions
          </label>
          <textarea
            id="dependency-additional-instructions"
            name="additional_instructions"
            value={formData.additional_instructions}
            onChange={handleFormChange}
            maxLength={1000}
            rows={3}
          />
        </div>

        <button type="submit" disabled={isLoading}>
          {isLoading ? "Analyzing Dependencies..." : "Analyze Dependencies"}
        </button>
        {isLoading && (
          <p className="loading-state" role="status" aria-live="polite">
            Analyzing Dependencies...
          </p>
        )}
      </form>

      {error && (
        <section className="error-message" role="alert">
          <h2>Dependency analysis failed</h2>
          <p>{error}</p>
        </section>
      )}

      {result && <RequirementDependencyResult result={result} />}
    </main>
  );
}
