from cricdata import CricinfoClient

c = CricinfoClient()
# Test with fmt="t20i"
for pid in [597806, 70132]:
    try:
        res = c.player_career_stats(pid, fmt="t20i", stat_type="batting")
        print(f"ID {pid} t20i batting summary:", res.get("summary"))
        print(f"ID {pid} breakdowns count:", len(res.get("breakdowns", [])))
        if res.get("breakdowns"):
            print("First breakdown:", res.get("breakdowns")[0])
    except Exception as e:
        print(f"ID {pid} error: {e}")

