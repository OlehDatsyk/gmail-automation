# Gmail API Reference (As Used In This Project)

This document explains how `app/services/gmail_service.py` uses the Gmail
API, for anyone extending the project.

## Client library

We use Google's official [`google-api-python-client`](https://github.com/googleapis/google-api-python-client)
to call the Gmail API (`gmail.googleapis.com`), authenticated with
credentials produced by the OAuth flow described in
[OAUTH_SETUP.md](./OAUTH_SETUP.md).

```python
service = build("gmail", "v1", credentials=creds)
```

## Reading messages

### List message IDs

```
GET https://gmail.googleapis.com/gmail/v1/users/me/messages?q=is:unread&maxResults=10
```

The `list` endpoint only returns message **IDs** — not content. This project
calls `messages.list`, then calls `messages.get` for each ID to fetch full
content. The `q` parameter accepts standard [Gmail search operators](https://support.google.com/mail/answer/7190),
e.g. `is:unread`, `from:boss@example.com`, `subject:invoice`, `newer_than:2d`.

### Get a full message

```
GET https://gmail.googleapis.com/gmail/v1/users/me/messages/{id}?format=full
```

Returns headers, MIME structure, and base64url-encoded body parts. Gmail
messages are MIME multipart — the body can be nested across `text/plain` and
`text/html` parts, sometimes with attachments. `GmailService._extract_body()`
recursively walks the MIME tree and prefers `text/plain`, falling back to
`text/html` if no plain-text part exists.

Body content is base64url-encoded (`-` and `_` instead of `+` and `/`), which
is why we use `base64.urlsafe_b64decode` rather than the standard decoder.

## Sending messages (auto-reply)

Gmail's `messages.send` endpoint expects a full **RFC 2822** MIME message,
base64url-encoded, in the `raw` field:

```
POST https://gmail.googleapis.com/gmail/v1/users/me/messages/send
{
  "raw": "<base64url-encoded MIME message>",
  "threadId": "<original thread id>"
}
```

We build this with Python's standard `email.mime.text.MIMEText`, set the
`To` and `Subject` headers (prefixing `Re:` if not already present), and
pass the original message's `threadId` so Gmail groups the reply into the
same conversation.

## Labels

Gmail labels are how folders/tags work. Two calls are involved:

1. **`labels.list`** — check if a label with the given name already exists
   (label names are case-insensitive for this comparison in our code, but
   Gmail itself is case-sensitive on the label ID).
2. **`labels.create`** — create it if not, with:
   ```json
   {
     "name": "Work",
     "labelListVisibility": "labelShow",
     "messageListVisibility": "show"
   }
   ```
3. **`messages.modify`** — apply the label's ID to a message:
   ```json
   { "addLabelIds": ["Label_123"] }
   ```

System labels like `INBOX`, `UNREAD`, `IMPORTANT`, `SPAM`, and category tabs
(`CATEGORY_PERSONAL`, `CATEGORY_UPDATES`, etc.) are separate from
user-created labels and are referenced directly by name (they double as their
own IDs).

## Rate limits

The Gmail API enforces per-user rate limits (roughly 250 quota units/user/second)
and a daily project quota. Each `messages.get` costs ~5 units, `messages.send`
costs 100 units, and `messages.list` costs 5 units. For personal-scale
automation (tens to low hundreds of emails per run) you will not come close
to these limits. If you see `429` or `403 rateLimitExceeded` errors, add
retry-with-backoff logic or reduce `MAX_EMAILS_PER_FETCH`.

## Error handling

All Gmail calls in this project raise `googleapiclient.errors.HttpError` on
failure, which is caught and logged in `GmailService`, and converted into an
appropriate HTTP status code (401 for auth issues, 502 for upstream Gmail
errors) at the API route layer.
