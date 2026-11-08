import type {
  ConflictAnalysisResponse,
  ConflictDifference,
  ConflictFinding,
  RequirementConflictRelationship,
} from "../types/requirementConflict";

interface RequirementConflictResultProps {
  result: ConflictAnalysisResponse;
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

function DifferenceCard({ difference }: { difference: ConflictDifference }) {
  const requirementValues = difference.requirement_values.filter(
    (item) =>
      item.requirement_id.trim().length > 0 && item.value.trim().length > 0
  );

  return (
    <article className="conflict-difference">
      <h5>{difference.comparison_area}</h5>
      {requirementValues.length > 0 ? (
        <dl className="conflict-requirement-values">
          {requirementValues.map((item, index) => (
            <div key={`${item.requirement_id}-${index}`}>
              <dt>{item.requirement_id}</dt>
              <dd>{item.value}</dd>
            </div>
          ))}
        </dl>
      ) : (
        <p className="empty-message">No requirement values provided.</p>
      )}
      <p>
        <strong>Conflict reason:</strong>{" "}
        {difference.conflict_reason.trim() || "No conflict reason provided."}
      </p>
    </article>
  );
}

function FindingCard({ finding }: { finding: ConflictFinding }) {
  const severityClass = finding.severity.toLowerCase();
  const requirementIds = nonEmpty(finding.requirement_ids);
  const statements = finding.conflicting_statements.filter(
    (item) =>
      item.requirement_id.trim().length > 0 && item.value.trim().length > 0
  );
  const clarificationQuestions = nonEmpty(finding.clarification_questions);
  const sourceReferences = nonEmpty(finding.source_references);

  return (
    <article className="conflict-finding">
      <div className="conflict-finding-heading">
        <div>
          <p className="conflict-finding-id">{finding.conflict_id}</p>
          <h3>{finding.summary}</h3>
        </div>
        <div className="conflict-finding-badges">
          <span
            className={`conflict-type-badge conflict-type-${finding.conflict_type
              .toLowerCase()
              .replaceAll(" ", "-")}`}
          >
            {finding.conflict_type}
          </span>
          <span className={`conflict-severity-badge severity-${severityClass}`}>
            {finding.severity}
          </span>
        </div>
      </div>

      <p>
        <strong>Requirement IDs:</strong>{" "}
        {requirementIds.length > 0 ? requirementIds.join(", ") : "None provided."}
      </p>
      <p>{finding.explanation}</p>

      <section className="conflicting-statements">
        <h4>Exact conflicting statements</h4>
        {statements.length > 0 ? (
          <div className="conflict-statement-list">
            {statements.map((item, index) => (
              <article
                className="conflict-statement"
                key={`${item.requirement_id}-${index}`}
              >
                <h5>{item.requirement_id}</h5>
                <p>{item.value}</p>
              </article>
            ))}
          </div>
        ) : (
          <p className="empty-message">No conflicting statements provided.</p>
        )}
      </section>

      <section className="conflict-differences">
        <h4>Differences by comparison area</h4>
        {finding.differences.length > 0 ? (
          finding.differences.map((difference, index) => (
            <DifferenceCard
              key={`${difference.comparison_area}-${index}`}
              difference={difference}
            />
          ))
        ) : (
          <p className="empty-message">No comparison differences identified.</p>
        )}
      </section>

      <dl className="conflict-impact-grid">
        <div>
          <dt>Business impact</dt>
          <dd>{finding.business_impact}</dd>
        </div>
        <div>
          <dt>Implementation impact</dt>
          <dd>{finding.implementation_impact}</dd>
        </div>
        <div>
          <dt>Testing impact</dt>
          <dd>{finding.testing_impact}</dd>
        </div>
      </dl>

      <p className="conflict-resolution-status">
        <strong>Resolution status:</strong> {finding.resolution_status}
      </p>

      <section className="conflict-recommended-action">
        <h4>Recommended action: {finding.recommended_action}</h4>
        <p>{finding.action_rationale}</p>
      </section>

      <div className="conflict-finding-details">
        <section>
          <h4>Clarification questions</h4>
          {clarificationQuestions.length > 0 ? (
            <ul className="compact-list">
              {clarificationQuestions.map((question, index) => (
                <li key={`${index}-${question}`}>{question}</li>
              ))}
            </ul>
          ) : (
            <p className="empty-message">No clarification questions provided.</p>
          )}
        </section>
        <section>
          <h4>Source references</h4>
          {sourceReferences.length > 0 ? (
            <ul className="compact-list">
              {sourceReferences.map((reference, index) => (
                <li key={`${index}-${reference}`}>{reference}</li>
              ))}
            </ul>
          ) : (
            <p className="empty-message">No source references provided.</p>
          )}
        </section>
      </div>

      <dl className="conflict-owner-grid">
        <div>
          <dt>Human validation</dt>
          <dd>
            {finding.requires_human_validation ? "Required" : "Not required"}
          </dd>
        </div>
        <div>
          <dt>Suggested owner</dt>
          <dd>{finding.suggested_owner}</dd>
        </div>
      </dl>
    </article>
  );
}

function RelationshipCard({
  relationship,
}: {
  relationship: RequirementConflictRelationship;
}) {
  const conflictingRequirementIds = nonEmpty(
    relationship.conflicting_requirement_ids
  );
  const conflictIds = nonEmpty(relationship.conflict_ids);

  return (
    <article className="conflict-relationship">
      <h3>{relationship.requirement_id}</h3>
      <dl className="conflict-relationship-facts">
        <div>
          <dt>Conflicting requirement IDs</dt>
          <dd>
            {conflictingRequirementIds.length > 0
              ? conflictingRequirementIds.join(", ")
              : "None identified."}
          </dd>
        </div>
        <div>
          <dt>Conflict IDs</dt>
          <dd>
            {conflictIds.length > 0
              ? conflictIds.join(", ")
              : "No related conflict IDs."}
          </dd>
        </div>
        <div>
          <dt>Conflict-free</dt>
          <dd>{relationship.conflict_free ? "Yes" : "No"}</dd>
        </div>
      </dl>
      <p>{relationship.notes.trim() || "No relationship notes provided."}</p>
    </article>
  );
}

export default function RequirementConflictResult({
  result,
}: RequirementConflictResultProps) {
  return (
    <div className="result-container requirement-conflict-result">
      <section className="result-section">
        <h2>Analysis Summary</h2>
        <p>{result.analysis_summary}</p>
      </section>

      <section className="result-section">
        <h2>Confirmed Information</h2>
        {nonEmpty(result.confirmed_information).length > 0 ? (
          <ul className="compact-list">
            {nonEmpty(result.confirmed_information).map((item, index) => (
              <li key={`${index}-${item}`}>{item}</li>
            ))}
          </ul>
        ) : (
          <p className="empty-message">No confirmed information provided.</p>
        )}
      </section>

      <section className="result-section">
        <h2>Conflict Summary</h2>
        <dl className="critical-conflict-summary">
          <div className="critical-conflict-count">
            <dt>Critical conflicts</dt>
            <dd>{result.critical_conflict_count}</dd>
          </div>
          <div>
            <dt>High conflicts</dt>
            <dd>{result.high_conflict_count}</dd>
          </div>
          <div>
            <dt>Medium conflicts</dt>
            <dd>{result.medium_conflict_count}</dd>
          </div>
          <div>
            <dt>Low conflicts</dt>
            <dd>{result.low_conflict_count}</dd>
          </div>
          <div>
            <dt>Conflict-free requirements</dt>
            <dd>{result.conflict_free_requirement_count}</dd>
          </div>
        </dl>
      </section>

      <section className="result-section">
        <h2>Conflict Findings</h2>
        {result.conflict_findings.length > 0 ? (
          <div className="conflict-findings">
            {result.conflict_findings.map((finding) => (
              <FindingCard key={finding.conflict_id} finding={finding} />
            ))}
          </div>
        ) : (
          <p className="empty-message">No conflicts identified.</p>
        )}
      </section>

      <section className="result-section">
        <h2>Requirement Relationships</h2>
        {result.requirement_relationships.length > 0 ? (
          <div className="conflict-relationships">
            {result.requirement_relationships.map((relationship, index) => (
              <RelationshipCard
                key={`${relationship.requirement_id}-${index}`}
                relationship={relationship}
              />
            ))}
          </div>
        ) : (
          <p className="empty-message">
            No requirement relationships provided.
          </p>
        )}
      </section>

      <ListSection
        title="Unresolved Decisions"
        items={result.unresolved_decisions}
        emptyMessage="No unresolved decisions."
      />
      <ListSection
        title="Assumptions"
        items={result.assumptions}
        emptyMessage="No assumptions identified."
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
