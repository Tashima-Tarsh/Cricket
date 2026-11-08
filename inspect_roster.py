import json
from cricdata import CricinfoClient

c = CricinfoClient()
m = next(x for x in c.live_matches() if x.get('objectId') == 1535653)
s_slug = m['series']['slug']
m_slug = f"{m['slug']}-{m['objectId']}"
sc = c.match_scorecard(s_slug, m_slug)
content = sc.get('content', {})
team_players = content.get('matchPlayers', {}).get('teamPlayers', [])

players_list = []
for t in team_players:
    t_name = t.get('team', {}).get('name')
    t_code = t.get('team', {}).get('abbreviation') or ('IND-W' if 'India' in t_name else 'ZIM-W')
    plist = t.get('players', [])
    print(f"=== {t_name} ({len(plist)} players) ===")
    for p in plist:
        p_obj = p.get('player', {})
        p_data = {
            'cricinfo_id': p_obj.get('id'),
            'cricinfo_object_id': p_obj.get('objectId'),
            'name': p_obj.get('name'),
            'long_name': p_obj.get('longName'),
            'slug': p_obj.get('slug'),
            'team': t_code,
            'playing_roles': p_obj.get('playingRoles', []),
            'batting_styles': p_obj.get('battingStyles', []),
            'bowling_styles': p_obj.get('bowlingStyles', []),
            'gender': p_obj.get('gender')
        }
        players_list.append(p_data)
        print(f"  {p_data['cricinfo_id']} | {p_data['name']} ({p_data['team']}) | {p_data['playing_roles']} | Bat: {p_data['batting_styles']} | Bowl: {p_data['bowling_styles']}")

print(f"\nTotal Players: {len(players_list)}")
with open("d:/cricket/data/indw_zimw_raw_roster.json", "w") as f:
    json.dump(players_list, f, indent=2)
print("Saved to d:/cricket/data/indw_zimw_raw_roster.json")

