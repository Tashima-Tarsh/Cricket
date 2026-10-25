import { providerTelemetry } from "../data/providerTelemetry";
import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from "react";
import {
  MatchInfo,
  Player,
  HeadToHeadBattle,
  Lineup,
  DataProviderTelemetry,
  WorkspaceTab
} from "../types";
const initialMatch: MatchInfo = {
  id: "ind_w_vs_zim_w_2026_02", 
  name: "India Women vs Zimbabwe Women, 2nd ODI (Vadodara)", 
  format: "Women's One Day International", 
  status: "TOSS CONCLUDED | Zimbabwe Opt to Bat | Both Teams Unchanged",
  venue: { 
    id: "bca_stadium_vadodara", 
    name: "BCA Stadium, Kotambi, Vadodara", 
    city: "Vadodara", 
    soil_type: "Spin-friendly abrasive black soil track at BCA Kotambi", 
    avg_first_innings: 258.0, 
    avg_second_innings: 178.0, 
    chasing_win_pct: 50.0, 
    pace_wicket_pct: 35.1, 
    spin_wicket_pct: 64.9, 
    dew_factor: 0.20, 
    pitch_nature: "Bowling surface favoring spinners (37 of 57 wickets = 64.9% taken by spinners). 1st innings avg 258, 2nd innings avg 178. Turn and grip for slow left-arm orthodox (S Charani) and off-spin (D Sharma, S Verma).", 
    boundaries: { square_leg: 64, midwicket: 68, long_on: 74, straight: 75, long_off: 74, cover: 68, point: 62 } 
  },
  teams: { 
    home: { name: "India Women", code: "IND-W", score: "Bowling First", overs: "50.0" }, 
    away: { name: "Zimbabwe Women", code: "ZIM-W", score: "Batting First", overs: "50.0" } 
  },
  toss: { 
    winner: "Zimbabwe Women", 
    choice: "bat", 
    statement: "Zimbabwe Women won the toss and opted to bat first. India Women bowl first." 
  }, 
  current_crr: 4.15, 
  projected_total: 218, 
  chasing_win_prob: 88.0
};

interface MatchContextType {
  stateStatus: "loading" | "ready" | "error";
  stateError: string | null;
  lastUpdated: string | null;
  refreshState: (targetMatchId?: string, targetOvers?: number) => Promise<void>;
  currentMatch: MatchInfo;
  setCurrentMatch: (m: MatchInfo) => void;
  currentPlayers: Player[];
  currentBattles: HeadToHeadBattle[];
  venuePlayers: any[];
  currentLineups: Lineup[];
  setCurrentLineups: (l: Lineup[]) => void;
  currentProviders: DataProviderTelemetry[];
  
  // Rain & Overs State
  activeOvers: number;
  setActiveOvers: (overs: number) => void;
  rainConstraints: any;
  
  // Navigation & Workspace state
  activeTab: WorkspaceTab;
  setActiveTab: (tab: WorkspaceTab) => void;
  isSidebarCollapsed: boolean;
  setIsSidebarCollapsed: (v: boolean | ((prev: boolean) => boolean)) => void;
  isDrawerOpen: boolean;
  setIsDrawerOpen: (v: boolean | ((prev: boolean) => boolean)) => void;
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  
  // Shared Tactical Focus
  selectedBatter: Player | null;
  setSelectedBatter: (p: Player | null) => void;
  selectedBowler: Player | null;
  setSelectedBowler: (p: Player | null) => void;
  selectedPhase: "Powerplay" | "Middle" | "Death";
  setSelectedPhase: (phase: "Powerplay" | "Middle" | "Death") => void;
  selectedTossChoice: "bat" | "bowl";
  setSelectedTossChoice: (choice: "bat" | "bowl") => void;
  
  // Quick navigation helper
  navigateToWorkspace: (tab: WorkspaceTab, batterId?: string, bowlerId?: string, phase?: "Powerplay" | "Middle" | "Death") => void;
}

const MatchContext = createContext<MatchContextType | undefined>(undefined);

export const MatchContextProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Read initial tab from URL param if available
  const getInitialTab = (): WorkspaceTab => {
    const params = new URLSearchParams(window.location.search);
    const tabParam = params.get("tab") as WorkspaceTab;
    const validTabs: WorkspaceTab[] = [
      "command-center", "match-studio", "player-intel", "battle-arena", "field-strategy",
      "ball-by-ball", "pitch-lab", "scenario-lab", "game-plan",
      "series-intelligence", "fantasy-lab", "ai-analyst", "providers"
    ];
    return validTabs.includes(tabParam) ? tabParam : "command-center";
  };

  const [activeTab, setActiveTabState] = useState<WorkspaceTab>(getInitialTab);
  const [currentMatch, setCurrentMatch] = useState<MatchInfo>(initialMatch);
  const [currentPlayers, setCurrentPlayers] = useState<Player[]>([]);
  const [currentBattles, setCurrentBattles] = useState<HeadToHeadBattle[]>([]);
  const [currentLineups, setCurrentLineups] = useState<Lineup[]>([]);
  const [venuePlayers, setVenuePlayers] = useState<any[]>([]);
  const [currentProviders, setCurrentProviders] = useState<DataProviderTelemetry[]>([]);
  const [activeOvers, setActiveOversState] = useState<number>(20);
  const [rainConstraints, setRainConstraints] = useState<any>(null);

  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);
  const [isDrawerOpen, setIsDrawerOpen] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>("");

  const [selectedBatter, setSelectedBatter] = useState<Player | null>(null);
  const [selectedBowler, setSelectedBowler] = useState<Player | null>(null);
  const [selectedPhase, setSelectedPhase] = useState<"Powerplay" | "Middle" | "Death">("Powerplay");
  const [selectedTossChoice, setSelectedTossChoice] = useState<"bat" | "bowl">("bowl");

  // Sync activeTab to URL without full page reload
  const setActiveTab = (tab: WorkspaceTab) => {
    setActiveTabState(tab);
    const url = new URL(window.location.href);
    url.searchParams.set("tab", tab);
    window.history.replaceState({}, "", url.toString());
  };

  // Navigate with optional focus params
  const navigateToWorkspace = (
    tab: WorkspaceTab,
    batterId?: string,
    bowlerId?: string,
    phase?: "Powerplay" | "Middle" | "Death"
  ) => {
    if (batterId) {
      const b = currentPlayers.find((p) => p.id === batterId);
      if (b) setSelectedBatter(b);
    }
    if (bowlerId) {
      const bw = currentPlayers.find((p) => p.id === bowlerId);
      if (bw) setSelectedBowler(bw);
    }
    if (phase) {
      setSelectedPhase(phase);
    }
    setActiveTab(tab);
  };

  const [stateStatus, setStateStatus] = useState<"loading" | "ready" | "error">("loading");
  const [stateError, setStateError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const requestRef = useRef<AbortController | null>(null);
  const activeMatchRef = useRef(currentMatch.id);
  activeMatchRef.current = currentMatch.id;
  const activeOversRef = useRef<number>(activeOvers);
  activeOversRef.current = activeOvers;

  const refreshState = useCallback(async (targetMatchId?: string, targetOvers?: number) => {
    requestRef.current?.abort();
    const controller = new AbortController();
    requestRef.current = controller;
    setStateStatus("loading"); setStateError(null);
    const timeout = window.setTimeout(() => controller.abort(), 60000);
    const oversToFetch = targetOvers !== undefined ? targetOvers : activeOversRef.current;
    try {
      const matchParam = `match_id=${encodeURIComponent(targetMatchId || activeMatchRef.current)}&`;
      const res = await fetch(`/api/state?${matchParam}overs=${oversToFetch}`, { signal: controller.signal });
      if (!res.ok) throw new Error(`State request failed (${res.status}).`);
      const data = await res.json();
      if (data.status !== "success" || !data.match || !Array.isArray(data.players) || !Array.isArray(data.lineups)) throw new Error("The server returned an incomplete snapshot.");
      if (requestRef.current !== controller) return;
      setCurrentMatch(data.match); setCurrentPlayers(data.players);
      setCurrentBattles(data.battles || []); setCurrentLineups(data.lineups);
      setVenuePlayers(data.venue_players || []);
      setRainConstraints(data.rain_constraints || null);
      setCurrentProviders((data.providers || []).map((raw: DataProviderTelemetry) => providerTelemetry(raw.id,raw)));
      setSelectedBatter(data.players.find((p: Player) => p.role === "BAT" || p.role === "WK") || null);
      setSelectedBowler(data.players.find((p: Player) => p.role === "BOWL" || p.role === "AR") || null);
      setLastUpdated(data.generated_at || new Date().toISOString()); setStateStatus("ready");
    } catch (error) {
      if (requestRef.current !== controller) return;
      setStateError(error instanceof Error && error.name !== "AbortError" ? error.message : "Loading timed out. Check the local server and retry.");
      setStateStatus("error");
    } finally { window.clearTimeout(timeout); }
  }, []);

  const setActiveOvers = (overs: number) => {
    setActiveOversState(overs);
    void refreshState(currentMatch.id, overs);
  };

  useEffect(() => { void refreshState(); return () => { requestRef.current?.abort(); requestRef.current = null; }; }, [refreshState]);

  return (
    <MatchContext.Provider
      value={{
        stateStatus, stateError, lastUpdated, refreshState,
        currentMatch,
        setCurrentMatch,
        currentPlayers,
        currentBattles,
        venuePlayers,
        currentLineups,
        setCurrentLineups,
        currentProviders,
        activeOvers,
        setActiveOvers,
        rainConstraints,
        activeTab,
        setActiveTab,
        isSidebarCollapsed,
        setIsSidebarCollapsed,
        isDrawerOpen,
        setIsDrawerOpen,
        searchQuery,
        setSearchQuery,
        selectedBatter,
        setSelectedBatter,
        selectedBowler,
        setSelectedBowler,
        selectedPhase,
        setSelectedPhase,
        selectedTossChoice,
        setSelectedTossChoice,
        navigateToWorkspace
      }}
    >
      {children}
    </MatchContext.Provider>
  );
};

export const useMatchContext = () => {
  const context = useContext(MatchContext);
  if (!context) {
    throw new Error("useMatchContext must be used within a MatchContextProvider");
  }
  return context;
};

