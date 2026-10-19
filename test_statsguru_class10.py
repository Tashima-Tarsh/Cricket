import urllib.request
import re


# Smriti Mandhana: 597806, class=10 (Women's T20I)
url = "https://stats.espncricinfo.com/stats/engine/player/597806.html?class=10;template=results;type=batting"
headers = {"User-Agent": "Mozilla/5.0"}
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
        print("Page fetched! Length:", len(html))
        # Look for career summary
        matches = re.findall(r'<tr class="data1"[^>]*>(.*?)</tr>', html, re.DOTALL)
        print("Data rows found:", len(matches))
        for m in matches[:5]:
            cols = [re.sub(r'<.*?>', '', c).strip() for c in re.findall(r'<td[^>]*>(.*?)</td>', m, re.DOTALL)]
            print("  Cols:", cols[:10])
except Exception as e:
    print("Error:", e)

