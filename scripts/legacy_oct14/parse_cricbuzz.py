from pathlib import Path
import re

content_path = Path(r"C:\Users\lenovo\.gemini\antigravity\brain\ed8f2892-024b-46d7-bf3c-efa849cc1232\.system_generated\steps\191\content.md")
html = content_path.read_text(encoding="utf-8")

# Extract venue
venue = re.search(r"Venue:\s*<a[^>]*>(.*?)</a>", html)
if venue:
    print("VENUE:", venue.group(1))

# Extract series
series = re.search(r"Series:\s*<a[^>]*>(.*?)</a>", html)
if series:
    print("SERIES:", series.group(1))

# Find all player links
player_links = re.findall(r'href="/profiles/(\d+)/([^"]+)"[^>]*>([^<]+)</a>', html)
print(f"Total player links found: {len(player_links)}")

seen = set()
players = []
for pid, slug, name in player_links:
    if name not in seen and len(name.strip()) > 2 and not name.startswith("View"):
        seen.add(name)
        players.append((pid, slug, name.strip()))

for p in players:
    print(f"Player ID: {p[0]} | Slug: {p[1]} | Name: {p[2]}")
