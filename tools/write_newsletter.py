import os
import base64
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def _b64_image(path: str, max_width: int = 640, quality: int = 60) -> tuple:
    """Returns (base64_string, mime_type). Resizes and compresses to keep email small."""
    try:
        from PIL import Image
        from io import BytesIO
        img = Image.open(path).convert("RGB")
        if img.width > max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        return base64.b64encode(buf.getvalue()).decode("utf-8"), "image/jpeg"
    except Exception:
        return "", "image/png"

def _generate_subject_lines(topic: str, research: dict) -> list:
    title = research.get("main_story", {}).get("title", topic)
    short_title = title[:52] + "..." if len(title) > 55 else title
    return [
        f"This Week in {topic[:40]}: What You Need to Know",
        f"Breaking: {short_title}",
        f"Your {topic[:35]} Briefing — {datetime.now().strftime('%b %d')}"
    ]

def _secondary_story_html(story: dict) -> str:
    title = story.get("title", "")
    summary = story.get("summary", "")
    source = story.get("source", "")
    source_html = (
        f'<a href="{source}" style="display:inline-block;margin-top:6px;font-size:12px;'
        f'color:#E94560;text-decoration:none;">Read more →</a>'
        if source else ""
    )
    return f"""
      <tr>
        <td style="padding:20px 0;border-bottom:1px solid #EBEBEB;">
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td style="width:4px;background-color:#E94560;border-radius:2px;">&nbsp;</td>
              <td style="padding-left:16px;">
                <p style="margin:0 0 6px 0;font-size:15px;font-weight:bold;color:#1A1A2E;font-family:Arial,sans-serif;line-height:1.4;">{title}</p>
                <p style="margin:0;font-size:14px;color:#555555;font-family:Arial,sans-serif;line-height:1.6;">{summary}</p>
                {source_html}
              </td>
            </tr>
          </table>
        </td>
      </tr>"""

def write_newsletter(research: dict, image_path: str, topic: str) -> str:
    os.makedirs("output", exist_ok=True)

    logo_b64, logo_mime = _b64_image("brand_assets/AIS.PNG", max_width=320, quality=80)
    header_b64, header_mime = _b64_image(image_path, max_width=640, quality=55)

    subject_lines = _generate_subject_lines(topic, research)
    with open("output/subject_lines.txt", "w", encoding="utf-8") as f:
        for i, sl in enumerate(subject_lines, 1):
            f.write(f"{i}. {sl}\n")

    main_story = research.get("main_story", {})
    secondary_stories = research.get("secondary_stories", [])
    takeaway = research.get("takeaway", "Stay informed and keep learning.")
    issue_date = datetime.now().strftime("%B %d, %Y")
    main_source = main_story.get("source", "")

    secondary_html = "".join(_secondary_story_html(s) for s in secondary_stories)

    # Gmail blocks data: URIs — use CSS-only logo and header banner
    logo_tag = (
        '<table cellpadding="0" cellspacing="0" style="margin:0 auto;">'
        '<tr><td style="background-color:#E94560;padding:8px 20px;border-radius:4px;">'
        '<span style="color:#ffffff;font-family:Arial,sans-serif;font-size:22px;'
        'font-weight:bold;letter-spacing:4px;">AIS</span>'
        '</td></tr></table>'
    )
    header_img = (
        '<table width="100%" cellpadding="0" cellspacing="0">'
        '<tr>'
        '<td style="background:linear-gradient(135deg,#1A1A2E 0%,#E94560 100%);'
        f'padding:48px 40px;text-align:center;">'
        f'<p style="margin:0;font-size:11px;font-weight:bold;color:rgba(255,255,255,0.6);'
        f'font-family:Arial,sans-serif;letter-spacing:3px;text-transform:uppercase;">'
        f'Weekly Intelligence Briefing</p>'
        f'<h2 style="margin:12px 0 0 0;font-size:26px;color:#ffffff;font-family:Arial,sans-serif;'
        f'font-weight:bold;line-height:1.3;">{topic}</h2>'
        f'</td>'
        '</tr></table>'
    )
    cta_href = main_source if main_source else "https://gemini.google.com"
    source_line = (
        f'<p style="margin:12px 0 0 0;font-size:13px;color:#999999;font-family:Arial,sans-serif;">'
        f'Source: <a href="{main_source}" style="color:#E94560;text-decoration:none;">{main_source}</a></p>'
        if main_source else ""
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{topic} Newsletter</title>
</head>
<body style="margin:0;padding:0;background-color:#EFEFEF;font-family:Arial,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#EFEFEF;padding:32px 0;">
  <tr><td align="center">
    <table width="640" cellpadding="0" cellspacing="0" style="max-width:640px;width:100%;">

      <!-- ── LOGO HEADER ── -->
      <tr>
        <td style="background-color:#1A1A2E;padding:28px 40px;text-align:center;border-radius:8px 8px 0 0;">
          {logo_tag}
          <p style="margin:10px 0 0 0;color:#aaaacc;font-size:12px;font-family:Arial,sans-serif;letter-spacing:1px;text-transform:uppercase;">AI &amp; Technology Intelligence</p>
        </td>
      </tr>

      <!-- ── HEADER IMAGE ── -->
      <tr><td style="padding:0;line-height:0;">{header_img}</td></tr>

      <!-- ── ISSUE BADGE ── -->
      <tr>
        <td style="background-color:#ffffff;padding:16px 40px 0 40px;">
          <table cellpadding="0" cellspacing="0">
            <tr>
              <td style="background-color:#1A1A2E;padding:4px 14px;border-radius:20px;">
                <span style="color:#ffffff;font-size:11px;font-family:Arial,sans-serif;font-weight:bold;letter-spacing:1px;text-transform:uppercase;">{issue_date}</span>
              </td>
              <td style="padding-left:10px;">
                <span style="color:#999999;font-size:12px;font-family:Arial,sans-serif;">{topic}</span>
              </td>
            </tr>
          </table>
        </td>
      </tr>

      <!-- ── FEATURED STORY ── -->
      <tr>
        <td style="background-color:#ffffff;padding:24px 40px 32px 40px;">
          <p style="margin:0 0 4px 0;font-size:11px;font-weight:bold;color:#E94560;font-family:Arial,sans-serif;letter-spacing:2px;text-transform:uppercase;">Featured Story</p>
          <h1 style="margin:0 0 16px 0;font-size:24px;font-weight:bold;color:#1A1A2E;font-family:Arial,sans-serif;line-height:1.35;">{main_story.get('title','')}</h1>
          <p style="margin:0;font-size:15px;color:#444444;font-family:Arial,sans-serif;line-height:1.75;">{main_story.get('content','')}</p>
          {source_line}
        </td>
      </tr>

      <!-- ── DIVIDER ── -->
      <tr><td style="background-color:#ffffff;padding:0 40px;"><hr style="border:none;border-top:2px solid #F0F0F0;margin:0;" /></td></tr>

      <!-- ── MORE THIS WEEK ── -->
      <tr>
        <td style="background-color:#ffffff;padding:28px 40px 8px 40px;">
          <p style="margin:0 0 4px 0;font-size:11px;font-weight:bold;color:#E94560;font-family:Arial,sans-serif;letter-spacing:2px;text-transform:uppercase;">More This Week</p>
          <h2 style="margin:0 0 4px 0;font-size:19px;color:#1A1A2E;font-family:Arial,sans-serif;">In Brief</h2>
        </td>
      </tr>
      <tr>
        <td style="background-color:#ffffff;padding:0 40px 24px 40px;">
          <table width="100%" cellpadding="0" cellspacing="0">
            {secondary_html}
          </table>
        </td>
      </tr>

      <!-- ── WHAT THIS MEANS FOR YOU ── -->
      <tr>
        <td style="background-color:#ffffff;padding:0 40px 32px 40px;">
          <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#FFF5F7;border-radius:8px;border:1px solid #FADADD;">
            <tr>
              <td style="padding:24px 28px;">
                <p style="margin:0 0 8px 0;font-size:11px;font-weight:bold;color:#E94560;font-family:Arial,sans-serif;letter-spacing:2px;text-transform:uppercase;">What This Means For You</p>
                <p style="margin:0;font-size:15px;color:#333333;font-family:Arial,sans-serif;line-height:1.7;">{takeaway}</p>
              </td>
            </tr>
          </table>
        </td>
      </tr>

      <!-- ── CTA BUTTON ── -->
      <tr>
        <td style="background-color:#ffffff;padding:0 40px 40px 40px;text-align:center;">
          <a href="{cta_href}" style="display:inline-block;background-color:#E94560;color:#ffffff;font-family:Arial,sans-serif;font-size:15px;font-weight:bold;padding:15px 40px;border-radius:50px;text-decoration:none;letter-spacing:0.5px;">Read Full Research &rarr;</a>
        </td>
      </tr>

      <!-- ── FOOTER ── -->
      <tr>
        <td style="background-color:#1A1A2E;padding:28px 40px;text-align:center;border-radius:0 0 8px 8px;">
          <p style="margin:0 0 8px 0;font-size:13px;color:#aaaacc;font-family:Arial,sans-serif;">You're receiving this because you subscribed to the AI Systems Newsletter.</p>
          <p style="margin:0;font-size:12px;font-family:Arial,sans-serif;">
            <a href="mailto:unsubscribe@example.com" style="color:#E94560;text-decoration:none;">Unsubscribe</a>
            <span style="color:#555577;">&nbsp;&nbsp;|&nbsp;&nbsp;</span>
            <span style="color:#777799;">&copy; {datetime.now().year} AI Systems. All rights reserved.</span>
          </p>
        </td>
      </tr>

    </table>
  </td></tr>
</table>

</body>
</html>"""

    html = html.encode('utf-8', errors='replace').decode('utf-8')
    output_path = "output/newsletter_draft.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  Newsletter draft saved to {output_path}")
    return output_path
