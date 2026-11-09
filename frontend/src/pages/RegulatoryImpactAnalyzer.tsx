import { useState } from "react";
import { axios } from "../api/apiClient";

import { analyzeRegulatoryImpact } from "../api/regulatoryImpactApi";
import RegulatoryImpactResult from "../components/RegulatoryImpactResult";
import type {
  ObligationCategory,
  RegulatoryImpactRequest,
  RegulatoryImpactResponse,
  RequirementCategory,
} from "../types/regulatoryImpact";

interface Keyed<T> {
  key: number;
  value: T;
}

interface ObligationForm {
  obligation_id: string;
  title: string;
  obligation_text: string;
  category: ObligationCategory;
  source_name: string;
  source_section: string;
  effective_date: string;
  jurisdiction: string;
}

interface RequirementForm {
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
  business_domain: string;
  known_controls: string;
  additional_instructions: string;
}

const obligationCategories: ObligationCategory[] = [
  "Access Control",
  "Data Protection",
  "Data Retention",
  "Consent",
  "Customer Communication",
  "Auditability",
  "Reporting",
  "Record Keeping",
  "Security",
  "Privacy",
  "Operational Control",
  "Business Process",
  "Other",
];

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
  business_domain: "",
  known_controls: "",
  additional_instructions: "",
};

function createObligation(): ObligationForm {
  return {
    obligation_id: "",
    title: "",
    obligation_text: "",
    category: "Other",
    source_name: "",
    source_section: "",
    effective_date: "",
    jurisdiction: "",
  };
}

function createRequirement(): RequirementForm {
  return {
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
      return "Unable to reach the regulatory impact service. Check that the backend is running and try again.";
    }
  }

  if (error instanceof Error && error.message) {
    return `Unable to analyze regulatory impact: ${error.message}`;
  }

  return "Unable to analyze regulatory impact. Please try again.";
}

function uniqueIdError<T>(
  items: Keyed<T>[],
  getId: (item: T) => string,
  label: string
): string {
  const ids = items.map(({ value }) => getId(value).trim().toLocaleLowerCase());
  if (ids.some((id) => id.length < 2)) {
    return `Every ${label} ID must be at least 2 characters.`;
  }
  if (ids.some((id) => id.length > 100)) {
    return `Every ${label} ID must be no more than 100 characters.`;
  }
  if (new Set(ids).size !== ids.length) {
    return `${label[0].toUpperCase()}${label.slice(1)} IDs must be unique.`;
  }
  return "";
}

function getValidationError(
  formData: FormData,
  obligations: Keyed<ObligationForm>[],
  requirements: Keyed<RequirementForm>[]
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
  if (formData.business_domain.trim().length < 2) {
    return "Business domain must be at least 2 characters.";
  }
  if (formData.business_domain.trim().length > 100) {
    return "Business domain must be no more than 100 characters.";
  }
  if (formData.additional_instructions.trim().length > 1000) {
    return "Additional instructions must be no more than 1000 characters.";
  }
  if (obligations.length < 1 || requirements.length < 1) {
    return "At least one obligation and one requirement are required.";
  }
  if (obligations.length > 100 || requirements.length > 200) {
    return "The number of artifacts exceeds the maximum allowed.";
  }

  const obligationIdError = uniqueIdError(
    obligations,
    (item) => item.obligation_id,
    "obligation"
  );
  if (obligationIdError) return obligationIdError;

  for (const [index, { value }] of obligations.entries()) {
    if (value.title.trim().length < 3 || value.title.trim().length > 300) {
      return `Obligation ${index + 1} title must be between 3 and 300 characters.`;
    }
    if (
      value.obligation_text.trim().length < 10 ||
      value.obligation_text.trim().length > 10000
    ) {
      return `Obligation ${index + 1} text must be between 10 and 10000 characters.`;
    }
    if (value.source_name.trim().length < 2 || value.source_name.trim().length > 300) {
      return `Obligation ${index + 1} source name must be between 2 and 300 characters.`;
    }
    if (value.source_section.trim().length > 300) {
      return `Obligation ${index + 1} source section must be no more than 300 characters.`;
    }
    if (value.effective_date.trim().length > 100) {
      return `Obligation ${index + 1} effective date must be no more than 100 characters.`;
    }
    if (value.jurisdiction.trim().length > 200) {
      return `Obligation ${index + 1} jurisdiction must be no more than 200 characters.`;
    }
  }

  const requirementIdError = uniqueIdError(
    requirements,
    (item) => item.requirement_id,
    "requirement"
  );
  if (requirementIdError) return requirementIdError;

  for (const [index, { value }] of requirements.entries()) {
    if (value.title.trim().length < 3 || value.title.trim().length > 200) {
      return `Requirement ${index + 1} title must be between 3 and 200 characters.`;
    }
    if (
      value.requirement_text.trim().length < 10 ||
      value.requirement_text.trim().length > 10000
    ) {
      return `Requirement ${index + 1} text must be between 10 and 10000 characters.`;
    }
    if (value.source_document.trim().length > 300) {
      return `Requirement ${index + 1} source document must be no more than 300 characters.`;
    }
    if (value.source_section.trim().length > 200) {
      return `Requirement ${index + 1} source section must be no more than 200 characters.`;
    }
  }

  return "";
}

function linesToList(value: string): string[] {
  return value
    .split(/\r?\n/)
    .map((item) => item.trim())
    .filter((item) => item.length > 0);
}

function ArtifactSection({
  title,
  addLabel,
  count,
  maxCount,
  onAdd,
  children,
}: {
  title: string;
  addLabel: string;
  count: number;
  maxCount: number;
  onAdd: () => void;
  children: React.ReactNode;
}) {
  return (
    <section className="regulatory-artifact-section">
      <div className="regulatory-artifact-heading">
        <h2>{title}</h2>
        <button type="button" onClick={onAdd} disabled={count >= maxCount}>
          Add {addLabel}
        </button>
      </div>
      {children}
    </section>
  );
}

export default function RegulatoryImpactAnalyzer() {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [obligations, setObligations] = useState<Keyed<ObligationForm>[]>([
    { key: 1, value: createObligation() },
  ]);
  const [requirements, setRequirements] = useState<Keyed<RequirementForm>[]>([
    { key: 2, value: createRequirement() },
  ]);
  const [nextKey, setNextKey] = useState(3);
  const [result, setResult] = useState<RegulatoryImpactResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  function updateForm(
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) {
    const { name, value } = event.target;
    setFormData((current) => ({ ...current, [name]: value }));
  }

  function updateObligation<K extends keyof ObligationForm>(
    key: number,
    field: K,
    value: ObligationForm[K]
  ) {
    setObligations((items) =>
      items.map((item) =>
        item.key === key
          ? { ...item, value: { ...item.value, [field]: value } }
          : item
      )
    );
  }

  function updateRequirement<K extends keyof RequirementForm>(
    key: number,
    field: K,
    value: RequirementForm[K]
  ) {
    setRequirements((items) =>
      items.map((item) =>
        item.key === key
          ? { ...item, value: { ...item.value, [field]: value } }
          : item
      )
    );
  }

  function addObligation() {
    setObligations((items) => [...items, { key: nextKey, value: createObligation() }]);
    setNextKey((key) => key + 1);
  }

  function addRequirement() {
    setRequirements((items) => [...items, { key: nextKey, value: createRequirement() }]);
    setNextKey((key) => key + 1);
  }

  function removeObligation(key: number) {
    setObligations((items) =>
      items.length > 1 ? items.filter((item) => item.key !== key) : items
    );
  }

  function removeRequirement(key: number) {
    setRequirements((items) =>
      items.length > 1 ? items.filter((item) => item.key !== key) : items
    );
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setResult(null);
    setError("");

    const validationError = getValidationError(formData, obligations, requirements);
    if (validationError) {
      setError(validationError);
      return;
    }

    const request: RegulatoryImpactRequest = {
      analysis_title: formData.analysis_title.trim(),
      business_context: formData.business_context.trim(),
      business_domain: formData.business_domain.trim(),
      obligations: obligations.map(({ value }) => ({
        obligation_id: value.obligation_id.trim(),
        title: value.title.trim(),
        obligation_text: value.obligation_text.trim(),
        category: value.category,
        source_name: value.source_name.trim(),
        source_section: value.source_section.trim() || null,
        effective_date: value.effective_date.trim() || null,
        jurisdiction: value.jurisdiction.trim() || null,
      })),
      requirements: requirements.map(({ value }) => ({
        requirement_id: value.requirement_id.trim(),
        title: value.title.trim(),
        requirement_text: value.requirement_text.trim(),
        category: value.category,
        source_document: value.source_document.trim() || null,
        source_section: value.source_section.trim() || null,
      })),
      known_controls: linesToList(formData.known_controls),
      additional_instructions: formData.additional_instructions.trim() || null,
    };

    setIsLoading(true);
    try {
      setResult(await analyzeRegulatoryImpact(request));
    } catch (requestError: unknown) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main>
      <h1>Regulatory Impact Analyzer</h1>
      <p>
        Assess how regulatory obligations relate to existing requirements and
        controls.
      </p>
      <p className="regulatory-legal-notice" role="note">
        This analysis supports requirement review and is not legal advice.
      </p>

      <form className="regulatory-analysis-form" onSubmit={handleSubmit} noValidate>
        <div className="form-field">
          <label htmlFor="regulatory-analysis-title">Analysis title</label>
          <input
            id="regulatory-analysis-title"
            name="analysis_title"
            value={formData.analysis_title}
            onChange={updateForm}
            minLength={3}
            maxLength={200}
            required
          />
        </div>
        <div className="form-field">
          <label htmlFor="regulatory-business-context">Business context</label>
          <textarea
            id="regulatory-business-context"
            name="business_context"
            value={formData.business_context}
            onChange={updateForm}
            minLength={10}
            maxLength={5000}
            rows={4}
            required
          />
        </div>
        <div className="form-field">
          <label htmlFor="regulatory-business-domain">Business domain</label>
          <input
            id="regulatory-business-domain"
            name="business_domain"
            value={formData.business_domain}
            onChange={updateForm}
            minLength={2}
            maxLength={100}
            required
          />
        </div>
        <div className="form-field">
          <label htmlFor="regulatory-known-controls">Known controls</label>
          <textarea
            id="regulatory-known-controls"
            name="known_controls"
            value={formData.known_controls}
            onChange={updateForm}
            rows={3}
            placeholder="Enter one control per line"
          />
          <span className="field-hint">Enter one control per line.</span>
        </div>

        <ArtifactSection
          title="Regulatory Obligations"
          addLabel="Obligation"
          count={obligations.length}
          maxCount={100}
          onAdd={addObligation}
        >
          <div className="regulatory-artifact-list">
            {obligations.map(({ key, value }, index) => (
              <article className="regulatory-obligation-card" key={key}>
                <div className="regulatory-card-heading">
                  <h3>Obligation {index + 1}</h3>
                  <button
                    type="button"
                    disabled={obligations.length <= 1}
                    onClick={() => removeObligation(key)}
                  >
                    Remove
                  </button>
                </div>
                <div className="form-field">
                  <label htmlFor={`reg-obligation-id-${key}`}>Obligation ID</label>
                  <input id={`reg-obligation-id-${key}`} value={value.obligation_id} onChange={(event) => updateObligation(key, "obligation_id", event.target.value)} maxLength={100} />
                </div>
                <div className="form-field">
                  <label htmlFor={`reg-obligation-title-${key}`}>Title</label>
                  <input id={`reg-obligation-title-${key}`} value={value.title} onChange={(event) => updateObligation(key, "title", event.target.value)} minLength={3} maxLength={300} />
                </div>
                <div className="form-field">
                  <label htmlFor={`reg-obligation-text-${key}`}>Obligation text</label>
                  <textarea id={`reg-obligation-text-${key}`} value={value.obligation_text} onChange={(event) => updateObligation(key, "obligation_text", event.target.value)} minLength={10} maxLength={10000} rows={4} />
                </div>
                <div className="form-field">
                  <label htmlFor={`reg-obligation-category-${key}`}>Category</label>
                  <select id={`reg-obligation-category-${key}`} value={value.category} onChange={(event) => updateObligation(key, "category", event.target.value as ObligationCategory)}>
                    {obligationCategories.map((category) => <option key={category} value={category}>{category}</option>)}
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor={`reg-obligation-source-${key}`}>Source name</label>
                  <input id={`reg-obligation-source-${key}`} value={value.source_name} onChange={(event) => updateObligation(key, "source_name", event.target.value)} minLength={2} maxLength={300} />
                </div>
                <div className="form-field">
                  <label htmlFor={`reg-obligation-section-${key}`}>Source section</label>
                  <input id={`reg-obligation-section-${key}`} value={value.source_section} onChange={(event) => updateObligation(key, "source_section", event.target.value)} maxLength={300} />
                </div>
                <div className="form-field">
                  <label htmlFor={`reg-obligation-effective-${key}`}>Effective date</label>
                  <input id={`reg-obligation-effective-${key}`} value={value.effective_date} onChange={(event) => updateObligation(key, "effective_date", event.target.value)} maxLength={100} />
                </div>
                <div className="form-field">
                  <label htmlFor={`reg-obligation-jurisdiction-${key}`}>Jurisdiction</label>
                  <input id={`reg-obligation-jurisdiction-${key}`} value={value.jurisdiction} onChange={(event) => updateObligation(key, "jurisdiction", event.target.value)} maxLength={200} />
                </div>
              </article>
            ))}
          </div>
        </ArtifactSection>

        <ArtifactSection
          title="Requirements"
          addLabel="Requirement"
          count={requirements.length}
          maxCount={200}
          onAdd={addRequirement}
        >
          <div className="regulatory-artifact-list">
            {requirements.map(({ key, value }, index) => (
              <article className="regulatory-requirement-card" key={key}>
                <div className="regulatory-card-heading">
                  <h3>Requirement {index + 1}</h3>
                  <button
                    type="button"
                    disabled={requirements.length <= 1}
                    onClick={() => removeRequirement(key)}
                  >
                    Remove
                  </button>
                </div>
                <div className="form-field">
                  <label htmlFor={`reg-requirement-id-${key}`}>Requirement ID</label>
                  <input id={`reg-requirement-id-${key}`} value={value.requirement_id} onChange={(event) => updateRequirement(key, "requirement_id", event.target.value)} maxLength={100} />
                </div>
                <div className="form-field">
                  <label htmlFor={`reg-requirement-title-${key}`}>Title</label>
                  <input id={`reg-requirement-title-${key}`} value={value.title} onChange={(event) => updateRequirement(key, "title", event.target.value)} minLength={3} maxLength={200} />
                </div>
                <div className="form-field">
                  <label htmlFor={`reg-requirement-text-${key}`}>Requirement text</label>
                  <textarea id={`reg-requirement-text-${key}`} value={value.requirement_text} onChange={(event) => updateRequirement(key, "requirement_text", event.target.value)} minLength={10} maxLength={10000} rows={4} />
                </div>
                <div className="form-field">
                  <label htmlFor={`reg-requirement-category-${key}`}>Category</label>
                  <select id={`reg-requirement-category-${key}`} value={value.category} onChange={(event) => updateRequirement(key, "category", event.target.value as RequirementCategory)}>
                    {requirementCategories.map((category) => <option key={category} value={category}>{category}</option>)}
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor={`reg-requirement-document-${key}`}>Source document</label>
                  <input id={`reg-requirement-document-${key}`} value={value.source_document} onChange={(event) => updateRequirement(key, "source_document", event.target.value)} maxLength={300} />
                </div>
                <div className="form-field">
                  <label htmlFor={`reg-requirement-section-${key}`}>Source section</label>
                  <input id={`reg-requirement-section-${key}`} value={value.source_section} onChange={(event) => updateRequirement(key, "source_section", event.target.value)} maxLength={200} />
                </div>
              </article>
            ))}
          </div>
        </ArtifactSection>

        <div className="form-field">
          <label htmlFor="regulatory-additional-instructions">Additional instructions</label>
          <textarea
            id="regulatory-additional-instructions"
            name="additional_instructions"
            value={formData.additional_instructions}
            onChange={updateForm}
            maxLength={1000}
            rows={3}
          />
        </div>
        <button type="submit" disabled={isLoading}>
          {isLoading ? "Analyzing Regulatory Impact..." : "Analyze Regulatory Impact"}
        </button>
        {isLoading && (
          <p className="loading-state" role="status" aria-live="polite">
            Analyzing Regulatory Impact...
          </p>
        )}
      </form>

      {error && (
        <section className="error-message" role="alert">
          <h2>Regulatory impact analysis failed</h2>
          <p>{error}</p>
        </section>
      )}
      {result && <RegulatoryImpactResult result={result} />}
    </main>
  );
}
