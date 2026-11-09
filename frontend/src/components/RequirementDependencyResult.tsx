import type {
  DependencyEvidence,
  DependencySummaryEntry,
  DeliveryStage,
  RequirementDependencyFinding,
  RequirementDependencyRelationship,
  RequirementDependencyResponse,
} from "../types/requirementDependency";

interface RequirementDependencyResultProps {
  result: RequirementDependencyResponse;
}

interface ListSectionProps {
  title: string;
  items: string[];
  emptyMessage: string;
}

function nonEmpty(items: string[]): string[] {
  return items.filter((item) => item.trim().length > 0);
}

function display(value: string, fallback = "Not provided."): string {
  return value.trim() || fallback;
}

function classSlug(value: string): string {
  return value.toLowerCase().replaceAll(/[^a-z]+/g, "-");
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

function EvidenceCard({ evidence }: { evidence: DependencyEvidence }) {
  return (
    <article className="dependency-evidence-card">
      <dl>
        <div>
          <dt>Source reference</dt>
          <dd>{display(evidence.source_reference)}</dd>
        </div>
        <div>
          <dt>Evidence</dt>
          <dd>{display(evidence.evidence_text)}</dd>
        </div>
        <div>
          <dt>Explanation</dt>
          <dd>{display(evidence.explanation)}</dd>
        </div>
      </dl>
    </article>
  );
}

function FindingCard({ finding }: { finding: RequirementDependencyFinding }) {
  const evidence = finding.evidence.filter(
    (item) =>
      item.source_reference.trim() ||
      item.evidence_text.trim() ||
      item.explanation.trim()
  );

  return (
    <article className="dependency-finding-card">
      <div className="dependency-finding-heading">
        <div>
          <p className="dependency-finding-id">
            {display(finding.dependency_id)}
          </p>
          <h3>
            {display(finding.source_requirement_id)}{" "}
            <span className="dependency-direction" aria-label="depends on">
              &rarr;
            </span>{" "}
            {display(finding.target_requirement_id)}
          </h3>
        </div>
        <div className="dependency-badges">
          <span className="dependency-type">{finding.dependency_type}</span>
          <span
            className={`dependency-strength strength-${classSlug(
              finding.dependency_strength
            )}`}
          >
            {finding.dependency_strength}
          </span>
          <span
            className={`dependency-status status-${classSlug(finding.status)}`}
          >
            {finding.status}
          </span>
          <span
            className={`dependency-confidence confidence-${classSlug(
              finding.confidence
            )}`}
          >
            {finding.confidence} confidence
          </span>
        </div>
      </div>

      <p>{display(finding.description)}</p>
      <dl className="dependency-facts">
        <div>
          <dt>Source requirement</dt>
          <dd>{display(finding.source_requirement_id)}</dd>
        </div>
        <div>
          <dt>Target requirement</dt>
          <dd>{display(finding.target_requirement_id)}</dd>
        </div>
        <div>
          <dt>Blocks target</dt>
          <dd>{finding.blocks_target ? "Yes" : "No"}</dd>
        </div>
        <div>
          <dt>Human validation</dt>
          <dd>{finding.requires_human_validation ? "Required" : "Not required"}</dd>
        </div>
        <div>
          <dt>Suggested owner</dt>
          <dd>{display(finding.suggested_owner)}</dd>
        </div>
      </dl>

      <section className="dependency-subsection">
        <h4>Rationale</h4>
        <p>{display(finding.rationale)}</p>
      </section>
      <div className="dependency-detail-grid">
        <section>
          <h4>Delivery impact</h4>
          <p>{display(finding.delivery_impact)}</p>
        </section>
        <section>
          <h4>Testing impact</h4>
          <p>{display(finding.testing_impact)}</p>
        </section>
      </div>

      <section className="dependency-subsection">
        <h4>Evidence</h4>
        {evidence.length > 0 ? (
          <div className="dependency-evidence-list">
            {evidence.map((item, index) => (
              <EvidenceCard key={`${item.source_reference}-${index}`} evidence={item} />
            ))}
          </div>
        ) : (
          <p className="empty-message">No evidence provided.</p>
        )}
      </section>
      <ListSection
        title="Missing information"
        items={finding.missing_information}
        emptyMessage="No missing information identified."
      />
      <ListSection
        title="Clarification questions"
        items={finding.clarification_questions}
        emptyMessage="No clarification questions identified."
      />
    </article>
  );
}

function RelationshipCard({
  relationship,
}: {
  relationship: RequirementDependencyRelationship;
}) {
  const dependsOn = nonEmpty(relationship.depends_on_requirement_ids);
  const requiredBy = nonEmpty(relationship.required_by_requirement_ids);
  const dependencyIds = nonEmpty(relationship.dependency_ids);
  const blockingReasons = nonEmpty(relationship.blocking_reasons);

  return (
    <article
      className={`dependency-relationship-card${relationship.blocked ? " is-blocked" : ""}`}
    >
      <div className="dependency-relationship-heading">
        <h3>{display(relationship.requirement_id)}</h3>
        <div className="dependency-badges">
          <span className={`dependency-blocking ${relationship.blocked ? "is-blocked" : ""}`}>
            {relationship.blocked ? "Blocked" : "Not blocked"}
          </span>
          <span className="dependency-standalone">
            {relationship.standalone ? "Standalone" : "Has relationships"}
          </span>
        </div>
      </div>
      <dl className="dependency-facts">
        <div>
          <dt>Depends on IDs</dt>
          <dd>{dependsOn.length > 0 ? dependsOn.join(", ") : "No dependencies."}</dd>
        </div>
        <div>
          <dt>Required by IDs</dt>
          <dd>{requiredBy.length > 0 ? requiredBy.join(", ") : "No dependent requirements."}</dd>
        </div>
        <div>
          <dt>Dependency IDs</dt>
          <dd>{dependencyIds.length > 0 ? dependencyIds.join(", ") : "No dependency findings."}</dd>
        </div>
      </dl>
      <section className="dependency-subsection">
        <h4>Blocking reasons</h4>
        {blockingReasons.length > 0 ? (
          <ul className="compact-list">
            {blockingReasons.map((reason, index) => (
              <li key={`${index}-${reason}`}>{reason}</li>
            ))}
          </ul>
        ) : (
          <p className="empty-message">No blocking reasons provided.</p>
        )}
      </section>
      <p className="dependency-relationship-notes">
        <strong>Notes:</strong> {display(relationship.notes)}
      </p>
    </article>
  );
}

function SummaryCard({ entry }: { entry: DependencySummaryEntry }) {
  const dependencyIds = nonEmpty(entry.dependency_ids);

  return (
    <article className="dependency-summary-card">
      <span className="dependency-type">{entry.dependency_type}</span>
      <p className="dependency-summary-count">{entry.count}</p>
      <p>
        {dependencyIds.length > 0
          ? dependencyIds.join(", ")
          : "No dependency IDs."}
      </p>
    </article>
  );
}

function DeliveryStageCard({ stage }: { stage: DeliveryStage }) {
  const requirementIds = nonEmpty(stage.requirement_ids);

  return (
    <article className="dependency-delivery-stage">
      <div className="dependency-stage-number">{stage.stage_number}</div>
      <div>
        <h3>{display(stage.stage_name)}</h3>
        <p>
          <strong>Requirements:</strong>{" "}
          {requirementIds.length > 0
            ? requirementIds.join(", ")
            : "No requirement IDs provided."}
        </p>
        <p>
          <strong>Rationale:</strong> {display(stage.rationale)}
        </p>
      </div>
    </article>
  );
}

export default function RequirementDependencyResult({
  result,
}: RequirementDependencyResultProps) {
  const readinessClass = classSlug(result.readiness_status);
  const blockingIds = nonEmpty(result.blocking_requirement_ids);
  const circularPaths = nonEmpty(result.circular_dependency_paths);

  return (
    <div className="result-container requirement-dependency-result">
      <section className="result-section">
        <h2>Analysis Summary</h2>
        <p>{display(result.analysis_summary)}</p>
      </section>

      <ListSection
        title="Confirmed Information"
        items={result.confirmed_information}
        emptyMessage="No confirmed information provided."
      />

      <section className="result-section">
        <div className="dependency-summary-heading">
          <h2>Readiness Status</h2>
          <span className={`dependency-readiness readiness-${readinessClass}`}>
            {result.readiness_status}
          </span>
        </div>
      </section>

      <section className="result-section">
        <h2>Dependency Findings</h2>
        {result.dependency_findings.length > 0 ? (
          <div className="dependency-finding-list">
            {result.dependency_findings.map((finding, index) => (
              <FindingCard
                key={`${finding.dependency_id}-${index}`}
                finding={finding}
              />
            ))}
          </div>
        ) : (
          <p className="empty-message">No dependency findings provided.</p>
        )}
      </section>

      <section className="result-section">
        <h2>Requirement Relationships</h2>
        {result.requirement_relationships.length > 0 ? (
          <div className="dependency-relationship-list">
            {result.requirement_relationships.map((relationship, index) => (
              <RelationshipCard
                key={`${relationship.requirement_id}-${index}`}
                relationship={relationship}
              />
            ))}
          </div>
        ) : (
          <p className="empty-message">No requirement relationships provided.</p>
        )}
      </section>

      <section className="result-section">
        <h2>Dependency Summary</h2>
        {result.dependency_summary.length > 0 ? (
          <div className="dependency-summary-list">
            {result.dependency_summary.map((entry, index) => (
              <SummaryCard
                key={`${entry.dependency_type}-${index}`}
                entry={entry}
              />
            ))}
          </div>
        ) : (
          <p className="empty-message">No dependency summary provided.</p>
        )}
      </section>

      <section className="result-section">
        <h2>Recommended Delivery Stages</h2>
        {result.recommended_delivery_stages.length > 0 ? (
          <div className="dependency-delivery-stages">
            {result.recommended_delivery_stages.map((stage, index) => (
              <DeliveryStageCard key={`${stage.stage_number}-${index}`} stage={stage} />
            ))}
          </div>
        ) : (
          <p className="empty-message">No delivery stages recommended.</p>
        )}
      </section>

      <section className="result-section">
        <h2>Blocking Requirement IDs</h2>
        {blockingIds.length > 0 ? (
          <ul className="compact-list dependency-blocking-list">
            {blockingIds.map((id, index) => (
              <li key={`${index}-${id}`}>{id}</li>
            ))}
          </ul>
        ) : (
          <p className="empty-message">No blocking requirements identified.</p>
        )}
      </section>

      <section
        className={`result-section dependency-circular-status${result.circular_dependency_detected ? " is-circular" : ""}`}
      >
        <h2>Circular Dependency Status</h2>
        <p>
          {result.circular_dependency_detected
            ? "Circular dependencies detected."
            : "No circular dependencies detected."}
        </p>
        <h3>Circular dependency paths</h3>
        {circularPaths.length > 0 ? (
          <ul className="compact-list">
            {circularPaths.map((path, index) => (
              <li key={`${index}-${path}`}>{path}</li>
            ))}
          </ul>
        ) : (
          <p className="empty-message">No circular dependency paths provided.</p>
        )}
      </section>

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
        title="Human Validation"
        items={result.human_validation_required}
        emptyMessage="No human validation items identified."
      />
    </div>
  );
}
