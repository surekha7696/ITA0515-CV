@echo off
setlocal
cd /d "%~dp0"
if exist "D:\installation_kit\python.exe" (
  set "PYTHON=D:\installation_kit\python.exe"
) else (
  set "PYTHON=python"
)
echo Starting RetinaAI. The first launch downloads the AI model (~33.4 MB). Keep internet connected.
"%PYTHON%" app.py
pause
