@echo off
cd /d %~dp0

if not exist .venv\Scripts\python.exe (
  echo [ERROR] Chua co virtual environment. Hay chay setup_windows.bat truoc.
  pause
  exit /b 1
)

.venv\Scripts\python.exe main.py --source all
