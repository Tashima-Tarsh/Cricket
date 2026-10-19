import type {DataProviderTelemetry} from "../types";
/** Provider configuration is not a successful authenticated request. */
export function providerTelemetry(id: string, raw: any): DataProviderTelemetry {
  const local = id === "cricsheet";
  return {id,name:raw.info?.name || raw.name || id,status:local ? "LOCAL_ARCHIVE_READY" : raw.mode === "LIVE" ? "CONFIGURED_UNVERIFIED" : "STANDBY",latency_ms:0,records_indexed:local ? raw.records_indexed || raw.matches_cached || 0 : 0,last_sync:new Date().toISOString(),best_use:raw.info?.best_use || raw.best_use || "",endpoint:raw.info?.documentation || raw.endpoint || ""};
}
