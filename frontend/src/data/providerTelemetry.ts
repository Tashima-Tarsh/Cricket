import type {DataProviderTelemetry} from "../types";
/** Unknown measurements remain null; key presence is not authentication. */
export function providerTelemetry(id: string, raw: any): DataProviderTelemetry {
  return {
    id, name: raw.info?.name || raw.name || id,
    status: raw.status === "LOCAL_ARCHIVE_READY" ? "LOCAL_ARCHIVE_READY" : raw.configured ? "CONFIGURED_UNVERIFIED" : "STANDBY",
    latency_ms: typeof raw.latency_ms === "number" ? raw.latency_ms : null,
    records_indexed: typeof raw.records_indexed === "number" ? raw.records_indexed : null,
    last_sync: raw.last_sync || "Unknown",
    best_use: raw.info?.best_use || raw.best_use || "",
    endpoint: raw.info?.documentation || raw.endpoint || ""
  };
}
