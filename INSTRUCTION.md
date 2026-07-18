# INSTRUCTION.md - Complete Beginner's Setup Guide

Welcome! This guide assumes you have **never used Python, Visual Studio Code,
Git, FastAPI, the OpenAI API, n8n, Zapier, or Make before.** Follow it top to
bottom, in order, and you will end up with a fully working Gmail automation
platform running on your computer.

Every command shown should be typed exactly as written into a terminal
window (Windows: **Command Prompt** or **PowerShell**; macOS: **Terminal**).

---

## Table of Contents

1. [Installing Python](#1-installing-python)
2. [Installing Visual Studio Code](#2-installing-visual-studio-code)
3. [Installing Git](#3-installing-git)
4. [Installing Required VS Code Extensions](#4-installing-required-vs-code-extensions)
5. [Opening the Project](#5-opening-the-project)
6. [Creating a Virtual Environment](#6-creating-a-virtual-environment)
7. [Activating the Virtual Environment](#7-activating-the-virtual-environment)
8. [Installing Dependencies](#8-installing-dependencies)
9. [Creating the .env File](#9-creating-the-env-file)
10. [Obtaining OpenAI API Keys](#10-obtaining-openai-api-keys)
11. [Setting Up Google Cloud](#11-setting-up-google-cloud)
12. [Setting Up a Telegram Bot](#12-setting-up-a-telegram-bot-optional)
13. [Setting Up a Discord Bot](#13-setting-up-a-discord-bot-optional)
14. [Configuring OAuth Credentials](#14-configuring-oauth-credentials)
15. [Running the Application](#15-running-the-application)
16. [Running the Automation Workflows](#16-running-the-automation-workflows)
17. [Importing the n8n Workflow](#17-importing-the-n8n-workflow)
18. [Importing the Zapier Workflow](#18-importing-the-zapier-workflow)
19. [Importing the Make Scenario](#19-importing-the-make-scenario)
20. [Testing Every Feature](#20-testing-every-feature)
21. [Common Errors](#21-common-errors)
22. [Troubleshooting](#22-troubleshooting)
23. [Project Architecture](#23-project-architecture)
24. [Folder Structure](#24-folder-structure)
25. [FAQ](#25-faq)
26. [Security Best Practices](#26-security-best-practices)
27. [Next Learning Steps](#27-next-learning-steps)

---

## 1. Installing Python

Python is the programming language this project is written in. You need
version **3.12 or newer**.

### Windows

1. Go to [python.org/downloads](https://www.python.org/downloads/).
2. Click the yellow **Download Python 3.x.x** button.
3. Run the downloaded installer.
4. **CRITICAL:** On the first install screen, check the box at the bottom
   that says **"Add python.exe to PATH"** before clicking Install Now.

   ```
   [ SCREENSHOT PLACEHOLDER: Python installer with "Add python.exe to PATH" checkbox highlighted ]
   ```
5. Click **Install Now** and wait for it to finish.
6. Open **Command Prompt** (press `Win`, type `cmd`, press Enter) and run:
   ```bash
   python --version
   ```
   **Expected output:**
   ```
   Python 3.12.x
   ```

### macOS

1. Go to [python.org/downloads](https://www.python.org/downloads/) and download the macOS installer, **or** if you have [Homebrew](https://brew.sh) installed, run:
   ```bash
   brew install python@3.12
   ```
2. Open **Terminal** (press `Cmd+Space`, type `Terminal`, press Enter) and run:
   ```bash
   python3 --version
   ```
   **Expected output:**
   ```
   Python 3.12.x
   ```

> If `python --version` shows Python 2.x on macOS, use `python3` instead of `python` throughout this guide.

---

## 2. Installing Visual Studio Code

Visual Studio Code (VS Code) is the code editor we'll use.

1. Go to [code.visualstudio.com](https://code.visualstudio.com/).
2. Click **Download** for your operating system.
3. Run the installer (Windows: check "Add to PATH" and "Register Code as an editor" during setup; macOS: drag the app into your Applications folder).
4. Launch VS Code once to confirm it opens.

   ```
   [ SCREENSHOT PLACEHOLDER: VS Code welcome screen ]
   ```

---

## 3. Installing Git

Git lets you download (clone) this project and track changes to code.

### Windows
1. Download from [git-scm.com/download/win](https://git-scm.com/download/win).
2. Run the installer, accepting the default options.

### macOS
```bash
brew install git
```
Or install the [Xcode Command Line Tools](https://developer.apple.com/xcode/resources/) which include Git.

### Verify installation (both platforms)
```bash
git --version
```
**Expected output:**
```
git version 2.4x.x
```

---

## 4. Installing Required VS Code Extensions

1. Open VS Code.
2. Click the **Extensions** icon in the left sidebar (four squares icon), or press `Ctrl+Shift+X` (Windows) / `Cmd+Shift+X` (macOS).
3. Search for and install each of the following:

| Extension | Publisher | Purpose |
|---|---|---|
| Python | Microsoft | Python language support |
| Pylance | Microsoft | Fast Python IntelliSense |
| Python Debugger | Microsoft | Debugging support |
| REST Client | Huachao Mao | Test API endpoints from `requests.http` |

```
[ SCREENSHOT PLACEHOLDER: VS Code Extensions panel with "Python" search results ]
```

> Tip: When you open this project folder (next step), VS Code will show a
> popup suggesting these same extensions automatically (from `.vscode/extensions.json`).

---

## 5. Opening the Project

If you downloaded this project as a `.zip` file, extract it first. Then:

1. Open VS Code.
2. Go to **File > Open Folder...**
3. Select the `gmail-automation` folder.
4. Click **Select Folder** (Windows) / **Open** (macOS).

You should now see the folder structure in the left sidebar (`app/`, `docs/`, `workflows/`, etc.).

```
[ SCREENSHOT PLACEHOLDER: VS Code Explorer sidebar showing the gmail-automation project tree ]
```

5. Open a terminal **inside VS Code**: **Terminal > New Terminal** (or `` Ctrl+` ``). All following commands can be typed here.

---

## 6. Creating a Virtual Environment

A virtual environment is an isolated Python installation just for this
project, so its dependencies don't conflict with anything else on your
computer.

In the VS Code terminal, from the project's root folder, run:

**Windows:**
```bash
python -m venv .venv
```

**macOS:**
```bash
python3 -m venv .venv
```

**Expected output:** no visible output, but a new `.venv` folder appears in your project.

> Skip this step if you plan to only use `Start App.bat` / `Start App (Mac).command` - they create it automatically. It's included here so you understand what those scripts do.

---

## 7. Activating the Virtual Environment

Activating tells your terminal to use the project's isolated Python instead of your system Python.

**Windows (Command Prompt):**
```bash
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```
> If PowerShell blocks this with an "execution policy" error, run:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` then try again.

**macOS:**
```bash
source .venv/bin/activate
```

**Expected result:** your terminal prompt now starts with `(.venv)`, e.g.:
```
(.venv) C:\projects\gmail-automation>
```

You must re-activate every time you open a new terminal window. VS Code often does this automatically if you selected the `.venv` interpreter (bottom-right corner of VS Code, click and choose `.venv`).

---

## 8. Installing Dependencies

With the virtual environment activated, install all required packages:

```bash
pip install -r requirements.txt
```

**Expected output (abbreviated):**
```
Collecting fastapi==0.115.6
  Downloading fastapi-0.115.6-py3-none-any.whl ...
...
Successfully installed fastapi-0.115.6 uvicorn-0.34.0 pydantic-2.10.4 ...
```

This takes 1-3 minutes depending on your internet connection.

For running the automated test suite too:
```bash
pip install -r requirements-dev.txt
```

---

## 9. Creating the .env File

The `.env` file holds your secret keys and configuration. It is never
uploaded to GitHub (see `.gitignore`).

1. Copy the template:

   **Windows:**
   ```bash
   copy .env.example .env
   ```

   **macOS:**
   ```bash
   cp .env.example .env
   ```

2. Open `.env` in VS Code (click it in the file explorer).
3. You'll fill in the real values in the next few sections. For now, leave it open.

---

## 10. Obtaining OpenAI API Keys

1. Go to [platform.openai.com](https://platform.openai.com/) and sign up or log in.
2. Click your profile icon (top right) -> **View API keys**, or go directly to [platform.openai.com/api-keys](https://platform.openai.com/api-keys).
3. Click **Create new secret key**, give it a name like `gmail-automation`, and click **Create secret key**.

   ```
   [ SCREENSHOT PLACEHOLDER: OpenAI API keys page with "Create new secret key" button ]
   ```
4. **Copy the key immediately** - OpenAI only shows it once. It looks like `sk-proj-...`.
5. You'll need billing set up on your OpenAI account (**Settings > Billing**) - the Responses API is pay-as-you-go; a few cents covers hundreds of test requests with small models.
6. In your `.env` file, set:
   ```env
   OPENAI_API_KEY=sk-proj-your-real-key-here
   ```

---

## 11. Setting Up Google Cloud

This is required so the app can read/send/label your Gmail. Full detailed
walkthrough (with more screenshots) is in
[docs/GOOGLE_CLOUD_SETUP.md](./docs/GOOGLE_CLOUD_SETUP.md) - summary below.

1. Go to [console.cloud.google.com](https://console.cloud.google.com/) and create a new project.
2. Go to **APIs & Services > Library**, search **Gmail API**, click **Enable**.
3. Go to **APIs & Services > OAuth consent screen**, choose **External**, fill in the app name and your email, add yourself as a **Test user**.
4. Go to **APIs & Services > Credentials > Create Credentials > OAuth client ID**.
5. Choose **Web application**, add this **Authorized redirect URI**:
   ```
   http://localhost:8000/auth/google/callback
   ```
6. Click **Create**, then copy the **Client ID** and **Client Secret** shown.

   ```
   [ SCREENSHOT PLACEHOLDER: Google Cloud "OAuth client created" dialog showing Client ID and Client Secret ]
   ```

7. In `.env`, set:
   ```env
   GOOGLE_CLIENT_ID=123456789-abc.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=GOCSPX-your-secret
   GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
   ```

---

## 12. Setting Up a Telegram Bot (Optional)

This core project does not include a built-in Telegram integration, but you
can trigger notifications through Telegram from your n8n/Make workflow if
you'd like urgent-email alerts there.

1. Open Telegram, search for **@BotFather**, and start a chat.
2. Send `/newbot`, follow the prompts to name your bot.
3. BotFather replies with a **bot token** like `123456:ABC-DEF...`.
4. Send a message to your new bot, then visit:
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```
   to find your **chat ID** in the JSON response.
5. In n8n or Make, add a **Telegram** node/module, paste your bot token, and use it to send messages such as `{{summary}}` after the webhook step described in [workflows/n8n](./workflows/n8n) or [workflows/make](./workflows/make).

---

## 13. Setting Up a Discord Bot (Optional)

Similarly optional - useful if you'd rather get urgent-email alerts in Discord.

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications) and click **New Application**.
2. Under **Bot**, click **Add Bot**, then **Reset Token** to reveal your bot token.
3. Under **OAuth2 > URL Generator**, check `bot` scope and `Send Messages` permission, then use the generated URL to invite the bot to your server.
4. The simplest integration doesn't even need a full bot: create a **Webhook** instead - go to your Discord channel's **Settings > Integrations > Webhooks > New Webhook**, copy the webhook URL, and call it directly from an n8n/Make/Zapier HTTP step with a JSON body like `{"content": "Urgent email: ..."}`.

---

## 14. Configuring OAuth Credentials

By this point your `.env` should have real values for:

```env
OPENAI_API_KEY=sk-proj-...
GOOGLE_CLIENT_ID=...apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-...
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

Also set two random secrets (these protect your own API - they aren't from
any external service, you make them up):

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Run this **twice** and paste the two different outputs into:
```env
SECRET_KEY=<first random value>
AUTOMATION_WEBHOOK_SECRET=<second random value>
```

Save the `.env` file.

---

## 15. Running the Application

With your virtual environment activated and `.env` configured:

```bash
uvicorn app.main:app --reload
```

**Expected output:**
```
INFO:     Will watch for changes in these directories: [...]
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
2026-07-18 10:00:00 | INFO     | app.main | Starting Gmail Automation Platform (env=development)
2026-07-18 10:00:00 | INFO     | app.repositories.database | Database initialized at ./data/gmail_automation.db
INFO:     Application startup complete.
```

Open your browser to **http://localhost:8000/docs** - you should see the
interactive Swagger UI listing every endpoint.

```
[ SCREENSHOT PLACEHOLDER: Swagger UI (/docs) showing all endpoints grouped by tag ]
```

Now connect Gmail: open **http://localhost:8000/auth/google/login**, log in
with the Google account you added as a test user, and approve the requested
permissions. You'll see a success message and can return to `/docs`.

> Prefer not to type commands? Double-click **`Start App.bat`** (Windows) or
> **`Start App (Mac).command`** (macOS) instead - they do steps 6-15 for you
> automatically every time.

---

## 16. Running the Automation Workflows

Once the FastAPI app is running and Gmail is connected, you can trigger
automation two ways:

1. **Manually**, via `/docs` or the `requests.http` file (see [Testing Every Feature](#20-testing-every-feature)).
2. **Automatically**, by connecting n8n, Zapier, or Make so they call this app whenever a new email arrives. Continue to the next three sections.

---

## 17. Importing the n8n Workflow

1. Install/open n8n ([n8n.io](https://n8n.io) - self-hosted or n8n Cloud).
2. In n8n, go to **Workflows > Import from File**.
3. Select `workflows/n8n/gmail-automation-workflow.json` from this project.
4. Open the **Gmail Trigger** node and connect your Gmail account (n8n runs its own separate OAuth popup).
5. Open the **Process Email** HTTP Request node and replace:
   - `REPLACE_WITH_YOUR_AUTOMATION_WEBHOOK_SECRET` with your `AUTOMATION_WEBHOOK_SECRET` value from `.env`.
   - The URL `http://localhost:8000/...` with your deployed URL if not running n8n on the same machine.
6. Click **Save**, then toggle the workflow **Active**.

```
[ SCREENSHOT PLACEHOLDER: n8n canvas showing Gmail Trigger -> Process Email -> Is Urgent? nodes connected ]
```

---

## 18. Importing the Zapier Workflow

Zapier doesn't support importing Zaps from a file, so follow the step-by-step
guide instead: **[workflows/zapier/zapier-setup-guide.md](./workflows/zapier/zapier-setup-guide.md)**.
It walks through building the equivalent automation (Gmail trigger -> Webhooks
by Zapier -> this app) in the Zapier UI in about 5 minutes.

---

## 19. Importing the Make Scenario

1. Open [Make](https://www.make.com/) and go to **Scenarios**.
2. Click **Create a new scenario**, then the **:** menu -> **Import Blueprint**.
3. Select `workflows/make/make-scenario.json` from this project.
4. Click each module and reconnect your **Gmail** account where prompted.
5. Open the HTTP module and replace `REPLACE_WITH_YOUR_AUTOMATION_WEBHOOK_SECRET` and the URL as described in the n8n section above.
6. Click **Save**, then toggle the scenario **ON** (bottom-left switch).

```
[ SCREENSHOT PLACEHOLDER: Make scenario editor showing Watch Gmail Inbox -> HTTP -> Filter -> Send Email modules ]
```

---

## 20. Testing Every Feature

The easiest way: open **http://localhost:8000/docs**, expand an endpoint,
click **Try it out**, fill in a real `message_id` (get one from
`GET /emails` first), and click **Execute**.

Alternatively, open `requests.http` in VS Code (with the REST Client
extension installed) and click **Send Request** above each block.

| Feature | Steps |
|---|---|
| Read Emails | `GET /emails?max_results=5` -> copy a `message_id` from the response |
| Summarize | `POST /emails/summarize` with that `message_id` |
| Categorize | `POST /emails/categorize` with that `message_id` |
| Auto Reply | `POST /emails/auto-reply` with `"send": false` first to preview |
| Extract Tasks | `POST /emails/extract-tasks` with that `message_id` |
| Translate | `POST /emails/translate` with `"target_language": "Spanish"` |
| Label | `POST /emails/label` with `"label_name": "Test"` - check your Gmail labels afterward |

**Expected response example** (`POST /emails/categorize`):
```json
{
  "message_id": "18f2a...",
  "category": "Work",
  "confidence": 0.91,
  "reasoning": "Discusses a project deadline and deliverables."
}
```

---

## 21. Common Errors

| Error message | Cause | Fix |
|---|---|---|
| `'python' is not recognized as an internal or external command` | Python not on PATH | Reinstall Python and check "Add to PATH" (Section 1) |
| `ModuleNotFoundError: No module named 'fastapi'` | Dependencies not installed, or venv not activated | Run Section 7 then Section 8 |
| `401 Not authenticated with Gmail yet` | You haven't completed the OAuth login | Visit `/auth/google/login` (Section 15) |
| `OPENAI_API_KEY is not configured` | `.env` missing or key not set | Check Section 9-10 |
| `redirect_uri_mismatch` (Google error page) | Redirect URI in `.env` doesn't match Google Cloud Console | Make sure both are exactly `http://localhost:8000/auth/google/callback` |
| `Access blocked: this app's request is invalid` | Your Google account isn't a test user | Add your email under OAuth consent screen -> Test users (Section 11) |
| `401 Missing or invalid webhook secret` | n8n/Zapier/Make sent wrong/missing secret | Match `webhook_secret` in the workflow to `AUTOMATION_WEBHOOK_SECRET` in `.env` |
| Port 8000 already in use | Another process is using port 8000 | Run `uvicorn app.main:app --reload --port 8001` and update URLs accordingly |

---

## 22. Troubleshooting

**The app starts but every Gmail call returns 401:**
Re-run the OAuth login flow at `/auth/google/login`. Tokens can expire if
your Google Cloud OAuth consent screen is still in "Testing" mode (7-day
expiry) - re-authenticate periodically, or publish the app.

**AI responses look wrong or return errors:**
Check your OpenAI account has billing enabled and hasn't hit a usage limit;
check `data/app.log` for the exact error message.

**n8n / Zapier / Make can't reach my local server:**
`localhost` only works if the automation tool runs on the *same machine*.
For n8n self-hosted on the same computer, this is fine. For Zapier, Make, or
n8n Cloud (all cloud-hosted), you must either deploy this app publicly or use
a tunnel like `ngrok http 8000` during testing.

**Changes to `.env` aren't taking effect:**
Restart the app (`Ctrl+C`, then re-run `uvicorn ...`). Environment variables
are only read at startup.

**Still stuck?** Check `data/app.log` for detailed error messages - every
request and error is logged there with a timestamp.

---

## 23. Project Architecture

This project follows **Clean Architecture**: business logic (services,
domain entities) is independent of frameworks (FastAPI) and external systems
(Gmail, OpenAI, SQLite), which keeps it testable and easy to extend.

```
HTTP Request
     │
     ▼
app/api/routes/* <- FastAPI routers (thin, no business logic)
     │
     ▼
app/services/* <- One class per feature; orchestrates the below
     │
     ├──▶ app/domain/* <- Plain Python entities (EmailMessage, etc.)
     ├──▶ app/services/gmail_service.py <- Gmail API client
     ├──▶ app/services/openai_service.py <- OpenAI Responses API client
     └──▶ app/repositories/* <- SQLite persistence
```

Full details: [docs/AUTOMATION_ARCHITECTURE.md](./docs/AUTOMATION_ARCHITECTURE.md).

---

## 24. Folder Structure

```
gmail-automation/
├── app/
│   ├── main.py # FastAPI app entrypoint
│   ├── core/ # Config, logging, security
│   ├── domain/ # Framework-free entities
│   ├── services/ # Feature services + Gmail/OpenAI clients
│   ├── repositories/ # SQLite access
│   ├── schemas/ # Pydantic v2 models
│   └── api/routes/ # HTTP endpoints
├── docs/ # In-depth documentation
├── workflows/ # n8n / Zapier / Make automation files
├── tests/ # Pytest test suite
├── data/ # SQLite DB + Gmail token cache (gitignored)
├── .vscode/ # Editor settings, debugger config
├── requests.http # Manual API test requests
├── requirements.txt # Production dependencies
├── requirements-dev.txt # + testing dependencies
├── .env.example # Environment variable template
├── Start App.bat # Windows launcher
├── Start App (Mac).command # macOS launcher
├── README.md
└── INSTRUCTION.md # This file
```

---

## 25. FAQ

**Q: Do I need a paid OpenAI plan?**
A: No - pay-as-you-go billing is enough. Small models like `gpt-4.1-mini` cost fractions of a cent per email.

**Q: Is my email data sent anywhere besides OpenAI and Google?**
A: No. This app only talks to the Gmail API (Google) and the OpenAI API. Nothing is sent to any other third party unless you configure one (e.g. a Slack webhook in your own n8n/Make workflow).

**Q: Can I use a different AI model?**
A: Yes - change `OPENAI_MODEL` in `.env` to any model available in your OpenAI account that supports the Responses API.

**Q: Can multiple people use this at once?**
A: This project is built for single-user/personal use (one Gmail account, one local token file). Multi-tenant support would require replacing the file-based token store with a per-user database table.

**Q: Does it work with Google Workspace (company) accounts?**
A: Yes, as long as your Workspace admin allows third-party app access and you configure the OAuth consent screen accordingly (may require admin approval).

**Q: Why SQLite instead of Postgres/MySQL?**
A: Zero setup, zero external dependencies, and more than sufficient for personal-scale automation. See [docs/AUTOMATION_ARCHITECTURE.md](./docs/AUTOMATION_ARCHITECTURE.md#data-persistence) for how to swap it out.

---

## 26. Security Best Practices

- **Never commit `.env` or `data/token.json`** to Git or share them - both grant access to your accounts. Both are already excluded via `.gitignore`.
- **Set `API_KEY` and `AUTOMATION_WEBHOOK_SECRET`** to strong random values (Section 14) before exposing this app beyond `localhost`.
- **Request only the Gmail scopes you need** - remove `gmail.send` from `GOOGLE_SCOPES` if you never plan to use auto-reply, for example.
- **Rotate your OpenAI key** periodically from [platform.openai.com/api-keys](https://platform.openai.com/api-keys), and immediately if you suspect it leaked.
- **Use HTTPS** if deploying beyond your own machine - never send credentials over plain HTTP on the public internet.
- **Review auto-reply output before enabling `send: true`** in production - AI-generated replies should be spot-checked, especially early on.

---

## 27. Next Learning Steps

Now that this is running, here's where to go deeper:

| Topic | Resource |
|---|---|
| Python basics | [docs.python.org/3/tutorial](https://docs.python.org/3/tutorial/) |
| FastAPI | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) |
| Git & GitHub | [docs.github.com/get-started](https://docs.github.com/en/get-started) |
| OpenAI API | [platform.openai.com/docs](https://platform.openai.com/docs) |
| Gmail API | [developers.google.com/gmail/api](https://developers.google.com/gmail/api) |
| n8n | [docs.n8n.io](https://docs.n8n.io/) |
| Make | [make.com/en/help](https://www.make.com/en/help) |
| Zapier | [zapier.com/help](https://zapier.com/help) |
| Pydantic v2 | [docs.pydantic.dev](https://docs.pydantic.dev/latest/) |
| Clean Architecture | *Clean Architecture* by Robert C. Martin |

Suggested extensions once you're comfortable:
- Add a web dashboard (React/Next.js) that calls this API.
- Swap SQLite for PostgreSQL for multi-user support.
- Add scheduled background processing (e.g. APScheduler or Celery) instead of relying solely on external triggers.
- Add more categories, custom prompts, or additional languages.

You're all set. Happy automating!
