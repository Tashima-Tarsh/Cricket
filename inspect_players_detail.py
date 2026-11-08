from cricdata import CricinfoClient
import json

c = CricinfoClient()
m = next(x for x in c.live_matches() if x.get('objectId') == 1535653)
s_slug = m['series']['slug']
m_slug = f"{m['slug']}-{m['objectId']}"
sc = c.match_scorecard(s_slug, m_slug)
mp = sc.get('content', {}).get('matchPlayers', {})

all_players = []
for t in mp.get('teamPlayers', []):
    t_name = t.get('team', {}).get('name')
    for p in t.get('players', []):
        pl = p.get('player', {})
        all_players.append({
            'name': pl.get('name'),
            'long_name': pl.get('longName'),
            'team': t_name,
            'id': pl.get('id'),
            'objectId': pl.get('objectId')
        })

print(f"Total extracted: {len(all_players)}")
for i, p in enumerate(all_players):
    print(f"{i+1}. {p['name']} ({p['long_name']}) - {p['team']} [ID: {p['id']}, ObjID: {p['objectId']}]")

