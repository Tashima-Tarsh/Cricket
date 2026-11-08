import os, time
print("1. Setting env...", flush=True)
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

print("2. Importing numpy...", flush=True)
import numpy as np

print("3. Importing pandas...", flush=True)
import pandas as pd

print("4. Importing xgboost...", flush=True)
import xgboost as xgb

print(f"5. XGBoost version: {xgb.__version__}", flush=True)

