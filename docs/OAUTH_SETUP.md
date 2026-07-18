# OAuth 2.0 Explained (For This Project)

This document explains how Gmail Automation Platform authenticates with
Gmail, and why the flow works the way it does.

## Why OAuth instead of a username/password?

Google never lets third-party apps use your Gmail password directly. Instead,
apps use **OAuth 2.0**: you log in on Google's own site, approve specific
permissions ("scopes"), and Google hands the app a **token** — not your
password. The app can only do what the token's scopes allow, and you can
revoke it at any time from your Google Account settings without changing your
password.

## The flow used by this app (Authorization Code flow)

```
┌──────────┐        1. GET /auth/google/login        ┌─────────────┐
│  Browser │ ───────────────────────────────────────▶ │ This App    │
└──────────┘                                           └─────────────┘
     │                                                        │
     │   2. Redirect to accounts.google.com consent screen    │
     ▼                                                        │
┌──────────────┐                                              │
│ Google Login │                                              │
└──────────────┘                                              │
     │  3. User approves requested scopes                     │
     ▼                                                        │
     4. Redirect to GOOGLE_REDIRECT_URI?code=AUTH_CODE ───────▶
                                                                │
                              5. App exchanges AUTH_CODE for   │
                                 an access_token + refresh_token
                                 by calling Google's token endpoint
                                                                │
                              6. Tokens saved to               │
                                 data/token.json (local file)  │
```

### Step by step, in this codebase

1. **`GET /auth/google/login`** (`app/api/routes/auth.py`) builds the Google
   consent-screen URL via `GmailService.build_authorization_url()` and
   redirects the browser there.
2. You approve the requested scopes on Google's site.
3. Google redirects back to **`GET /auth/google/callback?code=...`**.
4. `GmailService.exchange_code_for_token()` exchanges that one-time code for
   an **access token** (short-lived, ~1 hour) and a **refresh token**
   (long-lived — used to silently get new access tokens without asking you
   to log in again).
5. Both tokens are written to `data/token.json` (path configurable via
   `GOOGLE_TOKEN_STORE_PATH`). This file is in `.gitignore` — never commit it.
6. On every subsequent Gmail API call, `GmailService._load_credentials()`
   reads this file and automatically refreshes the access token if it has
   expired, using the refresh token — no user interaction required.

## Scopes requested

Configured via `GOOGLE_SCOPES` in `.env`:

| Scope | Used for |
|---|---|
| `gmail.readonly` | Reading emails, listing the inbox |
| `gmail.send` | Sending auto-replies |
| `gmail.modify` | Applying labels to messages |
| `gmail.labels` | Creating new labels |

Request only the scopes you need. Removing `gmail.send` from `.env`, for
example, means the auto-reply *sending* feature will fail, but reading,
summarizing, and categorizing will still work.

## Checking authentication status

```
GET /auth/status
```

Returns whether a valid token exists and, if so, the connected Gmail address.

## Revoking access

You can revoke this app's access at any time from
[myaccount.google.com/permissions](https://myaccount.google.com/permissions).
Doing so invalidates the refresh token; you'll need to log in again via
`/auth/google/login`.

## Security notes

- `data/token.json` grants whoever holds it access to your Gmail account
  under the scopes you approved. Treat it like a password.
- Never commit `.env` or `data/token.json` to Git (`.gitignore` already
  excludes both).
- In production, store tokens in an encrypted secret store rather than a
  plain JSON file — the file-based approach here is intentionally simple for
  local development and small personal deployments.
