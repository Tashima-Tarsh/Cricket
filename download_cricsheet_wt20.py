import urllib.request
import zipfile
import io
import os
import json

url = "https://cricsheet.org/downloads/wnt_json.zip"
print(f"Checking Cricsheet WT20I feed at {url}...", flush=True)

try:
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        content = resp.read()
        print(f"Downloaded {len(content) / (1024*1024):.2f} MB", flush=True)
        z = zipfile.ZipFile(io.BytesIO(content))
        names = z.namelist()
        print(f"Total WT20I match files in archive: {len(names)}", flush=True)
        
        # Save to d:/cricket/data/cricsheet/wt20i
        dest_dir = "d:/cricket/data/cricsheet/wt20i"
        os.makedirs(dest_dir, exist_ok=True)
        
        # Extract matches involving India Women or Zimbabwe Women
        target_matches = 0
        for name in names:
            if name.endswith(".json") and name != "README.txt":
                data = json.loads(z.read(name).decode("utf-8"))
                teams = data.get("info", {}).get("teams", [])
                if any("India" in t or "Zimbabwe" in t for t in teams):
                    with open(os.path.join(dest_dir, name), "w", encoding="utf-8") as f:
                        json.dump(data, f)
                    target_matches += 1
        print(f"Successfully extracted {target_matches} IND-W & ZIM-W ball-by-ball matches into {dest_dir}", flush=True)
except Exception as e:
    print("Error:", e, flush=True)

