from cricdata import CricinfoClient
c = CricinfoClient()
# Let's search series matches
m = next(x for x in c.live_matches() if x.get('objectId') == 1535653)
s_slug = m['series']['slug']
print("Series slug:", s_slug)
try:
    s_matches = c.series_matches(s_slug)
    print("Series matches count:", len(s_matches))
    for sm in s_matches:
        print(f"Match: {sm.get('title')} | slug: {sm.get('slug')} | objectId: {sm.get('objectId')}")
except Exception as e:
    print("Error:", e)

