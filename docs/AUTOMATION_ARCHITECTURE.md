# Automation Architecture

This document explains how Gmail Automation Platform is structured, and how
n8n, Zapier, and Make fit into the overall system.

## Clean Architecture layers

```
┌─────────────────────────────────────────────────────────────────┐
│  app/api/routes/*        HTTP layer (FastAPI routers)             │
│  - Translates HTTP requests <-> service calls                     │
│  - No business logic lives here                                   │
├─────────────────────────────────────────────────────────────────┤
│  app/services/*          Application / use-case layer             │
│  - One class per feature (SummarizerService, CategorizerService,  │
│    AutoReplyService, TaskExtractionService, TranslationService,   │
│    LabelingService)                                                │
│  - Orchestrates domain entities + external services                │
├─────────────────────────────────────────────────────────────────┤
│  app/domain/*            Domain layer                              │
│  - Framework-free dataclasses & enums (EmailMessage, EmailCategory)│
│  - No dependency on FastAPI, Gmail, OpenAI, or SQLite               │
├─────────────────────────────────────────────────────────────────┤
│  app/services/gmail_service.py, openai_service.py                  │
│  app/repositories/*       Infrastructure layer                     │
│  - Gmail API client, OpenAI Responses API client, SQLite access    │
└─────────────────────────────────────────────────────────────────┘
```

Dependencies point **inward**: routes depend on services, services depend on
domain entities and infrastructure clients, but domain entities depend on
nothing. This keeps the core business logic (what a "categorization" or
"task extraction" *is*) testable without a live Gmail/OpenAI connection —
see `tests/test_categorizer_service.py` for an example using mocked clients.

## Request flow example: categorizing an email

```
Client / n8n / Zapier / Make
        │
        ▼
POST /emails/categorize  (app/api/routes/emails.py)
        │
        ▼
CategorizerService.categorize(message_id)  (app/services/categorizer_service.py)
        │
        ├──▶ GmailService.get_message(id)     — fetch + parse the email
        ├──▶ OpenAIService.categorize_email()  — classify via Responses API
        └──▶ EmailRepository.save_processed_email() — persist to SQLite
        │
        ▼
CategorizeResponse JSON returned to caller
```

## Two integration patterns for automation tools

### 1. Direct feature calls (pull)

n8n / Zapier / Make can call any `/emails/*` endpoint directly with an HTTP
Request node — e.g. call `GET /emails?query=is:unread` on a schedule, then
loop over results calling `POST /emails/summarize` for each one.

**Best for:** workflows that need fine-grained control over each step, or
that mix Gmail Automation Platform calls with other services in between.

### 2. Webhook pipeline (push)

`POST /automation/webhook` accepts a single `message_id` and a list of
`actions` to run (`summarize`, `categorize`, `extract_tasks`, `translate`,
`auto_reply`, `label`), returning one combined JSON result. This minimizes
the number of HTTP nodes a no-code workflow needs.

**Best for:** simple "when a new email arrives, do X, Y, Z" automations —
this is the pattern used by the provided workflow files in `workflows/`.

### 3. Full-inbox pipeline

`POST /automation/process-inbox` runs categorize → summarize → label →
(optional) auto-reply across the most recent unread emails in a single call.
Ideal for a scheduled trigger (e.g. n8n Cron node every 15 minutes, or a
Zapier/Make schedule trigger) that processes the whole inbox at once without
per-message orchestration in the no-code tool.

## Where triggers live

Gmail "new email" triggers are handled by the automation platform itself
(n8n has a native Gmail trigger node; Zapier and Make both offer Gmail
triggers), **not** by this FastAPI app — this app does not poll Gmail on a
schedule internally. This keeps a clean separation: the automation tool owns
scheduling/triggering, and this app owns AI processing logic. See the
`workflows/` folder for ready-to-import examples of this pattern.

## Security model

- **Gmail access** is protected by OAuth 2.0 (see `docs/OAUTH_SETUP.md`).
- **`/emails/*` endpoints** are optionally protected by a static API key
  (`API_KEY` env var, sent via the `X-API-Key` header) — useful once you
  expose this app beyond `localhost`.
- **`/automation/*` endpoints** are protected by a separate shared secret
  (`AUTOMATION_WEBHOOK_SECRET`), sent in the JSON body as `webhook_secret`,
  since most no-code tools find it easier to add a body field than a custom
  header when using their built-in "Gmail Automation Platform" HTTP action.

## Data persistence

SQLite (`data/gmail_automation.db`) stores:

- `processed_emails` — a running log of what was done to each message
  (category, summary, label, reply status, task count) — visible via
  `GET /emails/history/recent`.
- `automation_logs` — a generic event log automation tools can query via
  `GET /automation/logs/recent` for debugging failed workflow runs.
- `extracted_tasks` — individual action items pulled out of emails.

SQLite was chosen (over Postgres/MySQL) to keep the project dependency-free
and runnable with zero external infrastructure — appropriate for a personal
or small-team automation tool. For multi-instance/production deployments,
swap `app/repositories/database.py` for a networked database; the
repository interface (`EmailRepository`) does not need to change.
