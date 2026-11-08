import type {
  DuplicateAnalysisResponse,
  DuplicateFinding,
  RequirementRelationship,
} from "../types/duplicateRequirement";

interface DuplicateRequirementResultProps {
  result: DuplicateAnalysisResponse;
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

function FindingCard({ finding }: { finding: DuplicateFinding }) {
  const classificationClass = finding.classification
    .toLowerCase()
    .replaceAll(" ", "-");
  const requirementIds = nonEmpty(finding.requirement_ids);
  const sharedMeaning = nonEmpty(finding.shared_meaning);
  const sourceReferences = nonEmpty(finding.source_references);
  const validationQuestions = nonEmpty(finding.validation_questions);

  return (
    <article className="duplicate-finding-card">
      <div className="duplicate-finding-heading">
        <div>
          <p className="duplicate-finding-id">{finding.finding_id}</p>
          <h3>{finding.classification}</h3>
        </div>
        <div className="duplicate-finding-badges">
          <span
            className={`duplicate-classification classification-${classificationClass}`}
          >
            {finding.classification}
          </span>
          <span
            className={`duplicate-confidence confidence-${finding.confidence.toLowerCase()}`}
          >
            {finding.confidence} confidence
          </span>
        </div>
      </div>

      <p>
        <strong>Requirement IDs:</strong>{" "}
        {requirementIds.length > 0 ? requirementIds.join(", ") : "None provided."}
      </p>
      <p>{finding.explanation}</p>

      <div className="duplicate-finding-details">
        <section>
          <h4>Shared meaning</h4>
          {sharedMeaning.length > 0 ? (
            <ul className="compact-list">
              {sharedMeaning.map((item, index) => (
                <li key={`${index}-${item}`}>{item}</li>
              ))}
            </ul>
          ) : (
            <p className="empty-message">No shared meaning identified.</p>
          )}
        </section>
        <section>
          <h4>Unique information per requirement</h4>
          {finding.differences.length > 0 ? (
            <div className="requirement-differences">
              {finding.differences.map((difference, index) => {
                const uniqueInformation = nonEmpty(
                  difference.unique_information
                );
                return (
                  <article
                    className="requirement-difference"
                    key={`${difference.requirement_id}-${index}`}
                  >
                    <h5>{difference.requirement_id}</h5>
                    {uniqueInformation.length > 0 ? (
                      <ul className="compact-list">
                        {uniqueInformation.map((item, itemIndex) => (
                          <li key={`${itemIndex}-${item}`}>{item}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="empty-message">
                        No unique information identified.
                      </p>
                    )}
                  </article>
                );
              })}
            </div>
          ) : (
            <p className="empty-message">
              No requirement-specific differences identified.
            </p>
          )}
        </section>
      </div>

      <section
        className={
          finding.conflict_detected
            ? "duplicate-conflict conflict-detected"
            : "duplicate-conflict no-conflict"
        }
      >
        <strong>
          Conflict: {finding.conflict_detected ? "Detected" : "Not detected"}
        </strong>
        {finding.conflict_detected ? (
          <p>{finding.conflict_description || "Conflict details not provided."}</p>
        ) : (
          <p>No conflict description provided.</p>
        )}
      </section>

      <div className="duplicate-action">
        <p>
          <strong>Recommended action:</strong> {finding.recommended_action}
        </p>
        <p>
          <strong>Rationale:</strong> {finding.action_rationale}
        </p>
      </div>

      <section className="consolidated-draft">
        <h4>Consolidated requirement</h4>
        {finding.consolidated_requirement?.trim() ? (
          <p>{finding.consolidated_requirement}</p>
        ) : (
          <p className="empty-message">
            No consolidated requirement proposed.
          </p>
        )}
      </section>

      <div className="duplicate-finding-details">
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
        <section>
          <h4>Validation questions</h4>
          {validationQuestions.length > 0 ? (
            <ol>
              {validationQuestions.map((question, index) => (
                <li key={`${index}-${question}`}>{question}</li>
              ))}
            </ol>
          ) : (
            <p className="empty-message">No validation questions provided.</p>
          )}
        </section>
      </div>

      <p>
        <strong>Human validation:</strong>{" "}
        {finding.requires_human_validation ? "Required" : "Not required"}
      </p>
    </article>
  );
}

function RelationshipCard({
  relationship,
}: {
  relationship: RequirementRelationship;
}) {
  const relatedIds = nonEmpty(relationship.related_requirement_ids);
  const findingIds = nonEmpty(relationship.covered_by_finding_ids);

  return (
    <article className="requirement-relationship">
      <div className="relationship-heading">
        <h3>{relationship.requirement_id}</h3>
        <span
          className={
            relationship.standalone
              ? "standalone-status standalone"
              : "standalone-status related"
          }
        >
          {relationship.standalone ? "Standalone" : "Related"}
        </span>
      </div>
      <dl className="relationship-facts">
        <div>
          <dt>Related requirement IDs</dt>
          <dd>
            {relatedIds.length > 0 ? relatedIds.join(", ") : "None identified."}
          </dd>
        </div>
        <div>
          <dt>Finding IDs</dt>
          <dd>
            {findingIds.length > 0 ? findingIds.join(", ") : "None identified."}
          </dd>
        </div>
      </dl>
      <p>{relationship.notes.trim() || "No relationship notes provided."}</p>
    </article>
  );
}

export default function DuplicateRequirementResult({
  result,
}: DuplicateRequirementResultProps) {
  return (
    <div className="duplicate-analysis-result">
      <section className="result-section">
        <h2>Analysis Summary</h2>
        <p>{result.analysis_summary}</p>
      </section>

      <section className="result-section">
        <h2>Duplicate Counts</h2>
        <dl className="duplicate-counts">
          <div>
            <dt>Exact duplicates</dt>
            <dd>{result.exact_duplicate_count}</dd>
          </div>
          <div>
            <dt>Semantic duplicates</dt>
            <dd>{result.semantic_duplicate_count}</dd>
          </div>
          <div>
            <dt>Partial overlaps</dt>
            <dd>{result.partial_overlap_count}</dd>
          </div>
          <div>
            <dt>Distinct requirements</dt>
            <dd>{result.distinct_requirement_count}</dd>
          </div>
        </dl>
      </section>

      <section className="result-section">
        <h2>Findings</h2>
        {result.findings.length > 0 ? (
          <div className="duplicate-findings">
            {result.findings.map((finding) => (
              <FindingCard key={finding.finding_id} finding={finding} />
            ))}
          </div>
        ) : (
          <p className="empty-message">No duplicate findings identified.</p>
        )}
      </section>

      <section className="result-section">
        <h2>Requirement Relationships</h2>
        {result.requirement_relationships.length > 0 ? (
          <div className="requirement-relationships">
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
        title="Conflicts"
        items={result.conflicts}
        emptyMessage="No conflicts identified."
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
        title="Human Validation Required"
        items={result.human_validation_required}
        emptyMessage="No human validation items identified."
      />
    </div>
  );
}
