import type {
  CoverageArea,
  GapAnalysisResponse,
  GapFinding,
} from "../types/gapAnalysis";

interface GapAnalysisResultProps {
  result: GapAnalysisResponse;
}

function nonEmpty(items: string[]): string[] {
  return items.filter((item) => item.trim().length > 0);
}

interface ListSectionProps {
  title: string;
  items: string[];
  emptyMessage: string;
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

function GapCard({ gap }: { gap: GapFinding }) {
  const severityClass = gap.severity.toLowerCase();
  const statusClass = gap.status.toLowerCase().replaceAll(" ", "-");
  const evidence = nonEmpty(gap.evidence_from_input);
  const questions = nonEmpty(gap.clarification_questions);

  return (
    <article className="gap-finding-card">
      <div className="gap-card-heading">
        <div>
          <p className="gap-id">{gap.gap_id}</p>
          <h3>{gap.title}</h3>
          <p className="gap-category">{gap.category}</p>
        </div>
        <div className="gap-badges">
          <span className={`gap-severity gap-severity-${severityClass}`}>
            {gap.severity}
          </span>
          <span className={`gap-status gap-status-${statusClass}`}>
            {gap.status}
          </span>
        </div>
      </div>

      <p>{gap.description}</p>

      <section className="gap-detail">
        <h4>Evidence from input</h4>
        {evidence.length > 0 ? (
          <ul className="compact-list">
            {evidence.map((item, index) => (
              <li key={`${index}-${item}`}>{item}</li>
            ))}
          </ul>
        ) : (
          <p className="empty-message">No direct evidence quoted.</p>
        )}
      </section>

      <p>
        <strong>Missing information:</strong> {gap.missing_information}
      </p>
      <p>
        <strong>Impact:</strong> {gap.impact}
      </p>

      <section className="gap-questions">
        <h4>Clarification questions</h4>
        <ol>
          {questions.map((question, index) => (
            <li key={`${gap.gap_id}-${index}-${question}`}>{question}</li>
          ))}
        </ol>
      </section>

      <dl className="gap-facts">
        <div>
          <dt>Suggested owner</dt>
          <dd>{gap.suggested_owner}</dd>
        </div>
        <div>
          <dt>Blocks implementation</dt>
          <dd>{gap.blocks_implementation ? "Yes" : "No"}</dd>
        </div>
        <div>
          <dt>Blocks testing</dt>
          <dd>{gap.blocks_testing ? "Yes" : "No"}</dd>
        </div>
        <div>
          <dt>Human validation</dt>
          <dd>{gap.requires_human_validation ? "Required" : "Not required"}</dd>
        </div>
      </dl>
    </article>
  );
}

function CoverageCard({ item }: { item: CoverageArea }) {
  const evidence = nonEmpty(item.evidence);
  const gapIds = nonEmpty(item.gap_ids);

  return (
    <article className="coverage-card">
      <div className="coverage-heading">
        <h3>{item.area}</h3>
        <span
          className={
            item.covered ? "coverage-status covered" : "coverage-status gap"
          }
        >
          {item.covered ? "Covered" : "Gap"}
        </span>
      </div>

      <div className="coverage-detail-grid">
        <section>
          <h4>Evidence</h4>
          {evidence.length > 0 ? (
            <ul className="compact-list">
              {evidence.map((entry, index) => (
                <li key={`${index}-${entry}`}>{entry}</li>
              ))}
            </ul>
          ) : (
            <p className="empty-message">No coverage evidence supplied.</p>
          )}
        </section>
        <section>
          <h4>Linked gap IDs</h4>
          {gapIds.length > 0 ? (
            <ul className="compact-list">
              {gapIds.map((gapId) => (
                <li key={gapId}>{gapId}</li>
              ))}
            </ul>
          ) : (
            <p className="empty-message">No linked gaps.</p>
          )}
        </section>
      </div>
      <p>
        <strong>Notes:</strong> {item.notes || "No additional notes."}
      </p>
    </article>
  );
}

export default function GapAnalysisResult({
  result,
}: GapAnalysisResultProps) {
  const readinessClass = result.readiness_status
    .toLowerCase()
    .replaceAll(" ", "-");

  return (
    <div className="gap-analysis-result">
      <section className="result-section">
        <h2>Requirement Summary</h2>
        <p>{result.requirement_summary}</p>
      </section>

      <ListSection
        title="Confirmed Information"
        items={result.confirmed_information}
        emptyMessage="No confirmed information identified."
      />

      <section className="result-section gap-readiness">
        <div className="readiness-heading">
          <h2>Readiness</h2>
          <span className={`readiness-status readiness-${readinessClass}`}>
            {result.readiness_status}
          </span>
        </div>
        <div
          className="readiness-score"
          role="progressbar"
          aria-label="Requirement readiness score"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={result.readiness_score}
        >
          <span>{result.readiness_score}</span>
          <small>/ 100</small>
        </div>
        <p>
          <strong>Score explanation:</strong> {result.score_explanation}
        </p>
      </section>

      <section className="result-section">
        <h2>Gap Findings</h2>
        {result.gap_findings.length > 0 ? (
          <div className="gap-finding-list">
            {result.gap_findings.map((gap) => (
              <GapCard key={gap.gap_id} gap={gap} />
            ))}
          </div>
        ) : (
          <p className="empty-message">No requirement gaps identified.</p>
        )}
      </section>

      <section className="result-section">
        <h2>Coverage Assessment</h2>
        {result.coverage_assessment.length > 0 ? (
          <div className="coverage-list">
            {result.coverage_assessment.map((item, index) => (
              <CoverageCard key={`${item.area}-${index}`} item={item} />
            ))}
          </div>
        ) : (
          <p className="empty-message">No coverage assessment provided.</p>
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
        emptyMessage="No next actions recommended."
      />
      <ListSection
        title="Human Validation Required"
        items={result.human_validation_required}
        emptyMessage="No human validation items identified."
      />
    </div>
  );
}
