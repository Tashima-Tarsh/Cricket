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
const UniqueEngineView = lazy(() => import("./views/UniqueEngineView").then(module => ({ default: module.UniqueEngineView })));
const AIAnalyst = lazy(() => import("./views/AIAnalyst").then(module => ({ default: module.AIAnalyst })));
const SettingsProviders = lazy(() => import("./views/SettingsProviders").then(module => ({ default: module.SettingsProviders })));
const ValueBetsOracle = lazy(() => import("./views/ValueBetsOracle").then(module => ({ default: module.ValueBetsOracle })));
const PlayerPropsOracle = lazy(() => import("./views/PlayerPropsOracle").then(module => ({ default: module.PlayerPropsOracle })));
const TeamDeepDiveOracle = lazy(() => import("./views/TeamDeepDiveOracle").then(module => ({ default: module.TeamDeepDiveOracle })));


import { MatchInfo, WorkspaceTab } from "./types";

const MainAppContent: React.FC = () => {
  const {
    stateStatus,
    stateError,
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
            {stateStatus === "loading" && (
        <div role="status" className="mb-4 flex items-center gap-3 rounded-lg border border-cyan-500/20 bg-slate-900/80 px-4 py-3 text-sm text-cyan-300">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-cyan-400 border-t-transparent" />
          <span>Synchronizing fixture telemetry, lineups and models...</span>
        </div>
      )}
      {stateStatus === "error" && (
        <div role="alert" className="mb-4 flex items-center justify-between rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-300">
          <span>{stateError || "Fixture telemetry error."}</span>
          <button type="button" onClick={() => setIsMatchSetupOpen(true)} className="rounded bg-amber-500/20 px-3 py-1 text-xs border border-amber-500/40 hover:bg-amber-500/30">
            Open Match Setup
          </button>
        </div>
      )}
      {!currentMatch.id && activeTab !== "providers" && activeTab !== "ai-analyst" && activeTab !== "pitch-lab" && activeTab !== "match-studio" && activeTab !== "series-intelligence" && activeTab !== "value-bets" && activeTab !== "player-props" && activeTab !== "team-deep-dive" && (
        <div className="mb-4 rounded-xl border border-white/10 bg-gradient-to-r from-slate-900 to-indigo-950/40 p-5 text-white flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <h3 className="font-bold text-base text-amber-300 flex items-center gap-2">
              <span>⚡</span> No Active Fixture Connected
            </h3>
            <p className="text-xs text-slate-300">
              Select an archived match from Cricsheet, sync live fixtures, or configure custom playing XIs in Match Studio to unlock full tactical analysis and GL lineup generation.
            </p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button
              type="button"
              onClick={() => setIsMatchSetupOpen(true)}
              className="px-4 py-2 text-xs font-bold rounded-lg bg-emerald-500 text-slate-950 hover:bg-emerald-400 transition"
            >
              Open Match Setup
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("series-intelligence")}
              className="px-3 py-2 text-xs rounded-lg border border-white/20 text-white hover:bg-white/10 transition"
            >
              Match Archive
            </button>
          </div>
        </div>
      )}
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
          trajectories={[]}
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

      {/* Grand League Unique Team Engine */}
      {activeTab === "unique-engine" && (
        <UniqueEngineView />
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

      {/* THENITISHKR-SPORTS Wicket Oracle Views */}
      {activeTab === "value-bets" && (
        <ValueBetsOracle />
      )}

      {activeTab === "player-props" && (
        <PlayerPropsOracle />
      )}

      {activeTab === "team-deep-dive" && (
        <TeamDeepDiveOracle />
      )}
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
