@echo off
cd /d %~dp0

where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Khong tim thay Python trong PATH.
  echo Cai Python 3.11+ va chon Add Python to PATH.
  pause
  exit /b 1
)

if not exist .venv (
  python -m venv .venv
)

.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\pip.exe install -r requirements.txt
.venv\Scripts\python.exe -m playwright install chromium

if not exist .env (
  copy .env.example .env >nul
  echo.
  echo Da tao file .env. Hay mo file .env va dien tai khoan HSC/Vietcap.
)

echo.
echo Setup hoan tat.
pause
