from pathlib import Path
import re

file2 = Path(r"C:\Users\lenovo\.gemini\antigravity\brain\ed8f2892-024b-46d7-bf3c-efa849cc1232\.system_generated\steps\191\content.md")
content = file2.read_text(encoding="utf-8")

# Let's inspect where player names occur
names = ["Samson", "Iyer", "Abhishek", "Kishan", "Tilak", "Dhir", "Reddy", "Axar", "Arshdeep", "Prince", "Bishnoi", "Kuldeep", "Hope", "Powell", "Hetmyer", "Rutherford", "Chase", "Shepherd", "Andrew", "Forde", "Hosein", "Motie", "Joseph"]

found = {}
for name in names:
    count = len(re.findall(rf"\b{name}\b", content, re.IGNORECASE))
    found[name] = count

print("Occurrences of player names in scraped page:")
for k, v in found.items():
    print(f"  {k}: {v}")

# Look at venue match details in file1
file1 = Path(r"C:\Users\lenovo\.gemini\antigravity\brain\ed8f2892-024b-46d7-bf3c-efa849cc1232\.system_generated\steps\187\content.md")
content1 = file1.read_text(encoding="utf-8")

venue_matches = re.findall(r"Rajiv Gandhi[^<,\"]*", content1)
print("Venue matches:", set(venue_matches))
time_matches = re.findall(r"(\d+:\d+\s+[AP]M)", content1)
print("Time matches:", set(time_matches))
