import { useSyncExternalStore } from "react";
export interface GraphicsPreferences { quality: "ULTRA" | "HIGH" | "BALANCED"; shadows: boolean; lights: boolean; fps: number; mode: "2D" | "3D" }
const defaults: GraphicsPreferences = { quality: "BALANCED", shadows: false, lights: true, fps: 30, mode: "2D" };
let current = defaults;
try {
  const saved = JSON.parse(localStorage.getItem("cricket.graphics.v1") || "null");
  if (saved) current = { quality: ["ULTRA", "HIGH", "BALANCED"].includes(saved.quality) ? saved.quality : defaults.quality, shadows: saved.shadows === true, lights: saved.lights !== false, fps: [30,60,120].includes(saved.fps) ? saved.fps : 30, mode: saved.mode === "3D" ? "3D" : "2D" };
} catch { /* Storage can be unavailable in private browsing. */ }
const listeners = new Set<() => void>();
const subscribe = (listener: () => void) => { listeners.add(listener); return () => { listeners.delete(listener); }; };
export function useGraphics() {
  const preferences = useSyncExternalStore(subscribe, () => current);
  const update = (patch: Partial<GraphicsPreferences>) => {
    current = { ...current, ...patch };
    let persisted = true;
    try { localStorage.setItem("cricket.graphics.v1", JSON.stringify(current)); } catch { persisted = false; }
    listeners.forEach(listener => listener());
    return persisted;
  };
  return { preferences, update };
}
