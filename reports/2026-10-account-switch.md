# Metricool account switch (after 10 Oct 2026)

The current Metricool account (brand `bizflowindia`, blogId 7206028) is on the **free plan:
20 published posts a month**, counted on publish, reset on the 1st. October already had ~12
published by 4 Oct, so on 4 Oct the schedule was cut to fit, and the owner moves to a new
Metricool account after 10 Oct.

## Still live in the old account (5–10 Oct)

| When (IST) | Post | Networks |
|---|---|---|
| Mon 5 10:00 | 3 signs you've outgrown the notebook (carousel) | Instagram |
| Mon 5 11:00 | Same, as an update | Google Business Profile |
| Mon 5 18:00 | Reel: "भाऊ, हे आहे का?" (`2026-10-05-reel-stock-search`) | Instagram + YouTube |
| Tue 6 18:00 | Reel: udhaar (`2026-10-06-reel-udhaar`) | Instagram + YouTube |
| Wed 7 13:30 | Barcode billing benefits (carousel) | Instagram |
| Thu 8 18:00 | Reel: 3 types of shopkeeper | Instagram + YouTube |
| Fri 9 10:00 | WhatsApp automation (carousel) | Instagram |
| Sat 10 11:00 | Motion promo Reel | Instagram + YouTube |

## Moved to drafts (42 posts, 5–16 Oct), ready for the new account

Everything is in the repo; nothing needs re-making. Media URLs:
`https://raw.githubusercontent.com/bizflowcrm-crypto/bizflow-social/<branch>/media/<id>/`.

- Carousels (`posts/2026-w41-extra.json`, `posts/2026-w41.json`, `posts/2026-w42.json`):
  GST invoice checklist, hotel daily numbers, GST bill 4 steps, udhaar tips, why a website,
  new-shop checklist, वही vs BizFlow, customers come back, Diwali prep, RetailFlow.
- Reels (`posts/2026-w41-extra-reels.json`, `posts/2026-w42-reels.json`): CA month-end,
  बिल हरवलं, festival rush, hotel bestseller, notebook soaked, Navratri, UPI suspense, galla tally.
- YouTube Shorts versions of every carousel (`media/<id>/short.mp4`).
- Google Business Profile updates (text in `gbp_text` in the specs; no phone numbers/hashtags).
- Navratri greeting 11 Oct (`posts/2026-w41-festival.json`).

## Status on 9 Oct

All 7 live posts from 5–9 Oct published; none failed. October has used about 19 of 20 free
posts (a post to Instagram + YouTube appears to count once). The 10 Oct 11:00 promo is the 20th.

## Switching the connector (owner)

1. Create the new Metricool account and brand; connect Instagram @bizflowindia, YouTube
   **bizflowcrm** and Google Business Profile in it.
2. At claude.ai/customize/connectors, disconnect Metricool and connect it again, signing in
   with the new Metricool account.
3. Start a new Claude session (connectors are read when a session starts) and ask it to
   reschedule the drafted posts from 11 Oct.

## In the new account

1. Connect Instagram @bizflowindia, YouTube **bizflowcrm** (not BizFlow POS), Google Business Profile.
2. Disconnect them from the old account first (or delete the old drafts) so nothing doubles.
3. Tell Claude the new brand: it reads `getBrandSettings`, updates the blogId in `PLAYBOOK.md`, and
   reschedules the drafted posts from 11 Oct, within whatever limit the new plan has.
4. If the new account is free too (20/month), plan per month: e.g. 8 Reels (Instagram + YouTube),
   8 carousels (Instagram), 4 Google updates. Ask Metricool whether a post going to two networks
   counts as one or two.
