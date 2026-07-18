#!/usr/bin/env bash
# Gmail Automation Platform - macOS Launcher
# Double-click this file in Finder to set up and start the app.
# (First time only: right-click > Open, to bypass Gatekeeper's "unidentified developer" warning.)

set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
RESET='\033[0m'

info()  { echo -e "${GREEN}==>${RESET} $1"; }
warn()  { echo -e "${YELLOW}WARNING:${RESET} $1"; }
error() { echo -e "${RED}ERROR:${RESET} $1"; }

fail() {
    error "$1"
    echo
    echo "See INSTRUCTION.md for troubleshooting steps."
    echo "Press Enter to close this window..."
    read -r
    exit 1
}

echo "============================================================"
echo "  Gmail Automation Platform - Startup"
echo "============================================================"
echo

# ---------------------------------------------------------------
# 1. Check Python is installed
# ---------------------------------------------------------------
info "[1/7] Checking for Python..."
PYTHON_BIN=""
for candidate in python3.12 python3.13 python3.11 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
        PYTHON_BIN="$candidate"
        break
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    fail "Python 3.12+ was not found. Install it from https://www.python.org/downloads/ or run: brew install python@3.12"
fi

PYVER=$("$PYTHON_BIN" --version 2>&1)
info "Found $PYVER (using '$PYTHON_BIN')"
echo

# ---------------------------------------------------------------
# 2. Check / create virtual environment
# ---------------------------------------------------------------
info "[2/7] Checking for virtual environment..."
if [ ! -f ".venv/bin/python" ]; then
    info "No virtual environment found. Creating one now (this may take a minute)..."
    "$PYTHON_BIN" -m venv .venv || fail "Failed to create the virtual environment."
    info "Virtual environment created at .venv/"
else
    info "Virtual environment already exists."
fi
echo

# ---------------------------------------------------------------
# 3. Activate virtual environment
# ---------------------------------------------------------------
info "[3/7] Activating virtual environment..."
# shellcheck disable=SC1091
source ".venv/bin/activate" || fail "Failed to activate the virtual environment."
info "Activated."
echo

# ---------------------------------------------------------------
# 4. Install dependencies if missing
# ---------------------------------------------------------------
info "[4/7] Checking dependencies..."
if ! python -c "import fastapi, uvicorn, openai, googleapiclient" >/dev/null 2>&1; then
    info "Installing dependencies from requirements.txt (this may take a few minutes)..."
    python -m pip install --upgrade pip >/dev/null
    python -m pip install -r requirements.txt || fail "Dependency installation failed. Check your internet connection."
    info "Dependencies installed successfully."
else
    info "Dependencies already installed."
fi
echo

# ---------------------------------------------------------------
# 5. Verify .env file
# ---------------------------------------------------------------
info "[5/7] Checking configuration file..."
if [ ! -f ".env" ]; then
    info "No .env file found. Creating one from .env.example..."
    cp ".env.example" ".env"
    echo
    warn "############################################################"
    warn "  A new .env file was created for you."
    warn "  Open it in VS Code and add your OpenAI and Google"
    warn "  credentials before using AI or Gmail features."
    warn "  See INSTRUCTION.md for step-by-step help."
    warn "############################################################"
    echo
else
    info ".env file found."
fi
echo

# ---------------------------------------------------------------
# 6. Warn if credentials look like placeholders
# ---------------------------------------------------------------
info "[6/7] Checking API credentials..."
MISSING_CREDS=0
grep -q "OPENAI_API_KEY=sk-your-openai-api-key-here" ".env" 2>/dev/null && MISSING_CREDS=1
grep -q "GOOGLE_CLIENT_ID=your-client-id" ".env" 2>/dev/null && MISSING_CREDS=1

if [ "$MISSING_CREDS" = "1" ]; then
    echo
    warn "------------------------------------------------------------"
    warn "It looks like your OpenAI and/or Google credentials have not"
    warn "been filled in yet in the .env file."
    warn "The app will still start, but AI and Gmail features will"
    warn "return errors until you add real credentials."
    warn "See INSTRUCTION.md sections 10-14 for help obtaining them."
    warn "------------------------------------------------------------"
    echo
else
    info "Credentials appear to be configured."
fi
echo

# ---------------------------------------------------------------
# 7. Start the application
# ---------------------------------------------------------------
info "[7/7] Starting Gmail Automation Platform..."
echo
echo "  Once started, open your browser to:"
echo "    http://localhost:8000/docs                (interactive API docs)"
echo "    http://localhost:8000/auth/google/login    (connect Gmail)"
echo
echo "  Press CTRL+C in this window to stop the server."
echo "============================================================"
echo

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    fail "The application exited with an error (exit code $EXIT_CODE). See messages above."
fi

echo
echo "Application stopped normally."
echo "Press Enter to close this window..."
read -r
