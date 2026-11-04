import type {
  GeneratedUserStory,
  UserStoryGenerationResponse,
} from "../types/userStory";

interface UserStoryResultProps {
  result: UserStoryGenerationResponse;
}

interface ListSectionProps {
  title: string;
  items: string[];
  emptyMessage: string;
}

interface InvestRowProps {
  name: string;
  passed: boolean;
  explanation: string;
}

const INVEST_CRITERIA: {
  key:
    | "independent"
    | "negotiable"
    | "valuable"
    | "estimable"
    | "small"
    | "testable";
  label: string;
  reasonKey:
    | "independent_reason"
    | "negotiable_reason"
    | "valuable_reason"
    | "estimable_reason"
    | "small_reason"
    | "testable_reason";
}[] = [
  {
    key: "independent",
    label: "Independent",
    reasonKey: "independent_reason",
  },
  {
    key: "negotiable",
    label: "Negotiable",
    reasonKey: "negotiable_reason",
  },
  {
    key: "valuable",
    label: "Valuable",
    reasonKey: "valuable_reason",
  },
  {
    key: "estimable",
    label: "Estimable",
    reasonKey: "estimable_reason",
  },
  {
    key: "small",
    label: "Small",
    reasonKey: "small_reason",
  },
  {
    key: "testable",
    label: "Testable",
    reasonKey: "testable_reason",
  },
];

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

function StringList({
  items,
  emptyMessage,
}: {
  items: string[];
  emptyMessage: string;
}) {
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

function InvestRow({ name, passed, explanation }: InvestRowProps) {
  return (
    <div className="invest-row">
      <strong>{name}</strong>
      <span className={passed ? "invest-status pass" : "invest-status review"}>
        {passed ? "Pass" : "Needs Review"}
      </span>
      <p>{explanation || "No explanation provided."}</p>
    </div>
  );
}

function StoryCard({ story }: { story: GeneratedUserStory }) {
  const { invest_assessment: assessment } = story;

  return (
    <article className="generated-story-card">
      <div className="generated-story-heading">
        <div>
          <p className="story-id">{story.story_id}</p>
          <h3>{story.title}</h3>
        </div>
        <span
          className={`priority-badge priority-${story.priority.toLowerCase()}`}
        >
          {story.priority}
        </span>
      </div>

      <div className="story-facts">
        <p>
          <strong>Actor:</strong> {story.actor}
        </p>
        <p>
          <strong>Goal:</strong> {story.goal}
        </p>
        <p>
          <strong>Business value:</strong> {story.business_value}
        </p>
      </div>

      <blockquote className="full-user-story">{story.story}</blockquote>

      <p>
        <strong>Priority justification:</strong>{" "}
        {story.priority_justification}
      </p>

      <div className="story-detail-grid">
        <div>
          <h4>Source Requirement References</h4>
          <StringList
            items={story.source_requirement_references}
            emptyMessage="No source requirement references identified."
          />
        </div>
        <div>
          <h4>Business Rules Applied</h4>
          <StringList
            items={story.business_rules_applied}
            emptyMessage="No business rules applied."
          />
        </div>
        <div>
          <h4>Dependencies</h4>
          <StringList
            items={story.dependencies}
            emptyMessage="No dependencies identified."
          />
        </div>
      </div>

      <section className="story-acceptance-criteria">
        <h4>Acceptance Criteria</h4>
        {story.acceptance_criteria.length > 0 ? (
          <ol>
            {story.acceptance_criteria.map((criterion) => (
              <li key={criterion.criterion_id}>
                <div className="criterion-heading">
                  <strong>{criterion.criterion_id}</strong>
                  <span
                    className={`criterion-type-badge criterion-type-${criterion.criterion_type
                      .toLowerCase()
                      .replaceAll(" ", "-")}`}
                  >
                    {criterion.criterion_type}
                  </span>
                </div>
                <p>{criterion.criterion}</p>
              </li>
            ))}
          </ol>
        ) : (
          <p className="empty-message">
            No acceptance criteria provided.
          </p>
        )}
      </section>

      <section className="invest-assessment">
        <h4>INVEST Assessment</h4>
        <div className="invest-rows">
          {INVEST_CRITERIA.map(({ key, label, reasonKey }) => (
            <InvestRow
              key={key}
              name={label}
              passed={assessment[key]}
              explanation={assessment[reasonKey]}
            />
          ))}
        </div>
      </section>

      <section
        className={
          story.may_require_further_splitting
            ? "splitting-warning"
            : "splitting-status"
        }
      >
        <h4>Further Splitting</h4>
        <p>
          {story.may_require_further_splitting
            ? "Further splitting may be required."
            : "Further splitting is not indicated."}
        </p>
        {story.splitting_reason && (
          <p>
            <strong>Splitting reason:</strong> {story.splitting_reason}
          </p>
        )}
      </section>
    </article>
  );
}

export default function UserStoryResult({ result }: UserStoryResultProps) {
  return (
    <div className="user-story-result">
      <section className="result-section">
        <h2>Requirement Summary</h2>
        <p>{result.requirement_summary || "No requirement summary provided."}</p>
      </section>

      <ListSection
        title="Confirmed Actors"
        items={result.confirmed_actors}
        emptyMessage="No confirmed actors identified."
      />
      <ListSection
        title="Identified User Goals"
        items={result.identified_user_goals}
        emptyMessage="No user goals identified."
      />

      <section className="result-section">
        <h2>Generated User Stories</h2>
        {result.generated_stories.length > 0 ? (
          <div className="generated-stories">
            {result.generated_stories.map((story) => (
              <StoryCard key={story.story_id} story={story} />
            ))}
          </div>
        ) : (
          <p className="empty-message">No user stories were generated.</p>
        )}
      </section>

      <section className="result-section">
        <h2>Splitting Summary</h2>
        <p>{result.splitting_summary || "No splitting summary provided."}</p>
      </section>

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
