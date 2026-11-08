@echo off
title STRIKE//OS Fantasy Cricket Engine (Port 8001)
echo ==============================================================
echo  STRIKE//OS Cricket Intelligence Engine - Port 8001
echo ==============================================================
echo.
echo Starting FastAPI & React Portal on http://localhost:8001 ...
python -m uvicorn gl_engine.web_app:app --host 0.0.0.0 --port 8001
pause
