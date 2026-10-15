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
   made from a long-lived user token does not expire) as **`IG_ACCESS_TOKEN`**.
5. `GET /PAGE_ID?fields=instagram_business_account` gives the id for **`IG_USER_ID`**.

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
- GitHub cron can run a few minutes late, so posts go out within about 15-25 minutes of their time.
