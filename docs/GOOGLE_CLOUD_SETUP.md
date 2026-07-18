# Google Cloud Setup

This guide walks through the one-time setup required in Google Cloud Console
so this application can access Gmail on your behalf.

## 1. Create a Google Cloud project

1. Go to [console.cloud.google.com](https://console.cloud.google.com/).
2. Click the project dropdown at the top of the page, then **New Project**.
3. Name it something like `gmail-automation` and click **Create**.
4. Wait for the project to finish creating, then make sure it's selected in the top dropdown.

## 2. Enable the Gmail API

1. In the left sidebar, go to **APIs & Services > Library**.
2. Search for `Gmail API`.
3. Click it, then click **Enable**.

## 3. Configure the OAuth consent screen

1. Go to **APIs & Services > OAuth consent screen**.
2. Choose **External** (unless you have a Google Workspace organization and want **Internal**).
3. Fill in:
   - **App name**: `Gmail Automation Platform`
   - **User support email**: your email
   - **Developer contact information**: your email
4. Click **Save and Continue** through the Scopes screen (you can add scopes later; the app requests them at login time).
5. On the **Test users** screen, add the Gmail address(es) you'll use to test the app. While your app is in "Testing" mode, only these accounts can authenticate.
6. Save and finish.

## 4. Create OAuth 2.0 credentials

1. Go to **APIs & Services > Credentials**.
2. Click **Create Credentials > OAuth client ID**.
3. Application type: **Web application**.
4. Name: `Gmail Automation Platform - Web`.
5. Under **Authorized redirect URIs**, add:
   ```
   http://localhost:8000/auth/google/callback
   ```
   (Match this exactly to `GOOGLE_REDIRECT_URI` in your `.env` file. If you deploy the app elsewhere, add that URL too.)
6. Click **Create**. A dialog shows your **Client ID** and **Client Secret** — copy both.

## 5. Add credentials to your `.env` file

```env
GOOGLE_CLIENT_ID=123456789-abc.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

## 6. Publishing status and quotas

- While in **Testing** mode, tokens expire after 7 days and only test users can log in — this is fine for development.
- To allow any Gmail user to authenticate, click **Publish App** on the OAuth consent screen. Google may require verification for sensitive scopes (like `gmail.modify`) if you plan to make the app public; for personal/internal use, Testing mode is sufficient indefinitely as long as you keep re-adding yourself as a test user (test users do not expire).
- The Gmail API free tier quota (1 billion quota units/day) is far more than a personal automation tool will ever use.

## Next step

Continue to [OAUTH_SETUP.md](./OAUTH_SETUP.md) to understand exactly how this application performs the OAuth login flow.
