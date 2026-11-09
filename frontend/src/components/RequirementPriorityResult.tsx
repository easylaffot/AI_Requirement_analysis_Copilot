import type {
  Priority,
  PriorityEvidence,
  PriorityFactor,
  PrioritySummaryEntry,
  PrioritizedRequirement,
  RequirementPriorityResponse,
} from "../types/requirementPriority";

interface RequirementPriorityResultProps {
  result: RequirementPriorityResponse;
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

function priorityClass(priority: Priority): string {
  return `priority-${priority.toLowerCase()}`;
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

function FactorRow({ factor }: { factor: PriorityFactor }) {
  const evidenceIds = nonEmpty(factor.evidence_ids);

  return (
    <article className="priority-factor-row">
      <div>
        <h5>{factor.factor}</h5>
        <span
          className={`factor-assessment assessment-${factor.assessment.toLowerCase()}`}
        >
          {factor.assessment}
        </span>
      </div>
      <p>{display(factor.rationale)}</p>
      <p>
        <strong>Evidence IDs:</strong>{" "}
        {evidenceIds.length > 0 ? evidenceIds.join(", ") : "None provided."}
      </p>
    </article>
  );
}

function EvidenceCard({ evidence }: { evidence: PriorityEvidence }) {
  return (
    <article className="priority-evidence-panel">
      <dl>
        <div>
          <dt>Evidence ID</dt>
          <dd>{display(evidence.evidence_id)}</dd>
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

function PrioritizedRequirementCard({
  requirement,
}: {
  requirement: PrioritizedRequirement;
}) {
  const dependencies = nonEmpty(requirement.dependency_ids);
  const missingInformation = nonEmpty(requirement.missing_information);
  const clarificationQuestions = nonEmpty(requirement.clarification_questions);
  const readinessClass = requirement.implementation_ready ? "ready" : "not-ready";

  return (
    <article className="prioritized-requirement-card">
      <div className="prioritized-requirement-heading">
        <div>
          <p className="prioritized-requirement-id">
            {display(requirement.requirement_id)}
          </p>
          <h3>{display(requirement.title)}</h3>
        </div>
        <div className="priority-badges">
          <span
            className={`priority-badge ${priorityClass(
              requirement.recommended_priority
            )}`}
          >
            {requirement.recommended_priority}
          </span>
          <span
            className={`moscow-badge moscow-${requirement.moscow_category
              .toLowerCase()
              .replaceAll(/[^a-z]+/g, "-")}`}
          >
            {requirement.moscow_category}
          </span>
          <span
            className={`evidence-strength-badge evidence-strength-${requirement.evidence_strength.toLowerCase()}`}
          >
            {requirement.evidence_strength} evidence
          </span>
        </div>
      </div>

      <section className="priority-rationale">
        <h4>Priority rationale</h4>
        <p>{display(requirement.priority_rationale)}</p>
      </section>

      <section className="priority-subsection">
        <h4>Priority factors</h4>
        {requirement.factors.length > 0 ? (
          <div className="priority-factor-list">
            {requirement.factors.map((factor, index) => (
              <FactorRow key={`${factor.factor}-${index}`} factor={factor} />
            ))}
          </div>
        ) : (
          <p className="empty-message">No priority factors provided.</p>
        )}
      </section>

      <section className="priority-subsection">
        <h4>Evidence</h4>
        {requirement.evidence.length > 0 ? (
          <div className="priority-evidence-list">
            {requirement.evidence.map((evidence, index) => (
              <EvidenceCard
                key={`${evidence.evidence_id}-${index}`}
                evidence={evidence}
              />
            ))}
          </div>
        ) : (
          <p className="empty-message">No evidence provided.</p>
        )}
      </section>

      <dl className="priority-requirement-facts">
        <div>
          <dt>Dependency IDs</dt>
          <dd>
            {dependencies.length > 0
              ? dependencies.join(", ")
              : "No dependencies identified."}
          </dd>
        </div>
        <div>
          <dt>Implementation ready</dt>
          <dd>
            <span className={`priority-readiness readiness-${readinessClass}`}>
              {requirement.implementation_ready ? "Ready" : "Not ready"}
            </span>
          </dd>
        </div>
        <div>
          <dt>Readiness explanation</dt>
          <dd>{display(requirement.readiness_explanation)}</dd>
        </div>
      </dl>

      {requirement.priority_conflict_detected && (
        <section className="priority-conflict-warning">
          <h4>Priority conflict detected</h4>
          <p>
            {display(
              requirement.priority_conflict_explanation ?? "",
              "No conflict explanation provided."
            )}
          </p>
        </section>
      )}

      <section className="priority-subsection">
        <h4>Missing information</h4>
        {missingInformation.length > 0 ? (
          <ul className="compact-list">
            {missingInformation.map((item, index) => (
              <li key={`${index}-${item}`}>{item}</li>
            ))}
          </ul>
        ) : (
          <p className="empty-message">No missing information identified.</p>
        )}
      </section>

      <section className="priority-subsection">
        <h4>Clarification questions</h4>
        {clarificationQuestions.length > 0 ? (
          <ul className="compact-list">
            {clarificationQuestions.map((item, index) => (
              <li key={`${index}-${item}`}>{item}</li>
            ))}
          </ul>
        ) : (
          <p className="empty-message">No clarification questions identified.</p>
        )}
      </section>

      <p className="priority-validation-status">
        <strong>Human validation:</strong>{" "}
        {requirement.requires_human_validation ? "Required" : "Not required"}
      </p>
      {requirement.requires_human_validation && (
        <p>
          <strong>Suggested owner:</strong> {display(requirement.suggested_owner)}
        </p>
      )}
    </article>
  );
}

function PrioritySummaryCard({ entry }: { entry: PrioritySummaryEntry }) {
  const requirementIds = nonEmpty(entry.requirement_ids);

  return (
    <article className="priority-summary-card">
      <span className={`priority-badge ${priorityClass(entry.priority)}`}>
        {entry.priority}
      </span>
      <p className="priority-summary-count">{entry.count}</p>
      <p>
        {requirementIds.length > 0
          ? requirementIds.join(", ")
          : "No requirement IDs."}
      </p>
    </article>
  );
}

export default function RequirementPriorityResult({
  result,
}: RequirementPriorityResultProps) {
  const readinessClass = result.readiness_status
    .toLowerCase()
    .replaceAll(/[^a-z]+/g, "-");
  const deliveryOrder = nonEmpty(result.recommended_delivery_order);
  const blockingIds = nonEmpty(result.blocking_requirement_ids);

  return (
    <div className="result-container requirement-priority-result">
      <section className="result-section">
        <h2>Analysis Summary</h2>
        <p>{display(result.analysis_summary)}</p>
      </section>

      <section className="result-section">
        <h2>Release Objective Summary</h2>
        <p>{display(result.release_objective_summary)}</p>
      </section>

      <section className="result-section">
        <div className="priority-summary-heading">
          <h2>Priority Summary</h2>
          <span
            className={`priority-readiness readiness-${readinessClass}`}
          >
            {result.readiness_status}
          </span>
        </div>
        {result.priority_summary.length > 0 ? (
          <div className="priority-summary-list">
            {result.priority_summary.map((entry, index) => (
              <PrioritySummaryCard
                key={`${entry.priority}-${index}`}
                entry={entry}
              />
            ))}
          </div>
        ) : (
          <p className="empty-message">No priority summary provided.</p>
        )}
        <h3>Blocking requirement IDs</h3>
        {blockingIds.length > 0 ? (
          <ul className="compact-list">
            {blockingIds.map((id, index) => (
              <li key={`${index}-${id}`}>{id}</li>
            ))}
          </ul>
        ) : (
          <p className="empty-message">No blocking requirements identified.</p>
        )}
      </section>

      <section className="result-section">
        <h2>Prioritized Requirements</h2>
        {result.prioritized_requirements.length > 0 ? (
          <div className="prioritized-requirement-list">
            {result.prioritized_requirements.map((requirement, index) => (
              <PrioritizedRequirementCard
                key={`${requirement.requirement_id}-${index}`}
                requirement={requirement}
              />
            ))}
          </div>
        ) : (
          <p className="empty-message">No prioritized requirements provided.</p>
        )}
      </section>

      <section className="result-section">
        <h2>Recommended Delivery Order</h2>
        {deliveryOrder.length > 0 ? (
          <ol className="priority-delivery-order">
            {deliveryOrder.map((requirementId, index) => (
              <li key={`${index}-${requirementId}`}>{requirementId}</li>
            ))}
          </ol>
        ) : (
          <p className="empty-message">No delivery order recommended.</p>
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
        title="Human Validation Required"
        items={result.human_validation_required}
        emptyMessage="No human validation items identified."
      />
    </div>
  );
}
