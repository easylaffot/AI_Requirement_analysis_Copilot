import { useState } from "react";

import BrdAnalyzer from "./pages/BrdAnalyzer";
import IncidentAnalyzer from "./pages/IncidentAnalyzer";
import UserStoryGenerator from "./pages/UserStoryGenerator";
import AcceptanceCriteriaGenerator from "./pages/AcceptanceCriteriaGenerator";
import NfrRecommender from "./pages/NfrRecommender";
import AmbiguityDetector from "./pages/AmbiguityDetector";

function App() {
  const [selectedModule, setSelectedModule] = useState<
    | "incident"
    | "brd"
    | "user-story"
    | "acceptance-criteria"
    | "nfr"
    | "ambiguity"
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
      </nav>

      {selectedModule === "incident" && <IncidentAnalyzer />}
      {selectedModule === "brd" && <BrdAnalyzer />}
      {selectedModule === "user-story" && <UserStoryGenerator />}
      {selectedModule === "acceptance-criteria" && (
        <AcceptanceCriteriaGenerator />
      )}
      {selectedModule === "nfr" && <NfrRecommender />}
      {selectedModule === "ambiguity" && <AmbiguityDetector />}
    </div>
  );
}

export default App;