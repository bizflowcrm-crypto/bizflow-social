# BizFlow Social Autopilot Playbook

This file is the standing instructions for the weekly scheduled task that runs
BizFlow India's Instagram. Every run starts fresh, so everything it needs is here.

## Brand facts (only claim what is listed here)

- **BizFlow India**, Sangamner, Maharashtra. Website: bizflowindia.cloud
- Business software for Indian SMEs: **GST billing, POS billing, CRM, cloud ERP,
  inventory, WhatsApp automation**, 20+ industry products.
- Industry products: **TableFlow** (restaurant/hotel POS: table billing, KOT, bar stock,
  accounts, 15+ reports), **RetailFlow** (retail POS), **AccountFlow** (GST accounting).
- Also builds **websites** for local businesses, schools, colleges and gram panchayats.
  Real customers are listed in `CUSTOMERS.md`; that is the only list of names we may use.
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
- 2026-10-02 review (18 Sep–2 Oct, 2 posts, average reach 229): only the visarjan post beat
  the average (409 reach, 790 views, 22 likes, 4 comments). The TableFlow carousel had 48 reach,
  4 likes, 0 comments. Neither post got saves, shares or follows, so graphics need a stronger
  comment hook: end with a question that can be answered in one word. No YouTube videos
  published yet (first Shorts go out 5 Oct), so no YouTube numbers to compare.
- Best posting time (Metricool): **10:00 IST Mon–Fri**, strongest Wed/Thu/Fri. 18:00 is second best.
  Weekends get about half the reach.

## Weekly procedure

Brand: Metricool `blogId` **7206028**, timezone `Asia/Calcutta`, Instagram `@bizflowindia`.

1. **Review**: pull Instagram post metrics for the last 14 days with
   `getAnalyticsDataByMetrics` (IGPO02 date, IGPO03 content, IGPO07 type, IGPO14 reach,
   IGPO13 likes, IGPO08 comments, IGPO15 saves, IGPO27 shares, IGPO28 views, IGPO29 follows).
   Add a dated line per post to "What has worked" above. Note what beat the average.
2. **Check the calendar**: `getScheduledPosts` for the **two full weeks (Mon–Sun) after today**.
   The standard slots are listed in step 3. Fill every standard slot that is empty in those
   two weeks, and leave filled slots alone. In normal running the nearer week is already full
   and you build the further one, so there is always a one-week buffer of scheduled posts.
3. **Plan each week that needs filling** (read `GROWTH.md` first: voice, rhythm, upcoming festival
   moments). Both platforms get every slot: Instagram **and** YouTube Shorts.
   - **3 carousels**, Mon/Wed/Fri at 10:00 (Instagram carousel + the same content as a vertical
     video on YouTube Shorts), one from each of three different pillars:
     pain point → solution; how-to / save-worthy tips; feature spotlight; industry product
     (TableFlow, RetailFlow, AccountFlow).
   - **2 Reels**, Tue/Thu at 18:00 (Instagram Reel + YouTube Short), funny and relatable dukandar-life humour in the
     "तुमचा दुकानातला मित्र" voice. Each must be a new idea, not a repeat of a past one
     (check `posts/` for what's been done).
   - **Festival greeting** at 09:00 on any festival day in the coming 8 days (search the
     web to confirm the date first). Single image, warm, ends with a question.
   - If `photos/` has new real photos (team, customers, events), build one post around
     them — real people outperform graphics.
   - Once a month, draft one **customer spotlight** from `CUSTOMERS.md` (a website we
     built, with screenshots). Follow the rules in that file: leave it unscheduled until
     the owner confirms the customer agreed.
   - Every caption ends with a question or a "tag a friend" line.
4. **Write the specs**: carousels and greetings in `posts/<YYYY>-w<WW>.json` (shape of
   `posts/2026-w41.json`; slide kinds `cover`, `point`, `list`, `chips`, `chat`, `cta`; 4–6
   slides, last is `cta`; `[[text]]` highlights). For real photos use the `photo` slide kind
   (`{"kind":"photo","src":"photos/<file>.jpg","title":...,"body":...}`; see
   `posts/2026-w40-team.json`, a team post that is drafted but not yet scheduled). Only use
   photos that are in `photos/`, never photos showing children, and don't reuse a photo within 4 weeks.
   The logo and blue palette live in `brand.py` and `assets/`; don't recolour or redraw the logo. Reels in `posts/<YYYY>-w<WW>-reels.json`
   (shape of `posts/2026-w41-reels.json`; scene kinds `big`, `mid`, `chat`, `cta`; 5–6 scenes,
   10–15 seconds total, last is `cta`).
5. **Render**: `pip install playwright --break-system-packages && python3 -m playwright install chromium`
   if needed, then `python3 build.py posts/<file>.json` and `python3 reel.py posts/<reels file>.json`
   (needs ffmpeg). Open 2–3 slides with Read, and extract a frame or two from each Reel with
   ffmpeg, to check Devanagari renders correctly and nothing overflows.
   In headings, a Latin word with a descender (p, y, g, q, j) on the line directly above a
   Devanagari line collides with the matras below it — write that word in Devanagari
   (पेन, पैसे) or move it to the last line.
   Specs may carry `youtube_title`, `youtube_description` and `youtube_tags` per post so the
   YouTube copy is kept in the repo next to the Instagram caption.
6. **Publish media**: commit `posts/` + `media/` and push to `main`. Base URL:
   `https://raw.githubusercontent.com/bizflowcrm-crypto/bizflow-social/main/media/<id>/`.
   `build.py` writes `NN.jpg` slides plus `short.mp4` and `cover.jpg` (the 9:16 video version)
   for every carousel; `reel.py` writes `reel.mp4` and `cover.jpg`.
7. **Schedule** with `createScheduledPost`, `autoPublish: true`,
   `publicationDate: {"dateTime":"YYYY-MM-DDTHH:MM:SS","timezone":"Asia/Calcutta"}`:
   - Carousel on Instagram: providers `[{"network":"instagram"}]`, `instagramData: {"type":"POST"}`,
     `media`: the slide JPG URLs in order.
   - The same carousel on YouTube, same date and time, as a separate post: providers
     `[{"network":"youtube"}]`, `media`: `short.mp4`, `videoThumbnailUrl`: `cover.jpg`,
     `youtubeData: {"title":"<Marathi title> | BizFlow #shorts","type":"short","privacy":"public","tags":[...],"madeForKids":false}`.
     Use a YouTube-friendly description (no "save this post"; add `🌐 bizflowindia.cloud`).
   - Reel: one post with providers `[{"network":"instagram"},{"network":"youtube"}]`, `media`:
     `reel.mp4`, `videoThumbnailUrl`: `cover.jpg`,
     `instagramData: {"type":"REEL","showReelOnFeed":true}` and `youtubeData` as above.
   - Festival greeting (single image): Instagram only.
   - **Motion-graphics promo**: `motion/bizflow-promo.html` + `motion/render.py` + `motion/audio.py`
     are a worked example of a richer animation (every style computed from time in `seek(t)`,
     rendered frame by frame with motion blur, with a synthesized soundtrack). In the first
     run of each month, make one new piece in that pattern on a fresh idea and schedule it as
     a Reel + Short on Saturday 11:00.
8. **Report**: write `reports/<YYYY>-w<WW>.md` with (a) last week's numbers in 5 lines,
   (b) this week's posts, (c) a **fresh comment kit**: 10 new witty comment lines in the
   GROWTH.md style for the owner to post by hand on other accounts this week, tied to that
   week's festivals and trends. Commit and push, then send the owner a short summary that
   includes the 10 comment lines.

## Hard rules

- Only post on BizFlow's own accounts. Never automate comments, likes, follows or DMs on
  other accounts — comment lines are written for the owner to post by hand.
- Never name a customer who isn't in `CUSTOMERS.md`, and never put passwords or logins
  in this repo.
- Never post anything about competitors by name, politics, or religion beyond warm
  festival greetings.
- If Metricool or GitHub fails, don't post half a week — report the error to the owner.
