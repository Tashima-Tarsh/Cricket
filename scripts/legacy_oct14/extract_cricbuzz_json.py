from pathlib import Path
import re
import json

file1 = Path(r"C:\Users\lenovo\.gemini\antigravity\brain\ed8f2892-024b-46d7-bf3c-efa849cc1232\.system_generated\steps\187\content.md")
file2 = Path(r"C:\Users\lenovo\.gemini\antigravity\brain\ed8f2892-024b-46d7-bf3c-efa849cc1232\.system_generated\steps\191\content.md")

for name, fpath in [("match_page", file1), ("squad_page", file2)]:
    content = fpath.read_text(encoding="utf-8")
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    print(f"{name}: found {len(scripts)} scripts")
    for i, s in enumerate(scripts):
        if "__NEXT_DATA__" in s or "props" in s or "pageProps" in s:
            print(f"Script {i} contains props, length {len(s)}")
            try:
                # find first {
                idx = s.find('{')
                if idx != -1:
                    data = json.loads(s[idx:])
                    out_name = f"cricbuzz_{name}.json"
                    with open(out_name, "w", encoding="utf-8") as out:
                        json.dump(data, out, indent=2)
                    print(f"Saved {out_name}")
            except Exception as e:
                print(f"Error parsing json in {name} script {i}: {e}")
