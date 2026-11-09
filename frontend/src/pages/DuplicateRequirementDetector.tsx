import { useState } from "react";
import { axios } from "../api/apiClient";

import { analyzeDuplicateRequirements } from "../api/duplicateRequirementApi";
import DuplicateRequirementResult from "../components/DuplicateRequirementResult";
import type {
  DuplicateAnalysisRequest,
  DuplicateAnalysisResponse,
  RequirementCategory,
} from "../types/duplicateRequirement";

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
      return "Unable to reach the duplicate requirement analysis service. Check that the backend is running and try again.";
    }
  }

  if (error instanceof Error && error.message) {
    return `Unable to analyze duplicate requirements: ${error.message}`;
  }

  return "Unable to analyze duplicate requirements. Please try again.";
}

export default function DuplicateRequirementDetector() {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [requirements, setRequirements] = useState<RequirementForm[]>([
    createRequirement(1),
    createRequirement(2),
  ]);
  const [nextRequirementKey, setNextRequirementKey] = useState(3);
  const [result, setResult] = useState<DuplicateAnalysisResponse | null>(null);
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

    const normalizedIds = requirements.map((requirement) =>
      requirement.requirement_id.trim().toLocaleLowerCase()
    );
    if (new Set(normalizedIds).size !== normalizedIds.length) {
      setResult(null);
      setError("Requirement IDs must be unique.");
      return;
    }

    setResult(null);
    setError("");
    setIsLoading(true);

    const request: DuplicateAnalysisRequest = {
      analysis_title: formData.analysis_title,
      business_context: formData.business_context,
      requirements: requirements.map((requirement) => ({
        requirement_id: requirement.requirement_id,
        title: requirement.title,
        requirement_text: requirement.requirement_text,
        category: requirement.category,
        source_document: requirement.source_document.trim() || null,
        source_section: requirement.source_section.trim() || null,
      })),
      additional_instructions: formData.additional_instructions.trim() || null,
    };

    try {
      setResult(await analyzeDuplicateRequirements(request));
    } catch (requestError: unknown) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main>
      <h1>Duplicate Requirement Detector</h1>
      <p>
        Compare requirements for duplicates, overlaps, conflicts, and
        opportunities to consolidate.
      </p>

      <form className="duplicate-analysis-form" onSubmit={handleSubmit}>
        <div className="form-field">
          <label htmlFor="analysis_title">Analysis title</label>
          <input
            id="analysis_title"
            name="analysis_title"
            value={formData.analysis_title}
            onChange={handleFormChange}
            minLength={3}
            maxLength={200}
            required
          />
        </div>

        <div className="form-field">
          <label htmlFor="business_context">Business context</label>
          <textarea
            id="business_context"
            name="business_context"
            value={formData.business_context}
            onChange={handleFormChange}
            minLength={10}
            maxLength={5000}
            rows={4}
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

          <div className="duplicate-requirement-list">
            {requirements.map((requirement, index) => (
              <article
                className="duplicate-requirement-card"
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
                  <label htmlFor={`requirement_id-${requirement.key}`}>
                    Requirement ID
                  </label>
                  <input
                    id={`requirement_id-${requirement.key}`}
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
                  <label htmlFor={`requirement_title-${requirement.key}`}>
                    Title
                  </label>
                  <input
                    id={`requirement_title-${requirement.key}`}
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
                  <label htmlFor={`requirement_text-${requirement.key}`}>
                    Requirement text
                  </label>
                  <textarea
                    id={`requirement_text-${requirement.key}`}
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
                  <label htmlFor={`category-${requirement.key}`}>Category</label>
                  <select
                    id={`category-${requirement.key}`}
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
                  <label htmlFor={`source_document-${requirement.key}`}>
                    Source document
                  </label>
                  <input
                    id={`source_document-${requirement.key}`}
                    name="source_document"
                    value={requirement.source_document}
                    onChange={(event) =>
                      handleRequirementChange(requirement.key, event)
                    }
                    maxLength={300}
                  />
                </div>

                <div className="form-field">
                  <label htmlFor={`source_section-${requirement.key}`}>
                    Source section
                  </label>
                  <input
                    id={`source_section-${requirement.key}`}
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
          <label htmlFor="additional_instructions">
            Additional instructions
          </label>
          <textarea
            id="additional_instructions"
            name="additional_instructions"
            value={formData.additional_instructions}
            onChange={handleFormChange}
            maxLength={1000}
            rows={3}
          />
        </div>

        <button type="submit" disabled={isLoading || requirements.length < 2}>
          {isLoading ? "Analyzing Requirements..." : "Analyze Requirements"}
        </button>
        {isLoading && (
          <p className="loading-state" role="status" aria-live="polite">
            Analyzing Requirements...
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
          aria-label="Duplicate requirement analysis results"
        >
          <DuplicateRequirementResult result={result} />
        </section>
      )}
    </main>
  );
}
