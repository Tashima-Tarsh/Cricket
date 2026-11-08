import urllib.request
import json

def test():
    # 1. Live matches
    print("Testing /api/live/matches...")
    resp = urllib.request.urlopen("http://127.0.0.1:8000/api/live/matches")
    data = json.loads(resp.read().decode())
    print(f"Total live matches: {data['count']}")
    print(f"Sample match 1: {data['matches'][0]['title']} | Cat: {data['matches'][0].get('category')} | Date: {data['matches'][0].get('match_date')}")

    # 2. Load Pakistan vs Sri Lanka (1550713)
    print("\nTesting /api/state?match_id=cricdata_1550713...")
    resp_pak = urllib.request.urlopen("http://127.0.0.1:8000/api/state?match_id=cricdata_1550713&force_refresh=true")
    data_pak = json.loads(resp_pak.read().decode())
    print("Match loaded:", data_pak["match"]["name"])
    print("Format:", data_pak["match"]["format"])
    print("Toss:", data_pak["match"]["toss"]["statement"])
    print("Players count:", len(data_pak["players"]))
    print("Sample players:", [p["name"] for p in data_pak["players"][:6]])
    print("Generated Lineups count:", len(data_pak["lineups"]))
    if data_pak["lineups"]:
        l1 = data_pak["lineups"][0]
        print(f"Lineup 1: Captain={l1['captain']['name']}, VC={l1['vice_captain']['name']}, Credits={l1['total_credits']}")

    # 3. Load IND Women vs ZIM Women (1535653)
    print("\nTesting /api/state?match_id=cricdata_1535653...")
    resp_indw = urllib.request.urlopen("http://127.0.0.1:8000/api/state?match_id=cricdata_1535653&force_refresh=true")
    data_indw = json.loads(resp_indw.read().decode())
    print("Match loaded:", data_indw["match"]["name"])
    print("Players count:", len(data_indw["players"]))
    print("Generated Lineups count:", len(data_indw["lineups"]))

test()

