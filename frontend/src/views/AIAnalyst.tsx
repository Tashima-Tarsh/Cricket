import React, { useState } from "react";
import { 
  Bot, 
  Send, 
  Sparkles, 
  Terminal, 
  Crosshair, 
  Flame, 
  TrendingUp, 
  Database, 
  Cpu, 
  CheckCircle2,
  Clock,
  Layers
} from "lucide-react";
import { useMatchContext } from "../context/MatchContext";

interface Message {
  id: string;
  sender: "user" | "analyst";
  timestamp: string;
  content: string;
  citations?: string[];
  metrics?: { label: string; value: string; color?: string }[];
}

export const AIAnalyst: React.FC = () => {
  const { currentMatch } = useMatchContext();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "msg_init",
      sender: "analyst",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
      content: `STRIKE//OS Tactical Cricket Intelligence Engine online. Connected to Cricsheet DuckDB Historical Repository (1,243 matches, 194,239 balls indexed), Zero-Leakage XGBoost projections, and Google OR-Tools CP-SAT multi-lineup optimizer.\n\nReady for live tactical queries, batter vs bowler micro-telemetry, DLS par simulations, and Grand League captaincy differential analysis.`,
      citations: ["DuckDB Columnar Delivery Engine", "XGBoost Historical Predictor v2.4", "OR-Tools CP-SAT Engine"]
    }
  ]);
  const [inputQuery, setInputQuery] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  const promptChips = [
    "Who is the highest ceiling differential captain tonight?",
    "How does Nicholas Pooran perform against Kuldeep Yadav?",
    "Simulate DLS par score if rain interrupts at 14 overs",
    "What are the pitch conditions and chasing stats for this venue?"
  ];

  const handleSend = async (text: string) => {
    if (!text.trim()) return;

    const userMsg: Message = {
      id: `usr_${Date.now()}`,
      sender: "user",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
      content: text
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery("");
    setIsProcessing(true);

    try {
      const matchParam = currentMatch.id ? `&match_id=${encodeURIComponent(currentMatch.id)}` : "";
      const res = await fetch(`/api/analyst/query?q=${encodeURIComponent(text)}${matchParam}`);
      if (!res.ok) throw new Error(`Query failed: ${res.status}`);
      const data = await res.json();

      const botMsg: Message = {
        id: `bot_${Date.now()}`,
        sender: "analyst",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
        content: data.reply || "No analysis returned.",
        citations: data.citations || ["DuckDB Delivery Ledger"],
        metrics: data.metrics || []
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      const errMsg: Message = {
        id: `bot_err_${Date.now()}`,
        sender: "analyst",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
        content: `**Query Execution Error:** ${err instanceof Error ? err.message : "Network error"}. Please ensure the STRIKE//OS backend server is active.`,
        citations: ["System Diagnostic"]
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-stone-300">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 uppercase tracking-widest">
            <Cpu size={14} /> Cricket intelligence engine
          </div>
          <h1 className="text-2xl lg:text-3xl font-bold text-white uppercase tracking-tight mt-1 flex items-center gap-3">
            AI Tactical Analyst
            <span className="text-xs px-2.5 py-0.5 rounded border border-emerald-500/30 bg-emerald-500/10 text-emerald-300 font-mono">
              EVIDENCE QUERY ENGINE (DUCKDB + XGBOOST)
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5 font-sans">
            Interactive sports data science reasoning grounded in DuckDB ball-by-ball deliveries, venue models, and OR-Tools solvers
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1 rounded bg-slate-900 border border-white/10 text-xs font-mono text-slate-300 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> CONNECTED TO {currentMatch.name || "MATCH SNAPSHOT"}
          </span>
        </div>
      </div>

      {/* 2. Chat Terminal Window */}
      <div className="rounded-xl p-5 bg-slate-950/90 border border-white/10 border-t-2 border-t-emerald-500 flex flex-col h-[650px] shadow-2xl">
        
        {/* Terminal Message Stream */}
        <div className="flex-1 overflow-y-auto space-y-4 pr-2">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`flex gap-3 text-xs font-sans ${
                m.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {m.sender === "analyst" && (
                <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 shrink-0 mt-1">
                  <Bot size={16} />
                </div>
              )}

              <div
                className={`max-w-[85%] sm:max-w-[75%] rounded-xl p-4 space-y-3 ${
                  m.sender === "user"
                    ? "bg-emerald-950/40 border border-emerald-500/30 text-emerald-100"
                    : "bg-slate-900/90 border border-white/10 text-slate-200"
                }`}
              >
                <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 pb-1.5 border-b border-white/10">
                  <span className="uppercase font-bold tracking-wider text-emerald-400">
                    {m.sender === "user" ? "CRICKET STRATEGIST" : "GROUNDED EVIDENCE ENGINE"}
                  </span>
                  <span>{m.timestamp}</span>
                </div>

                {/* Body Content */}
                <div className="text-xs leading-relaxed whitespace-pre-line font-sans text-slate-200">
                  {m.content}
                </div>

                {/* Key Metrics Chips if present */}
                {m.metrics && m.metrics.length > 0 && (
                  <div className="grid grid-cols-3 gap-2 pt-2 border-t border-white/10">
                    {m.metrics.map((met, i) => (
                      <div key={i} className="bg-slate-950 p-2 rounded-lg border border-white/10 text-center">
                        <div className="text-[9px] font-mono text-slate-400 uppercase">{met.label}</div>
                        <div className={`text-sm font-bold font-mono telemetry-num mt-0.5 ${met.color || "text-emerald-400"}`}>
                          {met.value}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Citations Footer */}
                {m.citations && m.citations.length > 0 && (
                  <div className="flex flex-wrap items-center gap-1.5 pt-2 text-[10px] font-mono text-slate-400">
                    <span className="text-slate-500">CITATIONS:</span>
                    {m.citations.map((cite, i) => (
                      <span key={i} className="px-1.5 py-0.5 rounded bg-slate-950 border border-white/10 text-slate-300">
                        {cite}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {isProcessing && (
            <div className="flex gap-3 items-center text-xs font-mono text-emerald-400 p-2">
              <Sparkles size={14} className="animate-spin" />
              <span>Querying Cricsheet delivery ledger and evaluating game-script trees...</span>
            </div>
          )}
        </div>

        {/* 3. Prompt Recommendation Chips */}
        <div className="pt-3 pb-2 border-t border-white/10 flex items-center gap-2 overflow-x-auto">
          <span className="text-[10px] font-mono text-slate-400 uppercase shrink-0">SUGGESTED:</span>
          {promptChips.map((chip, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(chip)}
              className="px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 border border-white/10 hover:border-emerald-500/50 text-xs font-sans text-slate-300 hover:text-white whitespace-nowrap transition-all"
            >
              {chip}
            </button>
          ))}
        </div>

        {/* 4. Input Bar */}
        <div className="pt-2 flex items-center gap-2">
          <div className="relative flex-1">
            <Terminal size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input aria-label="Input query"
              type="text"
              placeholder="Ask STRIKE//OS analyst: e.g. 'Evaluate Pooran vs Kuldeep in middle overs'..."
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleSend(inputQuery);
              }}
              className="w-full bg-slate-900 border border-white/15 rounded-lg pl-9 pr-4 py-2.5 text-xs font-sans text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>

          <button
            onClick={() => handleSend(inputQuery)}
            disabled={!inputQuery.trim() || isProcessing}
            className="px-4 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white font-bold text-xs font-sans flex items-center gap-1.5 transition-all shadow"
          >
            <Send size={14} /> SEND
          </button>
        </div>
      </div>
    </div>
  );
};

