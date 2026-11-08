from cricdata import CricinfoClient
c = CricinfoClient()
# Let's try match_info for 1535652
for mid in [1535652, 1535651, 1535654]:
    try:
        sc = c.match_scorecard("zimbabwe-women-in-india-2026-27", f"match-{mid}")
        print("Found:", mid)
    except Exception:
        pass

