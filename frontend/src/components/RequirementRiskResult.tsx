import type {
  RequirementRiskFinding,
  RequirementRiskResponse,
  RequirementRiskRelationship,
  RiskEvidence,
  RiskMitigation,
  RiskSeverity,
  RiskSummaryEntry,
} from "../types/requirementRisk";

interface RequirementRiskResultProps {
  result: RequirementRiskResponse;
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

function severityClass(severity: RiskSeverity): string {
  return `risk-severity-${severity.toLowerCase()}`;
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

function EvidenceCard({ evidence }: { evidence: RiskEvidence }) {
  return (
    <article className="risk-evidence-panel">
      <dl>
        <div>
          <dt>Requirement ID</dt>
          <dd>{display(evidence.requirement_id)}</dd>
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

function MitigationCard({ mitigation }: { mitigation: RiskMitigation }) {
  const statusClass = mitigation.status.toLowerCase().replaceAll(" ", "-");

  return (
    <article className="risk-mitigation-panel">
      <div className="risk-mitigation-heading">
        <h5>{display(mitigation.mitigation_id)}</h5>
        <span className={`risk-mitigation-status status-${statusClass}`}>
          {mitigation.status}
        </span>
      </div>
      <dl>
        <div>
          <dt>Action</dt>
          <dd>{display(mitigation.action)}</dd>
        </div>
        <div>
          <dt>Rationale</dt>
          <dd>{display(mitigation.rationale)}</dd>
        </div>
        <div>
          <dt>Owner</dt>
          <dd>{display(mitigation.owner)}</dd>
        </div>
        <div>
          <dt>Validation required</dt>
          <dd>{mitigation.validation_required ? "Yes" : "No"}</dd>
        </div>
      </dl>
    </article>
  );
}

function RiskFindingCard({ finding }: { finding: RequirementRiskFinding }) {
  const affectedRequirementIds = nonEmpty(finding.affected_requirement_ids);
  const assumptions = nonEmpty(finding.assumptions);
  const monitoringIndicators = nonEmpty(finding.monitoring_indicators);
  const validationQuestions = nonEmpty(finding.validation_questions);
  const severity = severityClass(finding.severity);
  const likelihoodClass = finding.likelihood.toLowerCase();
  const impactClass = finding.impact.toLowerCase();

  return (
    <article className={`risk-finding-card ${severity}`}>
      <div className="risk-finding-heading">
        <div>
          <p className="risk-finding-id">{display(finding.risk_id)}</p>
          <h3>{display(finding.title)}</h3>
        </div>
        <div className="risk-finding-badges">
          <span className="risk-category-badge">{finding.category}</span>
          <span className={`risk-status-badge ${severity}`}>{finding.severity}</span>
          <span className={`risk-likelihood-badge likelihood-${likelihoodClass}`}>
            Likelihood: {finding.likelihood}
          </span>
          <span className={`risk-impact-badge impact-${impactClass}`}>
            Impact: {finding.impact}
          </span>
        </div>
      </div>

      <dl className="risk-facts">
        <div>
          <dt>Status</dt>
          <dd>{finding.status}</dd>
        </div>
        <div>
          <dt>Affected requirement IDs</dt>
          <dd>
            {affectedRequirementIds.length > 0
              ? affectedRequirementIds.join(", ")
              : "None provided."}
          </dd>
        </div>
      </dl>

      <div className="risk-statement">
        <h4>Risk statement</h4>
        <p>{display(finding.risk_statement)}</p>
      </div>

      <dl className="risk-detail-grid">
        <div>
          <dt>Cause</dt>
          <dd>{display(finding.cause)}</dd>
        </div>
        <div>
          <dt>Consequence</dt>
          <dd>{display(finding.consequence)}</dd>
        </div>
      </dl>

      <section className="risk-subsection">
        <h4>Evidence</h4>
        {finding.evidence.length > 0 ? (
          <div className="risk-evidence-list">
            {finding.evidence.map((evidence, index) => (
              <EvidenceCard
                key={`${evidence.requirement_id}-${index}`}
                evidence={evidence}
              />
            ))}
          </div>
        ) : (
          <p className="empty-message">No evidence provided.</p>
        )}
      </section>

      <section className="risk-subsection">
        <h4>Assumptions</h4>
        {assumptions.length > 0 ? (
          <ul className="compact-list">
            {assumptions.map((item, index) => (
              <li key={`${index}-${item}`}>{item}</li>
            ))}
          </ul>
        ) : (
          <p className="empty-message">No assumptions identified.</p>
        )}
      </section>

      <section className="risk-subsection">
        <h4>Mitigation actions</h4>
        {finding.mitigation_actions.length > 0 ? (
          <div className="risk-mitigation-list">
            {finding.mitigation_actions.map((mitigation, index) => (
              <MitigationCard
                key={`${mitigation.mitigation_id}-${index}`}
                mitigation={mitigation}
              />
            ))}
          </div>
        ) : (
          <p className="empty-message">No mitigation actions identified.</p>
        )}
      </section>

      <section className="risk-subsection">
        <h4>Monitoring indicators</h4>
        {monitoringIndicators.length > 0 ? (
          <ul className="compact-list">
            {monitoringIndicators.map((item, index) => (
              <li key={`${index}-${item}`}>{item}</li>
            ))}
          </ul>
        ) : (
          <p className="empty-message">No monitoring indicators identified.</p>
        )}
      </section>

      <div className="risk-blocker-indicators">
        <span className={finding.blocks_implementation ? "is-blocker" : ""}>
          Blocks implementation: {finding.blocks_implementation ? "Yes" : "No"}
        </span>
        <span className={finding.blocks_testing ? "is-blocker" : ""}>
          Blocks testing: {finding.blocks_testing ? "Yes" : "No"}
        </span>
      </div>

      <section className="risk-subsection">
        <h4>
          Human validation:{" "}
          {finding.requires_human_validation ? "Required" : "Not required"}
        </h4>
        {finding.requires_human_validation && (
          <p>
            <strong>Suggested owner:</strong>{" "}
            {display(finding.suggested_owner)}
          </p>
        )}
        {validationQuestions.length > 0 ? (
          <ul className="compact-list">
            {validationQuestions.map((question, index) => (
              <li key={`${index}-${question}`}>{question}</li>
            ))}
          </ul>
        ) : (
          <p className="empty-message">No validation questions provided.</p>
        )}
      </section>
    </article>
  );
}

function RiskSummaryCard({ entry }: { entry: RiskSummaryEntry }) {
  const riskIds = nonEmpty(entry.risk_ids);

  return (
    <article className={`risk-summary-card ${severityClass(entry.severity)}`}>
      <span className={`risk-status-badge ${severityClass(entry.severity)}`}>
        {entry.severity}
      </span>
      <p className="risk-summary-count">{entry.count}</p>
      <p>risks</p>
      <p className="risk-summary-ids">
        {riskIds.length > 0 ? riskIds.join(", ") : "No risk IDs."}
      </p>
    </article>
  );
}

function RelationshipCard({
  relationship,
}: {
  relationship: RequirementRiskRelationship;
}) {
  const riskIds = nonEmpty(relationship.risk_ids);

  return (
    <article className="risk-relationship-card">
      <h3>{display(relationship.requirement_id)}</h3>
      <dl className="risk-detail-grid">
        <div>
          <dt>Risk IDs</dt>
          <dd>{riskIds.length > 0 ? riskIds.join(", ") : "No related risks."}</dd>
        </div>
        <div>
          <dt>Highest severity</dt>
          <dd>
            {relationship.highest_severity ? (
              <span
                className={`risk-status-badge ${severityClass(
                  relationship.highest_severity
                )}`}
              >
                {relationship.highest_severity}
              </span>
            ) : (
              "None"
            )}
          </dd>
        </div>
        <div>
          <dt>Risk-free</dt>
          <dd>{relationship.risk_free ? "Yes" : "No"}</dd>
        </div>
      </dl>
      <p>{display(relationship.notes, "No relationship notes provided.")}</p>
    </article>
  );
}

export default function RequirementRiskResult({
  result,
}: RequirementRiskResultProps) {
  const readinessClass = result.overall_readiness
    .toLowerCase()
    .replaceAll(" ", "-");

  return (
    <div className="result-container requirement-risk-result">
      <section className="result-section">
        <h2>Analysis Summary</h2>
        <p>{display(result.analysis_summary)}</p>
      </section>

      <ListSection
        title="Confirmed Information"
        items={result.confirmed_information}
        emptyMessage="No confirmed information provided."
      />

      <section className="result-section risk-overview">
        <h2>Overall Risk Overview</h2>
        <div className="risk-overview-heading">
          <div>
            <p className="risk-score">{result.overall_risk_score}</p>
            <p className="risk-score-label">out of 100</p>
          </div>
          <span className={`risk-readiness readiness-${readinessClass}`}>
            {result.overall_readiness}
          </span>
        </div>
        <p>{display(result.score_explanation)}</p>
      </section>

      <section className="result-section">
        <h2>Risk Severity Summary</h2>
        {result.risk_summary.length > 0 ? (
          <div className="risk-summary-list">
            {result.risk_summary.map((entry, index) => (
              <RiskSummaryCard
                key={`${entry.severity}-${index}`}
                entry={entry}
              />
            ))}
          </div>
        ) : (
          <p className="empty-message">No risks identified.</p>
        )}
      </section>

      <section className="result-section">
        <h2>Risk Findings</h2>
        {result.risk_findings.length > 0 ? (
          <div className="risk-finding-list">
            {result.risk_findings.map((finding) => (
              <RiskFindingCard key={finding.risk_id} finding={finding} />
            ))}
          </div>
        ) : (
          <p className="empty-message">No risks identified.</p>
        )}
      </section>

      <section className="result-section">
        <h2>Requirement Relationships</h2>
        {result.requirement_relationships.length > 0 ? (
          <div className="risk-relationship-list">
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
