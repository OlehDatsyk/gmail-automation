@echo off
setlocal enabledelayedexpansion
title Gmail Automation Platform - Launcher
cd /d "%~dp0"

echo ============================================================
echo   Gmail Automation Platform - Startup
echo ============================================================
echo.

REM ---------------------------------------------------------------
REM 1. Check Python is installed
REM ---------------------------------------------------------------
echo [1/7] Checking for Python...
where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo   ERROR: Python was not found on your system.
    echo   Please install Python 3.12 or newer from https://www.python.org/downloads/
    echo   IMPORTANT: During installation, check the box "Add Python to PATH".
    echo.
    goto :error_exit
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo   Found Python %PYVER%
echo.

REM ---------------------------------------------------------------
REM 2. Check / create virtual environment
REM ---------------------------------------------------------------
echo [2/7] Checking for virtual environment...
if not exist ".venv\Scripts\python.exe" (
    echo   No virtual environment found. Creating one now ^(this may take a minute^)...
    python -m venv .venv
    if errorlevel 1 (
        echo   ERROR: Failed to create the virtual environment.
        goto :error_exit
    )
    echo   Virtual environment created at .venv\
) else (
    echo   Virtual environment already exists.
)
echo.

REM ---------------------------------------------------------------
REM 3. Activate virtual environment
REM ---------------------------------------------------------------
echo [3/7] Activating virtual environment...
call ".venv\Scripts\activate.bat"
if errorlevel 1 (
    echo   ERROR: Failed to activate the virtual environment.
    goto :error_exit
)
echo   Activated.
echo.

REM ---------------------------------------------------------------
REM 4. Install dependencies if missing
REM ---------------------------------------------------------------
echo [4/7] Checking dependencies...
python -c "import fastapi, uvicorn, openai, googleapiclient" >nul 2>nul
if errorlevel 1 (
    echo   Installing dependencies from requirements.txt ^(this may take a few minutes^)...
    python -m pip install --upgrade pip >nul
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo   ERROR: Dependency installation failed. Check your internet connection.
        goto :error_exit
    )
    echo   Dependencies installed successfully.
) else (
    echo   Dependencies already installed.
)
echo.

REM ---------------------------------------------------------------
REM 5. Verify .env file
REM ---------------------------------------------------------------
echo [5/7] Checking configuration file...
if not exist ".env" (
    echo   No .env file found. Creating one from .env.example...
    copy ".env.example" ".env" >nul
    echo.
    echo   ############################################################
    echo   #  IMPORTANT: A new .env file was created for you.         #
    echo   #  Open it in VS Code and add your OpenAI and Google       #
    echo   #  credentials before using AI or Gmail features.          #
    echo   #  See INSTRUCTION.md for step-by-step help.                #
    echo   ############################################################
    echo.
) else (
    echo   .env file found.
)
echo.

REM ---------------------------------------------------------------
REM 6. Warn if credentials look like placeholders
REM ---------------------------------------------------------------
echo [6/7] Checking API credentials...
set MISSING_CREDS=0
findstr /C:"OPENAI_API_KEY=sk-your-openai-api-key-here" ".env" >nul 2>nul
if not errorlevel 1 set MISSING_CREDS=1
findstr /C:"OPENAI_API_KEY=" ".env" >nul 2>nul
if errorlevel 1 set MISSING_CREDS=1
findstr /C:"GOOGLE_CLIENT_ID=your-client-id" ".env" >nul 2>nul
if not errorlevel 1 set MISSING_CREDS=1

if "!MISSING_CREDS!"=="1" (
    echo.
    echo   ------------------------------------------------------------
    echo   NOTICE: It looks like your OpenAI and/or Google credentials
    echo   have not been filled in yet in the .env file.
    echo   The app will still start, but AI and Gmail features will
    echo   return errors until you add real credentials.
    echo   See INSTRUCTION.md sections 10-14 for help obtaining them.
    echo   ------------------------------------------------------------
    echo.
) else (
    echo   Credentials appear to be configured.
)
echo.

REM ---------------------------------------------------------------
REM 7. Start the application
REM ---------------------------------------------------------------
echo [7/7] Starting Gmail Automation Platform...
echo.
echo   Once started, open your browser to:
echo     http://localhost:8000/docs        (interactive API docs)
echo     http://localhost:8000/auth/google/login   (connect Gmail)
echo.
echo   Press CTRL+C in this window to stop the server.
echo ============================================================
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
if errorlevel 1 (
    echo.
    echo   ERROR: The application exited with an error. See messages above.
    goto :error_exit
)

echo.
echo Application stopped normally.
pause
exit /b 0

:error_exit
echo.
echo ============================================================
echo   Startup failed. Review the messages above for details.
echo   See INSTRUCTION.md for troubleshooting steps.
echo ============================================================
pause
exit /b 1
