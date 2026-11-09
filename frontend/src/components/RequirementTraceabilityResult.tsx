import type {
  BrokenReference,
  CoverageSummaryEntry,
  OrphanArtifact,
  RequirementCoverageEntry,
  RequirementTraceabilityResponse,
  TraceabilityRisk,
  TraceLink,
} from "../types/requirementTraceability";

interface RequirementTraceabilityResultProps {
  result: RequirementTraceabilityResponse;
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

function slug(value: string): string {
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

function RequirementCoverageCard({
  coverage,
}: {
  coverage: RequirementCoverageEntry;
}) {
  const stories = nonEmpty(coverage.story_ids);
  const criteria = nonEmpty(coverage.criterion_ids);
  const testCases = nonEmpty(coverage.test_case_ids);
  const missing = nonEmpty(coverage.missing_coverage);

  return (
    <article className="trace-coverage-card">
      <div className="trace-card-heading">
        <h3>{display(coverage.requirement_id)}</h3>
        <span className={`trace-coverage-status coverage-${slug(coverage.coverage_status)}`}>
          {coverage.coverage_status}
        </span>
      </div>
      <dl className="trace-facts">
        <div>
          <dt>Story IDs</dt>
          <dd>{stories.length ? stories.join(", ") : "No stories linked."}</dd>
        </div>
        <div>
          <dt>Criterion IDs</dt>
          <dd>{criteria.length ? criteria.join(", ") : "No criteria linked."}</dd>
        </div>
        <div>
          <dt>Test-case IDs</dt>
          <dd>{testCases.length ? testCases.join(", ") : "No test cases linked."}</dd>
        </div>
        <div>
          <dt>Validation status</dt>
          <dd>{coverage.requires_human_validation ? "Human validation required" : "No human validation flagged"}</dd>
        </div>
      </dl>
      <section className="trace-subsection">
        <h4>Coverage explanation</h4>
        <p>{display(coverage.coverage_explanation)}</p>
      </section>
      <section className="trace-subsection">
        <h4>Missing coverage</h4>
        {missing.length ? (
          <ul className="compact-list">
            {missing.map((item, index) => <li key={`${index}-${item}`}>{item}</li>)}
          </ul>
        ) : (
          <p className="empty-message">No missing coverage identified.</p>
        )}
      </section>
    </article>
  );
}

function TraceLinkCard({ link }: { link: TraceLink }) {
  return (
    <article className="trace-link-card">
      <div className="trace-card-heading">
        <h3>{display(link.link_id)}</h3>
        <span className={`trace-link-status link-${slug(link.status)}`}>{link.status}</span>
      </div>
      <p className="trace-link-direction">
        <strong>{link.source_artifact_type}:</strong> {display(link.source_artifact_id)}
        <span aria-label="links to"> &rarr; </span>
        <strong>{link.target_artifact_type}:</strong> {display(link.target_artifact_id)}
      </p>
      <p>{display(link.explanation)}</p>
      <dl className="trace-facts">
        <div>
          <dt>Explicit-reference status</dt>
          <dd>{link.supported_by_explicit_reference ? "Explicit reference" : "Inferred reference"}</dd>
        </div>
        <div>
          <dt>Human-validation status</dt>
          <dd>{link.requires_human_validation ? "Required" : "Not required"}</dd>
        </div>
      </dl>
    </article>
  );
}

function OrphanCard({ orphan }: { orphan: OrphanArtifact }) {
  return (
    <article className="trace-orphan-card">
      <div className="trace-card-heading">
        <h3>{orphan.artifact_type}: {display(orphan.artifact_id)}</h3>
        <span className="trace-validation">
          {orphan.requires_human_validation ? "Validation required" : "No validation flagged"}
        </span>
      </div>
      <p><strong>Reason:</strong> {display(orphan.reason)}</p>
      <p><strong>Suggested action:</strong> {display(orphan.suggested_action)}</p>
    </article>
  );
}

function BrokenReferenceCard({ reference }: { reference: BrokenReference }) {
  return (
    <article className="trace-broken-reference">
      <h3>
        {reference.source_artifact_type}: {display(reference.source_artifact_id)}
        {" → "}
        Missing {reference.missing_target_type}: {display(reference.missing_target_id)}
      </h3>
      <p><strong>Impact:</strong> {display(reference.impact)}</p>
      <p><strong>Suggested action:</strong> {display(reference.suggested_action)}</p>
    </article>
  );
}

function RiskCard({ risk }: { risk: TraceabilityRisk }) {
  const affected = nonEmpty(risk.affected_artifact_ids);
  return (
    <article className={`trace-risk-card risk-${slug(risk.level)}`}>
      <div className="trace-card-heading">
        <div>
          <p className="trace-risk-id">{display(risk.risk_id)}</p>
          <h3>{display(risk.title)}</h3>
        </div>
        <span className={`trace-risk-level risk-level-${slug(risk.level)}`}>{risk.level}</span>
      </div>
      <p>{display(risk.description)}</p>
      <dl className="trace-facts">
        <div>
          <dt>Affected artifact IDs</dt>
          <dd>{affected.length ? affected.join(", ") : "No affected IDs provided."}</dd>
        </div>
        <div>
          <dt>Suggested owner</dt>
          <dd>{display(risk.suggested_owner)}</dd>
        </div>
      </dl>
      <p><strong>Mitigation:</strong> {display(risk.mitigation)}</p>
    </article>
  );
}

function CoverageSummaryCard({ entry }: { entry: CoverageSummaryEntry }) {
  const requirementIds = nonEmpty(entry.requirement_ids);
  return (
    <article className="trace-summary-card">
      <span className={`trace-coverage-status coverage-${slug(entry.coverage_status)}`}>
        {entry.coverage_status}
      </span>
      <p className="trace-summary-count">{entry.count}</p>
      <p>{requirementIds.length ? requirementIds.join(", ") : "No requirement IDs."}</p>
    </article>
  );
}

export default function RequirementTraceabilityResult({
  result,
}: RequirementTraceabilityResultProps) {
  return (
    <div className="result-container requirement-traceability-result">
      <section className="result-section">
        <h2>Analysis Summary</h2>
        <p>{display(result.analysis_summary)}</p>
      </section>

      <section className="result-section trace-score-section">
        <div className="trace-score">
          <span>{result.overall_coverage_percentage}%</span>
          <small>Overall coverage</small>
        </div>
        <div>
          <h2>Readiness Status</h2>
          <span className={`trace-readiness readiness-${slug(result.readiness_status)}`}>
            {result.readiness_status}
          </span>
        </div>
        <section className="trace-score-explanation">
          <h3>Score explanation</h3>
          <p>{display(result.score_explanation)}</p>
        </section>
      </section>

      <section className="result-section">
        <h2>Coverage Summary</h2>
        {result.coverage_summary.length ? (
          <div className="trace-summary-list">
            {result.coverage_summary.map((entry, index) => (
              <CoverageSummaryCard key={`${entry.coverage_status}-${index}`} entry={entry} />
            ))}
          </div>
        ) : (
          <p className="empty-message">No coverage summary provided.</p>
        )}
      </section>

      <section className="result-section">
        <h2>Requirement Coverage</h2>
        {result.requirement_coverage.length ? (
          <div className="trace-card-list">
            {result.requirement_coverage.map((coverage, index) => (
              <RequirementCoverageCard key={`${coverage.requirement_id}-${index}`} coverage={coverage} />
            ))}
          </div>
        ) : (
          <p className="empty-message">No requirement coverage provided.</p>
        )}
      </section>

      <section className="result-section">
        <h2>Trace Links</h2>
        {result.trace_links.length ? (
          <div className="trace-card-list">
            {result.trace_links.map((link, index) => (
              <TraceLinkCard key={`${link.link_id}-${index}`} link={link} />
            ))}
          </div>
        ) : (
          <p className="empty-message">No trace links identified.</p>
        )}
      </section>

      <section className="result-section">
        <h2>Orphan Artifacts</h2>
        {result.orphan_artifacts.length ? (
          <div className="trace-card-list">
            {result.orphan_artifacts.map((orphan, index) => (
              <OrphanCard key={`${orphan.artifact_type}-${orphan.artifact_id}-${index}`} orphan={orphan} />
            ))}
          </div>
        ) : (
          <p className="empty-message">No orphan artifacts identified.</p>
        )}
      </section>

      <section className="result-section">
        <h2>Broken References</h2>
        {result.broken_references.length ? (
          <div className="trace-card-list">
            {result.broken_references.map((reference, index) => (
              <BrokenReferenceCard key={`${reference.source_artifact_id}-${reference.missing_target_id}-${index}`} reference={reference} />
            ))}
          </div>
        ) : (
          <p className="empty-message">No broken references identified.</p>
        )}
      </section>

      <section className="result-section">
        <h2>Traceability Risks</h2>
        {result.traceability_risks.length ? (
          <div className="trace-card-list">
            {result.traceability_risks.map((risk, index) => (
              <RiskCard key={`${risk.risk_id}-${index}`} risk={risk} />
            ))}
          </div>
        ) : (
          <p className="empty-message">No traceability risks identified.</p>
        )}
      </section>

      <ListSection title="Assumptions" items={result.assumptions} emptyMessage="No assumptions identified." />
      <ListSection title="Missing Information" items={result.missing_information} emptyMessage="No missing information identified." />
      <ListSection title="Recommended Next Actions" items={result.recommended_next_actions} emptyMessage="No recommended next actions provided." />
      <ListSection title="Human Validation" items={result.human_validation_required} emptyMessage="No human validation items identified." />
    </div>
  );
}
