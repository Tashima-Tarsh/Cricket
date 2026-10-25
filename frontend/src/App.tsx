import { WorkspaceBoundary } from "./components/WorkspaceBoundary";
import React, { useState, lazy, Suspense } from "react";
import { MatchContextProvider, useMatchContext } from "./context/MatchContext";
import { AppShell } from "./components/AppShell";
import { MatchSetupModal } from "./components/MatchSetupModal";

// 12 Views
const CommandCenter = lazy(() => import("./views/CommandCenter").then(module => ({ default: module.CommandCenter })));
const MatchStudio = lazy(() => import("./views/MatchStudio").then(module => ({ default: module.MatchStudio })));
const BallByBallLab = lazy(() => import("./views/BallByBallLab").then(module => ({ default: module.BallByBallLab })));
const MatchArchive = lazy(() => import("./views/MatchArchive").then(module => ({ default: module.MatchArchive })));
const PitchLab = lazy(() => import("./views/PitchLab").then(module => ({ default: module.PitchLab })));
const BattleArena = lazy(() => import("./views/BattleArena").then(module => ({ default: module.BattleArena })));
const FieldStrategy = lazy(() => import("./views/FieldStrategy").then(module => ({ default: module.FieldStrategy })));
const GamePlan = lazy(() => import("./views/GamePlan").then(module => ({ default: module.GamePlan })));
const PlayerIntel = lazy(() => import("./views/PlayerIntel").then(module => ({ default: module.PlayerIntel })));
const ScenarioLab = lazy(() => import("./views/ScenarioLab").then(module => ({ default: module.ScenarioLab })));
const FantasyLab = lazy(() => import("./views/FantasyLab").then(module => ({ default: module.FantasyLab })));
const AIAnalyst = lazy(() => import("./views/AIAnalyst").then(module => ({ default: module.AIAnalyst })));
const SettingsProviders = lazy(() => import("./views/SettingsProviders").then(module => ({ default: module.SettingsProviders })));

import { mockTrajectories } from "./data/mockData";
import { MatchInfo, WorkspaceTab } from "./types";

const MainAppContent: React.FC = () => {
  const {
    stateStatus,
    activeTab,
    setActiveTab,
    currentMatch,
    setCurrentMatch,
    currentPlayers,
    currentBattles,
    currentLineups,
    currentProviders,
    navigateToWorkspace,
    refreshState
  } = useMatchContext();

  const [isMatchSetupOpen, setIsMatchSetupOpen] = useState<boolean>(false);

  const handleApplyMatch = (newMatch: MatchInfo) => {
    void refreshState(newMatch.id);
  };

  return (
    <AppShell onOpenMatchSetup={() => setIsMatchSetupOpen(true)}>
      <WorkspaceBoundary workspace={activeTab}>
      <Suspense fallback={<p role="status">Loading workspace...</p>}>
      {stateStatus !== "ready" ? <p>Load the local snapshot to open analysis workspaces.</p> : <>
      {/* 1. Command Center */}
      {activeTab === "command-center" && (
        <CommandCenter
          match={currentMatch}
          players={currentPlayers}
          battles={currentBattles}
          onNavigate={(tab) => navigateToWorkspace(tab)}
        />
      )}

      {/* Match & Lineup Studio */}
      {activeTab === "match-studio" && (
        <MatchStudio />
      )}

      {/* 2. Ball-by-Ball Lab */}
      {activeTab === "ball-by-ball" && (
        <BallByBallLab />
      )}

      {/* 3. Series Intelligence */}
      {activeTab === "series-intelligence" && (
        <MatchArchive currentMatch={currentMatch} />
      )}

      {/* 4. 3D Pitch Lab */}
      {activeTab === "pitch-lab" && (
        <PitchLab />
      )}

      {/* 5. Battle Arena */}
      {activeTab === "battle-arena" && (
        <BattleArena
          battles={currentBattles}
          trajectories={mockTrajectories}
        />
      )}

      {/* 6. Field Strategy Lab */}
      {activeTab === "field-strategy" && (
        <FieldStrategy />
      )}

      {/* 7. Over-by-Over Game Plan */}
      {activeTab === "game-plan" && (
        <GamePlan />
      )}

      {/* 8. Player Intel */}
      {activeTab === "player-intel" && (
        <PlayerIntel players={currentPlayers} />
      )}

      {/* 9. Scenario & DLS Lab */}
      {activeTab === "scenario-lab" && (
        <ScenarioLab />
      )}

      {/* 10. Fantasy Optimizer */}
      {activeTab === "fantasy-lab" && (
        <FantasyLab
          lineups={currentLineups}
          players={currentPlayers}
        />
      )}

      {/* 11. AI Tactical Analyst */}
      {activeTab === "ai-analyst" && (
        <AIAnalyst />
      )}

      {/* 12. Live Providers */}
      {activeTab === "providers" && (
        <SettingsProviders providers={currentProviders} />
      )}

      </>}
      </Suspense>
      </WorkspaceBoundary>
      {/* Match Setup & Ingestion Modal */}
      <MatchSetupModal
        isOpen={isMatchSetupOpen}
        onClose={() => setIsMatchSetupOpen(false)}
        currentMatch={currentMatch}
        onApplyMatch={handleApplyMatch}
        players={currentPlayers}
      />
    </AppShell>
  );
};

export function App() {
  return (
    <MatchContextProvider>
      <MainAppContent />
    </MatchContextProvider>
  );
}

export default App;
