@echo off
echo ╔══════════════════════════════════════════════╗
echo ║         CollegePath AI — Setup (Windows)     ║
echo ╚══════════════════════════════════════════════╝

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.10+ is required
    pause
    exit /b 1
)

REM Create venv
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

REM Install deps
echo Installing dependencies...
pip install -r requirements.txt -q

REM Setup .env
if not exist ".env" (
    copy .env.example .env
    echo.
    echo  IMPORTANT: Edit .env and add your GROQ_API_KEY
    echo  Get a free key at: https://console.groq.com
    echo.
    notepad .env
)

REM Create data dirs
if not exist "data\uploads" mkdir data\uploads
if not exist "data\processed" mkdir data\processed
if not exist "data\vectorstore\chroma" mkdir data\vectorstore\chroma

echo.
echo  Starting CollegePath AI...
echo  URL:   http://localhost:8000
echo  Docs:  http://localhost:8000/docs
echo  Admin: http://localhost:8000/admin
echo.
echo  TIP: Go to Admin panel and click Seed Sample Data on first run!
echo.

python main.py
pause
