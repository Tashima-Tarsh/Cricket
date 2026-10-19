import sys, time
sys.path.insert(0, r"d:\cricket")

modules = [
    "gl_engine.models",
    "gl_engine.cricsheet",
    "gl_engine.cricketdata_api",
    "gl_engine.predict11",
    "gl_engine.xgboost_model",
    "gl_engine.ortools_optimizer",
    "gl_engine.rain_model",
    "gl_engine.csv_exporter",
    "gl_engine.live_feed",
    "gl_engine.match_catalog",
]

for m in modules:
    t0 = time.time()
    print(f"Importing {m}...", flush=True)
    __import__(m)
    print(f"  Done in {time.time()-t0:.2f}s", flush=True)

print("All modules imported cleanly!", flush=True)

