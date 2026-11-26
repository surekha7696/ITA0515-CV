@echo off
setlocal
cd /d "%~dp0"
if exist "D:\installation_kit\python.exe" (
  set "PYTHON=D:\installation_kit\python.exe"
) else (
  set "PYTHON=python"
)
echo Installing website and AI model dependencies...
"%PYTHON%" -m pip install --upgrade pip
if errorlevel 1 goto failed
"%PYTHON%" -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo.
echo Setup complete. Run start_windows.bat to launch RetinaAI.
pause
exit /b 0
:failed
echo.
echo Installation failed. Check that Python 3.10-3.12 is installed and try again.
pause
exit /b 1
