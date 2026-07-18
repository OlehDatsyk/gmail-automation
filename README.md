# Gmail Automation Platform

A production-ready Gmail automation platform built with **FastAPI**, the
**OpenAI Responses API**, and the **Gmail API** - with first-class
integration hooks for **n8n**, **Zapier**, and **Make**.

Read, summarize, categorize, auto-reply to, extract tasks from, translate,
and label your emails automatically, either via the REST API directly or by
wiring it into a no-code automation platform.

> **New to Python, VS Code, or APIs?** Skip straight to
> **[INSTRUCTION.md](./INSTRUCTION.md)** - a complete beginner's walkthrough
> from "install Python" to "workflow is running."

---

## Features

| Feature | Endpoint | Description |
|---|---|---|
| Read Emails | `GET /emails` | List/search recent Gmail messages |
| Summarize Emails | `POST /emails/summarize` | AI-generated summary + key points |
| Categorize Emails | `POST /emails/categorize` | Classify into Work / Urgent / Finance / etc. |
| Auto Reply | `POST /emails/auto-reply` | Draft (and optionally send) an AI reply |
| Extract Tasks | `POST /emails/extract-tasks` | Pull out action items, due dates, priority |
| Translate Emails | `POST /emails/translate` | Translate a message into any language |
| Label Emails | `POST /emails/label` | Apply (creating if needed) a Gmail label |

Plus automation endpoints (`/automation/webhook`, `/automation/process-inbox`)
designed specifically for n8n, Zapier, and Make - see
[docs/AUTOMATION_ARCHITECTURE.md](./docs/AUTOMATION_ARCHITECTURE.md).

## Tech Stack

- **Python 3.12+**
- **FastAPI** - async REST API framework
- **Google Gmail API** (`google-api-python-client` + OAuth 2.0)
- **OpenAI Responses API** (latest `openai` SDK)
- **SQLite** - zero-config local persistence (no external database needed)
- **Pydantic v2** - request/response validation and settings

## Architecture

Clean Architecture with modular, single-responsibility services:

```
app/
├── api/routes/ # HTTP layer - FastAPI routers (health, auth, emails, automation)
├── services/ # Use-case layer - one service per feature + Gmail/OpenAI clients
├── domain/ # Framework-free entities and enums
├── repositories/ # Infrastructure - SQLite access
├── schemas/ # Pydantic v2 request/response models
└── core/ # Config, logging, security
```

See [docs/AUTOMATION_ARCHITECTURE.md](./docs/AUTOMATION_ARCHITECTURE.md) for
the full breakdown and request-flow diagrams.

## Quick Start

```bash
# 1. Clone and enter the project
git clone <your-fork-url> gmail-automation
cd gmail-automation

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# then edit .env with your OpenAI + Google credentials (see docs below)

# 5. Run the app
uvicorn app.main:app --reload
```

Then open **http://localhost:8000/docs** for interactive API docs, and
**http://localhost:8000/auth/google/login** to connect your Gmail account.

Prefer double-click setup? Use **`Start App.bat`** (Windows) or
**`Start App (Mac).command`** (macOS) - they handle all of the above
automatically. Full details in [INSTRUCTION.md](./INSTRUCTION.md).

## Configuration

All configuration lives in `.env` (copy from `.env.example`). Key variables:

| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `OPENAI_MODEL` | Model used for AI features (default: `gpt-4.1-mini`) |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Google Cloud OAuth credentials |
| `GOOGLE_REDIRECT_URI` | Must match a redirect URI configured in Google Cloud Console |
| `DATABASE_PATH` | SQLite file location |
| `AUTOMATION_WEBHOOK_SECRET` | Shared secret required by `/automation/*` endpoints |
| `API_KEY` | Optional key protecting `/emails/*` endpoints |

Full setup walkthroughs:
- [docs/GOOGLE_CLOUD_SETUP.md](./docs/GOOGLE_CLOUD_SETUP.md) - create your Google Cloud project & OAuth credentials
- [docs/OAUTH_SETUP.md](./docs/OAUTH_SETUP.md) - how the login flow works
- [docs/GMAIL_API.md](./docs/GMAIL_API.md) - Gmail API usage reference

## Automation (n8n / Zapier / Make)

Ready-to-use workflow definitions live in [`workflows/`](./workflows):

| Platform | File | Import method |
|---|---|---|
| n8n | `workflows/n8n/gmail-automation-workflow.json` | Workflows -> Import from File |
| Zapier | `workflows/zapier/zapier-setup-guide.md` | Step-by-step build guide (Zaps aren't portable JSON) |
| Make | `workflows/make/make-scenario.json` | Scenarios -> Import Blueprint |

See [docs/AUTOMATION_ARCHITECTURE.md](./docs/AUTOMATION_ARCHITECTURE.md) for
the design behind these integrations.

## Testing

```bash
pip install -r requirements-dev.txt
pytest
```

## Project Structure

```
gmail-automation/
├── app/ # FastAPI application (Clean Architecture)
├── docs/ # OAuth, Google Cloud, Gmail API, architecture docs
├── workflows/ # n8n / Zapier / Make automation definitions
├── tests/ # Pytest test suite
├── data/ # SQLite DB + OAuth token cache (gitignored)
├── .vscode/ # VS Code settings, launch config, extensions
├── requirements.txt # Production dependencies
├── requirements-dev.txt # + testing dependencies
├── .env.example # Environment variable template
├── Start App.bat # Windows one-click launcher
├── Start App (Mac).command # macOS one-click launcher
├── INSTRUCTION.md # Complete beginner's setup guide
└── README.md # This file
```

## Security Notes

- Never commit `.env` or `data/token.json` - both are already gitignored.
- Set `API_KEY` and `AUTOMATION_WEBHOOK_SECRET` to strong random values before deploying anywhere beyond `localhost`.
- Gmail access is scoped via OAuth 2.0 - review requested scopes in `docs/OAUTH_SETUP.md` and remove any you don't need.

## License

MIT - see [LICENSE](./LICENSE).
