import React from "react";
import {
  LayoutDashboard,
  Layers,
  Swords,
  Users,
  Archive,
  Trophy,
  Bot,
  Settings,
  Activity,
  Maximize2,
  Radio,
  Sparkles,
  ChevronDown
} from "lucide-react";
import { MatchInfo } from "../types";

export type NavTab = 
  | "command"
  | "pitch"
  | "battle"
  | "players"
  | "archive"
  | "fantasy"
  | "ai"
  | "settings";

export const NAV_ITEMS = [
  { id: "command" as NavTab, label: "Command Center", icon: LayoutDashboard, badge: "DECIDER" },
  { id: "fantasy" as NavTab, label: "Fantasy Lab", icon: Trophy, badge: "CP-SAT" },
  { id: "pitch" as NavTab, label: "Pitch Lab 3D", icon: Layers, badge: "3D" },
  { id: "battle" as NavTab, label: "Battle Arena", icon: Swords, badge: "H2H" },
  { id: "players" as NavTab, label: "Player Intel", icon: Users },
  { id: "ai" as NavTab, label: "AI Analyst", icon: Bot, badge: "MCP" },
  { id: "archive" as NavTab, label: "2026 Archive", icon: Archive },
  { id: "settings" as NavTab, label: "Live Providers", icon: Settings, badge: "5 APIS" }
];

interface HeaderProps {
  match: MatchInfo;
  currentTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
  onOpenMatchSetup: () => void;
}

export const Header: React.FC<HeaderProps> = ({ 
  match, 
  currentTab, 
  onSelectTab, 
  onOpenMatchSetup 
}) => {
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(() => {});
    } else {
      document.exitFullscreen().catch(() => {});
    }
  };

  return (
    <header className="h-16 border-b border-white/10 bg-[#060913]/95 backdrop-blur-2xl px-4 lg:px-8 flex items-center justify-between z-30 shrink-0 sticky top-0 shadow-2xl">
      {/* 1. Left: Brand Icon & Title */}
      <div className="flex items-center gap-3.5 shrink-0">
        <div className="flex items-center justify-center w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-400 via-emerald-400 to-[#C8FF35] text-slate-950 font-black font-mono text-sm shadow-[0_0_20px_rgba(0,240,255,0.4)]">
          //S
        </div>
        <div className="cursor-pointer" onClick={() => onSelectTab("command")}>
          <div className="flex items-center gap-2">
            <span className="font-heading font-black tracking-wider text-base text-white">
              STRIKE<span className="text-cyan-400">//</span>OS
            </span>
            <span className="px-2 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-[9px] font-mono text-cyan-300 font-bold">
              v2.6 PRO
            </span>
          </div>
          <div className="text-[10px] font-mono tracking-widest text-slate-400 uppercase hidden sm:block">
            CRICKET INTELLIGENCE.
          </div>
        </div>
      </div>

      {/* 2. Center: Prominent Broadcast Navigation Bar */}
      <nav className="hidden md:flex items-center gap-1.5 p-1 rounded-2xl bg-white/[0.03] border border-white/10 backdrop-blur-xl">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-mono font-medium transition-all ${
                isActive
                  ? "bg-gradient-to-r from-cyan-500/20 via-cyan-500/10 to-transparent border border-cyan-500/40 text-cyan-300 font-bold shadow-[0_0_15px_rgba(0,240,255,0.2)]"
                  : "text-slate-400 hover:text-white hover:bg-white/[0.04]"
              }`}
            >
              <Icon size={14} className={isActive ? "text-cyan-400" : "text-slate-400"} />
              <span>{item.label}</span>
              {item.badge && (
                <span className={`text-[9px] px-1.5 py-0.2 rounded-full font-bold ${
                  isActive
                    ? "bg-cyan-400 text-slate-950"
                    : "bg-white/[0.06] text-slate-500"
                }`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* 3. Right: Live Match Switcher & Tools */}
      <div className="flex items-center gap-3 shrink-0">
        {/* Match Pill Capsule */}
        <div 
          onClick={onOpenMatchSetup}
          className="flex items-center gap-2.5 bg-white/[0.03] hover:bg-white/[0.07] px-3.5 py-1.5 rounded-xl border border-white/10 hover:border-cyan-400/50 cursor-pointer transition-all shadow-inner group"
          title="Click to Switch Match or Edit Ground Report"
        >
          <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-pulse shadow-[0_0_8px_rgba(244,63,94,0.6)]" />
          <div className="flex flex-col text-left">
            <span className="text-xs font-bold text-white group-hover:text-cyan-300 transition-colors">
              IND vs WI (5th T20I)
            </span>
            <span className="text-[10px] font-mono text-emerald-400">
              Bengaluru • Today 7 PM
            </span>
          </div>
          <ChevronDown size={14} className="text-slate-400 group-hover:text-white transition-colors" />
        </div>

        {/* Sync Feeds Button */}
        <button
          onClick={onOpenMatchSetup}
          className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-cyan-950/60 to-slate-900 border border-cyan-500/40 hover:border-cyan-400 text-white hover:text-cyan-300 text-xs font-mono font-bold transition-all shadow-[0_0_15px_rgba(0,240,255,0.15)]"
        >
          <Radio size={14} className="text-cyan-400 animate-pulse" />
          <span>SYNC FEEDS</span>
        </button>

        {/* Fullscreen Toggle */}
        <button
          onClick={toggleFullscreen}
          title="Toggle Fullscreen Mode"
          className="p-2 rounded-xl bg-white/[0.04] border border-white/10 text-slate-400 hover:text-white hover:border-cyan-400/40 transition-all"
        >
          <Maximize2 size={16} />
        </button>
      </div>
    </header>
  );
};

interface MobileNavProps {
  currentTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
}

export const MobileNav: React.FC<MobileNavProps> = ({ currentTab, onSelectTab }) => {
  return (
    <div className="md:hidden fixed bottom-0 left-0 right-0 h-16 bg-[#060913]/95 border-t border-white/10 px-2 flex items-center justify-around z-30 backdrop-blur-2xl">
      {NAV_ITEMS.slice(0, 5).map((item) => {
        const Icon = item.icon;
        const isActive = currentTab === item.id;
        return (
          <button
            key={item.id}
            onClick={() => onSelectTab(item.id)}
            className={`flex flex-col items-center gap-1 p-2 rounded-lg text-[10px] font-mono transition-all ${
              isActive ? "text-cyan-400 font-bold" : "text-slate-400 hover:text-white"
            }`}
          >
            <Icon size={16} />
            <span>{item.label.split(" ")[0]}</span>
          </button>
        );
      })}
    </div>
  );
};
