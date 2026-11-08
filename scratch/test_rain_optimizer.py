import urllib.request
import json

res = urllib.request.urlopen('http://127.0.0.1:8000/api/ortools/optimize?overs=12')
data = json.loads(res.read().decode('utf-8'))

print(f"=== 12-OVER SHORTENED MATCH OPTIMIZER RESULTS ({len(data['lineups'])} Teams) ===")
for i, l in enumerate(data['lineups']):
    c = l.get('captain', {}).get('name')
    vc = l.get('vice_captain', {}).get('name')
    cr = l.get('total_credits')
    csp = l.get('csp')
    mnc = l.get('mnc_summary')
    combo = l.get('cvc_combo_type')
    tname = l.get('team_name')
    print(f"[{i+1}] {tname}")
    print(f"     Captain: {c} | Vice-Captain: {vc}")
    print(f"     Credits: {cr} | CSP: {csp}% | M-N-C: {mnc}")
    print(f"     C/VC: {combo}")

