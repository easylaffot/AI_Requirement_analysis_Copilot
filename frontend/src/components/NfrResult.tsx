import type {
  NfrCategoryAssessment,
  NfrRecommendationResponse,
  RecommendedNfr,
} from "../types/nfr";

interface NfrResultProps {
  result: NfrRecommendationResponse;
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

function RecommendationCard({ item }: { item: RecommendedNfr }) {
  const statusClass = item.status.toLowerCase().replaceAll(" ", "-");

  return (
    <article className="nfr-recommendation-card">
      <div className="nfr-card-heading">
        <div>
          <p className="story-id">{item.nfr_id}</p>
          <h3>{item.title}</h3>
        </div>
        <div className="nfr-badges">
          <span className="nfr-category-badge">{item.category}</span>
          <span className={`nfr-status nfr-status-${statusClass}`}>
            {item.status}
          </span>
        </div>
      </div>

      <p>
        <strong>Requirement:</strong> {item.requirement}
      </p>
      <p>
        <strong>Rationale:</strong> {item.rationale}
      </p>

      <div className="nfr-detail-grid">
        <div>
          <h4>Source References</h4>
          {renderStringList(
            item.source_references,
            "No source references identified."
          )}
        </div>
        <div>
          <h4>Assumptions</h4>
          {renderStringList(item.assumptions, "No recommendation assumptions.")}
        </div>
      </div>

      <dl className="nfr-facts">
        <div>
          <dt>Measurable</dt>
          <dd>{item.measurable ? "Yes" : "No"}</dd>
        </div>
        <div>
          <dt>Measurement method</dt>
          <dd>{item.measurement_method || "Not provided."}</dd>
        </div>
        <div>
          <dt>Missing target</dt>
          <dd>{item.missing_target || "No missing target."}</dd>
        </div>
      </dl>

      <div
        className={
          item.requires_human_validation ? "review-needed" : "review-pass"
        }
      >
        <strong>
          Human validation:{" "}
          {item.requires_human_validation ? "Required" : "Not required"}
        </strong>
        <p>{item.validation_reason || "No additional validation reason."}</p>
      </div>
    </article>
  );
}

function CategoryAssessmentCard({
  assessment,
}: {
  assessment: NfrCategoryAssessment;
}) {
  return (
    <article className="nfr-category-assessment">
      <div className="nfr-category-heading">
        <h3>{assessment.category}</h3>
        <span
          className={
            assessment.relevant
              ? "nfr-relevance nfr-relevance-yes"
              : "nfr-relevance nfr-relevance-no"
          }
        >
          {assessment.relevant ? "Relevant" : "Not relevant"}
        </span>
      </div>
      <p>
        <strong>Rationale:</strong> {assessment.rationale}
      </p>
      <h4>Recommendation IDs</h4>
      {renderStringList(
        assessment.recommendation_ids,
        "No recommendations linked."
      )}
    </article>
  );
}

export default function NfrResult({ result }: NfrResultProps) {
  return (
    <div className="nfr-result">
      <section className="result-section">
        <h2>Requirement Summary</h2>
        <p>{result.requirement_summary}</p>
      </section>

      <section className="result-section">
        <h2>Relevant Category Assessments</h2>
        {result.relevant_categories.length > 0 ? (
          <div className="nfr-category-list">
            {result.relevant_categories.map((assessment, index) => (
              <CategoryAssessmentCard
                key={`${assessment.category}-${index}`}
                assessment={assessment}
              />
            ))}
          </div>
        ) : (
          <p className="empty-message">No category assessments provided.</p>
        )}
      </section>

      <section className="result-section">
        <h2>Recommendations</h2>
        {result.recommendations.length > 0 ? (
          <div className="nfr-recommendations">
            {result.recommendations.map((item) => (
              <RecommendationCard key={item.nfr_id} item={item} />
            ))}
          </div>
        ) : (
          <p className="empty-message">No NFR recommendations generated.</p>
        )}
      </section>

      <ListSection
        title="Existing NFR Coverage"
        items={result.existing_nfr_coverage}
        emptyMessage="No existing NFR coverage identified."
      />
      <ListSection
        title="Duplicate Existing NFRs"
        items={result.duplicate_existing_nfrs}
        emptyMessage="No duplicate existing NFRs identified."
      />
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
        title="Human Validation Required"
        items={result.human_validation_required}
        emptyMessage="No human validation items identified."
      />
    </div>
  );
}
