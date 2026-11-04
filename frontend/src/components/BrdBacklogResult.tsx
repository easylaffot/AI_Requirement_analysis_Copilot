import type {
  BrdAnalysisResponse,
  Epic,
  Feature,
  UserStory,
} from "../types/brd";

interface BrdBacklogResultProps {
  result: BrdAnalysisResponse;
}

interface ListSectionProps {
  title: string;
  items: string[];
  emptyMessage: string;
}

function ListSection({
  title,
  items,
  emptyMessage,
}: ListSectionProps) {
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

function renderIdList(ids: string[], emptyMessage: string) {
  return ids.length > 0 ? (
    <ul className="compact-list">
      {ids.map((id) => (
        <li key={id}>{id}</li>
      ))}
    </ul>
  ) : (
    <p className="empty-message">{emptyMessage}</p>
  );
}

function renderStory(story: UserStory) {
  return (
    <article className="story-card" key={story.story_id}>
      <div className="story-heading">
        <h5>
          {story.story_id}: {story.title}
        </h5>
        <span
          className={`priority-badge priority-${story.priority.toLowerCase()}`}
        >
          {story.priority}
        </span>
      </div>

      <p>{story.story}</p>
      <p>
        <strong>Priority justification:</strong>{" "}
        {story.priority_justification}
      </p>

      <div className="story-metadata">
        <div>
          <h6>Source requirement IDs</h6>
          {renderIdList(
            story.source_requirement_ids,
            "No source requirements were listed."
          )}
        </div>
        <div>
          <h6>Dependencies</h6>
          {renderIdList(story.dependencies, "No dependencies.")}
        </div>
      </div>

      <p>
        <strong>Splitting:</strong>{" "}
        {story.may_require_splitting
          ? "May require splitting"
          : "Splitting is not currently indicated"}
      </p>
      {story.may_require_splitting && story.splitting_reason && (
        <p>
          <strong>Splitting reason:</strong> {story.splitting_reason}
        </p>
      )}

      <div className="acceptance-criteria">
        <h6>Acceptance Criteria</h6>
        {story.acceptance_criteria.length > 0 ? (
          <ol>
            {story.acceptance_criteria.map((criterion) => (
              <li key={criterion.criterion_id}>
                <strong>{criterion.criterion_id}:</strong> {criterion.criterion}
              </li>
            ))}
          </ol>
        ) : (
          <p className="empty-message">
            No acceptance criteria were provided.
          </p>
        )}
      </div>
    </article>
  );
}

function renderFeature(feature: Feature) {
  return (
    <section className="feature-card" key={feature.feature_id}>
      <h4>
        Feature {feature.feature_id}: {feature.name}
      </h4>
      <p>{feature.description}</p>
      <div className="backlog-source-ids">
        <strong>Source requirement IDs:</strong>
        {renderIdList(
          feature.source_requirement_ids,
          "No source requirements were listed."
        )}
      </div>

      <div className="user-stories">
        <h5>User Stories</h5>
        {feature.user_stories.length > 0 ? (
          feature.user_stories.map(renderStory)
        ) : (
          <p className="empty-message">No user stories were generated.</p>
        )}
      </div>
    </section>
  );
}

function renderEpic(epic: Epic) {
  return (
    <article className="epic-card" key={epic.epic_id}>
      <h3>
        Epic {epic.epic_id}: {epic.name}
      </h3>
      <p>
        <strong>Business value:</strong> {epic.business_value}
      </p>
      <div className="backlog-source-ids">
        <strong>Source requirement IDs:</strong>
        {renderIdList(
          epic.source_requirement_ids,
          "No source requirements were listed."
        )}
      </div>

      <div className="features">
        <h4>Features</h4>
        {epic.features.length > 0 ? (
          epic.features.map(renderFeature)
        ) : (
          <p className="empty-message">No features were generated.</p>
        )}
      </div>
    </article>
  );
}

export default function BrdBacklogResult({
  result,
}: BrdBacklogResultProps) {
  return (
    <div className="brd-result">
      <section className="result-section">
        <h2>BRD Summary</h2>
        <p>{result.brd_summary}</p>
      </section>

      <section className="result-section">
        <h2>Business Problem</h2>
        <p>{result.business_problem}</p>
      </section>

      <ListSection
        title="Business Goals"
        items={result.business_goals}
        emptyMessage="No business goals were identified."
      />
      <ListSection
        title="Stakeholders and Actors"
        items={result.stakeholders_and_actors}
        emptyMessage="No stakeholders or actors were identified."
      />
      <ListSection
        title="Confirmed Scope"
        items={result.confirmed_scope}
        emptyMessage="No confirmed scope items were identified."
      />

      <section className="result-section">
        <h2>Extracted Requirements</h2>
        {result.extracted_requirements.length > 0 ? (
          <div className="requirement-list">
            {result.extracted_requirements.map((requirement) => (
              <article
                className="requirement-card"
                key={requirement.requirement_id}
              >
                <h3>{requirement.requirement_id}</h3>
                <p>{requirement.requirement_text}</p>
                <dl>
                  <div>
                    <dt>Category</dt>
                    <dd>{requirement.category}</dd>
                  </div>
                  <div>
                    <dt>Source reference</dt>
                    <dd>{requirement.source_reference}</dd>
                  </div>
                  <div>
                    <dt>Confidence</dt>
                    <dd>{requirement.confidence}</dd>
                  </div>
                </dl>
              </article>
            ))}
          </div>
        ) : (
          <p className="empty-message">
            No requirements were extracted from this BRD.
          </p>
        )}
      </section>

      <section className="result-section">
        <h2>Agile Backlog</h2>
        {result.epics.length > 0 ? (
          <div className="epic-list">{result.epics.map(renderEpic)}</div>
        ) : (
          <p className="empty-message">No epics were generated.</p>
        )}
      </section>

      <ListSection
        title="Assumptions"
        items={result.assumptions}
        emptyMessage="No assumptions were identified."
      />
      <ListSection
        title="Ambiguities"
        items={result.ambiguities}
        emptyMessage="No ambiguities were identified."
      />
      <ListSection
        title="Missing Information"
        items={result.missing_information}
        emptyMessage="No missing information was identified."
      />
      <ListSection
        title="Risks"
        items={result.risks}
        emptyMessage="No risks were identified."
      />
      <ListSection
        title="Human Validation Required"
        items={result.human_validation_required}
        emptyMessage="No human validation items were identified."
      />

      <section className="result-section">
        <h2>Traceability</h2>
        {result.traceability.length > 0 ? (
          <div className="traceability-list">
            {result.traceability.map((entry) => (
              <article
                className="traceability-entry"
                key={entry.requirement_id}
              >
                <h3>Requirement {entry.requirement_id}</h3>
                <p>
                  <strong>Backlog item IDs:</strong>
                </p>
                {renderIdList(
                  entry.backlog_item_ids,
                  "No backlog items are linked."
                )}
                <p>
                  <strong>Coverage status:</strong> {entry.coverage_status}
                </p>
                <p>
                  <strong>Notes:</strong> {entry.notes}
                </p>
              </article>
            ))}
          </div>
        ) : (
          <p className="empty-message">
            No traceability entries were provided.
          </p>
        )}
      </section>
    </div>
  );
}
