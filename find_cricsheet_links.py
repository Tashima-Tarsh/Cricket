import urllib.request
import re

url = "https://cricsheet.org/downloads/"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode("utf-8")
        links = re.findall(r'href=["\']([^"\']+\.zip)["\']', html)
        print("Total zip links:", len(links))
        for l in links:
            if "t20" in l.lower() or "women" in l.lower() or "all" in l.lower() or "wbb" in l.lower():
                print("  ", l)
except Exception as e:
    print("Error:", e)

