@echo off
title ICICI Bank AI Agent Gatekeeper - Streamlit
echo ========================================================
echo   ICICI Bank - AI Agent Gatekeeper Security Console
echo   Enrollment ID: PGD202563326
echo ========================================================
echo.

set PYTHON_EXE=python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    set PYTHON_EXE="C:\Users\urvashi\AppData\Local\Programs\Python\Python312\python.exe"
)

echo Starting Streamlit on http://localhost:8501 ...
%PYTHON_EXE% -m streamlit run app.py --server.port 8501
pause
