import type {
  AcceptanceCriteriaResponse,
  CoverageEntry,
  GeneratedAcceptanceCriterion,
} from "../types/acceptanceCriteria";

interface AcceptanceCriteriaResultProps {
  result: AcceptanceCriteriaResponse;
}

interface ListSectionProps {
  title: string;
  items: string[];
  emptyMessage: string;
}

function ListSection({
  title,
  items,
  emptyMessage,
}: ListSectionProps) {
  return (
    <section className="result-section">
      <h2>{title}</h2>
      {items.length > 0 ? (
        <ul>
          {items.map((item, index) => (
            <li key={`${index}-${item}`}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="empty-message">{emptyMessage}</p>
      )}
    </section>
  );
}

function CriterionCard({
  criterion,
}: {
  criterion: GeneratedAcceptanceCriterion;
}) {
  return (
    <article className="acceptance-criterion-card">
      <div className="acceptance-criterion-heading">
        <div>
          <p className="story-id">{criterion.criterion_id}</p>
          <h3>{criterion.title}</h3>
        </div>
        <span
          className={`criterion-type-badge criterion-type-${criterion.criterion_type
            .toLowerCase()
            .replaceAll(" ", "-")}`}
        >
          {criterion.criterion_type}
        </span>
      </div>

      <dl className="criterion-steps">
        <div>
          <dt>Given</dt>
          <dd>{criterion.given}</dd>
        </div>
        <div>
          <dt>When</dt>
          <dd>{criterion.when}</dd>
        </div>
        <div>
          <dt>Then</dt>
          <dd>{criterion.then}</dd>
        </div>
      </dl>

      <p>
        <strong>Complete criterion:</strong> {criterion.criterion}
      </p>

      <div className="criterion-meta-grid">
        <div>
          <h4>Source References</h4>
          {renderStringList(
            criterion.source_references,
            "No source references identified."
          )}
        </div>
        <div>
          <h4>Business Rules Applied</h4>
          {renderStringList(
            criterion.business_rules_applied,
            "No business rules applied."
          )}
        </div>
      </div>

      <div className="criterion-review-grid">
        <div className={criterion.testable ? "review-pass" : "review-needed"}>
          <strong>Testability: {criterion.testable ? "Testable" : "Needs Review"}</strong>
          <p>{criterion.testability_reason || "No testability reason provided."}</p>
        </div>
        <div
          className={
            criterion.requires_human_validation
              ? "review-needed"
              : "review-pass"
          }
        >
          <strong>
            Human validation:{" "}
            {criterion.requires_human_validation ? "Required" : "Not required"}
          </strong>
          <p>
            {criterion.validation_reason || "No additional validation reason."}
          </p>
        </div>
      </div>
    </article>
  );
}

function renderStringList(items: string[], emptyMessage: string) {
  return items.length > 0 ? (
    <ul className="compact-list">
      {items.map((item, index) => (
        <li key={`${index}-${item}`}>{item}</li>
      ))}
    </ul>
  ) : (
    <p className="empty-message">{emptyMessage}</p>
  );
}

function CoverageCard({ entry }: { entry: CoverageEntry }) {
  const statusClass = entry.status.toLowerCase().replaceAll(" ", "-");

  return (
    <article className="coverage-entry">
      <div className="coverage-heading">
        <h3>{entry.coverage_area}</h3>
        <span className={`coverage-status coverage-${statusClass}`}>
          {entry.status}
        </span>
      </div>
      <h4>Criterion IDs</h4>
      {renderStringList(entry.criterion_ids, "No criteria linked.")}
      <p>
        <strong>Notes:</strong> {entry.notes || "No notes provided."}
      </p>
    </article>
  );
}

export default function AcceptanceCriteriaResult({
  result,
}: AcceptanceCriteriaResultProps) {
  return (
    <div className="acceptance-criteria-result">
      <section className="result-section">
        <h2>Story Summary</h2>
        <p>{result.story_summary}</p>
        <dl className="story-summary-details">
          <div>
            <dt>Confirmed actor</dt>
            <dd>{result.confirmed_actor || "Not confirmed."}</dd>
          </div>
          <div>
            <dt>Confirmed goal</dt>
            <dd>{result.confirmed_goal || "Not confirmed."}</dd>
          </div>
          <div>
            <dt>Confirmed business value</dt>
            <dd>{result.confirmed_business_value || "Not confirmed."}</dd>
          </div>
        </dl>
      </section>

      <ListSection
        title="Preconditions"
        items={result.preconditions}
        emptyMessage="No preconditions identified."
      />

      <section className="result-section">
        <h2>Generated Criteria</h2>
        {result.generated_criteria.length > 0 ? (
          <div className="generated-criteria">
            {result.generated_criteria.map((criterion) => (
              <CriterionCard
                key={criterion.criterion_id}
                criterion={criterion}
              />
            ))}
          </div>
        ) : (
          <p className="empty-message">No acceptance criteria generated.</p>
        )}
      </section>

      <section className="result-section">
        <h2>Coverage</h2>
        {result.coverage.length > 0 ? (
          <div className="coverage-list">
            {result.coverage.map((entry, index) => (
              <CoverageCard
                key={`${entry.coverage_area}-${index}`}
                entry={entry}
              />
            ))}
          </div>
        ) : (
          <p className="empty-message">No coverage entries provided.</p>
        )}
      </section>

      <ListSection
        title="Assumptions"
        items={result.assumptions}
        emptyMessage="No assumptions identified."
      />
      <ListSection
        title="Ambiguities"
        items={result.ambiguities}
        emptyMessage="No ambiguities identified."
      />
      <ListSection
        title="Missing Information"
        items={result.missing_information}
        emptyMessage="No missing information identified."
      />
      <ListSection
        title="Risks"
        items={result.risks}
        emptyMessage="No risks identified."
      />
      <ListSection
        title="Duplicate Existing Criteria"
        items={result.duplicate_existing_criteria}
        emptyMessage="No duplicate existing criteria identified."
      />
      <ListSection
        title="Human Validation Required"
        items={result.human_validation_required}
        emptyMessage="No human validation items identified."
      />
    </div>
  );
}
