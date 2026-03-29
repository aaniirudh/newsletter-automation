import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def send_newsletter(subject: str, html_path: str) -> bool:
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    recipient_list_raw = os.getenv("RECIPIENT_LIST", "")
    recipients = [r.strip() for r in recipient_list_raw.split(",") if r.strip()]

    if not all([gmail_user, gmail_password, recipients]):
        print("  Missing email credentials or recipient list in .env")
        return False

    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"  HTML file not found: {html_path}")
        return False

    html_content = html_content.encode('utf-8', errors='replace').decode('utf-8')

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = gmail_user
        msg["To"] = ", ".join(recipients)
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, recipients, msg.as_string())

        print(f"  Newsletter sent successfully to {len(recipients)} recipients")
        return True

    except UnicodeEncodeError as e:
        print(f"  UnicodeEncodeError: {e}. Re-encoding and retrying...")
        try:
            html_content = html_content.encode('ascii', errors='replace').decode('ascii')
            msg2 = MIMEMultipart("alternative")
            msg2["Subject"] = subject
            msg2["From"] = gmail_user
            msg2["To"] = ", ".join(recipients)
            msg2.attach(MIMEText(html_content, "html", "utf-8"))
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(gmail_user, gmail_password)
                server.sendmail(gmail_user, recipients, msg2.as_string())
            print(f"  Newsletter sent (re-encoded) to {len(recipients)} recipients")
            return True
        except Exception as e2:
            print(f"  Send failed on retry: {e2}")
            return False
    except Exception as e:
        print(f"  Send failed: {e}")
        return False
