import os
import sys
import uvicorn

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(__file__))
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run("gl_engine.web_app:app", host="127.0.0.1", port=port, reload=False, log_level="info")
