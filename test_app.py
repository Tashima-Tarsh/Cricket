import sys
sys.path.insert(0, r"d:\cricket")
print("Starting import...")
try:
    from gl_engine.web_app import app
    print("Web app imported successfully!")
except Exception as e:
    import traceback
    traceback.print_exc()

