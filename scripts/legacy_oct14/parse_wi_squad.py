from pathlib import Path
import re
import json

content = Path(r"C:\Users\lenovo\.gemini\antigravity\brain\ed8f2892-024b-46d7-bf3c-efa849cc1232\.system_generated\steps\229\content.md").read_text(encoding="utf-8")

# Extract names from self.__next_f pushes
matches = re.findall(r'"name":"([^"]+)"', content)
roles = re.findall(r'"role":"([^"]+)"', content)
print("Matches found for name:", len(matches))
for m in matches:
    if not m.startswith("West Indies") and not m.startswith("India") and len(m) > 2:
        print("Player:", m)
