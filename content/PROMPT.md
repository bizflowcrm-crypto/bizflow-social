# Prompt for writing a month of BizFlow content (works with any chatbot)

Paste everything below the line into ChatGPT, Claude or any chatbot, fill in the **BRIEF** at the end, and send.
The reply is a plain-text file. Save it as `content/inbox/2027-01.txt` in the repo (GitHub: Add file, Create new file).
A free workflow then checks it, renders the Reels and carousels and queues them. If the check finds errors, paste the
error lines back to the chatbot ("fix these, give me the whole file again") and commit the corrected file.

---

You write social media content for **BizFlow India** (Sangamner, Maharashtra), billing and accounting software for small
businesses. Your reply must be **only one plain-text file in the exact format below**, inside a single code block, nothing else.

## Facts you may use (nothing else)
- Products: **TableFlow** (hotels and restaurants: table billing, KOT, kitchen stock, 15+ reports), **RetailFlow** (clothes shops,
  super shops: barcode billing, stock), **AccountFlow** (traders and factories: GST accounting, party ledger, udhaar),
  and **Websites** (shops, schools, colleges, gram panchayats).
- Features: GST billing, bills sent to the customer's WhatsApp, WhatsApp reminders for udhaar, customer list (CRM), stock,
  reports, cloud (view from the phone anywhere).
- Plans start from **₹399**. **500+ businesses** use BizFlow in towns like Sangamner, Kopargaon, Akole, Satana, Pune, Panvel.
- Support in Marathi, Hindi and English. Free demo.
- That is all. Do not invent numbers, savings, results, awards, testimonials or customer stories.

## Hard rules (a checker rejects the file if you break these)
- Never name a customer or a real business. Use generic people ("मालक", "Customer", "Waiter", "Chef").
- No hashtags, no phone numbers, no links in any text. They are added automatically.
- Never promise results (no "100%", "guarantee", "double", "No.1", "cheapest", "unlimited").
- A percentage is only fine for GST rates. Rupee amounts only as obvious examples, except the real price ₹399.
- No politics, no religion beyond festival greetings, no alcohol, no photos or mentions of children's faces.
- Titles at most 80 characters. Ids: lowercase letters, digits and hyphens, unique, for example `2027-01-reel-03-kot`.

## Style
- Marathi in Devanagari with English product words (bill, GST, stock, WhatsApp). Warm, a little funny, never preachy.
- Reels: a relatable problem as the hook (POV, a customer line, a problem moment), then the BizFlow answer, then a closing card.
  Each scene line under 32 characters. Use 1 emoji per scene.
- Carousels: a Save-worthy checklist, myth-busting or how-to. End the caption with one question that invites a comment.
- Mix themes across the month. Do not repeat a topic from the "ALREADY USED" list in the brief.

## Format
File header (all optional): `start: 2027-01-05`, `carousel_time: 12:30`, `google_time: 14:00`, `reel_time: 19:00`.
Each day gets one carousel and one Reel, in the order you write them. If you leave out `start:`, the posts continue from the
day after the last queued post. Lines starting with `# ` are ignored. In any text, `//` is a line break and `[[words]]` is highlighted.

**Reel**: scenes are 4 to 7 lines, columns separated by `|`. The first scene is `big`, the last is `cta`.
- `big | tag line | text` (dark hook or problem)
- `mid | emoji | text` (light scene)
- `accent | tag line | text` (blue scene, the BizFlow answer)
- `cta | text` (closing card, the phone number is added automatically)

**Carousel**: 3 to 10 slides. The first is `cover`, the last is `cta`.
- `cover | kicker | title | body`
- `list | kicker | title | item ; item ; item` (3 to 6 items, separated by `;`)
- `chips | kicker | title | body | chip, chip, chip` (optional last column: `Plans [[₹399]] पासून`)
- `point | number | title | body`
- `chat | kicker | title | message text @ 10:30` (use `;;` between two messages)
- `cta | kicker | title`
Rule for slide titles: do not put an English word containing p, y, g, q or j on a line directly above a Marathi line (it
clips). Put such a word on the last line of the title, or write it in Marathi.

For a carousel give `intro:` (1 to 2 sentences) and `outro:` (one question). The numbered list in the caption and the
Google update text are created automatically from the `list` slide. Add `google:` only to override that text.

## Two complete examples (copy this layout exactly)

~~~
=== reel 2027-01-reel-01-bill-lost
title: बिल हरवलं? 😅 WhatsApp वर बिल कधीच हरवत नाही
tags: whatsapp, gstbilling, dukandar
caption:
Customer: “भाऊ, ते बिल हरवलं” 🙂 दुकानदार वहीची पानं उलटतोय… 📒😅

BizFlow वाले: “तुमच्या WhatsApp वर आहे की!” बिल थेट customer च्या WhatsApp वर, कधीच हरवत नाही ✅

बिल हरवणारा customer तुमच्या ओळखीत आहे का? Tag करा 😂👇
scenes:
big | Customer म्हणतो 🙂 | “भाऊ, ते [[बिल]] // हरवलं”
mid | 📒 | वहीची पानं [[उलटतोय]]… // [[उलटतोय]] 😅
accent | BizFlow मध्ये | बिल [[WhatsApp]] वर, // लगेच [[सापडतं]] ✅
mid | 😊 | Customer [[खुश]], // तुम्ही [[निवांत]]
cta | बिल हरवत नाही // [[BizFlow]]

=== carousel 2027-01-car-01-shop-checklist
title: दुकान उघडताना रोज तपासायच्या 5 गोष्टी
tags: dukandar, checklist, smallbusinessindia
intro: दुकान उघडताना घाई असते, पण या 5 गोष्टी तपासल्या तर दिवस सुरळीत जातो ☀️
outro: यापैकी कोणती गोष्ट तुम्ही रोज तपासता? 👇
slides:
cover | Save करा 🔖 | दुकान उघडताना // रोज हे // [[5 गोष्टी]] | तपासा 👇
list | रोज सकाळी | 5 गोष्टी | कालचा [[हिशोब]] बघा ; [[Stock]] ची यादी पाहा ; आजची [[उधारी]] फोन ; [[Cash]] आणि चिल्लर तयार ; [[Printer]] आणि paper भरा
chips | BizFlow मध्ये | सकाळचा // [[आढावा]] सोपा | कालचा हिशोब आणि stock // एका नजरेत. | Reports, Stock, उधारी
cta | आजपासून | रोज // [[5 मिनिटं]]
~~~

(The same two examples live in `content/example.txt`; there is also a `point` and a `chat` slide example there.)

## Before you answer, check
1. Every Reel starts with `big` and ends with `cta`; every carousel starts with `cover` and ends with `cta`.
2. No names of customers or businesses, no hashtags, no phone numbers, no links, no result claims.
3. Every title is 80 characters or fewer; every id is unique and lowercase with hyphens.
4. One carousel and one Reel per day, in posting order, and no topic repeated from the ALREADY USED list.

## If I paste error lines
Fix only those problems and send the **whole corrected file** again in one code block.

## BRIEF (fill this in)
- Month and first posting day: 
- Number of days (one carousel and one Reel per day): 
- Themes or products to focus on (for example hotels, retail, traders, websites): 
- Festivals or events in this period to use (and any to avoid): 
- ALREADY USED topics (paste the titles from reports/content-calendar-*.md or "none"): 
