import { useState } from "react";

import BrdAnalyzer from "./pages/BrdAnalyzer";
import IncidentAnalyzer from "./pages/IncidentAnalyzer";

function App() {
  const [selectedModule, setSelectedModule] = useState<
    "incident" | "brd"
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
      </nav>

      {selectedModule === "incident" ? (
        <IncidentAnalyzer />
      ) : (
        <BrdAnalyzer />
      )}
    </div>
  );
}

export default App;