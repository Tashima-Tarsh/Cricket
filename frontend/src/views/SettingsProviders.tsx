import { providerTelemetry } from "../data/providerTelemetry";
import { useGraphics } from "../hooks/useGraphics";
import React, { useState } from "react";
import { DataProviderTelemetry } from "../types";
import { 
  Server, 
  CheckCircle2, 
  AlertTriangle, 
  Activity, 
  Sliders, 
  Cpu, 
  Key, 
  Terminal, 
  Database, 
  RefreshCw,
  Layers,
  Settings
} from "lucide-react";

interface SettingsProvidersProps {
  providers: DataProviderTelemetry[];
}

export const SettingsProviders: React.FC<SettingsProvidersProps> = ({ providers }) => {
  const { preferences, update } = useGraphics();
  const graphicsQuality = preferences.quality, enableShadows = preferences.shadows, enableVolumetricLight = preferences.lights;
  const targetFPS = `${preferences.fps} FPS`;
  const setGraphicsQuality = (quality: typeof preferences.quality) => saveGraphics({quality});
  const setEnableShadows = (shadows: boolean) => saveGraphics({shadows});
  const setEnableVolumetricLight = (lights: boolean) => saveGraphics({lights});
  const setTargetFPS = (fps: string) => saveGraphics({fps: parseInt(fps)});
  const [graphicsNotice, setGraphicsNotice] = useState("");
  const saveGraphics = (patch: Partial<typeof preferences>) => setGraphicsNotice(update(patch) ? "Display preferences saved on this device." : "Applied for this session. Browser storage is unavailable.");
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [providerRows, setProviderRows] = useState(providers);
  const [refreshMessage, setRefreshMessage] = useState("");

  const mcpTools = [
    {
      name: "cricket_h2h_matchup",
      description: "Queries micro head-to-head records (balls, runs, dismissals, dot ball %, strike rate, length breakdown) between any batter and bowler.",
      input_schema: "{ batter: string, bowler: string, format?: 'T20' | 'ODI' | 'Test' }",
      status: "DESCRIBED"
    },
    {
      name: "cricket_dls_calculator",
      description: "Calculates revised target runs and Duckworth-Lewis-Stern par score given interrupted overs and wickets lost.",
      input_schema: "{ target_base: number, rain_overs: number, rain_wickets: number }",
      status: "DESCRIBED"
    },
    {
      name: "cricket_venue_intel",
      description: "Retrieves boundary dimensions, soil degradation index, pace/spin wicket ratio, and dew impact metrics for any venue.",
      input_schema: "{ venue_id: string }",
      status: "DESCRIBED"
    },
    {
      name: "cricket_fantasy_optimize",
      description: "Executes Google OR-Tools CP-SAT multi-lineup solver enforcing Dream11 constraints and overlap bounds.",
      input_schema: "{ num_lineups: number, max_overlap: number, team_weights: object }",
      status: "DESCRIBED"
    }
  ];

  const handleRefreshProviders = async () => {
    setIsRefreshing(true); setRefreshMessage("");
    try {
      const response = await fetch("/api/providers/status", {signal: AbortSignal.timeout(15000)});
      if (!response.ok) throw new Error(`Refresh failed (${response.status}).`);
      const data = await response.json();
      setProviderRows(Object.entries(data).map(([id, raw]) => providerTelemetry(id,raw)));
      setRefreshMessage(`Configuration read at ${new Date().toLocaleString()}. Key presence does not establish a live connection; latency is not measured.`);
    } catch (error) { setRefreshMessage(error instanceof Error ? error.message : "Provider refresh failed."); }
    finally { setIsRefreshing(false); }
  };

  return (
    <div className="space-y-6">
      <p role="status">{refreshMessage || "Provider configuration only. Live availability has not been checked."}</p>
      <p role="status">{graphicsNotice}</p>
      {/* 1. Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 uppercase tracking-widest">
            <Server size={14} /> Telemetry & Infrastructure Management
          </div>
          <h1 className="text-2xl lg:text-3xl font-bold text-white uppercase tracking-tight mt-1 flex items-center gap-3">
            System Providers & Telemetry
            <span className="text-xs px-2.5 py-0.5 rounded border border-emerald-500/30 bg-emerald-500/10 text-emerald-300 font-mono">
              PROVIDER CONFIGURATION
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5 font-sans">
            Provider health status, MCP Tool Registry endpoints, and WebGL 3D graphics rendering configurations
          </p>
        </div>

        <button
          onClick={handleRefreshProviders}
          className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 border border-white/10 text-slate-200 hover:text-white text-xs font-mono font-bold flex items-center gap-2 transition-all shadow"
        >
          <RefreshCw size={14} className={isRefreshing ? "animate-spin text-emerald-400" : ""} />
          REFRESH CONFIGURATION
        </button>
      </div>

      {/* 2. Provider Health & Telemetry Grid (5 Providers) */}
      <div className="space-y-3">
        <div className="text-xs font-mono text-slate-400 uppercase tracking-wider flex items-center gap-2">
          <Activity size={14} className="text-emerald-400" /> Active Data Ingestion Pipelines
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {providerRows.map((p) => {
            return (
              <div
                key={p.id}
                className="rounded-xl p-4 flex flex-col justify-between bg-slate-900/80 border border-white/10 hover:border-emerald-500/40 transition-all shadow-md"
              >
                <div>
                  <div className="flex items-center justify-between pb-2 border-b border-white/10">
                    <span className="font-bold text-white text-sm">{p.name}</span>
                    {p.status === "ONLINE" || p.status === "ONLINE / AUTHENTICATED_LIVE" ? (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded font-bold flex items-center gap-1 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                        <CheckCircle2 size={10} /> AUTHENTICATED LIVE
                      </span>
                    ) : p.status === "LOCAL_ARCHIVE_READY" ? (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded font-bold flex items-center gap-1 bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                        <Database size={10} /> LOCAL ARCHIVE
                      </span>
                    ) : (p.status === "CONFIGURED_UNVERIFIED") ? (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded font-bold flex items-center gap-1 bg-emerald-900/30 text-emerald-400 border border-emerald-500/40">
                        <CheckCircle2 size={10} /> CONFIGURED
                      </span>
                    ) : (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded font-bold flex items-center gap-1 bg-amber-500/20 text-amber-300 border border-amber-500/30">
                        <AlertTriangle size={10} /> STANDBY / FALLBACK
                      </span>
                    )}
                  </div>

                  <div className="space-y-2 mt-3 text-xs font-sans">
                    <div>
                      <div className="text-[10px] text-slate-500 uppercase font-mono">BEST USE & DOMAIN</div>
                      <div className="text-slate-300 mt-0.5">{p.best_use}</div>
                    </div>

                    <div>
                      <div className="text-[10px] text-slate-500 uppercase font-mono">ENDPOINT / PROTOCOL</div>
                      <div className="text-xs text-cyan-400 truncate mt-0.5 font-mono">{p.endpoint}</div>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 pt-3 mt-3 border-t border-white/10 text-xs font-sans">
                  <div>
                    <div className="text-[9px] text-slate-500 uppercase font-mono">LATENCY</div>
                    <div className="text-slate-300 font-bold font-mono">
                      {p.latency_ms > 0 ? `${p.latency_ms.toFixed(1)} ms` : "Direct Memory / Local"}
                    </div>
                  </div>
                  <div>
                    <div className="text-[9px] text-slate-500 uppercase font-mono">INDEXED RECORDS</div>
                    <div className="text-emerald-400 font-bold font-mono">
                      {p.records_indexed > 0 ? `${p.records_indexed.toLocaleString()} rows` : "Standby (0 live)"}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 3. MCP (Model Context Protocol) Tool Registry */}
      <div className="rounded-xl p-5 bg-slate-900/80 border border-white/10">
        <div className="flex items-center justify-between pb-3 border-b border-white/10">
          <div>
            <div className="text-xs font-mono text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
              <Cpu size={14} /> MODEL CONTEXT PROTOCOL (MCP)
            </div>
            <h3 className="text-base font-bold text-white uppercase mt-0.5">Available tool descriptions</h3>
          </div>
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-white/10">
            LOCAL REGISTRY
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          {mcpTools.map((tool) => (
            <div key={tool.name} className="p-3.5 rounded-xl bg-slate-950/70 border border-white/10 space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-mono font-bold text-emerald-400 text-xs">
                  `{tool.name}`
                </span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                  {tool.status}
                </span>
              </div>
              <p className="text-xs font-sans text-slate-300 leading-relaxed">
                {tool.description}
              </p>
              <div className="text-[11px] font-mono text-slate-400 bg-slate-900 p-2 rounded-lg truncate border border-white/5">
                Schema: <span className="text-slate-200">{tool.input_schema}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 4. Three.js / WebGL Graphics Rendering Preferences */}
      <div className="rounded-xl p-5 bg-slate-900/80 border border-white/10">
        <div className="flex items-center justify-between pb-3 border-b border-white/10">
          <div>
            <div className="text-xs font-mono text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Sliders size={14} /> DISPLAY PREFERENCES
            </div>
            <h3 className="text-base font-bold text-white uppercase mt-0.5">3D WebGL Graphics Engine Settings</h3>
          </div>
          <span className="text-xs font-sans text-slate-400">
            3D is optional; 2D is the default
          </span>
        </div>

        <div className="mt-4 flex items-center gap-3">
          <label className="text-xs font-sans text-slate-300">Pitch display mode:</label>
          <select 
            aria-label="Pitch display mode" 
            value={preferences.mode} 
            onChange={event => saveGraphics({mode: event.target.value as "2D" | "3D"})}
            className="p-1.5 rounded-lg bg-slate-950 border border-white/15 text-xs font-sans text-white focus:outline-none focus:border-emerald-500"
          >
            <option value="2D">2D - low power</option>
            <option value="3D">3D - WebGL</option>
          </select>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
          {/* Quality Preset */}
          <div className="p-3 rounded-xl bg-slate-950/70 border border-white/10 space-y-2">
            <div className="text-[10px] font-mono text-slate-400 uppercase">GRAPHICS QUALITY</div>
            <div className="grid grid-cols-3 gap-1">
              {(["ULTRA", "HIGH", "BALANCED"] as const).map((lvl) => (
                <button
                  key={lvl}
                  onClick={() => setGraphicsQuality(lvl)}
                  className={`py-1 rounded text-xs font-sans font-bold transition-all ${
                    graphicsQuality === lvl
                      ? "bg-emerald-600 text-white shadow"
                      : "bg-slate-900 text-slate-400 hover:text-white"
                  }`}
                >
                  {lvl}
                </button>
              ))}
            </div>
          </div>

          {/* Shadows Toggle */}
          <div className="p-3 rounded-xl bg-slate-950/70 border border-white/10 flex items-center justify-between">
            <div>
              <div className="text-xs font-sans text-white font-bold">Dynamic Pitch Shadows</div>
              <div className="text-[11px] font-sans text-slate-400">Soft PCF shadow maps</div>
            </div>
            <button
              aria-label="Dynamic pitch shadows" aria-pressed={enableShadows}
              onClick={() => setEnableShadows(!enableShadows)}
              className={`w-11 h-6 rounded-full transition-all relative p-0.5 ${
                enableShadows ? "bg-emerald-600" : "bg-slate-800 border border-white/10"
              }`}
            >
              <div className={`w-5 h-5 rounded-full bg-white transition-all shadow ${
                enableShadows ? "translate-x-5" : "translate-x-0"
              }`}></div>
            </button>
          </div>

          {/* Volumetric Lights */}
          <div className="p-3 rounded-xl bg-slate-950/70 border border-white/10 flex items-center justify-between">
            <div>
              <div className="text-xs font-sans text-white font-bold">Stadium Floodlights</div>
              <div className="text-[11px] font-sans text-slate-400">Directional stadium lighting</div>
            </div>
            <button
              aria-label="Stadium lighting" aria-pressed={enableVolumetricLight}
              onClick={() => setEnableVolumetricLight(!enableVolumetricLight)}
              className={`w-11 h-6 rounded-full transition-all relative p-0.5 ${
                enableVolumetricLight ? "bg-emerald-600" : "bg-slate-800 border border-white/10"
              }`}
            >
              <div className={`w-5 h-5 rounded-full bg-white transition-all shadow ${
                enableVolumetricLight ? "translate-x-5" : "translate-x-0"
              }`}></div>
            </button>
          </div>

          {/* Target FPS */}
          <div className="p-3 rounded-xl bg-slate-950/70 border border-white/10 space-y-2">
            <div className="text-[10px] font-mono text-slate-400 uppercase">FRAME RATE CAP</div>
            <div className="grid grid-cols-3 gap-1">
              {["30 FPS", "60 FPS", "120 FPS"].map((fps) => (
                <button
                  key={fps}
                  onClick={() => setTargetFPS(fps)}
                  className={`py-1 rounded text-xs font-sans font-bold transition-all ${
                    targetFPS === fps
                      ? "bg-emerald-600 text-white shadow"
                      : "bg-slate-900 text-slate-400 hover:text-white"
                  }`}
                >
                  {fps}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

