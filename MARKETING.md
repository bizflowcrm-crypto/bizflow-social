# BizFlow Marketing Plan: Instagram + YouTube, Oct–Dec 2026

The one-line strategy: **stop saying what BizFlow does, start showing who uses it.**
BizFlow has 100+ real customers within a few hours' drive of Sangamner (`CUSTOMERS.md`):
hotels and bars on TableFlow, clothing stores and super shops on RetailFlow, traders and
factories on AccountFlow, and 30+ websites. Every other software brand posts feature lists.
Only BizFlow can post "Hotel Tarang, Sangamner runs on this". The numbers back it: the post
with real local people reached 409, the product graphic reached 48.

`PLAYBOOK.md` stays the weekly routine and `GROWTH.md` the voice. This file says **what**
to post over the next three months, and what the owner needs to do for it.

## 1. Before anything else (owner, this week)

1. **Confirm the headline claim.** Can we say "100+ businesses use BizFlow"? The sheets list
   ~100 named customers, but many renewal dates are from 2021–2024. If yes, add it to the brand
   facts in `PLAYBOOK.md`. If not, give the number you're comfortable with.
2. **Get permission from 10 customers** using the WhatsApp message in section 7. Start with
   the ones you know best and whose shop looks good: Hotel Tarang, Hira Hotel, Patel Tiles,
   Style Mantra, Jagdamba Super Market, Kaka Super Shop, Ujwala Cotton King, Omkar Solar,
   Shyam Oils, Dr. Deshmukh's Ayurved. Note who said yes in `CUSTOMERS.md`.
3. **Shoot on every support visit** (section 6). Ten minutes per shop.
4. **Open the network for this repo's environment** so the autopilot can screenshot the
   websites with `python3 shots.py` (the customer sites are currently blocked here), or run it
   on any laptop and put the images in `photos/sites/`.

### About customer images

We use **only** images we made ourselves, or that the customer gave us and agreed we can use:
- Photos and clips the team shoots at the shop, with the owner's OK.
- Screenshots of websites BizFlow built (`shots.py`). This is our own work, but still ask
  before naming the customer in a post.
- Photos the customer sends us on WhatsApp for this purpose.

We **don't** take shop photos from Google Maps, Justdial, Facebook or the customer's site
without asking. Those belong to whoever took them, and a customer who finds their photo in
our ad without being asked is a customer we lose.

## 2. Content pillars (what every post is about)

| Pillar | Share | Format | Example |
|---|---|---|---|
| **Our customers** (proof) | 30% | Collab carousel, shop Reel, YouTube case study | "Hotel Tarang मध्ये KOT कसा निघतो" |
| **Dukandar humour** (reach) | 30% | Reel + Short | Existing Tue/Thu Reels |
| **How-to / save-worthy** (saves) | 20% | Carousel + Short, YouTube tutorial | "Diwali stock मोजायची 5-minute पद्धत" |
| **Product** (conversion) | 15% | Carousel, screen-recording Short | RetailFlow barcode billing in 20 seconds |
| **Festivals / local** (community) | 5% | Greeting, local event | Dussehra, Diwali, Sangamner events |

## 3. Signature series

These repeat with the same look and name, so people recognise them and come back.

1. **"BizFlow वापरणारे" (Customer of the Week)**, Fridays 10:00. One customer, 5 slides:
   their shop photo → what they sell and where → which BizFlow product → one line from the
   owner (their words, never ours) → CTA. Published as an **Instagram Collab** with the customer
   so it lands on their followers' feed too. YouTube: a 30–45s Short of the shop with the
   owner speaking. Replaces the Friday product carousel whenever a customer has said yes.
2. **"आम्ही बनवलेली website" (Website Wednesday)**, every other Wednesday. Phone + desktop
   screenshots of a site we built, a scroll-through video for Shorts. Start with Shyam Oils,
   Vishwagandha Ayurved, Agri Expert India, Vishwa Hi-Tech Nursery, Akshay Urja. Ends with
   "तुमच्या business ची website? 📞 8888567870".
3. **"गावागावात BizFlow" (town map)**, once a month. A map slide of the towns we serve:
   Sangamner, Kopargaon, Akole, Loni, Rahuri, Rahata, Satana, Sinnar, Alephata, Ghargaon,
   Vadgaon Pan, Nimgaon Sawa, Narayangaon, Pune, Bhosari, Chakan, Panvel, Raigad, Mumbai.
   Caption asks "तुमचं गाव यादीत आहे का?" so people tag their town. Pure comment bait, all true.
4. **Industry weeks**, one week each month themed on one product, so all five posts that week
   speak to one audience:
   - **Hotel week (TableFlow)**: KOT, table billing, bar stock, the 1am closing hisab.
   - **Shop week (RetailFlow)**: barcode billing, festival rush queue, size/colour stock.
   - **Trader week (AccountFlow)**: GST return month-end, ledger, outstanding.

## 4. YouTube: more than Shorts

Shorts are already automated. Add **one long video every week** in Marathi (8–12 min),
because long videos are what people find by searching, and searchers are buyers.

**Tutorials** (screen recording + voice, no editing skill needed):
1. TableFlow मध्ये पहिलं बिल कसं बनवायचं (hotel/restaurant)
2. KOT आणि table transfer, TableFlow मध्ये
3. Bar stock आणि peg calculation (TableFlow)
4. RetailFlow: barcode print करून billing सुरू करा
5. RetailFlow: size आणि colour नुसार stock
6. AccountFlow: GST return साठी data कसा तयार करायचा
7. उधारी आणि payment reminder WhatsApp वर
8. रोजचा हिशोब 5 मिनिटांत बंद करा (day-end report)

**Customer case studies** (3–5 min), once a month: visit a customer who agreed, show the shop,
the counter, the billing in action, owner talks for one minute. "Hotel X ने वही का सोडली?"

**Channel setup**: playlists per product (TableFlow, RetailFlow, AccountFlow, Websites,
Customer Stories, Shorts). Titles in Marathi with the English search words: "TableFlow
Restaurant Billing Software in Marathi | KOT, Table Billing". Pin a comment with
📞 8888567870 on every video. Channel trailer: the motion promo.

The autopilot writes the script, title, description and tags for each long video in
`posts/<YYYY>-w<WW>-youtube.json`. Someone at BizFlow records it.

## 5. Instagram beyond the feed

- **Highlights**: TableFlow, RetailFlow, AccountFlow, Websites, Customers, Demo. Each one
  holds 5–10 stories, so a new visitor can see "who uses this" in 30 seconds.
- **Stories daily**: repost every customer collab, a poll ("वही की app?"), a behind-the-scenes
  clip from a support visit.
- **Bio**: "Billing, GST आणि hotel software | 100+ दुकानदार आमच्यासोबत | Free demo 👇", link,
  WhatsApp button. (Number only once confirmed.)
- **Collabs**: every customer spotlight is a Collab post. Plus 1–2 Sangamner creators a month
  (what produced the best post so far).
- **Tag the town**: location tag on every post (the customer's town for spotlights,
  Sangamner otherwise).

## 6. Shoot list for support visits

Whoever visits a customer, after the work is done and the owner agrees:
1. Wide shot of the shop front with the name board (5s, horizontal and vertical).
2. The counter with BizFlow on screen (5s).
3. A real bill being made, hands only (10s).
4. The printed bill or WhatsApp bill on the phone (5s).
5. Owner, one sentence, looking at the camera, in their own words: what changed since BizFlow.
6. 3 photos: front, counter, owner + BizFlow team member.

Phone vertical, daylight, no customers' faces without asking, **no children, no alcohol
bottles in frame at bars**. Drop files in `photos/customers/<shop-name>/`. The autopilot
builds the spotlight post and Short from them.

## 7. Asking customers (WhatsApp templates)

**Permission**
> नमस्कार {नाव} जी 🙏 BizFlow कडून {आपलं नाव}. आम्ही Instagram आणि YouTube वर आमच्या
> customers ची ओळख करून देतोय: "BizFlow वापरणारे". तुमच्या {दुकानाचं नाव} चे 2–3 फोटो
> आणि तुमचं एक वाक्य टाकायला आवडेल. तुमच्या दुकानाची free जाहिरात होईल, आणि post तुमच्या
> account वर पण दिसेल. चालेल का?

**Renewal + feature** (for customers whose renewal lapsed)
> नमस्कार {नाव} जी 🙏 {दुकानाचं नाव} चं BizFlow renewal बाकी आहे. या महिन्यात renew केलं तर
> आमच्या Instagram/YouTube वर तुमच्या दुकानाची ओळख free करून देऊ. Call: 8888567870

Any discount or offer in these messages is the owner's call. The autopilot never invents one.

## 8. Three-month calendar

Normal weekly rhythm stays (`GROWTH.md` section 2). On top of it:

| Week | Theme | Extra |
|---|---|---|
| 19–25 Oct | **Shop week** (RetailFlow) + Dussehra 20 Oct | "जुनी वही दहन करा" Dussehra post; first Website Wednesday |
| 26 Oct–1 Nov | **Diwali rush, shops** | Customer of the Week #1; "गर्दीत billing queue" Reel; YouTube: RetailFlow barcode tutorial |
| 2–8 Nov | **Diwali** | Dhanteras 6 Nov "नवी वही = नवं software"; Lakshmi Pujan 8 Nov greeting; Nov motion promo on Sat 7 Nov |
| 9–15 Nov | **Padwa 10 Nov / new business year** | Bhaubeej; town map #1; YouTube: day-end report |
| 16–22 Nov | **Hotel week** (TableFlow) | Wedding-season rush for hotels; Customer of the Week (a hotel) |
| 23–29 Nov | **Websites** | Website Wednesday ×2; "तुमच्या दुकानाची website ₹?" (price only if owner gives one) |
| 30 Nov–6 Dec | **Trader week** (AccountFlow) | GST month-end; Dec motion promo Sat 5 Dec |
| 7–13 Dec | **Customer stories** | First YouTube case study (3–5 min) |
| 14–20 Dec | **Shop week** | Year-end stock count how-to |
| 21–27 Dec | **Year in review** | "2026 मध्ये BizFlow वापरणारे" collage of every customer who said yes; Christmas |
| 28 Dec–3 Jan | **New year** | "2027 चा संकल्प: वही बंद"; Jan motion promo |

Festival dates are from `GROWTH.md`; confirm each one the week before, as the playbook says.

## 9. Paid boost (optional, owner decides the budget)

Once a customer spotlight or Reel does well organically (above-average reach after 48h), boost
it for 5–7 days to business owners aged 25–55 within 40 km of Sangamner, Kopargaon and
Akole, goal "messages" to WhatsApp. Start small (a few hundred rupees a day) and only scale
what brings demo calls. Never boost a post naming a customer without telling them.

## 10. What to measure

Weekly (in `reports/`): reach and views per post, saves, shares, follows, profile visits,
and **demo calls/WhatsApps that mention Instagram or YouTube**. Ask every caller "आम्हाला
कुठे पाहिलं?" and note it.
Monthly: followers on both platforms, YouTube watch hours and search traffic, which series
won. A series that loses three months running gets dropped.

## 11. Who does what

| Owner / team | Autopilot (weekly run) |
|---|---|
| Ask customers, note consent in `CUSTOMERS.md` | Builds spotlight posts from `photos/customers/` |
| Shoot on support visits | Writes long-video scripts and YouTube copy |
| Record long YouTube videos | Builds and schedules the feed, Reels and Shorts |
| Post comments by hand (GROWTH.md §3) | Writes the weekly comment kit and report |
| Decide offers, ad budget, headline numbers | Never invents a number, quote or offer |
