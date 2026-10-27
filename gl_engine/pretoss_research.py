"""User-supplied snapshot research and post-toss XI verification, no synthetic athletes."""
import json
import os
import tempfile
from collections import Counter
from pathlib import Path
from fastapi import HTTPException

SNAPSHOT_ID = "nz_ind_2026_10_27_3rd_t20i_pretoss"
SNAPSHOT_PATH = Path(__file__).resolve().parents[1] / "data" / "snapshots" / "nz_ind_2026_10_27_pretoss.json"
MANUAL_XI_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "nz_ind_2026_10_27_manual_xi.json"


def load_snapshot():
    return json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))


def lineup_evidence(names, captain, vice_captain, players, available=None):
    pool = {p["name"]: p for p in players}
    names = list(names)
    if len(names) != 11 or len(set(names)) != 11:
        raise HTTPException(422, "Require eleven distinct real players")
    if any(n not in pool for n in names):
        raise HTTPException(422, "Unknown player: " + ", ".join(n for n in names if n not in pool))
    if available is not None and not set(names).issubset(available):
        raise HTTPException(422, "Lineup contains player not in the manually announced XI")
    if captain == vice_captain or captain not in names or vice_captain not in names:
        raise HTTPException(422, "C and VC must differ and belong to selected eleven")
    roles = Counter(pool[n]["role"] for n in names)
    if not (1 <= roles["WK"] <= 4 and 3 <= roles["BAT"] <= 6
            and 1 <= roles["AR"] <= 4 and 3 <= roles["BOWL"] <= 6):
        raise HTTPException(422, "Fantasy roster role limits violated")
    split = Counter(pool[n]["team"] for n in names)
    if set(split) != {"NZ", "IND"} or max(split.values()) > 7:
        raise HTTPException(422, "Both teams required; no more than seven from one side")
    credits = round(sum(pool[n]["credits"] for n in names), 1)
    if credits > 100.0 or credits <= 0:
        raise HTTPException(422, "Invalid credit total")
    return {"names": names, "captain": captain, "vice_captain": vice_captain,
            "credits": credits, "credits_unspent": round(100.0 - credits, 1),
            "team_split": dict(split), "roles": dict(roles),
            "ownership_sum_snapshot": round(sum(pool[n]["selected_pct"] for n in names), 2),
            "captain_selection_pct_snapshot": pool[captain]["captain_pct"],
            "vice_captain_selection_pct_snapshot": pool[vice_captain]["captain_pct"],
            "rank_1_probability": None, "predicted_points": None,
            "status": "PROVISIONAL_SCENARIO_NOT_CALIBRATED"}


def get_pretoss_research():
    doc = load_snapshot()
    doc["provisional_teams"] = [
        {"contest": seed["id"], "scenario": seed["scenario"],
         **lineup_evidence(seed["names"], seed["c"], seed["vc"], doc["players"])}
        for seed in doc["provisional_templates"]
    ]
    return doc


def validate_manual_xi(nz_names, ind_names):
    doc = load_snapshot()
    pool = {(p["team"], p["name"]): p for p in doc["players"]}
    if len(nz_names) != 11 or len(ind_names) != 11:
        raise HTTPException(422, "Exactly eleven named players per team are required")
    if len(set(nz_names)) != 11 or len(set(ind_names)) != 11:
        raise HTTPException(422, "Duplicate XI names")
    keys = [("NZ", n.strip()) for n in nz_names] + [("IND", n.strip()) for n in ind_names]
    missing = [f"{team}:{name}" for team, name in keys if (team,name) not in pool]
    if missing:
        raise HTTPException(422, "After-toss XI names not present in screenshot pool; update snapshot/credits: " + ", ".join(missing[:6]))
    from .roster_safety import validate_confirmed_xi
    roster = [{"id": team + "_" + name.casefold().replace(" ","_"), "name": name,
               "team": team, "role": pool[(team,name)]["role"], "credits": pool[(team,name)]["credits"],
               "is_confirmed_xi": True} for team,name in keys]
    validate_confirmed_xi(roster)
    return roster


def save_manual_xi(nz_names, ind_names, source_note, toss_winner, toss_decision):
    from datetime import datetime, timezone
    roster = validate_manual_xi(nz_names, ind_names)
    if toss_winner not in {"NZ", "IND"} or toss_decision not in {"bat", "bowl"}:
        raise HTTPException(422, "Actual toss winner and choice must be provided")
    record = {"fixture_id": SNAPSHOT_ID,
              "provenance":{"source":"USER_ENTERED_POST_TOSS",
                            "verification_status":"UNVERIFIED",
                            "notes":"Authenticated user attestation only; no provider confirmation"},
              "attested_at_utc": datetime.now(timezone.utc).isoformat(),
              "source_note": source_note, "toss": {"winner":toss_winner,"decision":toss_decision},
              "players": roster, "confirmed_count": 22}
    MANUAL_XI_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Atomic overwrite prevents half-saved XI artifacts
    fd, tmp = tempfile.mkstemp(dir=MANUAL_XI_PATH.parent, prefix=".xi_", suffix=".json")
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as stream:
            json.dump(record, stream, indent=2)
        os.replace(tmp, MANUAL_XI_PATH)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    available = {p["name"] for p in roster}
    research = get_pretoss_research()
    accepted = [
        team for team in research["provisional_teams"]
        if set(team["names"]).issubset(available)
    ]
    return {"status":"MANUAL_USER_ATTESTED_NOT_PROVIDER_VERIFIED",
            "confirmed_count":22,"fixture_id":SNAPSHOT_ID,
            "eligible_provisional_teams":accepted,
            "need_rebuild":len(accepted)<3,
            "message":"Provisional templates containing absent XI players are discarded, not repaired by substitution."}


POST_TOSS_PATH = Path(__file__).resolve().parents[1] / "data" / "snapshots" / "nz_ind_2026_10_27_post_toss.json"


def get_post_toss_research():
    """Validate user-attested playing XI and recompute all contest portfolios.

    This is an explicitly recorded manual announcement, not independent
    provider confirmation. No player absent from either XI may enter a team.
    """
    from .roster_safety import validate_confirmed_xi
    doc = load_snapshot()
    record = json.loads(POST_TOSS_PATH.read_text(encoding="utf-8"))
    if record.get("fixture_id") != SNAPSHOT_ID:
        raise HTTPException(409, "Post-toss and pre-toss fixture IDs differ")
    teams = record["players"]
    nz = teams.get("NZ", [])
    ind = teams.get("IND", [])
    if len(nz) != 11 or len(ind) != 11:
        raise HTTPException(409, "Exactly eleven names required per team")
    for team, players in teams.items():
        if team not in {"NZ", "IND"}:
            raise HTTPException(409, "Unexpected opponent fixture")
        if any(not isinstance(pair, list) or len(pair) != 2 or not all(pair) for pair in players):
            raise HTTPException(409, "Full-name/credit-identity aliases required")
    ids = {team: [pair[0] for pair in players] for team, players in teams.items()}
    # Reject duplicates, wrong team membership and screenshot identity mismatches.
    confirmed = validate_manual_xi(ids["NZ"], ids["IND"])
    validate_confirmed_xi(confirmed)
    all_real_names = [pair[1].casefold().strip() for pairs in teams.values() for pair in pairs]
    if len(set(all_real_names)) != 22:
        raise HTTPException(409, "Playing XI has duplicate real names")
    available = set(ids["NZ"] + ids["IND"])
    generated = []
    for seed in record["contest_scenarios"]:
        portfolio = lineup_evidence(
            seed["names"], seed["captain"], seed["vice_captain"],
            doc["players"], available=available,
        )
        generated.append({
            "contest": seed["contest"],
            "scenario": seed["scenario"],
            "predictions_status": "SCENARIO_ONLY_NOT_HISTORICALLY_CALIBRATED",
            **portfolio,
        })
    if len({p["contest"] for p in generated}) != 3:
        raise HTTPException(409, "Missing or duplicated entry-tier strategy")
    return {
        "fixture_id": SNAPSHOT_ID,
        "provenance": record["provenance"],
        "status": "USER_ATTESTED_XI_NOT_INDEPENDENTLY_VERIFIED",
        "toss": record["toss"],
        "full_player_names": teams,
        "player_pool": confirmed,
        "contest_sizes": doc["contests"],
        "teams": generated,
        "rank_1_probability": None,
        "source_snapshot_time_ist": "2026-10-27T11:44:00+05:30",
        "caveat": "Verify exact contest lock time and screenshot credits in app",
    }
