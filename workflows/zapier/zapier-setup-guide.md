# Zapier Setup Guide

Zapier does not support importing/exporting Zaps as portable JSON files the
way n8n and Make do (Zaps are tied to your account and connected apps), so
this guide walks through building the equivalent Zap step by step instead.
It takes about 5 minutes.

## What this Zap does

**Trigger:** New email arrives in Gmail
**Action:** Call the Gmail Automation Platform's `/automation/webhook` endpoint to summarize, categorize, extract tasks, and label it
**Optional filter/action:** If the category is "Urgent", send a Slack/SMS/email notification

## Prerequisites

- A Zapier account (free tier works for testing; scheduled/multi-step Zaps beyond the free plan's limits may need a paid plan).
- Gmail Automation Platform running somewhere Zapier's servers can reach it. **`localhost` will not work** — Zapier is cloud-based. Either:
  - Deploy the app to a small cloud host (Render, Railway, Fly.io, a VPS, etc.), or
  - Use a tunnel like [ngrok](https://ngrok.com/) during testing: `ngrok http 8000`, then use the `https://xxxx.ngrok-free.app` URL it gives you.
- Your `AUTOMATION_WEBHOOK_SECRET` value from `.env`.

## Step 1 — Create a new Zap

1. Log into [zapier.com](https://zapier.com) and click **Create Zap**.
2. Name it `Gmail Automation Platform - New Email Pipeline`.

## Step 2 — Set the trigger

1. Search for and select the **Gmail** app.
2. Choose the trigger event **New Email**.
3. Connect your Gmail account (Zapier will run its own OAuth flow — separate from this app's).
4. Set **Search String** to `is:unread` (or leave blank to trigger on all mail, filtered later).
5. Test the trigger — Zapier will fetch a sample recent email.

## Step 3 — Add the webhook action

1. Click **+** to add a step.
2. Search for and select **Webhooks by Zapier**.
3. Choose action event **POST**.
4. Configure:

   | Field | Value |
   |---|---|
   | URL | `https://YOUR_DEPLOYED_URL/automation/webhook` |
   | Payload Type | `json` |
   | Data | See JSON body below |
   | Headers | `Content-Type: application/json` |

5. In the **Data** section, add these key/value pairs (map `message_id` to the Gmail trigger's **Message ID** field using Zapier's field picker):

   | Key | Value |
   |---|---|
   | `message_id` | *(map to Gmail trigger's Message ID)* |
   | `actions` | `["summarize","categorize","extract_tasks","label"]` |
   | `label_name` | `Processed` |
   | `webhook_secret` | *(your `AUTOMATION_WEBHOOK_SECRET` value)* |

6. Test the step. You should get back a `200 OK` with JSON containing `summary`, `category`, `tasks`, and `label_applied`.

## Step 4 (optional) — Notify on urgent emails

1. Add a **Filter by Zapier** step after the webhook step.
2. Condition: `category` (from the webhook response) **Exactly matches** `Urgent`.
3. Add a final action step — e.g. **Slack: Send Channel Message**, **SMS by Zapier**, or **Gmail: Send Email** — using `{{summary}}` from the webhook response in the message body.

## Step 5 — Turn the Zap on

Click **Publish** in the top right. Your pipeline is now live: every new
unread email in Gmail will be summarized, categorized, checked for tasks,
and labeled automatically by Gmail Automation Platform.

## Alternative: full-inbox pipeline on a schedule

Instead of a per-email trigger, you can use a **Schedule by Zapier** trigger
(e.g. every 15 minutes) with a **Webhooks by Zapier: POST** action calling:

```
POST https://YOUR_DEPLOYED_URL/automation/process-inbox
Content-Type: application/json

{
  "max_results": 10,
  "apply_labels": true,
  "auto_reply": false
}
```

This processes the most recent unread emails in one call instead of
triggering once per message — useful if you're on Zapier's free plan and
want to conserve monthly task quota.

## Troubleshooting

| Problem | Fix |
|---|---|
| Webhook step returns `401` | Double-check `webhook_secret` matches `AUTOMATION_WEBHOOK_SECRET` in your `.env` exactly. |
| Webhook step returns `502` | Your OpenAI or Gmail credentials on the server side are likely misconfigured — check the app's logs. |
| Webhook step times out | Make sure your deployed URL is reachable from the public internet (not `localhost`), and that your server isn't asleep (some free hosts sleep after inactivity). |
| Zap doesn't trigger | Confirm the Gmail trigger step's search string isn't excluding the test email, and that the Zap is published/turned on. |
