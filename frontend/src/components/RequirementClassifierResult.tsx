import type {
  ClassificationLabel,
  ClassifiedRequirement,
  RequirementClassificationResponse,
} from "../types/requirementClassifier";

interface RequirementClassifierResultProps {
  result: RequirementClassificationResponse;
}

interface ListSectionProps {
  title: string;
  items: string[];
  emptyMessage: string;
}

function nonEmpty(items: string[]): string[] {
  return items.filter((item) => item.trim().length > 0);
}

function ListSection({ title, items, emptyMessage }: ListSectionProps) {
  const visibleItems = nonEmpty(items);

  return (
    <section className="result-section">
      <h2>{title}</h2>
      {visibleItems.length > 0 ? (
        <ul className="compact-list">
          {visibleItems.map((item, index) => (
            <li key={`${index}-${item}`}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="empty-message">{emptyMessage}</p>
      )}
    </section>
  );
}

function ClassificationCard({
  classification,
  label,
}: {
  classification: ClassificationLabel;
  label: string;
}) {
  const evidence = classification.evidence.filter(
    (item) => item.evidence_text.trim().length > 0 || item.explanation.trim().length > 0
  );

  return (
    <section className="classifier-label">
      <h4>{label}</h4>
      <div className="classifier-label-badges">
        <span className="classifier-type-badge">
          {classification.requirement_type}
        </span>
        <span className="classifier-subtype-badge">
          {classification.requirement_subtype}
        </span>
        <span
          className={`classifier-confidence confidence-${classification.confidence.toLowerCase()}`}
        >
          {classification.confidence} confidence
        </span>
      </div>
      <p>
        <strong>Rationale:</strong> {classification.rationale}
      </p>
      <div className="classifier-evidence-panel">
        <h5>Evidence</h5>
        {evidence.length > 0 ? (
          evidence.map((item, index) => (
            <article
              className="classifier-evidence-item"
              key={`${index}-${item.evidence_text}`}
            >
              {item.evidence_text.trim() && <blockquote>{item.evidence_text}</blockquote>}
              {item.explanation.trim() && <p>{item.explanation}</p>}
            </article>
          ))
        ) : (
          <p className="empty-message">No evidence provided.</p>
        )}
      </div>
    </section>
  );
}

function ClassifiedRequirementCard({
  item,
}: {
  item: ClassifiedRequirement;
}) {
  const mixed = item.classification_status === "Mixed Requirement";
  const missingInformation = nonEmpty(item.missing_information);
  const clarificationQuestions = nonEmpty(item.clarification_questions);
  const statusClass = item.requirement_quality.toLowerCase().replaceAll(" ", "-");
  const priorityClass = item.suggested_priority.toLowerCase();

  return (
    <article className="classified-requirement-card">
      <div className="classified-requirement-heading">
        <div>
          <p className="classified-requirement-id">{item.requirement_id}</p>
          <h3>{item.original_title}</h3>
        </div>
        <div className="classifier-status-badges">
          <span
            className={`classifier-quality-badge quality-${statusClass}`}
          >
            {item.requirement_quality}
          </span>
          <span
            className={`classifier-priority-badge priority-${priorityClass}`}
          >
            {item.suggested_priority} priority
          </span>
        </div>
      </div>

      {mixed && (
        <p className="classifier-mixed-warning">
          This requirement contains multiple requirements and may need to be
          split.
        </p>
      )}

      <section className="classifier-original">
        <h4>Original requirement text</h4>
        <p>{item.original_text}</p>
      </section>

      <ClassificationCard
        classification={item.primary_classification}
        label="Primary classification"
      />

      <section className="classifier-secondary">
        <h4>Secondary classifications</h4>
        {item.secondary_classifications.length > 0 ? (
          item.secondary_classifications.map((classification, index) => (
            <ClassificationCard
              key={`${classification.requirement_type}-${classification.requirement_subtype}-${index}`}
              classification={classification}
              label={`Secondary classification ${index + 1}`}
            />
          ))
        ) : (
          <p className="empty-message">No secondary classifications.</p>
        )}
      </section>

      <dl className="classifier-facts">
        <div>
          <dt>Classification status</dt>
          <dd>{item.classification_status}</dd>
        </div>
        <div>
          <dt>Quality explanation</dt>
          <dd>{item.quality_explanation}</dd>
        </div>
        <div>
          <dt>Priority rationale</dt>
          <dd>{item.priority_rationale}</dd>
        </div>
        <div>
          <dt>Contains multiple requirements</dt>
          <dd>{item.contains_multiple_requirements ? "Yes" : "No"}</dd>
        </div>
        <div>
          <dt>Splitting recommended</dt>
          <dd>{item.splitting_recommended ? "Yes" : "No"}</dd>
        </div>
        <div>
          <dt>Splitting reason</dt>
          <dd>
            {item.splitting_reason?.trim() || "No splitting reason provided."}
          </dd>
        </div>
        <div>
          <dt>Human validation</dt>
          <dd>
            {item.requires_human_validation ? "Required" : "Not required"}
          </dd>
        </div>
        <div>
          <dt>Validation owner</dt>
          <dd>{item.validation_owner.trim() || "No owner provided."}</dd>
        </div>
      </dl>

      <div className="classifier-follow-up">
        <section>
          <h4>Missing information</h4>
          {missingInformation.length > 0 ? (
            <ul className="compact-list">
              {missingInformation.map((entry, index) => (
                <li key={`${index}-${entry}`}>{entry}</li>
              ))}
            </ul>
          ) : (
            <p className="empty-message">No missing information identified.</p>
          )}
        </section>
        <section>
          <h4>Clarification questions</h4>
          {clarificationQuestions.length > 0 ? (
            <ul className="compact-list">
              {clarificationQuestions.map((question, index) => (
                <li key={`${index}-${question}`}>{question}</li>
              ))}
            </ul>
          ) : (
            <p className="empty-message">No clarification questions.</p>
          )}
        </section>
      </div>
    </article>
  );
}

export default function RequirementClassifierResult({
  result,
}: RequirementClassifierResultProps) {
  return (
    <div className="result-container requirement-classifier-result">
      <section className="result-section">
        <h2>Analysis Summary</h2>
        <p>{result.analysis_summary}</p>
      </section>

      <section className="result-section">
        <h2>Classification Summary</h2>
        {result.classification_summary.length > 0 ? (
          <div className="classification-summary">
            {result.classification_summary.map((entry, index) => {
              const requirementIds = nonEmpty(entry.requirement_ids);
              return (
                <article
                  className="classification-summary-entry"
                  key={`${entry.requirement_type}-${index}`}
                >
                  <div className="classifier-label-badges">
                    <span className="classifier-type-badge">
                      {entry.requirement_type}
                    </span>
                    <strong>{entry.count}</strong>
                  </div>
                  {requirementIds.length > 0 ? (
                    <ul className="compact-list">
                      {requirementIds.map((id, idIndex) => (
                        <li key={`${idIndex}-${id}`}>{id}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="empty-message">No requirement IDs listed.</p>
                  )}
                </article>
              );
            })}
          </div>
        ) : (
          <p className="empty-message">No classification summary provided.</p>
        )}
      </section>

      <ListSection
        title="Mixed Requirement IDs"
        items={result.mixed_requirement_ids}
        emptyMessage="No mixed requirements identified."
      />
      <ListSection
        title="Unclear Requirement IDs"
        items={result.unclear_requirement_ids}
        emptyMessage="No unclear requirements identified."
      />

      <section className="result-section">
        <h2>Classified Requirements</h2>
        {result.classified_requirements.length > 0 ? (
          <div className="classified-requirements">
            {result.classified_requirements.map((item, index) => (
              <ClassifiedRequirementCard
                key={`${item.requirement_id}-${index}`}
                item={item}
              />
            ))}
          </div>
        ) : (
          <p className="empty-message">No classified requirements provided.</p>
        )}
      </section>

      <ListSection
        title="Assumptions"
        items={result.assumptions}
        emptyMessage="No assumptions identified."
      />
      <ListSection
        title="Risks"
        items={result.risks}
        emptyMessage="No risks identified."
      />
      <ListSection
        title="Recommended Next Actions"
        items={result.recommended_next_actions}
        emptyMessage="No recommended next actions provided."
      />
      <ListSection
        title="Human Validation Required"
        items={result.human_validation_required}
        emptyMessage="No human validation items identified."
      />
    </div>
  );
}
