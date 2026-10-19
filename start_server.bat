@echo off
title STRIKE//OS Fantasy Cricket Engine (Port 8000)
cd /d "d:\cricket"
echo ==============================================================
echo  STRIKE//OS Cricket Intelligence Engine - Port 8000
echo ==============================================================
echo.
echo Starting FastAPI & React Portal on http://localhost:8000 ...
d:\cricket\.venv\Scripts\python.exe -m uvicorn gl_engine.web_app:app --host 0.0.0.0 --port 8000
pause

