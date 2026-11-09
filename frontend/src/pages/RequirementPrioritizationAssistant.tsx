import { useState } from "react";
import axios from "axios";

import { analyzeRequirementPriorities } from "../api/requirementPriorityApi";
import RequirementPriorityResult from "../components/RequirementPriorityResult";
import type {
  Priority,
  PriorityMethod,
  RequirementCategory,
  RequirementPriorityRequest,
  RequirementPriorityResponse,
} from "../types/requirementPriority";

interface RequirementForm {
  key: number;
  requirement_id: string;
  title: string;
  requirement_text: string;
  category: RequirementCategory;
  stated_priority: Priority;
  source_document: string;
  source_section: string;
}

interface FormData {
  analysis_title: string;
  business_context: string;
  release_objective: string;
  prioritization_method: PriorityMethod;
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

const priorities: Priority[] = [
  "Critical",
  "High",
  "Medium",
  "Low",
  "Unknown",
];

const priorityMethods: PriorityMethod[] = [
  "MoSCoW",
  "Value and Risk",
  "Evidence-Based Recommendation",
];

const initialFormData: FormData = {
  analysis_title: "",
  business_context: "",
  release_objective: "",
  prioritization_method: "Evidence-Based Recommendation",
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
    stated_priority: "Unknown",
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
      return "Unable to reach the requirement prioritization service. Check that the backend is running and try again.";
    }
  }

  if (error instanceof Error && error.message) {
    return `Unable to prioritize requirements: ${error.message}`;
  }

  return "Unable to prioritize requirements. Please try again.";
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
  if (formData.release_objective.trim().length < 10) {
    return "Release objective must be at least 10 characters.";
  }
  if (requirements.length < 1) {
    return "Add at least one requirement.";
  }
  if (requirements.length > 100) {
    return "A maximum of 100 requirements can be prioritized.";
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

function linesToList(value: string): string[] {
  return value
    .split(/\r?\n/)
    .map((item) => item.trim())
    .filter((item) => item.length > 0);
}

export default function RequirementPrioritizationAssistant() {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [requirements, setRequirements] = useState<RequirementForm[]>([
    createRequirement(1),
  ]);
  const [nextRequirementKey, setNextRequirementKey] = useState(2);
  const [result, setResult] = useState<RequirementPriorityResponse | null>(
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
    const request: RequirementPriorityRequest = {
      analysis_title: formData.analysis_title.trim(),
      business_context: formData.business_context.trim(),
      release_objective: formData.release_objective.trim(),
      prioritization_method: formData.prioritization_method,
      requirements: requirements.map((requirement) => ({
        requirement_id: requirement.requirement_id.trim(),
        title: requirement.title.trim(),
        requirement_text: requirement.requirement_text.trim(),
        category: requirement.category,
        stated_priority: requirement.stated_priority,
        source_document: requirement.source_document.trim() || null,
        source_section: requirement.source_section.trim() || null,
      })),
      known_dependencies: linesToList(formData.known_dependencies),
      known_constraints: linesToList(formData.known_constraints),
      additional_instructions:
        formData.additional_instructions.trim() || null,
    };

    try {
      setResult(await analyzeRequirementPriorities(request));
    } catch (requestError: unknown) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main>
      <h1>Requirement Prioritization Assistant</h1>
      <p>
        Prioritize requirements for a release using business objectives,
        evidence, dependencies, and readiness.
      </p>

      <form className="priority-analysis-form" onSubmit={handleSubmit} noValidate>
        <div className="form-field">
          <label htmlFor="priority-analysis-title">Analysis title</label>
          <input
            id="priority-analysis-title"
            name="analysis_title"
            value={formData.analysis_title}
            onChange={handleFormChange}
            minLength={3}
            maxLength={200}
            required
          />
        </div>

        <div className="form-field">
          <label htmlFor="priority-business-context">Business context</label>
          <textarea
            id="priority-business-context"
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
          <label htmlFor="priority-release-objective">Release objective</label>
          <textarea
            id="priority-release-objective"
            name="release_objective"
            value={formData.release_objective}
            onChange={handleFormChange}
            minLength={10}
            maxLength={2000}
            rows={3}
            required
          />
        </div>

        <div className="form-field">
          <label htmlFor="prioritization-method">Prioritization method</label>
          <select
            id="prioritization-method"
            name="prioritization_method"
            value={formData.prioritization_method}
            onChange={handleFormChange}
          >
            {priorityMethods.map((method) => (
              <option key={method} value={method}>
                {method}
              </option>
            ))}
          </select>
        </div>

        <div className="form-field">
          <label htmlFor="priority-known-dependencies">
            Known dependencies
          </label>
          <textarea
            id="priority-known-dependencies"
            name="known_dependencies"
            value={formData.known_dependencies}
            onChange={handleFormChange}
            rows={3}
            placeholder="Enter one dependency per line"
          />
          <span className="field-hint">Enter one dependency per line.</span>
        </div>

        <div className="form-field">
          <label htmlFor="priority-known-constraints">Known constraints</label>
          <textarea
            id="priority-known-constraints"
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

          <div className="priority-requirement-list">
            {requirements.map((requirement, index) => (
              <article
                className="requirement-card priority-requirement-card"
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
                  <label htmlFor={`priority-requirement-id-${requirement.key}`}>
                    Requirement ID
                  </label>
                  <input
                    id={`priority-requirement-id-${requirement.key}`}
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
                  <label
                    htmlFor={`priority-requirement-title-${requirement.key}`}
                  >
                    Title
                  </label>
                  <input
                    id={`priority-requirement-title-${requirement.key}`}
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
                  <label
                    htmlFor={`priority-requirement-text-${requirement.key}`}
                  >
                    Requirement text
                  </label>
                  <textarea
                    id={`priority-requirement-text-${requirement.key}`}
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
                  <label htmlFor={`priority-category-${requirement.key}`}>
                    Category
                  </label>
                  <select
                    id={`priority-category-${requirement.key}`}
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
                  <label htmlFor={`stated-priority-${requirement.key}`}>
                    Stated priority
                  </label>
                  <select
                    id={`stated-priority-${requirement.key}`}
                    name="stated_priority"
                    value={requirement.stated_priority}
                    onChange={(event) =>
                      handleRequirementChange(requirement.key, event)
                    }
                  >
                    {priorities.map((priority) => (
                      <option key={priority} value={priority}>
                        {priority}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-field">
                  <label
                    htmlFor={`priority-source-document-${requirement.key}`}
                  >
                    Source document
                  </label>
                  <input
                    id={`priority-source-document-${requirement.key}`}
                    name="source_document"
                    value={requirement.source_document}
                    onChange={(event) =>
                      handleRequirementChange(requirement.key, event)
                    }
                    maxLength={300}
                  />
                </div>
                <div className="form-field">
                  <label htmlFor={`priority-source-section-${requirement.key}`}>
                    Source section
                  </label>
                  <input
                    id={`priority-source-section-${requirement.key}`}
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
          <label htmlFor="priority-additional-instructions">
            Additional instructions
          </label>
          <textarea
            id="priority-additional-instructions"
            name="additional_instructions"
            value={formData.additional_instructions}
            onChange={handleFormChange}
            maxLength={1000}
            rows={3}
          />
        </div>

        <button type="submit" disabled={isLoading}>
          {isLoading ? "Prioritizing Requirements..." : "Prioritize Requirements"}
        </button>
        {isLoading && (
          <p className="loading-state" role="status" aria-live="polite">
            Prioritizing Requirements...
          </p>
        )}
      </form>

      {error && (
        <section className="error-message" role="alert">
          <h2>Prioritization failed</h2>
          <p>{error}</p>
        </section>
      )}

      {result && <RequirementPriorityResult result={result} />}
    </main>
  );
}
