import urllib.request
import zipfile
import io
import os

url = "https://cricsheet.org/downloads/t20s_female_json.zip"
print(f"Downloading {url}...", flush=True)

dest_dir = "d:/cricket/data/cricsheet/t20s_female"
os.makedirs(dest_dir, exist_ok=True)

req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=90) as resp:
    data = resp.read()
    print(f"Downloaded {len(data)/(1024*1024):.2f} MB", flush=True)
    z = zipfile.ZipFile(io.BytesIO(data))
    names = z.namelist()
    print(f"Total matches in zip: {len(names)}", flush=True)
    
    extracted_count = 0
    for name in names:
        if name.endswith(".json") and name != "README.txt":
            z.extract(name, dest_dir)
            extracted_count += 1

print(f"Extracted {extracted_count} Women's T20 match JSON files to {dest_dir}!", flush=True)

