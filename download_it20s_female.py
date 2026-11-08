import urllib.request
import zipfile
import io
import os
import json

url = "https://cricsheet.org/downloads/it20s_female_json.zip"
print(f"Downloading {url}...", flush=True)

dest_dir = "d:/cricket/data/cricsheet/it20s_female"
os.makedirs(dest_dir, exist_ok=True)

req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=60) as resp:
    data = resp.read()
    print(f"Downloaded {len(data)/(1024*1024):.2f} MB", flush=True)
    z = zipfile.ZipFile(io.BytesIO(data))
    names = z.namelist()
    print(f"Total matches in zip: {len(names)}", flush=True)
    
    extracted_target = 0
    for name in names:
        if name.endswith(".json") and name != "README.txt":
            # Extract all JSONs
            z.extract(name, dest_dir)
            extracted_target += 1

print(f"Extracted {extracted_target} Women's IT20 match JSON files to {dest_dir}!", flush=True)

