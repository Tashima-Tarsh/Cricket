from pathlib import Path
import re

content = Path(r"C:\Users\lenovo\.gemini\antigravity\brain\ed8f2892-024b-46d7-bf3c-efa849cc1232\.system_generated\steps\237\content.md").read_text(encoding="utf-8")

# Find news articles
clean = re.sub(r"<[^>]+>", "\n", content)
lines = [l.strip() for l in clean.split("\n") if l.strip()]

print("Total lines:", len(lines))
for i, l in enumerate(lines):
    if any(k in l.lower() for k in ["preview", "pitch", "weather", "hyderabad", "rajiv gandhi", "toss", "spin", "pace", "squad", "playing xi"]):
        print(f"Line {i}: {l}")
