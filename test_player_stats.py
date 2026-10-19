from cricdata import CricinfoClient
import json

c = CricinfoClient()
# Let's test player_career_stats for Smriti Mandhana
p_stats = c.player_career_stats(597806)
print("Smriti stats type:", type(p_stats))
if isinstance(p_stats, dict):
    print("Keys:", list(p_stats.keys()))
    for k in list(p_stats.keys())[:5]:
        print(k, ":", str(p_stats[k])[:120])

# Let's test player_career_stats for Kelis Ndhlovu (1250707)
zim_stats = c.player_career_stats(1250707)
print("Kelis Ndhlovu stats type:", type(zim_stats))
if isinstance(zim_stats, dict):
    print("Keys:", list(zim_stats.keys()))

