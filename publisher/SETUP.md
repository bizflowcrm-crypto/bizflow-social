# Auto-publisher setup (GitHub Actions, no Metricool)

`.github/workflows/publish.yml` runs every 15 minutes, reads `publisher/queue.json`, posts
whatever is due and records it in `publisher/state.json`. It posts straight to the platform APIs,
so there is no monthly post limit. A network whose secrets are missing is skipped (not failed)
and posts on a later run once you add them (anything more than 7 days late is marked `expired` (`MAX_LATE_HOURS`)).

Never paste tokens in chat or commit them. They go in **Settings > Secrets and variables >
Actions > New repository secret**.

## 0. Make it run
- Scheduled workflows only run from the **default branch** (`main`), and media is read from
  `raw.githubusercontent.com/.../main/media/...`. So this branch must be merged to `main`.
- Settings > Actions > General > Workflow permissions: **Read and write**.
- Test without posting: Actions tab > "Publish scheduled posts" > Run workflow > mode **verify** (checks every secret works and shows which accounts it reached), then **dry-run**.

## 1. Instagram (works the same day)
1. @bizflowindia must be a **Business or Creator** account linked to a Facebook Page.
2. developers.facebook.com > My Apps > Create app (type: Business). Add the **Instagram** product
   (Instagram API with Facebook Login) and permissions `instagram_basic`,
   `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`.
   While the app is in Development mode it works for people with a role on the app (you), so no
   app review is needed to post to your own account.
3. Graph API Explorer: select your app, generate a user token with those permissions, then
   exchange it for a long-lived token:
   `GET /oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=SHORT_TOKEN`
4. With the long-lived token call `GET /me/accounts`. Use that Page's `access_token` (a Page token
   made from a long-lived user token does not expire) as **`INSTAGRAM_ACCESS_TOKEN`** (`IG_ACCESS_TOKEN` also works).
5. `GET /PAGE_ID?fields=instagram_business_account` gives the id for **`INSTAGRAM_ACCOUNT_ID`** (`IG_USER_ID` also works).

## 2. YouTube + Google Business Profile (one Google token for both)
1. console.cloud.google.com, signed in as **bizflowcrm**: new project > enable **YouTube Data API
   v3** and **Google My Business API / Business Profile APIs**.
2. OAuth consent screen: External, add yourself as a test user, then **Publish app** (otherwise the
   token expires after 7 days). Credentials > Create OAuth client ID > **Desktop app**.
3. On your computer: `python3 publisher/google_token.py CLIENT_ID CLIENT_SECRET`, approve while
   signed in as bizflowcrm, copy the printed refresh token.
4. Secrets: `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`.
5. Choose the **bizflowcrm channel** (not BizFlow POS) on the Google screen that asks which
   channel/Brand Account.
6. **Approvals Google requires** (both free, can take days to weeks):
   - YouTube: uploads from an unaudited API project are forced private until the project passes the
     YouTube API Services audit (form in the API console). Until then schedule Shorts in YouTube Studio.
   - Business Profile API: apply for access at the "Business Profile API access" form. Until then post the daily update by hand.
7. Secret `GBP_LOCATION` = `accounts/ACCOUNT_ID/locations/LOCATION_ID`. Ours (from Metricool) was
   `accounts/112835129773898375955/locations/14988455239875861557`.

## Adding posts
```
python3 publisher/enqueue.py posts/<spec>.json --start 2026-10-16 --slots 11:00,17:30,20:30
python3 publisher/enqueue.py posts/<carousel-spec>.json --start 2026-10-16 --slots 12:30,19:00 --gbp-slot 14:00
```
Commit and push `publisher/queue.json`. Slots fill day by day (Asia/Kolkata). Reels go to Instagram +
YouTube; carousels go to Instagram and YouTube (`short.mp4`); `--gbp-slot` adds at most one Google post a
day (only specs with `gbp_text`).

## Limits and notes
- Instagram: 100 API posts per 24 h. YouTube: default quota allows about 6 uploads a day.
- A failed network is retried on the next 3 runs, then the workflow fails and you get an email.
  The error is in `state.json`.
- Quiet hours: scheduled runs post nothing from 00:00 to 07:00 IST (due posts wait for morning). Manual runs ignore this.
- GitHub cron can run a few minutes late, so posts go out within about 15-25 minutes of their time.

## Token expired ("Session has expired", OAuthException 190)
Instagram tokens from the Graph API Explorer last only an hour or two. The publisher now stops and the workflow
fails (you get an email) when a token is rejected, and it does not use up a post's attempts.
To fix it for good: run `python3 publisher/ig_token.py APP_ID APP_SECRET SHORT_LIVED_TOKEN` on your computer. It prints a
Page token that never expires and the Instagram account ID. Put them in the GitHub secrets `INSTAGRAM_ACCESS_TOKEN` and
`INSTAGRAM_ACCOUNT_ID`, then run the workflow with mode `verify`.

## Daily health check and queue refill (no action needed)
`.github/workflows/maintenance.yml` runs every day at 08:45 IST.
- **Refill** (`publisher/recycle.py`): if any day in the next 14 days has no carousel or no Reel, it fills every such day
  up to 28 days ahead (carousel 12:30, plus its Google update at 14:00; Reel 19:00) with evergreen posts. Posts that never
  actually went out (expired or failed) are picked first, then the ones used longest ago.
  Recycled posts go to Instagram and Google only. Festival, seasonal and date-specific posts are never recycled; the
  rules are in `publisher/evergreen.json` (add an id there to stop it repeating).
- **Health check** (`publisher/health.py`): Instagram token valid and not expiring within 10 days, Google token accepted,
  days of posts left, posts due but not going out, failed posts. If anything needs attention the run fails (GitHub emails you)
  and an issue called "Social automation needs attention" is opened; it closes itself when everything is green again.
- Run it by hand any time: Actions > "Daily health check and queue refill" > Run workflow.

## More accounts (several Instagram pages and YouTube channels)
One workflow manages all of them. Each account is a short name in `publisher/accounts.json`; every queue entry has an
`account` (entries without one belong to the default account, `bizflow`). Each account posts only with its own keys, has its own
queue, recycler and health check, and posts one item per run, so a rejected token pauses only that account.

1. **Add the name** in `publisher/accounts.json`, e.g. `"pos": {"label": "BizFlow POS (Instagram @..., YouTube ...)"}`.
2. **Instagram:** the page must be a Business or Creator account linked to a Facebook Page you administer (or be added as a tester
   on your Meta app). Generate the user token as in section 1 and run `python3 publisher/ig_token.py APP_ID APP_SECRET TOKEN`: it
   lists every Page with a linked Instagram account and prints a JSON block to paste in the secret.
3. **YouTube / Google Business:** run `python3 publisher/google_token.py CLIENT_ID CLIENT_SECRET` once per channel and pick that
   channel on Google's screen. Each Google Cloud project allows about 6 uploads a day, so give each channel its own project (free)
   if they post daily. Every project needs its own audit before Shorts go public.
4. **Put all keys in one secret `ACCOUNTS_SECRETS`** (Settings > Secrets > Actions), JSON, only the keys you have:
   ```
   {"pos": {"ig_user_id": "...", "ig_token": "...",
            "yt_client_id": "...", "yt_client_secret": "...", "yt_refresh_token": "...", "gbp_location": "accounts/1/locations/2"}}
   ```
   The default account keeps working with the old secrets (`INSTAGRAM_*`, `YT_*`, `GBP_LOCATION`); `ACCOUNTS_SECRETS` can also override it.
5. **Check:** Actions > "Publish scheduled posts" > mode `verify` shows every account's Instagram username and YouTube channel.
6. **Content:** start the content file with `account: pos` (see content/README.md); or `python3 publisher/enqueue.py SPEC --account pos ...`.
   Post ids must be unique across all accounts. The new account's first posts start the day after its own last queued post.
