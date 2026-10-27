# Monthly content, with any chatbot and no API

AI only has to write text. Everything after that is free scripts on GitHub's own machines.

## The monthly routine (about 20 minutes of your time)
1. Open ChatGPT, Claude or any chatbot. Paste `content/PROMPT.md` (everything under the line), fill in the BRIEF, send.
2. On GitHub: **Add file > Create new file**, name it `content/inbox/2027-01.txt`, paste the chatbot's reply, **Commit**.
3. Open the **Actions** tab, the run "Make content from a file":
   - Red with error lines? Paste them back to the chatbot ("fix these, give me the whole file again") and commit the corrected
     file over the old one. Errors carry line numbers.
   - Green: the Reels and carousels were rendered (1 to 3 hours for a month, you do not need to watch), added to
     `publisher/queue.json` and the file moved to `content/done/`. The daily health check and the publisher take it from there.

## What is checked automatically
Format and column counts; unique ids; title length; no hashtags, phone numbers or links in text; no customer names (the list
comes from `CUSTOMERS.md`, so a named customer is rejected until they agree); no promise-style claims ("100%", "guarantee");
Marathi headings that would clip; then after rendering, that every slide and Reel exists, durations are 8 to 25 seconds and the
middle frame is not blank. Warnings (long lines, rupee amounts, percentages) do not stop the run.

## Pieces
- `content/PROMPT.md`: the prompt to give a chatbot. `content/example.txt`: a complete sample file.
- `content/inbox_lib.py` and `content/process_inbox.py`: parse, check, render, queue (`--stage check|prepare|queue`).
- `.github/workflows/content.yml`: runs it when a file lands in `content/inbox/`. Manual run options: `check-only`,
  `render-test` (renders to a throwaway branch `content-test`, queues nothing).
- `content/lib.py`: the shared helpers; `content/nov_dec_*.py` is the Python version used for the first two months.

## Keeping the repository small (storage)
Media is committed to git, and git keeps history, so deleting files later does not shrink the repository. What helps:
- New Reels are encoded at a higher compression (about half the size), and carousel YouTube Shorts are no longer made
  unless `MAKE_SHORTS=1` (turn it on only when YouTube posting is approved).
- The recycler re-uses the evergreen posts, so you do not need new media every month.
- The daily health check warns when the repository passes 1.5 GB. If that ever happens, the fix is to keep media on a separate
  branch that is rewritten each month (ask Claude to set it up), not to delete files.

## Several accounts
Add `account: pos` as the first header line of the content file to queue it for another account listed in
`publisher/accounts.json` (without it, the main account is used). Each account has its own posting calendar. Use a separate
chatbot prompt per account (copy PROMPT.md and change the brand facts and voice). Setup: publisher/SETUP.md, 'More accounts'.
