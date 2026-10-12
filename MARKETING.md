# BizFlow Marketing Plan: Instagram + YouTube, Oct–Dec 2026

The one-line strategy: **stop saying what BizFlow does, start showing who uses it.**
BizFlow has 500+ real customers within a few hours' drive of Sangamner (`CUSTOMERS.md`):
hotels and bars on TableFlow, clothing stores and super shops on RetailFlow, traders and
factories on AccountFlow, and 30+ websites. Every other software brand posts feature lists.
Only BizFlow can post "Hotel Tarang, Sangamner runs on this". The numbers back it: the post
with real local people reached 409, the product graphic reached 48.

`PLAYBOOK.md` stays the weekly routine and `GROWTH.md` the voice. This file says **what**
to post over the next three months, and what the owner needs to do for it.

## 1. Before anything else (owner, this week)

1. ~~Confirm the headline claim.~~ Done: **500+ businesses** (owner, 2 Oct). It's in the brand
   facts. Launch post Sun 4 Oct (`posts/2026-w40-launch.json`).
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

### Customer bites (from Mon 5 Oct)

Film each customer the way section 6 describes, keep the raw clip (don't edit it), and drop it
in `photos/customers/<shop-name>/` with a note of who it is and that they agreed. The weekly
run turns it into a branded Reel + Short with `bite.py`: intro card with the customer's own
line, their clip with name strip and Marathi subtitles, CTA card. Best clips: 20–60 seconds,
vertical, phone held still, owner looking slightly off-camera, the counter or the screen in
the background, quiet spot (fan off, music off).

Good questions to ask on camera (let them answer in their own words):
1. BizFlow च्या आधी हिशोब/billing कसं करायचा?
2. सगळ्यात जास्त कुठे फरक पडला?
3. एखादा दिवस आठवतो का, जेव्हा BizFlow मुळे काम सोपं झालं?
4. दुसऱ्या दुकानदाराला काय सांगाल?

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

## 4. YouTube growth (channel: bizflowcrm, connected 4 Oct)

Goal by end of December: **1,000 subscribers** and **4,000 watch hours**. That's the bar for
YouTube's partner programme, and it means the channel is showing up in search. Shorts bring
subscribers; long videos bring watch hours and buyers, because people who search
"restaurant billing software Marathi" are about to buy.

**Every week (automatic):** 5 Shorts, one from each Instagram carousel and Reel. Reels are
motion-graphics videos with sound (`motion/reels.py`).

**Every week (someone at BizFlow records, the autopilot writes the script):** one long video
in Marathi, 8–12 minutes, screen recording plus voice. Script, title, description, chapters
and tags go in `posts/<YYYY>-w<WW>-youtube.json`. Start with these, in this order:
1. TableFlow मध्ये पहिलं बिल कसं बनवायचं (hotel/restaurant)
2. RetailFlow: barcode print करून billing सुरू करा
3. GST बिल 2 मिनिटांत: AccountFlow
4. KOT आणि table transfer, TableFlow मध्ये
5. उधारी आणि payment reminder WhatsApp वर
6. रोजचा हिशोब 5 मिनिटांत बंद करा (day-end report)
7. RetailFlow: size आणि colour नुसार stock
8. Bar stock आणि peg calculation (TableFlow)

**Monthly:** one customer story (3–5 min) from the customer bites, once customers agree.

**Search wording.** Titles start with what people type, then the Marathi: "Restaurant
Billing Software in Marathi | TableFlow KOT आणि Table Billing". Descriptions: first two lines
say what the video solves and give 📞 8888567870, then chapters (00:00 …), then
bizflowindia.cloud. Tags: product name, "billing software", "GST billing", "Marathi", town names.

**Channel setup (owner, once, in YouTube Studio):**
- Name **BizFlow India**, handle @bizflowcrm, banner and logo from `assets/`.
- About: "Billing, GST आणि business software: TableFlow, RetailFlow, AccountFlow. 500+
  व्यवसाय, Sangamner." Links: website, WhatsApp, Instagram.
- Playlists: TableFlow, RetailFlow, AccountFlow, WhatsApp automation, Customer stories, Shorts.
- Channel trailer for new visitors: the motion promo (`motion/bizflow-promo.mp4`).
- Default upload settings: language Marathi, category Science & Technology, description footer
  with the phone number and website.
- On every long video: end screen (subscribe + next tutorial) and a pinned comment
  "Free demo: 📞 8888567870".
- Reply to every comment within a day. Comments are the strongest signal YouTube reads.

**Clean-up:** three Shorts went to the BizFlow POS channel on 3–4 Oct before the switch.
They're re-posted on bizflowcrm (4–5 Oct). Delete or keep them on BizFlow POS, the owner's choice.

## 4b. Google Business Profile growth (connected 4 Oct)

Goal: show up in the **top 3 on Google Maps** for "billing software Sangamner", "GST software
near me", "hotel billing software" and "POS software" in Sangamner, Kopargaon, Akole, Rahuri
and Sinnar. That ranking comes from three things: a complete profile, steady activity and
reviews.

**Reviews: the biggest lever, and 500+ customers is a huge head start.**
- Get the review link: Google Business Profile → "Ask for reviews" → copy link.
- Send it to existing customers on WhatsApp, 10–15 a day (not all at once, Google flags
  bursts). Message:
  > नमस्कार {नाव} जी 🙏 BizFlow वापरल्याबद्दल धन्यवाद. तुमचा अनुभव Google वर 1 मिनिटात
  > लिहाल का? इतर दुकानदारांना खूप मदत होईल: {review link}
- Never offer a discount or gift for a review (Google removes them and can suspend the profile).
- Reply to every review within 24 hours, by name, in the language they wrote in.
- Target: 50 reviews by end of October, 150 by December.

**Complete the profile (owner, once):**
- Primary category **Software company**; extra categories: *Computer support and services*,
  *Website designer*, *Point of sale equipment supplier*.
- Description (750 chars) with the words people search: GST billing software, POS, restaurant
  billing, retail billing, accounting software, website development, Sangamner, Maharashtra.
- **Products**: TableFlow, RetailFlow, AccountFlow, Websites, each with a photo, a line and
  "₹399 पासून" where it applies. **Services**: GST billing setup, POS installation, training,
  website development, WhatsApp automation.
- Hours, phone, website, WhatsApp chat, "Service areas": Sangamner, Kopargaon, Akole, Rahuri,
  Rahata, Sinnar, Loni, Ahilyanagar, Nashik, Pune.
- Q&A: add 5 real questions with answers (price, Marathi support, offline billing, training,
  barcode printer).

**Posting (automatic, Metricool network `gmb`):**
- An update with every carousel (Mon/Wed/Fri 11:00), cover slide as the image. Rules: **no
  phone numbers and no hashtags in the text** (Google rejects those posts; the profile's call
  button does the job), end with "Free demo साठी call करा किंवा bizflowindia.cloud ला भेट द्या".
- Photos to the gallery every week: team, office, and (once customers agree) customer shops.
  Profiles with fresh photos get more calls and direction requests.
- Festival greetings as updates too.

**Measure monthly** (Google Business Profile → Performance): searches, calls, website clicks,
direction requests, reviews count and average.

## 5. Instagram beyond the feed

- **Highlights**: TableFlow, RetailFlow, AccountFlow, Websites, Customers, Demo. Each one
  holds 5–10 stories, so a new visitor can see "who uses this" in 30 seconds.
- **Stories daily**: repost every customer collab, a poll ("वही की app?"), a behind-the-scenes
  clip from a support visit.
- **Bio**: "Billing, GST आणि hotel software | 500+ व्यवसाय आमच्यासोबत | Free demo 👇", link,
  WhatsApp button. Highlight covers are ready in `media/highlights/`.
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
