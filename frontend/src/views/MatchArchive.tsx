import React, { useEffect, useState } from "react";
import type { MatchInfo } from "../types";
import { useMatchContext } from "../context/MatchContext";

type Fixture = {id: string; name: string; format: string; status: string; venue_name?: string; data_provenance?: string};

/** Backend catalog entries are scenarios unless an evidence source says otherwise. */
export const MatchArchive: React.FC<{currentMatch: MatchInfo}> = ({currentMatch}) => {
  const {refreshState} = useMatchContext();
  const [fixtures, setFixtures] = useState<Fixture[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [switching, setSwitching] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  useEffect(() => {
    const controller = new AbortController();
    fetch("/api/catalog", {signal: controller.signal}).then(async response => {
      if (!response.ok) throw new Error(`Catalog unavailable (${response.status}).`);
      const data = await response.json();
      if (!Array.isArray(data.matches)) throw new Error("Invalid fixture catalog.");
      setFixtures(data.matches);
    }).catch(err => {if (!controller.signal.aborted) setError(String(err.message));})
      .finally(() => {if (!controller.signal.aborted) setLoading(false);});
    return () => controller.abort();
  }, []);
  const select = async (id: string) => {
    setSwitching(id); setError("");
    try { await refreshState(id); }
    catch (err) {setError(err instanceof Error ? err.message : "Match could not be loaded.");}
    finally {setSwitching(null);}
  };
  return <section className="space-y-6 max-w-5xl mx-auto">
    <header><h1 className="text-2xl font-bold">Fixture archive</h1>
      <p className="mt-2">Browse fixtures supplied by the backend catalog. Bundled fixtures and user entries require verification; they do not establish a current schedule or confirmed result.</p>
    </header>
    <p className="evidence-note">[VERIFY REQUIRED] No verified scorecards, match dates or calibrated win probabilities are attached to this catalog.</p>
    <label className="block">Find a fixture<input aria-label="Find a fixture" value={query} onChange={e => setQuery(e.target.value)} className="block w-full mt-2 p-3 border rounded" /></label>
    {loading && <p role="status">Loading fixture catalog...</p>}
    {error && <p role="alert">{error}</p>}
    {!loading && fixtures.length === 0 && <p>No fixtures are available.</p>}
    <div className="grid gap-4 md:grid-cols-2">{fixtures.filter(f => f.name.toLowerCase().includes(query.toLowerCase())).map(f =>
      <article key={f.id} className="border rounded p-4 space-y-3 min-w-0">
        <p className="text-sm">{f.format} | {f.data_provenance || "[VERIFY REQUIRED]"}</p>
        <h2 className="text-lg font-bold">{f.name}</h2>
        <p>{f.venue_name || "Venue unavailable"}</p><p>{f.status}</p>
        <button disabled={switching !== null} aria-pressed={currentMatch.id === f.id} onClick={() => select(f.id)} className="border rounded px-4 py-2">
          {switching === f.id ? "Loading..." : currentMatch.id === f.id ? "Selected fixture" : "Read fixture analysis"}
        </button>
      </article>)}</div>
  </section>;
};
