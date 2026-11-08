import { useState } from "react";

import BrdAnalyzer from "./pages/BrdAnalyzer";
import IncidentAnalyzer from "./pages/IncidentAnalyzer";
import UserStoryGenerator from "./pages/UserStoryGenerator";
import AcceptanceCriteriaGenerator from "./pages/AcceptanceCriteriaGenerator";
import NfrRecommender from "./pages/NfrRecommender";
import AmbiguityDetector from "./pages/AmbiguityDetector";
import GapAnalyzer from "./pages/GapAnalyzer";
import DuplicateRequirementDetector from "./pages/DuplicateRequirementDetector";
import RequirementConflictDetector from "./pages/RequirementConflictDetector";

function App() {
  const [selectedModule, setSelectedModule] = useState<
    | "incident"
    | "brd"
    | "user-story"
    | "acceptance-criteria"
    | "nfr"
    | "ambiguity"
    | "gap-analysis"
    | "duplicate-requirements"
    | "requirement-conflicts"
  >("incident");

  return (
    <div className="app-shell">
      <nav className="module-navigation" aria-label="Application modules">
        <button
          type="button"
          className={selectedModule === "incident" ? "active" : ""}
          aria-current={selectedModule === "incident" ? "page" : undefined}
          onClick={() => setSelectedModule("incident")}
        >
          Incident Analyzer
        </button>
        <button
          type="button"
          className={selectedModule === "brd" ? "active" : ""}
          aria-current={selectedModule === "brd" ? "page" : undefined}
          onClick={() => setSelectedModule("brd")}
        >
          BRD to Backlog
        </button>
        <button
          type="button"
          className={selectedModule === "user-story" ? "active" : ""}
          aria-current={
            selectedModule === "user-story" ? "page" : undefined
          }
          onClick={() => setSelectedModule("user-story")}
        >
          User Story Generator
        </button>
        <button
          type="button"
          className={
            selectedModule === "acceptance-criteria" ? "active" : ""
          }
          aria-current={
            selectedModule === "acceptance-criteria" ? "page" : undefined
          }
          onClick={() => setSelectedModule("acceptance-criteria")}
        >
          Acceptance Criteria
        </button>
        <button
          type="button"
          className={selectedModule === "nfr" ? "active" : ""}
          aria-current={selectedModule === "nfr" ? "page" : undefined}
          onClick={() => setSelectedModule("nfr")}
        >
          NFR Recommender
        </button>
        <button
          type="button"
          className={selectedModule === "ambiguity" ? "active" : ""}
          aria-current={selectedModule === "ambiguity" ? "page" : undefined}
          onClick={() => setSelectedModule("ambiguity")}
        >
          Ambiguity Detector
        </button>
        <button
          type="button"
          className={selectedModule === "gap-analysis" ? "active" : ""}
          aria-current={
            selectedModule === "gap-analysis" ? "page" : undefined
          }
          onClick={() => setSelectedModule("gap-analysis")}
        >
          Gap Analyzer
        </button>
        <button
          type="button"
          className={
            selectedModule === "duplicate-requirements" ? "active" : ""
          }
          aria-current={
            selectedModule === "duplicate-requirements" ? "page" : undefined
          }
          onClick={() => setSelectedModule("duplicate-requirements")}
        >
          Duplicate Detector
        </button>
        <button
          type="button"
          className={selectedModule === "requirement-conflicts" ? "active" : ""}
          aria-current={
            selectedModule === "requirement-conflicts" ? "page" : undefined
          }
          onClick={() => setSelectedModule("requirement-conflicts")}
        >
          Conflict Detector
        </button>
      </nav>

      {selectedModule === "incident" && <IncidentAnalyzer />}
      {selectedModule === "brd" && <BrdAnalyzer />}
      {selectedModule === "user-story" && <UserStoryGenerator />}
      {selectedModule === "acceptance-criteria" && (
        <AcceptanceCriteriaGenerator />
      )}
      {selectedModule === "nfr" && <NfrRecommender />}
      {selectedModule === "ambiguity" && <AmbiguityDetector />}
      {selectedModule === "gap-analysis" && <GapAnalyzer />}
      {selectedModule === "duplicate-requirements" && (
        <DuplicateRequirementDetector />
      )}
      {selectedModule === "requirement-conflicts" && (
        <RequirementConflictDetector />
      )}
    </div>
  );
}

export default App;