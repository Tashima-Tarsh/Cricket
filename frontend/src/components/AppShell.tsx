import React, { useState } from "react";
import { 
  Menu, 
  X, 
  Search, 
  PanelRightOpen, 
  LayoutDashboard, 
  Activity, 
  Archive, 
  Compass, 
  Swords, 
  Shield, 
  Clock, 
  Users, 
  Sliders, 
  Trophy, 
  Bot, 
  Database,
  Radio,
  RefreshCw,
  Sparkles,
  CloudRain
} from "lucide-react";
import { useMatchContext } from "../context/MatchContext";
import { WorkspaceTab } from "../types";
import { IntelligenceDrawer } from "./IntelligenceDrawer";
import { useDialog } from "../hooks/useDialog";

interface NavItem {
  id: WorkspaceTab;
  label: string;
  icon: React.ElementType;
}

const groups: { label: string; items: NavItem[] }[] = [
  {
    label: "Match & Feed",
    items: [
      { id: "command-center", label: "Command Center", icon: LayoutDashboard },
      { id: "ball-by-ball", label: "Ball by Ball 3D", icon: Activity },
      { id: "series-intelligence", label: "Match Archive", icon: Archive }
    ]
  },
  {
    label: "Opposition Intel",
    items: [
      { id: "battle-arena", label: "H2H Battles", icon: Swords },
      { id: "pitch-lab", label: "Pitch & Venue Lab", icon: Compass },
      { id: "field-strategy", label: "Field Strategy", icon: Shield },
      { id: "game-plan", label: "Over-by-Over Plan", icon: Clock },
      { id: "player-intel", label: "Player Directory", icon: Users },
      { id: "scenario-lab", label: "Match Scenarios", icon: Sliders }
    ]
  },
  {
    label: "Optimization & AI",
    items: [
      { id: "fantasy-lab", label: "GL Lineup Solver", icon: Trophy },
      { id: "ai-analyst", label: "AI Analyst Query", icon: Bot },
      { id: "providers", label: "Data Providers Hub", icon: Database }
    ]
  }
];

export const AppShell: React.FC<{ children: React.ReactNode; onOpenMatchSetup: () => void }> = ({
  children,
  onOpenMatchSetup
}) => {
  const {
    currentMatch,
    currentPlayers,
    activeTab,
    setActiveTab,
    activeOvers,
    setActiveOvers,
    isDrawerOpen,
    setIsDrawerOpen,
    searchQuery,
    setSearchQuery,
    navigateToWorkspace,
    stateStatus,
    stateError,
    lastUpdated,
    refreshState
  } = useMatchContext();

  const [mobileOpen, setMobileOpen] = useState(false);
  const mobileRef = useDialog(mobileOpen, () => setMobileOpen(false));
  const query = searchQuery.trim().toLowerCase();

  const allItems = groups.flatMap((group) => group.items);
  const matchingWorkspaces = allItems.filter((item) =>
    item.label.toLowerCase().includes(query)
  );
  const matchingPlayers = currentPlayers
    .filter((player) => player.name.toLowerCase().includes(query))
    .slice(0, 6);

  const navigate = (tab: WorkspaceTab) => {
    setActiveTab(tab);
    setMobileOpen(false);
    setSearchQuery("");
  };

  const navigation = (
    <nav aria-label="Workspaces" className="space-y-4">
      {groups.map((group) => (
        <section key={group.label} className="nav-group">
          <h2>{group.label}</h2>
          <div className="space-y-1">
            {group.items.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  aria-current={isActive ? "page" : undefined}
                  onClick={() => navigate(item.id)}
                  className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-[0_0_12px_rgba(16,185,129,0.15)] font-semibold"
                      : "text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]"
                  }`}
                >
                  <Icon size={15} className={isActive ? "text-emerald-400" : "text-slate-400"} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>
        </section>
      ))}
    </nav>
  );

  return (
    <div className="editorial-app">
      <a href="#workspace" className="skip-link">Skip to workspace</a>

      {/* Top Professional Command Header */}
      <header className="app-header">
        <button
          className="mobile-menu"
          aria-label="Open navigation"
          aria-expanded={mobileOpen}
          onClick={() => setMobileOpen(true)}
        >
          <Menu size={20} />
        </button>

        <button className="brand" onClick={() => navigate("command-center")}>
          <div className="w-8 h-8 rounded-lg bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shadow-[0_0_12px_rgba(16,185,129,0.2)]">
            <Radio size={16} className="animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-white text-base font-bold tracking-tight">STRIKE//OS</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-mono font-bold tracking-widest">PRO</span>
            </div>
            <span>Cricket analysis workspace</span>
          </div>
        </button>

        {/* Center Current Fixture Pill & Global Overs Selector */}
        <div className="hidden lg:flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/90 border border-white/10 text-xs font-mono">
            <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-slate-200 font-semibold">{currentMatch.name}</span>
            <span className="text-slate-500">|</span>
            <span className="text-slate-400">{currentMatch.venue?.name?.split(",")[0] || "Chinnaswamy"}</span>
          </div>

          {/* Interactive Rain Curtailment Control (Any Over 5 to 20) */}
          <div className="flex items-center gap-1.5 bg-slate-950/80 border border-white/10 p-1 rounded-lg shadow-inner">
            <span className="text-[10px] font-mono uppercase px-1.5 text-slate-400 font-bold flex items-center gap-1">
              <CloudRain size={13} className={activeOvers < 20 ? "text-amber-400 animate-bounce" : "text-slate-400"} />
              {activeOvers < 20 ? `${activeOvers} OV (ILLUSTRATIVE)` : "20 OV"}
            </span>

            {/* Stepper buttons & direct input */}
            <div className="flex items-center bg-slate-900 border border-white/10 rounded px-0.5">
              <button
                type="button"
                onClick={() => setActiveOvers(Math.max(5, activeOvers - 1))}
                className="px-1 text-slate-400 hover:text-white font-mono font-bold text-xs"
                title="Decrease 1 over"
              >
                -
              </button>
              <input
                type="number"
                min={5}
                max={20}
                value={activeOvers}
                onChange={(e) => {
                  const val = parseInt(e.target.value, 10);
                  if (!isNaN(val)) setActiveOvers(Math.max(5, Math.min(20, val)));
                }}
                className="w-8 bg-transparent text-center font-mono font-extrabold text-xs text-amber-400 focus:outline-none"
                title="Type any over count (5 to 20)"
              />
              <button
                type="button"
                onClick={() => setActiveOvers(Math.min(20, activeOvers + 1))}
                className="px-1 text-slate-400 hover:text-white font-mono font-bold text-xs"
                title="Increase 1 over"
              >
                +
              </button>
            </div>

            {/* Quick Chips */}
            {[20, 15, 13, 10, 5].map((ov) => (
              <button
                key={ov}
                onClick={() => setActiveOvers(ov)}
                className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-bold transition-all ${
                  activeOvers === ov
                    ? (ov < 20 ? "bg-amber-500 text-slate-950 font-extrabold shadow-md" : "bg-emerald-500 text-slate-950 font-extrabold shadow-md")
                    : "text-slate-400 hover:text-white hover:bg-white/5"
                }`}
                title={`Curtain match to ${ov} overs (heuristic projections)`}
              >
                {ov}
              </button>
            ))}
          </div>
        </div>

        <div className="header-actions">
          <button onClick={onOpenMatchSetup} className="flex items-center gap-2">
            <Sparkles size={14} className="text-emerald-400" />
            <span>SERIES FIXTURES</span>
          </button>
          <button
            aria-label="Open analyst notes"
            onClick={() => setIsDrawerOpen(true)}
            className="flex items-center gap-2"
          >
            <PanelRightOpen size={15} />
            <span className="desktop-label">ANALYST INTEL</span>
          </button>
        </div>
      </header>

      {/* Main Body */}
      <div className="app-body">
        <aside className="desktop-nav">{navigation}</aside>

        <main id="workspace" tabIndex={-1}>
          {/* Top Heading & Quick Command Search */}
          <div className="workspace-heading">
            <div>
              <p className="eyebrow flex items-center gap-2">
                <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400" />
                LOCAL ANALYSIS &bull; FIXTURE & MODEL ASSUMPTIONS REQUIRE VERIFICATION
              </p>
              <h2 className="text-lg font-semibold text-white tracking-tight mt-0.5">
                {currentMatch.name} &bull; {currentMatch.venue?.name}
              </h2>
            </div>

            <form
              className="workspace-search"
              role="search"
              onSubmit={(event) => {
                event.preventDefault();
                if (matchingWorkspaces[0]) navigate(matchingWorkspaces[0].id);
                else if (matchingPlayers[0]) {
                  navigateToWorkspace("player-intel", matchingPlayers[0].id);
                  setSearchQuery("");
                }
              }}
            >
              <Search size={15} />
              <input
                aria-label="Search workspaces and players"
                placeholder="Search workspaces or players..."
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
              />
              {query && (
                <div className="search-results">
                  {matchingWorkspaces.map((item) => (
                    <button
                      type="button"
                      key={item.id}
                      onClick={() => navigate(item.id)}
                    >
                      Workspace &bull; {item.label}
                    </button>
                  ))}
                  {matchingPlayers.map((player) => (
                    <button
                      type="button"
                      key={player.id}
                      onClick={() => {
                        navigateToWorkspace("player-intel", player.id);
                        setSearchQuery("");
                      }}
                    >
                      Player &bull; {player.name} ({player.team} &bull; {player.role})
                    </button>
                  ))}
                  {!matchingWorkspaces.length && !matchingPlayers.length && (
                    <p className="p-2 text-xs text-slate-500">No matching workspace or player.</p>
                  )}
                </div>
              )}
            </form>
          </div>

          {/* Institutional Telemetry Status Strip */}
          <div className="data-status" role="status">
            <div className="flex items-center gap-2.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>
                {stateStatus === "loading"
                  ? "Synchronizing DuckDB Telemetry & CP-SAT Optimizations..."
                  : stateStatus === "error"
                  ? stateError
                  : `Local snapshot | Uncalibrated projections | Generated ${lastUpdated ? new Date(lastUpdated).toLocaleTimeString() : "Live"}`}
              </span>
            </div>
            <button
              onClick={() => refreshState(currentMatch.id)}
              disabled={stateStatus === "loading"}
              className="flex items-center gap-1.5"
            >
              <RefreshCw size={12} className={stateStatus === "loading" ? "animate-spin" : ""} />
              <span>SYNC TELEMETRY</span>
            </button>
          </div>

          {children}
        </main>
      </div>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div className="dialog-backdrop" onClick={() => setMobileOpen(false)}>
          <div
            ref={mobileRef}
            role="dialog"
            aria-modal="true"
            aria-label="Workspace navigation"
            tabIndex={-1}
            className="mobile-navigation"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4 pb-2 border-b border-white/10">
              <span className="font-bold text-sm tracking-wider uppercase text-emerald-400">STRIKE//OS PRO</span>
              <button aria-label="Close navigation" onClick={() => setMobileOpen(false)}>
                <X size={18} />
              </button>
            </div>
            {navigation}
          </div>
        </div>
      )}

      <IntelligenceDrawer isOpen={isDrawerOpen} onClose={() => setIsDrawerOpen(false)} />
    </div>
  );
};
