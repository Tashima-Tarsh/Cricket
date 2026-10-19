from pathlib import Path
import re

content = Path(r"C:\Users\lenovo\.gemini\antigravity\brain\ed8f2892-024b-46d7-bf3c-efa849cc1232\.system_generated\steps\303\content.md").read_text(encoding="utf-8")

# Let's search for "Playing XI" or team members
idx = content.find("Playing XI")
if idx != -1:
    print("Found Playing XI:")
    print(content[idx-50:idx+800])
else:
    print("Playing XI string not found, scanning all bold texts:")
    bolds = re.findall(r"<b>([^<]+)</b>", content)
    for b in bolds:
        if any(w in b.lower() for w in ["ind", "wi", "hope", "shepherd", "joseph", "motie", "paul", "springer", "forde"]):
            print("Bold:", b)
