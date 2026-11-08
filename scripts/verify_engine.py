import sys
from pathlib import Path

repo_dir = Path("C:/Users/lenovo/.gemini/antigravity/scratch/Cricket")
sys.path.insert(0, str(repo_dir))

from gl_engine.universal_engine import get_universal_engine

def test_engine():
    engine = get_universal_engine()
    state = engine.get_unified_state("ind_w_vs_zim_w_2026_03", force_refresh=True)
    print("Match Name:", state["match"]["name"])
    print("Status:", state["match"]["status"])
    print("Total Lineups:", len(state["lineups"]))
    for i, l in enumerate(state["lineups"]):
        print(f"Team {i+1}: {l['name']}")
        print(f"  Credits: {l['credits_used']} used, {l['credits_left']} unspent")
        print(f"  C: {l['captain']['name']} | VC: {l['vice_captain']['name']}")
        print(f"  Players: {[p['name'] for p in l['players']]}")

if __name__ == "__main__":
    test_engine()

