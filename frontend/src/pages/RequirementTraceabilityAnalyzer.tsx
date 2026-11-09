import { useState } from "react";
import axios from "axios";

import { analyzeRequirementTraceability } from "../api/requirementTraceabilityApi";
import RequirementTraceabilityResult from "../components/RequirementTraceabilityResult";
import type {
  RequirementCategory,
  RequirementTraceabilityRequest,
  RequirementTraceabilityResponse,
  TraceRequirementItem,
} from "../types/requirementTraceability";

interface Keyed<T> {
  key: number;
  value: T;
}

interface FormData {
  analysis_title: string;
  business_context: string;
  additional_instructions: string;
}

interface RequirementForm extends TraceRequirementItem {}

interface UserStoryForm {
  story_id: string;
  title: string;
  story_text: string;
  source_requirement_ids: string;
}

interface AcceptanceCriterionForm {
  criterion_id: string;
  criterion_text: string;
  source_story_ids: string;
  source_requirement_ids: string;
}

interface TestCaseForm {
  test_case_id: string;
  title: string;
  test_description: string;
  source_criterion_ids: string;
  source_story_ids: string;
  source_requirement_ids: string;
}

const categories: RequirementCategory[] = [
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
  additional_instructions: "",
};

function createRequirement(): RequirementForm {
  return {
    requirement_id: "",
    title: "",
    requirement_text: "",
    category: "Unknown",
  };
}

function createUserStory(): UserStoryForm {
  return { story_id: "", title: "", story_text: "", source_requirement_ids: "" };
}

function createCriterion(): AcceptanceCriterionForm {
  return {
    criterion_id: "",
    criterion_text: "",
    source_story_ids: "",
    source_requirement_ids: "",
  };
}

function createTestCase(): TestCaseForm {
  return {
    test_case_id: "",
    title: "",
    test_description: "",
    source_criterion_ids: "",
    source_story_ids: "",
    source_requirement_ids: "",
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
      return "Unable to reach the requirement traceability service. Check that the backend is running and try again.";
    }
  }

  if (error instanceof Error && error.message) {
    return `Unable to analyze traceability: ${error.message}`;
  }

  return "Unable to analyze traceability. Please try again.";
}

function commaSeparated(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter((item) => item.length > 0);
}

function hasUniqueIds<T>(
  artifacts: Keyed<T>[],
  getId: (value: T) => string,
  label: string
): string {
  const ids = artifacts.map(({ value }) => getId(value).trim().toLocaleLowerCase());
  if (ids.some((id) => !id)) {
    return `Every ${label} must have an ID of at least 2 characters.`;
  }
  if (ids.some((id) => id.length < 2)) {
    return `Every ${label} must have an ID of at least 2 characters.`;
  }
  if (new Set(ids).size !== ids.length) {
    return `${label[0].toUpperCase()}${label.slice(1)} IDs must be unique.`;
  }
  return "";
}

function getValidationError(
  formData: FormData,
  requirements: Keyed<RequirementForm>[],
  stories: Keyed<UserStoryForm>[],
  criteria: Keyed<AcceptanceCriterionForm>[],
  testCases: Keyed<TestCaseForm>[]
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
  if (formData.additional_instructions.trim().length > 1000) {
    return "Additional instructions must be no more than 1000 characters.";
  }
  if (requirements.length < 1) {
    return "At least one requirement is required.";
  }
  if (requirements.length > 100 || stories.length > 300 || criteria.length > 500 || testCases.length > 500) {
    return "The number of artifacts exceeds the maximum allowed.";
  }

  const requirementIdError = hasUniqueIds(
    requirements,
    (item) => item.requirement_id,
    "requirement"
  );
  if (requirementIdError) return requirementIdError;

  for (const [index, { value }] of requirements.entries()) {
    if (value.title.trim().length < 3) {
      return `Requirement ${index + 1} title must be at least 3 characters.`;
    }
    if (value.title.trim().length > 200) {
      return `Requirement ${index + 1} title must be no more than 200 characters.`;
    }
    if (value.requirement_text.trim().length < 10) {
      return `Requirement ${index + 1} text must be at least 10 characters.`;
    }
    if (value.requirement_text.trim().length > 10000) {
      return `Requirement ${index + 1} text must be no more than 10000 characters.`;
    }
  }

  const storyIdError = hasUniqueIds(stories, (item) => item.story_id, "user story");
  if (storyIdError) return storyIdError;
  for (const [index, { value }] of stories.entries()) {
    if (value.title.trim().length < 3 || value.title.trim().length > 200) {
      return `User story ${index + 1} title must be between 3 and 200 characters.`;
    }
    if (value.story_text.trim().length < 10 || value.story_text.trim().length > 5000) {
      return `User story ${index + 1} text must be between 10 and 5000 characters.`;
    }
  }

  const criterionIdError = hasUniqueIds(
    criteria,
    (item) => item.criterion_id,
    "acceptance criterion"
  );
  if (criterionIdError) return criterionIdError;
  for (const [index, { value }] of criteria.entries()) {
    if (value.criterion_text.trim().length < 10 || value.criterion_text.trim().length > 5000) {
      return `Acceptance criterion ${index + 1} text must be between 10 and 5000 characters.`;
    }
  }

  const testCaseIdError = hasUniqueIds(
    testCases,
    (item) => item.test_case_id,
    "test case"
  );
  if (testCaseIdError) return testCaseIdError;
  for (const [index, { value }] of testCases.entries()) {
    if (value.title.trim().length < 3 || value.title.trim().length > 200) {
      return `Test case ${index + 1} title must be between 3 and 200 characters.`;
    }
    if (value.test_description.trim().length < 10 || value.test_description.trim().length > 5000) {
      return `Test case ${index + 1} description must be between 10 and 5000 characters.`;
    }
  }

  return "";
}

function ArtifactFields({
  label,
  addLabel,
  children,
  onAdd,
  count,
  maxCount,
}: {
  label: string;
  addLabel: string;
  children: React.ReactNode;
  onAdd: () => void;
  count: number;
  maxCount: number;
}) {
  return (
    <section className="trace-artifact-section">
      <div className="trace-artifact-heading">
        <h2>{label}</h2>
        <button type="button" onClick={onAdd} disabled={count >= maxCount}>
          Add {addLabel}
        </button>
      </div>
      {children}
    </section>
  );
}

function ReferenceField({
  id,
  label,
  value,
  onChange,
}: {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <div className="form-field">
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="IDs separated by commas"
      />
    </div>
  );
}

export default function RequirementTraceabilityAnalyzer() {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [requirements, setRequirements] = useState<Keyed<RequirementForm>[]>([
    { key: 1, value: createRequirement() },
  ]);
  const [stories, setStories] = useState<Keyed<UserStoryForm>[]>([]);
  const [criteria, setCriteria] = useState<Keyed<AcceptanceCriterionForm>[]>([]);
  const [testCases, setTestCases] = useState<Keyed<TestCaseForm>[]>([]);
  const [nextKey, setNextKey] = useState(2);
  const [result, setResult] = useState<RequirementTraceabilityResponse | null>(
    null
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  function updateForm(
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) {
    const { name, value } = event.target;
    setFormData((current) => ({ ...current, [name]: value }));
  }

  function updateArtifact<T extends object>(
    setter: React.Dispatch<React.SetStateAction<Keyed<T>[]>>,
    key: number,
    field: keyof T,
    value: string
  ) {
    setter((items) =>
      items.map((item) =>
        item.key === key
          ? { ...item, value: { ...item.value, [field]: value } }
          : item
      )
    );
  }

  function addArtifact<T>(
    setter: React.Dispatch<React.SetStateAction<Keyed<T>[]>>,
    create: () => T
  ) {
    setter((items) => [...items, { key: nextKey, value: create() }]);
    setNextKey((key) => key + 1);
  }

  function removeArtifact<T>(
    setter: React.Dispatch<React.SetStateAction<Keyed<T>[]>>,
    key: number,
    minimum = 0
  ) {
    setter((items) =>
      items.length > minimum ? items.filter((item) => item.key !== key) : items
    );
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setResult(null);
    setError("");

    const validationError = getValidationError(
      formData,
      requirements,
      stories,
      criteria,
      testCases
    );
    if (validationError) {
      setError(validationError);
      return;
    }

    const request: RequirementTraceabilityRequest = {
      analysis_title: formData.analysis_title.trim(),
      business_context: formData.business_context.trim(),
      requirements: requirements.map(({ value }) => ({
        ...value,
        requirement_id: value.requirement_id.trim(),
        title: value.title.trim(),
        requirement_text: value.requirement_text.trim(),
      })),
      user_stories: stories.map(({ value }) => ({
        story_id: value.story_id.trim(),
        title: value.title.trim(),
        story_text: value.story_text.trim(),
        source_requirement_ids: commaSeparated(value.source_requirement_ids),
      })),
      acceptance_criteria: criteria.map(({ value }) => ({
        criterion_id: value.criterion_id.trim(),
        criterion_text: value.criterion_text.trim(),
        source_story_ids: commaSeparated(value.source_story_ids),
        source_requirement_ids: commaSeparated(value.source_requirement_ids),
      })),
      test_cases: testCases.map(({ value }) => ({
        test_case_id: value.test_case_id.trim(),
        title: value.title.trim(),
        test_description: value.test_description.trim(),
        source_criterion_ids: commaSeparated(value.source_criterion_ids),
        source_story_ids: commaSeparated(value.source_story_ids),
        source_requirement_ids: commaSeparated(value.source_requirement_ids),
      })),
      additional_instructions: formData.additional_instructions.trim() || null,
    };

    setIsLoading(true);
    try {
      setResult(await analyzeRequirementTraceability(request));
    } catch (requestError: unknown) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }

  function handleArtifactChange<T extends object>(
    setter: React.Dispatch<React.SetStateAction<Keyed<T>[]>>,
    key: number,
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) {
    updateArtifact(setter, key, event.target.name as keyof T, event.target.value);
  }

  return (
    <main>
      <h1>Requirement Traceability Analyzer</h1>
      <p>
        Analyze traceability from requirements through stories, acceptance
        criteria, and test cases.
      </p>

      <form className="trace-analysis-form" onSubmit={handleSubmit} noValidate>
        <div className="form-field">
          <label htmlFor="trace-analysis-title">Analysis title</label>
          <input
            id="trace-analysis-title"
            name="analysis_title"
            value={formData.analysis_title}
            onChange={updateForm}
            minLength={3}
            maxLength={200}
            required
          />
        </div>
        <div className="form-field">
          <label htmlFor="trace-business-context">Business context</label>
          <textarea
            id="trace-business-context"
            name="business_context"
            value={formData.business_context}
            onChange={updateForm}
            minLength={10}
            maxLength={5000}
            rows={4}
            required
          />
        </div>

        <ArtifactFields
          label="Requirements"
          addLabel="Requirement"
          onAdd={() => addArtifact(setRequirements, createRequirement)}
          count={requirements.length}
          maxCount={100}
        >
          <div className="trace-artifact-list">
            {requirements.map(({ key, value }, index) => (
              <article className="trace-artifact-card" key={key}>
                <div className="trace-artifact-card-heading">
                  <h3>Requirement {index + 1}</h3>
                  <button
                    type="button"
                    disabled={requirements.length <= 1}
                    onClick={() => removeArtifact(setRequirements, key, 1)}
                  >
                    Remove
                  </button>
                </div>
                <div className="form-field">
                  <label htmlFor={`trace-req-id-${key}`}>ID</label>
                  <input id={`trace-req-id-${key}`} name="requirement_id" value={value.requirement_id} onChange={(event) => handleArtifactChange(setRequirements, key, event)} maxLength={100} />
                </div>
                <div className="form-field">
                  <label htmlFor={`trace-req-title-${key}`}>Title</label>
                  <input id={`trace-req-title-${key}`} name="title" value={value.title} onChange={(event) => handleArtifactChange(setRequirements, key, event)} minLength={3} maxLength={200} />
                </div>
                <div className="form-field">
                  <label htmlFor={`trace-req-text-${key}`}>Text</label>
                  <textarea id={`trace-req-text-${key}`} name="requirement_text" value={value.requirement_text} onChange={(event) => handleArtifactChange(setRequirements, key, event)} minLength={10} maxLength={10000} rows={3} />
                </div>
                <div className="form-field">
                  <label htmlFor={`trace-req-category-${key}`}>Category</label>
                  <select id={`trace-req-category-${key}`} name="category" value={value.category} onChange={(event) => handleArtifactChange(setRequirements, key, event)}>
                    {categories.map((category) => <option key={category}>{category}</option>)}
                  </select>
                </div>
              </article>
            ))}
          </div>
        </ArtifactFields>

        <ArtifactFields
          label="User Stories"
          addLabel="User Story"
          onAdd={() => addArtifact(setStories, createUserStory)}
          count={stories.length}
          maxCount={300}
        >
          <div className="trace-artifact-list">
            {stories.map(({ key, value }, index) => (
              <article className="trace-artifact-card" key={key}>
                <div className="trace-artifact-card-heading">
                  <h3>User Story {index + 1}</h3>
                  <button type="button" onClick={() => removeArtifact(setStories, key)}>Remove</button>
                </div>
                <div className="form-field"><label htmlFor={`trace-story-id-${key}`}>Story ID</label><input id={`trace-story-id-${key}`} name="story_id" value={value.story_id} onChange={(event) => handleArtifactChange(setStories, key, event)} maxLength={100} /></div>
                <div className="form-field"><label htmlFor={`trace-story-title-${key}`}>Title</label><input id={`trace-story-title-${key}`} name="title" value={value.title} onChange={(event) => handleArtifactChange(setStories, key, event)} minLength={3} maxLength={200} /></div>
                <div className="form-field"><label htmlFor={`trace-story-text-${key}`}>Story text</label><textarea id={`trace-story-text-${key}`} name="story_text" value={value.story_text} onChange={(event) => handleArtifactChange(setStories, key, event)} minLength={10} maxLength={5000} rows={3} /></div>
                <ReferenceField id={`trace-story-refs-${key}`} label="Source requirement IDs" value={value.source_requirement_ids} onChange={(text) => updateArtifact(setStories, key, "source_requirement_ids", text)} />
              </article>
            ))}
          </div>
        </ArtifactFields>

        <ArtifactFields
          label="Acceptance Criteria"
          addLabel="Acceptance Criterion"
          onAdd={() => addArtifact(setCriteria, createCriterion)}
          count={criteria.length}
          maxCount={500}
        >
          <div className="trace-artifact-list">
            {criteria.map(({ key, value }, index) => (
              <article className="trace-artifact-card" key={key}>
                <div className="trace-artifact-card-heading">
                  <h3>Acceptance Criterion {index + 1}</h3>
                  <button type="button" onClick={() => removeArtifact(setCriteria, key)}>Remove</button>
                </div>
                <div className="form-field"><label htmlFor={`trace-criterion-id-${key}`}>Criterion ID</label><input id={`trace-criterion-id-${key}`} name="criterion_id" value={value.criterion_id} onChange={(event) => handleArtifactChange(setCriteria, key, event)} maxLength={100} /></div>
                <div className="form-field"><label htmlFor={`trace-criterion-text-${key}`}>Criterion text</label><textarea id={`trace-criterion-text-${key}`} name="criterion_text" value={value.criterion_text} onChange={(event) => handleArtifactChange(setCriteria, key, event)} minLength={10} maxLength={5000} rows={3} /></div>
                <ReferenceField id={`trace-criterion-stories-${key}`} label="Source story IDs" value={value.source_story_ids} onChange={(text) => updateArtifact(setCriteria, key, "source_story_ids", text)} />
                <ReferenceField id={`trace-criterion-requirements-${key}`} label="Source requirement IDs" value={value.source_requirement_ids} onChange={(text) => updateArtifact(setCriteria, key, "source_requirement_ids", text)} />
              </article>
            ))}
          </div>
        </ArtifactFields>

        <ArtifactFields
          label="Test Cases"
          addLabel="Test Case"
          onAdd={() => addArtifact(setTestCases, createTestCase)}
          count={testCases.length}
          maxCount={500}
        >
          <div className="trace-artifact-list">
            {testCases.map(({ key, value }, index) => (
              <article className="trace-artifact-card" key={key}>
                <div className="trace-artifact-card-heading">
                  <h3>Test Case {index + 1}</h3>
                  <button type="button" onClick={() => removeArtifact(setTestCases, key)}>Remove</button>
                </div>
                <div className="form-field"><label htmlFor={`trace-test-id-${key}`}>Test-case ID</label><input id={`trace-test-id-${key}`} name="test_case_id" value={value.test_case_id} onChange={(event) => handleArtifactChange(setTestCases, key, event)} maxLength={100} /></div>
                <div className="form-field"><label htmlFor={`trace-test-title-${key}`}>Title</label><input id={`trace-test-title-${key}`} name="title" value={value.title} onChange={(event) => handleArtifactChange(setTestCases, key, event)} minLength={3} maxLength={200} /></div>
                <div className="form-field"><label htmlFor={`trace-test-description-${key}`}>Description</label><textarea id={`trace-test-description-${key}`} name="test_description" value={value.test_description} onChange={(event) => handleArtifactChange(setTestCases, key, event)} minLength={10} maxLength={5000} rows={3} /></div>
                <ReferenceField id={`trace-test-criteria-${key}`} label="Source criterion IDs" value={value.source_criterion_ids} onChange={(text) => updateArtifact(setTestCases, key, "source_criterion_ids", text)} />
                <ReferenceField id={`trace-test-stories-${key}`} label="Source story IDs" value={value.source_story_ids} onChange={(text) => updateArtifact(setTestCases, key, "source_story_ids", text)} />
                <ReferenceField id={`trace-test-requirements-${key}`} label="Source requirement IDs" value={value.source_requirement_ids} onChange={(text) => updateArtifact(setTestCases, key, "source_requirement_ids", text)} />
              </article>
            ))}
          </div>
        </ArtifactFields>

        <div className="form-field">
          <label htmlFor="trace-additional-instructions">Additional instructions</label>
          <textarea id="trace-additional-instructions" name="additional_instructions" value={formData.additional_instructions} onChange={updateForm} maxLength={1000} rows={3} />
        </div>

        <button type="submit" disabled={isLoading}>
          {isLoading ? "Analyzing Traceability..." : "Analyze Traceability"}
        </button>
        {isLoading && <p className="loading-state" role="status" aria-live="polite">Analyzing Traceability...</p>}
      </form>

      {error && <section className="error-message" role="alert"><h2>Traceability analysis failed</h2><p>{error}</p></section>}
      {result && <RequirementTraceabilityResult result={result} />}
    </main>
  );
}
