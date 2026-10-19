from pathlib import Path
import re

content = Path(r"C:\Users\lenovo\.gemini\antigravity\brain\ed8f2892-024b-46d7-bf3c-efa849cc1232\.system_generated\steps\243\content.md").read_text(encoding="utf-8")

clean = re.sub(r"<[^>]+>", "\n", content)
lines = [l.strip() for l in clean.split("\n") if l.strip()]

print("Lines count:", len(lines))
for i, l in enumerate(lines):
    if len(l) > 30 and not l.startswith("self.") and not l.startswith("{") and not "cricbuzz" in l.lower():
        print(f"--- {l}\n")
