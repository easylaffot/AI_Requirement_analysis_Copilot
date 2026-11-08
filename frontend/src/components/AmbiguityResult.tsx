import type {
  AmbiguityAnalysisResponse,
  AmbiguityFinding,
  SuggestedRewrite,
} from "../types/ambiguity";

interface AmbiguityResultProps {
  result: AmbiguityAnalysisResponse;
}

interface ListSectionProps {
  title: string;
  items: string[];
  emptyMessage: string;
}

function ListSection({ title, items, emptyMessage }: ListSectionProps) {
  return (
    <section className="result-section">
      <h2>{title}</h2>
      {items.length > 0 ? (
        <ul className="compact-list">
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

function FindingCard({ finding }: { finding: AmbiguityFinding }) {
  const severityClass = finding.severity.toLowerCase();

  return (
    <article className="ambiguity-card">
      <div className="ambiguity-card-heading">
        <div>
          <p className="ambiguity-id">{finding.finding_id}</p>
          <h3>{finding.category}</h3>
        </div>
        <span className={`severity-badge severity-${severityClass}`}>
          {finding.severity}
        </span>
      </div>

      <blockquote className="ambiguous-text">
        <strong>Exact ambiguous text:</strong>
        <p>{finding.ambiguous_text}</p>
      </blockquote>

      <p>
        <strong>Explanation:</strong> {finding.explanation}
      </p>
      <p>
        <strong>Interpretation risk:</strong> {finding.interpretation_risk}
      </p>

      <section className="ambiguity-subsection">
        <h4>Possible interpretations</h4>
        <div className="interpretation-list">
          {finding.possible_interpretations.map((item) => (
            <article
              className="interpretation-card"
              key={item.interpretation_id}
            >
              <h5>{item.interpretation_id}</h5>
              <p>{item.interpretation}</p>
              <p>
                <strong>Supported by input:</strong>{" "}
                {item.supported_by_input ? "Yes" : "No"}
              </p>
              <p>
                <strong>Notes:</strong> {item.notes}
              </p>
            </article>
          ))}
        </div>
      </section>

      <section className="clarification-questions">
        <h4>Clarification questions</h4>
        <ol>
          {finding.clarification_questions.map((question, index) => (
            <li key={`${finding.finding_id}-${index}-${question}`}>
              {question}
            </li>
          ))}
        </ol>
      </section>

      <dl className="ambiguity-facts">
        <div>
          <dt>Source reference</dt>
          <dd>{finding.source_reference}</dd>
        </div>
        <div>
          <dt>Human validation</dt>
          <dd>{finding.requires_human_validation ? "Required" : "Not required"}</dd>
        </div>
        <div>
          <dt>Validation owner</dt>
          <dd>{finding.validation_owner}</dd>
        </div>
      </dl>
    </article>
  );
}

function RewriteCard({ rewrite }: { rewrite: SuggestedRewrite }) {
  const statusClass = rewrite.status.toLowerCase().replaceAll(" ", "-");

  return (
    <article className={`rewrite-card rewrite-${statusClass}`}>
      <div className="rewrite-heading">
        <h3>{rewrite.rewrite_id}</h3>
        <span className={`rewrite-status rewrite-status-${statusClass}`}>
          {rewrite.status}
        </span>
      </div>

      <p>
        <strong>Rewritten requirement:</strong> {rewrite.rewritten_requirement}
      </p>

      <section className="rewrite-detail">
        <h4>Unresolved placeholders</h4>
        {rewrite.unresolved_placeholders.length > 0 ? (
          <ul className="placeholder-list">
            {rewrite.unresolved_placeholders.map((placeholder, index) => (
              <li key={`${index}-${placeholder}`}>
                <span className="placeholder-badge">{placeholder}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="empty-message">No unresolved placeholders.</p>
        )}
      </section>

      <div className="rewrite-detail-grid">
        <div className="rewrite-detail">
          <h4>Assumptions used</h4>
          {rewrite.assumptions_used.length > 0 ? (
            <ul className="compact-list">
              {rewrite.assumptions_used.map((assumption, index) => (
                <li key={`${index}-${assumption}`}>{assumption}</li>
              ))}
            </ul>
          ) : (
            <p className="empty-message">No assumptions used.</p>
          )}
        </div>
        <div className="rewrite-detail">
          <h4>Source finding IDs</h4>
          {rewrite.source_finding_ids.length > 0 ? (
            <ul className="compact-list">
              {rewrite.source_finding_ids.map((findingId) => (
                <li key={findingId}>{findingId}</li>
              ))}
            </ul>
          ) : (
            <p className="empty-message">No source findings identified.</p>
          )}
        </div>
      </div>
    </article>
  );
}

export default function AmbiguityResult({ result }: AmbiguityResultProps) {
  const statusClass = result.overall_status.toLowerCase().replaceAll(" ", "-");

  return (
    <div className="ambiguity-result">
      <section className="result-section">
        <h2>Requirement Summary</h2>
        <p>{result.requirement_summary}</p>
      </section>

      <ListSection
        title="Confirmed Information"
        items={result.confirmed_information}
        emptyMessage="No confirmed information identified."
      />

      <section className="result-section ambiguity-quality">
        <div className="quality-heading">
          <h2>Overall Quality</h2>
          <span className={`overall-status status-${statusClass}`}>
            {result.overall_status}
          </span>
        </div>
        <div
          className="quality-score"
          role="progressbar"
          aria-label="Requirement quality score"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={result.overall_score}
        >
          <span>{result.overall_score}</span>
          <small>/ 100</small>
        </div>
        <p>
          <strong>Score explanation:</strong> {result.score_explanation}
        </p>
      </section>

      <section className="result-section">
        <h2>Ambiguity Findings</h2>
        {result.ambiguity_findings.length > 0 ? (
          <div className="ambiguity-findings">
            {result.ambiguity_findings.map((finding) => (
              <FindingCard key={finding.finding_id} finding={finding} />
            ))}
          </div>
        ) : (
          <p className="empty-message">No ambiguity findings identified.</p>
        )}
      </section>

      <section className="result-section">
        <h2>Suggested Rewrites</h2>
        {result.suggested_rewrites.length > 0 ? (
          <div className="suggested-rewrites">
            {result.suggested_rewrites.map((rewrite) => (
              <RewriteCard key={rewrite.rewrite_id} rewrite={rewrite} />
            ))}
          </div>
        ) : (
          <p className="empty-message">No suggested rewrites provided.</p>
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
        title="Human Validation Required"
        items={result.human_validation_required}
        emptyMessage="No human validation items identified."
      />
    </div>
  );
}
