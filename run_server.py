import uvicorn
import os
import sys

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(__file__))
    uvicorn.run("gl_engine.web_app:app", host="127.0.0.1", port=8000, reload=False, log_level="info")

