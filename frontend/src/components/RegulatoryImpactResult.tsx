import type {
  ImpactSummaryEntry,
  ObligationCoverageEntry,
  RegulatoryEvidence,
  RegulatoryImpactFinding,
  RegulatoryImpactResponse,
  RequirementImpactEntry,
} from "../types/regulatoryImpact";

interface RegulatoryImpactResultProps {
  result: RegulatoryImpactResponse;
}

interface ListSectionProps {
  title: string;
  items: string[];
  emptyMessage: string;
  className?: string;
}

function nonEmpty(items: string[]): string[] {
  return items.filter((item) => item.trim().length > 0);
}

function display(value: string, fallback = "Not provided."): string {
  return value.trim() || fallback;
}

function slug(value: string): string {
  return value.toLowerCase().replaceAll(/[^a-z]+/g, "-");
}

function ListSection({
  title,
  items,
  emptyMessage,
  className,
}: ListSectionProps) {
  const visibleItems = nonEmpty(items);
  return (
    <section className={`result-section${className ? ` ${className}` : ""}`}>
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

function EvidenceCard({ evidence }: { evidence: RegulatoryEvidence }) {
  return (
    <article className="regulatory-evidence-card">
      <dl>
        <div>
          <dt>Source type</dt>
          <dd>{evidence.source_type}</dd>
        </div>
        <div>
          <dt>Source reference</dt>
          <dd>{display(evidence.source_reference)}</dd>
        </div>
        <div>
          <dt>Evidence text</dt>
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

function ImpactFindingCard({
  finding,
}: {
  finding: RegulatoryImpactFinding;
}) {
  const obligationIds = nonEmpty(finding.obligation_ids);
  const requirementIds = nonEmpty(finding.affected_requirement_ids);
  const evidence = finding.evidence.filter(
    (item) =>
      item.source_type.trim() ||
      item.source_reference.trim() ||
      item.evidence_text.trim() ||
      item.explanation.trim()
  );
  const validationQuestions = nonEmpty(finding.validation_questions);

  return (
    <article className={`regulatory-impact-finding severity-${slug(finding.severity)}`}>
      <div className="regulatory-finding-heading">
        <div>
          <p className="regulatory-impact-id">{display(finding.impact_id)}</p>
          <h3>{display(finding.title)}</h3>
        </div>
        <div className="regulatory-badges">
          <span className={`regulatory-impact-type impact-type-${slug(finding.impact_type)}`}>
            {finding.impact_type}
          </span>
          <span className={`regulatory-coverage coverage-${slug(finding.coverage_status)}`}>
            {finding.coverage_status}
          </span>
          <span className={`regulatory-severity severity-badge-${slug(finding.severity)}`}>
            {finding.severity}
          </span>
          <span className={`regulatory-confidence confidence-${slug(finding.confidence)}`}>
            {finding.confidence} confidence
          </span>
        </div>
      </div>

      <p>{display(finding.explanation)}</p>
      <dl className="regulatory-facts">
        <div>
          <dt>Obligation IDs</dt>
          <dd>{obligationIds.length ? obligationIds.join(", ") : "No obligation IDs."}</dd>
        </div>
        <div>
          <dt>Affected requirement IDs</dt>
          <dd>{requirementIds.length ? requirementIds.join(", ") : "No affected requirements."}</dd>
        </div>
        <div>
          <dt>Validation status</dt>
          <dd>{finding.requires_human_validation ? "Human validation required" : "No human validation flagged"}</dd>
        </div>
        <div>
          <dt>Suggested owner</dt>
          <dd>{display(finding.suggested_owner)}</dd>
        </div>
      </dl>

      <div className="regulatory-impact-detail-grid">
        <section>
          <h4>Current coverage</h4>
          <p>{display(finding.current_coverage)}</p>
        </section>
        <section>
          <h4>Coverage gap</h4>
          <p>{display(finding.coverage_gap)}</p>
        </section>
        <section>
          <h4>Business impact</h4>
          <p>{display(finding.business_impact)}</p>
        </section>
        <section>
          <h4>Implementation impact</h4>
          <p>{display(finding.implementation_impact)}</p>
        </section>
        <section>
          <h4>Testing impact</h4>
          <p>{display(finding.testing_impact)}</p>
        </section>
        <section>
          <h4>Operational impact</h4>
          <p>{display(finding.operational_impact)}</p>
        </section>
      </div>

      <section className="regulatory-subsection">
        <h4>Evidence</h4>
        {evidence.length ? (
          <div className="regulatory-evidence-list">
            {evidence.map((item, index) => (
              <EvidenceCard
                key={`${item.source_type}-${item.source_reference}-${index}`}
                evidence={item}
              />
            ))}
          </div>
        ) : (
          <p className="empty-message">No evidence provided.</p>
        )}
      </section>

      <section className="regulatory-recommended-action">
        <h4>Recommended requirement action</h4>
        <p>{display(finding.recommended_requirement_action)}</p>
      </section>
      {finding.proposed_requirement_text?.trim() && (
        <section className="regulatory-proposed-draft">
          <h4>Proposed requirement text</h4>
          <p>{finding.proposed_requirement_text.trim()}</p>
        </section>
      )}
      <section className="regulatory-subsection">
        <h4>Validation questions</h4>
        {validationQuestions.length ? (
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

function ObligationCoverageCard({
  coverage,
}: {
  coverage: ObligationCoverageEntry;
}) {
  const requirementIds = nonEmpty(coverage.requirement_ids);
  const impactIds = nonEmpty(coverage.impact_ids);
  const missingCoverage = nonEmpty(coverage.missing_coverage);

  return (
    <article className="regulatory-obligation-coverage">
      <div className="regulatory-finding-heading">
        <h3>{display(coverage.obligation_id)}</h3>
        <span className={`regulatory-coverage coverage-${slug(coverage.coverage_status)}`}>
          {coverage.coverage_status}
        </span>
      </div>
      <dl className="regulatory-facts">
        <div>
          <dt>Requirement IDs</dt>
          <dd>{requirementIds.length ? requirementIds.join(", ") : "No requirements linked."}</dd>
        </div>
        <div>
          <dt>Impact IDs</dt>
          <dd>{impactIds.length ? impactIds.join(", ") : "No impacts linked."}</dd>
        </div>
        <div>
          <dt>Validation status</dt>
          <dd>{coverage.requires_human_validation ? "Human validation required" : "No human validation flagged"}</dd>
        </div>
      </dl>
      <section className="regulatory-subsection">
        <h4>Explanation</h4>
        <p>{display(coverage.coverage_explanation)}</p>
      </section>
      <section className="regulatory-subsection">
        <h4>Missing coverage</h4>
        {missingCoverage.length ? (
          <ul className="compact-list">
            {missingCoverage.map((item, index) => (
              <li key={`${index}-${item}`}>{item}</li>
            ))}
          </ul>
        ) : (
          <p className="empty-message">No missing coverage identified.</p>
        )}
      </section>
    </article>
  );
}

function RequirementImpactCard({
  impact,
}: {
  impact: RequirementImpactEntry;
}) {
  const obligationIds = nonEmpty(impact.obligation_ids);
  const impactIds = nonEmpty(impact.impact_ids);
  return (
    <article className="regulatory-requirement-impact">
      <div className="regulatory-finding-heading">
        <h3>{display(impact.requirement_id)}</h3>
        <span className={`regulatory-impacted ${impact.impacted ? "is-impacted" : ""}`}>
          {impact.impacted ? "Impacted" : "Not impacted"}
        </span>
      </div>
      <dl className="regulatory-facts">
        <div>
          <dt>Obligation IDs</dt>
          <dd>{obligationIds.length ? obligationIds.join(", ") : "No obligations linked."}</dd>
        </div>
        <div>
          <dt>Impact IDs</dt>
          <dd>{impactIds.length ? impactIds.join(", ") : "No impacts linked."}</dd>
        </div>
        <div>
          <dt>Highest severity</dt>
          <dd>{impact.highest_severity ?? "Not provided."}</dd>
        </div>
      </dl>
      <p><strong>Recommended action:</strong> {display(impact.recommended_action)}</p>
      <p><strong>Notes:</strong> {display(impact.notes)}</p>
    </article>
  );
}

function ImpactSummaryCard({ entry }: { entry: ImpactSummaryEntry }) {
  const impactIds = nonEmpty(entry.impact_ids);
  return (
    <article className={`regulatory-impact-summary severity-${slug(entry.severity)}`}>
      <span className={`regulatory-severity severity-badge-${slug(entry.severity)}`}>
        {entry.severity}
      </span>
      <p className="regulatory-summary-count">{entry.count}</p>
      <p>{impactIds.length ? impactIds.join(", ") : "No impact IDs."}</p>
    </article>
  );
}

export default function RegulatoryImpactResult({
  result,
}: RegulatoryImpactResultProps) {
  const impactedIds = nonEmpty(result.impacted_requirement_ids);
  const uncoveredIds = nonEmpty(result.uncovered_obligation_ids);

  return (
    <div className="result-container regulatory-impact-result">
      <p className="regulatory-legal-notice" role="note">
        This analysis supports requirement review and is not legal advice.
      </p>
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
        <h2>Readiness Status</h2>
        <span className={`regulatory-readiness readiness-${slug(result.readiness_status)}`}>
          {result.readiness_status}
        </span>
      </section>

      <section className="result-section">
        <h2>Impact Severity Summary</h2>
        {result.impact_summary.length ? (
          <div className="regulatory-impact-summary-list">
            {result.impact_summary.map((entry, index) => (
              <ImpactSummaryCard key={`${entry.severity}-${index}`} entry={entry} />
            ))}
          </div>
        ) : (
          <p className="empty-message">No impact severity summary provided.</p>
        )}
      </section>

      <section className="result-section">
        <h2>Impact Findings</h2>
        {result.impact_findings.length ? (
          <div className="regulatory-impact-list">
            {result.impact_findings.map((finding, index) => (
              <ImpactFindingCard key={`${finding.impact_id}-${index}`} finding={finding} />
            ))}
          </div>
        ) : (
          <p className="empty-message">No impact findings identified.</p>
        )}
      </section>

      <section className="result-section">
        <h2>Obligation Coverage</h2>
        {result.obligation_coverage.length ? (
          <div className="regulatory-impact-list">
            {result.obligation_coverage.map((coverage, index) => (
              <ObligationCoverageCard key={`${coverage.obligation_id}-${index}`} coverage={coverage} />
            ))}
          </div>
        ) : (
          <p className="empty-message">No obligation coverage provided.</p>
        )}
      </section>

      <section className="result-section">
        <h2>Requirement Impacts</h2>
        {result.requirement_impacts.length ? (
          <div className="regulatory-impact-list">
            {result.requirement_impacts.map((impact, index) => (
              <RequirementImpactCard key={`${impact.requirement_id}-${index}`} impact={impact} />
            ))}
          </div>
        ) : (
          <p className="empty-message">No requirement impacts provided.</p>
        )}
      </section>

      <ListSection
        title="Impacted Requirement IDs"
        items={impactedIds}
        emptyMessage="No impacted requirements identified."
      />
      <ListSection
        title="Uncovered Obligation IDs"
        items={uncoveredIds}
        emptyMessage="No uncovered obligations identified."
      />
      <ListSection
        title="Potential Conflicts"
        items={result.potential_conflicts}
        emptyMessage="No potential conflicts identified."
        className="regulatory-potential-conflicts"
      />
      <ListSection title="Assumptions" items={result.assumptions} emptyMessage="No assumptions identified." />
      <ListSection title="Missing Information" items={result.missing_information} emptyMessage="No missing information identified." />
      <ListSection title="Risks" items={result.risks} emptyMessage="No risks identified." />
      <ListSection title="Recommended Next Actions" items={result.recommended_next_actions} emptyMessage="No recommended next actions provided." />
      <ListSection title="Human Validation" items={result.human_validation_required} emptyMessage="No human validation items identified." />
    </div>
  );
}
