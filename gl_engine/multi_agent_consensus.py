"""
multi_agent_consensus.py
Multi-Agent Pre-Match Consensus Debate (The 3-Agent Syndicate).

Orchestrates 3 specialized quantitative agents:
1. BullAgent: High-ceiling tournament aggressor (seeking 200+ blowout stacks, captain leverage).
2. BearAgent: Risk and variance stress-tester (hedging against early swing, low scores, collapse traps).
3. QuantSolver: Mathematical consensus arbiter running the CP-SAT solver to output the final portfolio.
"""

from typing import Dict, Any, List

class BullAgent:
    """Argues for aggressive, high-ceiling GPP breakout scenarios."""
    def analyze(self, match_meta: Dict[str, Any], archetype: str) -> Dict[str, Any]:
        if archetype == "ROAD_HIGHWAY":
            thesis = "Pristine flat surface. Total ceiling will come from top-order batters and death finishers. Stack overs 1-6 and overs 16-20."
            recommended_c = "Top-Order Batter (Openers / No. 3)"
            risk_tolerance = "HIGH_CEILING"
        elif archetype == "ASYMMETRIC_MISMATCH":
            thesis = "Powerhouse team dominates. Middle order gets extended hitting volume while underdog struggles to chase 10+ RRR. Leverage middle-order captaincy."
            recommended_c = "Powerhouse Middle Order (No. 4/5)"
            risk_tolerance = "LEVERAGE_MAX"
        else:
            thesis = "Exploit low-owned multi-stat all-rounders who bowl 4 overs and bat in top 5."
            recommended_c = "Dual-Threat All-Rounder"
            risk_tolerance = "BALANCED"

        return {
            "agent": "BULL_AGGRESSOR",
            "thesis": thesis,
            "recommended_captain_profile": recommended_c,
            "target_ceiling_score": 850.0,
            "preferred_credit_spent": 84.5
        }

class BearAgent:
    """Stress-tests downside, early swing collapse, and pitch trickiness."""
    def analyze(self, match_meta: Dict[str, Any], archetype: str) -> Dict[str, Any]:
        if archetype == "ASYMMETRIC_MISMATCH":
            warning = "Beware dead-rubber rotations. Star captains frequently rest themselves from batting. Opposition 2-way all-rounders carry highest floor."
            recommended_vc = "Opposition Death-Bowler All-Rounder"
            fade_target = "Powerhouse Captain if Dead-Rubber"
        elif archetype == "SPIN_CHOKE_MINEFIELD":
            warning = "Boundary hitters will get stumped or caught in ring. Avoid high-credit openers with low spin strike rates."
            recommended_vc = "Mystery Spinner or Defensive Anchor"
            fade_target = "Stroke-Making Openers"
        else:
            warning = "Ensure team does not duplicate chalk combinations. Leave at least 14 credits unspent."
            recommended_vc = "Death Bowler"
            fade_target = "Over-Owned Specialist Bowlers"

        return {
            "agent": "BEAR_STRESS_TESTER",
            "risk_warning": warning,
            "recommended_vc_profile": recommended_vc,
            "fade_recommendation": fade_target,
            "minimum_unspent_credits": 14.0
        }

class QuantSolverArbiter:
    """Synthesizes Bull and Bear theses and formulates mathematical solver weights."""
    def arbitrate(self, bull_view: Dict[str, Any], bear_view: Dict[str, Any], match_meta: Dict[str, Any]) -> Dict[str, Any]:
        consensus_script = {
            "synthesis_summary": f"Bull Thesis: {bull_view['thesis']} | Bear Guard: {bear_view['risk_warning']}",
            "enforced_credit_range": [81.0, 86.0],
            "enforced_unspent_range": [14.0, 19.0],
            "cvc_independence_rule": "P(C) * P(VC) <= 0.05",
            "recommended_c": bull_view["recommended_captain_profile"],
            "recommended_vc": bear_view["recommended_vc_profile"],
            "fade_filter": bear_view["fade_recommendation"]
        }
        return consensus_script

class MultiAgentDebateEngine:
    def __init__(self):
        self.bull = BullAgent()
        self.bear = BearAgent()
        self.quant = QuantSolverArbiter()

    def run_pre_match_debate(self, match_meta: Dict[str, Any], archetype: str) -> Dict[str, Any]:
        """Runs the 3-agent adversarial loop and returns final consensus parameters."""
        bull_output = self.bull.analyze(match_meta, archetype)
        bear_output = self.bear.analyze(match_meta, archetype)
        consensus = self.quant.arbitrate(bull_output, bear_output, match_meta)

        return {
            "match_id": match_meta.get("id"),
            "archetype": archetype,
            "bull_agent": bull_output,
            "bear_agent": bear_output,
            "consensus_directives": consensus
        }

_MULTI_AGENT_INSTANCE = None

def get_multi_agent_engine() -> MultiAgentDebateEngine:
    global _MULTI_AGENT_INSTANCE
    if _MULTI_AGENT_INSTANCE is None:
        _MULTI_AGENT_INSTANCE = MultiAgentDebateEngine()
    return _MULTI_AGENT_INSTANCE

