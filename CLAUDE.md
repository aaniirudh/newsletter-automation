# CLAUDE.md — Newsletter Automation Agent

## Project Overview
This is a fully automated newsletter pipeline built with the WAT framework (Workflows, Agents, Tools). It researches a topic, generates a header image, writes a branded HTML newsletter, pauses for human subject-line approval, then sends via Gmail SMTP.

## Pipeline Steps
1. **Research** (`tools/research.py`) — Perplexity API sonar model
2. **Image Generation** (`tools/generate_image.py`) — Together.xyz FLUX model
3. **Newsletter Writing** (`tools/write_newsletter.py`) — Jinja2 + inline CSS
4. **Human Review** (`tools/human_review.py`) — Terminal prompt (BLOCKING)
5. **Send** (`tools/send_email.py`) — Gmail SMTP SSL

## Key Rules
- Human review step MUST NOT be bypassed. Pipeline halts until input received.
- All API calls use retry logic: 3 attempts with exponential backoff.
- All content is UTF-8 encoded to prevent UnicodeEncodeError.
- If any step fails after 3 retries, use fallback data and continue (except send).
- Output files go to `output/` (gitignored).

## Environment Variables (.env)
- `PERPLEXITY_API_KEY` — Perplexity API
- `IMAGE_API_KEY` — Together.xyz API
- `GMAIL_USER` — sender Gmail address
- `GMAIL_APP_PASSWORD` — 16-char Gmail app password
- `RECIPIENT_LIST` — comma-separated email addresses
- `NEWSLETTER_TOPIC` — topic string for research
- `SEND_DAY` / `SEND_TIME` — for scheduled runs

## Self-Healing Directives
- `UnicodeEncodeError` → re-encode with errors='replace'
- `ModuleNotFoundError` → pip install and retry
- API 404 → log error, try alternative endpoint, retry
- `FileNotFoundError` for output/ → create directory first
- Max 3 self-healing attempts before escalating to user

## Extending the Project
- Add new tools in `tools/` and import in `main.py`
- Brand updates go in `brand_assets/brand_guidelines.md`
- Logo replacement: overwrite `brand_assets/AIS.PNG`
