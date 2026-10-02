# BizFlow Social Autopilot Playbook

This file is the standing instructions for the weekly scheduled task that runs
BizFlow India's Instagram. Every run starts fresh, so everything it needs is here.

## Brand facts (only claim what is listed here)

- **BizFlow India**, Sangamner, Maharashtra. Website: bizflowindia.cloud
- Business software for Indian SMEs: **GST billing, POS billing, CRM, cloud ERP,
  inventory, WhatsApp automation**, 20+ industry products.
- Industry products: **TableFlow** (restaurant/hotel POS: table billing, KOT, bar stock,
  accounts, 15+ reports), **RetailFlow** (retail POS), **AccountFlow** (GST accounting).
- Plans **from ₹399**. Support in **English, Hindi and Marathi**.
- CTA: **📞 8888567870, free demo**. Email hello@bizflowindia.cloud
- Never invent numbers (customer counts, speed claims, savings %, testimonials).
  If a claim isn't listed above, leave it out.

## Audience and voice

- Small business owners in Maharashtra: shops, traders, restaurants, service businesses.
- Write in **Marathi mixed with everyday English words** (business, bill, stock, demo),
  like the account's existing posts. Short, warm, practical. Emojis in moderation.
- Hashtags: 6–8, always `#bizflow #bizflowindia` plus topic and local tags
  (`#sangamner #maharashtrabusiness #marathibusiness #smallbusinessindia`).

## What has worked (update this section every run)

- 2026-09-25 Ganesh visarjan post with local Sangamner influencers: **790 views, 409 reach,
  22 likes** — by far the best. Real people + local community wins.
- 2026-09-29 TableFlow product carousel: 131 views, 48 reach. Pure product posts reach less.
- 2026-09-14 team Ganpati celebration: 138 views, 56 reach.
- Best posting time (Metricool): **10:00 IST Mon–Fri**, strongest Wed/Thu/Fri. 18:00 is second best.
  Weekends get about half the reach.

## Weekly procedure

Brand: Metricool `blogId` **7206028**, timezone `Asia/Calcutta`, Instagram `@bizflowindia`.

1. **Review**: pull Instagram post metrics for the last 14 days with
   `getAnalyticsDataByMetrics` (IGPO02 date, IGPO03 content, IGPO07 type, IGPO14 reach,
   IGPO13 likes, IGPO08 comments, IGPO15 saves, IGPO27 shares, IGPO28 views, IGPO29 follows).
   Add a dated line per post to "What has worked" above. Note what beat the average.
2. **Check the calendar**: `getScheduledPosts` for next Mon–Sun so nothing is doubled.
3. **Plan 3 posts** for Mon, Wed, Fri at 10:00, one from each of three different pillars,
   leaning toward whatever performed best:
   - Pain point → solution (udhaar, GST stress, stock guesswork, missed follow-ups)
   - How-to / save-worthy tips (GST invoice steps, reminders, reports)
   - Feature spotlight (WhatsApp automation, CRM, inventory, Marathi/Hindi support)
   - Industry product (TableFlow restaurants, RetailFlow shops, AccountFlow)
   - Festival / local / community (Indian & Maharashtra festivals that week; Sangamner)
   - If `photos/` has new real photos (team, customers, events), build one post around them —
     real people outperform graphics.
4. **Write the spec** as `posts/<YYYY>-w<WW>.json` (copy the shape of `posts/2026-w41.json`).
   Slide kinds: `cover`, `point`, `list`, `chips`, `chat`, `cta`. 4–6 slides; last slide is
   always `cta`. Use `[[text]]` to highlight. Keep each slide to one idea.
5. **Render**: `pip install playwright --break-system-packages && python3 -m playwright install chromium`
   if needed, then `python3 build.py posts/<file>.json`. Open 2–3 slides with Read and check
   Devanagari renders correctly (Poppins covers it; FreeSans is the fallback) and nothing
   overflows.
6. **Publish images**: commit `posts/` + `media/` and push to `main`. Image URLs are
   `https://raw.githubusercontent.com/bizflowcrm-crypto/bizflow-social/main/media/<post-id>/NN.jpg`.
   Confirm one URL returns HTTP 200 before scheduling.
7. **Schedule** each post with `createScheduledPost`: providers `[{"network":"instagram"}]`,
   `instagramData: {"type":"POST"}`, `media`: the slide URLs in order, `autoPublish: true`,
   `publicationDate: {"dateTime":"YYYY-MM-DDT10:00:00","timezone":"Asia/Calcutta"}`.
8. **Report**: write `reports/<YYYY>-w<WW>.md` (last week's numbers in 5 lines, this week's 3
   posts), commit and push, then send the owner a short summary.

## Hard rules

- Only post BizFlow's own content. No engagement bait that breaks Instagram rules,
  no follow/unfollow, no auto-commenting on other accounts.
- Never post anything about competitors by name, politics, or religion beyond warm
  festival greetings.
- If Metricool or GitHub fails, don't post half a week — report the error to the owner.
