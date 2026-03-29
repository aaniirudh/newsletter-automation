# Newsletter Automation Agent

An agentic newsletter pipeline that researches a topic, generates a header image, writes a fully branded HTML email, pauses for your approval, and sends via Gmail — all from one command.

---

## How It Works

```
python3 main.py
```

1. **Research** — Gemini AI researches your topic and pulls the latest stories
2. **Image Generation** — Gemini Imagen generates a branded header image
3. **Write Newsletter** — Builds a fully formatted HTML email with brand styling
4. **Human Approval** — Pauses and asks you to pick a subject line
5. **Send** — Delivers via Gmail SMTP to your recipient list

---

## Setup

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd newsletter-automation
```

### 2. Install dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Configure your environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

| Variable | How to get it |
|----------|--------------|
| `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com) → Get API key |
| `GMAIL_USER` | Your Gmail address (e.g. `you@gmail.com`) |
| `GMAIL_APP_PASSWORD` | Google Account → Security → 2-Step Verification → App passwords → Create |
| `RECIPIENT_LIST` | Comma-separated emails to send to |
| `NEWSLETTER_TOPIC` | The topic you want researched each run |

### 4. (Optional) Replace the logo

Drop your logo file at:
```
brand_assets/AIS.PNG
```

### 5. Run

```bash
python3 main.py
```

When prompted, type `1`, `2`, `3` to pick a subject line — or `C` to enter your own. The email sends immediately after.

---

## File Structure

```
newsletter-automation/
├── main.py                    # Pipeline orchestrator — run this
├── requirements.txt
├── .env                       # Your credentials (never commit this)
├── .env.example               # Template for .env
├── tools/
│   ├── research.py            # Gemini AI research
│   ├── generate_image.py      # Gemini Imagen header image
│   ├── write_newsletter.py    # HTML email builder
│   ├── human_review.py        # Subject line approval prompt
│   └── send_email.py          # Gmail SMTP sender
├── brand_assets/
│   ├── brand_guidelines.md    # Colors, fonts, tone
│   └── AIS.PNG                # Logo (replace with yours)
└── output/                    # Generated files (gitignored)
    ├── research_raw.json
    ├── header_image.png
    ├── newsletter_draft.html
    └── subject_lines.txt
```

---

## Customisation

**Change the topic** — edit `NEWSLETTER_TOPIC` in `.env`

**Change brand colors/tone** — edit `brand_assets/brand_guidelines.md`

**Send to multiple people** — add comma-separated emails to `RECIPIENT_LIST` in `.env`:
```
RECIPIENT_LIST=alice@example.com,bob@example.com,carol@example.com
```

**Preview the newsletter** — open `output/newsletter_draft.html` in any browser after running

---

## Requirements

- Python 3.10+
- A Google AI Studio API key (free tier works for research; Imagen requires paid)
- A Gmail account with 2-Step Verification and an App Password

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `535 Username and Password not accepted` | Gmail App Password is wrong — regenerate it at myaccount.google.com/apppasswords |
| `Research failed: 404` | Your Gemini API key may not have access to that model — check aistudio.google.com |
| `Image generation failed` | Imagen 3 requires a paid Google AI Studio plan — the pipeline uses a placeholder and continues |
| Email shows broken images | Expected — Gmail blocks embedded images. The CSS banner displays instead |
