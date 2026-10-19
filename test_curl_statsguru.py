from curl_cffi import requests
import re

url = "https://stats.espncricinfo.com/stats/engine/player/597806.html?class=10;template=results;type=batting"
s = requests.Session(impersonate="chrome")
try:
    r = s.get(url, timeout=10)
    print("Status code:", r.status_code)
    print("Page length:", len(r.text))
    # Look for career summary
    matches = re.findall(r'<tr class="data1"[^>]*>(.*?)</tr>', r.text, re.DOTALL)
    print("Data rows found:", len(matches))
    for m in matches[:5]:
        cols = [re.sub(r'<.*?>', '', c).strip() for c in re.findall(r'<td[^>]*>(.*?)</td>', m, re.DOTALL)]
        print("  Cols:", cols[:10])
except Exception as e:
    print("Error:", e)

