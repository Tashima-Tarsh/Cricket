// ==UserScript==
// @name         WBBL Dream11 Read-Only Collector (Free / Local)
// @namespace    https://github.com/Tashima-Tarsh/Cricket
// @version      0.1.0
// @description  Export visible Dream11 player information to local n8n, without modifying a team.
// @match        https://www.dream11.com/*
// @match        https://dream11.com/*
// @grant        GM_xmlhttpRequest
// @connect      127.0.0.1
// ==/UserScript==

/* Read-only collector: no scraping of private endpoints, no credentials, no clicks.
   UI selectors are provisional and MUST be tested against the real Dream11 page.
   Only visible, fully parsed rows are sent. Missing values are never guessed.
*/
(function () {
  "use strict";
  const WEBHOOK = "http://127.0.0.1:5678/webhook/wbbl-dream11-browser";
  const intervalMs = 15000;
  let previousSignature = "";
  let currentMatch = "";
  let pendingPlayers = new Map();

  function text(node) {
    return (node?.textContent || "").replace(/\s+/g, " ").trim();
  }

  function matchId() {
    const url = new URL(location.href);
    return url.searchParams.get("matchId")
      || url.pathname.match(/\/match\/([a-zA-Z0-9_-]+)/i)?.[1]
      || url.pathname.match(/\/matches\/([a-zA-Z0-9_-]+)/i)?.[1]
      || null;
  }

  function activeRole() {
    const active = [...document.querySelectorAll('[role="tab"][aria-selected="true"], [class*="tab"][class*="active"], [class*="Tab"][class*="active"]')]
      .map(text).join(" ").toUpperCase();
    if (/\b(WK|WICKET.?KEEPER)\b/.test(active)) return "WK";
    if (/\b(BAT|BATTER)\b/.test(active)) return "BAT";
    if (/\b(AR|ALL.?ROUNDER)\b/.test(active)) return "AR";
    if (/\b(BOWL|BOWLER)\b/.test(active)) return "BOWL";
    return null;
  }

  function roleFrom(row) {
    const raw = (row.getAttribute("data-player-role") || text(row.querySelector('[data-testid*="role"], [class*="playerRole"], [class*="PlayerRole"]'))).toUpperCase();
    if (/^(WK|WICKET.?KEEPER)$/.test(raw)) return "WK";
    if (/^(BAT|BATTER|BATSMAN)$/.test(raw)) return "BAT";
    if (/^(AR|ALL.?ROUNDER)$/.test(raw)) return "AR";
    if (/^(BOWL|BOWLER)$/.test(raw)) return "BOWL";
    return activeRole();
  }

  function parseRow(row) {
    if (!row.getClientRects().length || getComputedStyle(row).visibility === "hidden") return null;
    const name = row.getAttribute("data-player-name")
      || text(row.querySelector('[data-testid*="name"], [class*="playerName"], [class*="PlayerName"], [class*="player-name"]'));
    const team = row.getAttribute("data-player-team")
      || text(row.querySelector('[data-testid*="team"], [class*="teamName"], [class*="TeamName"], [class*="team-name"]'));
    const role = roleFrom(row);
    const content = text(row);
    const explicitCredit = row.getAttribute("data-player-credit")
      || text(row.querySelector('[data-testid*="credit"], [class*="credit"], [class*="Credit"]'));
    const creditMatch = explicitCredit
      ? explicitCredit.match(/^\s*(\d{1,2}(?:\.\d+)?)\s*(?:cr(?:edits?)?)?\s*$/i)
      : content.match(/\b(\d{1,2}(?:\.\d+)?)\s*(?:cr(?:edits?)?)\b/i);
    if (!name || !team || !role || !creditMatch) return null;

    const credits = Number(creditMatch[1]);
    if (!(credits > 0 && credits <= 20)) return null;
    const ownNode = row.querySelector('[data-testid*="selected"], [class*="selectedBy"], [class*="SelectedBy"], [class*="pickPercentage"]');
    const ownText = row.getAttribute("data-selected-by") || text(ownNode);
    const selectionText = ownText || content;
    const selectedMatch = ownText
      ? selectionText.match(/(\d{1,3}(?:\.\d+)?)\s*%/)
      : selectionText.match(/(?:selected\s*by|selected|picked\s*by)\s*:?\s*(\d{1,3}(?:\.\d+)?)\s*%/i)
        || selectionText.match(/(\d{1,3}(?:\.\d+)?)\s*%\s*(?:selected|picked)/i);
    const selected = selectedMatch ? Number(selectedMatch[1]) : null;
    if (selected !== null && (selected < 0 || selected > 100)) return null;
    // Local stable ID: not a Dream11-issued player identifier.
    const playerId = row.getAttribute("data-player-id")
      || "browser:" + [team, name].map(v => v.toLowerCase().replace(/[^a-z0-9]+/g, "-")).join(":");
    return { player_id: playerId, name: name.trim(), team: team.trim(), role, credits,
             selected_by_pct: selected };
  }

  function scan() {
    const id = matchId();
    if (!id) return; // Avoid mixing players from unrelated matches.
    if (currentMatch !== id) {
      pendingPlayers = new Map();
      previousSignature = "";
      currentMatch = id;
    }
    const selectors = '[data-testid*="player-card"], [data-testid*="player-row"], [data-player-id], [class*="playerCard"], [class*="PlayerCard"], [class*="playerRow"], [class*="PlayerRow"]';
    const visible = [...new Set(document.querySelectorAll(selectors))];
    for (const row of visible) {
      const player = parseRow(row);
      if (player) pendingPlayers.set(player.team + ":" + player.player_id, player);
    }
    if (!pendingPlayers.size) return;
    const players = [...pendingPlayers.values()].sort((a, b) => (a.team + a.name).localeCompare(b.team + b.name));
    const signature = JSON.stringify(players);
    if (signature === previousSignature) return;
    previousSignature = signature;
    const page = new URL(location.href);
    const payload = {
      match_id: id,
      page_url: page.origin + page.pathname,
      observed_at_utc: new Date().toISOString(),
      players,
    };
    GM_xmlhttpRequest({
      method: "POST",
      url: WEBHOOK,
      headers: { "Content-Type": "application/json" },
      data: JSON.stringify(payload),
      timeout: 10000,
      onload(response) {
        if (response.status >= 400) {
          previousSignature = "";
          console.warn("[WBBL collector] Local n8n webhook rejected snapshot:", response.status);
        } else {
          console.info("[WBBL collector] Sent", players.length, "visible players to local n8n.");
        }
      },
      onerror() {
        previousSignature = "";
        console.warn("[WBBL collector] n8n is unavailable. Check localhost:5678 and workflow activation.");
      },
      ontimeout() { previousSignature = ""; },
    });
  }

  setInterval(scan, intervalMs);
  document.addEventListener("visibilitychange", () => { if (!document.hidden) scan(); });
  scan();
})();
