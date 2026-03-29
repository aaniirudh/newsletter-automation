import os
import sys
from dotenv import load_dotenv

load_dotenv()
os.makedirs("output", exist_ok=True)

def main():
    topic = os.getenv("NEWSLETTER_TOPIC", "AI and Machine Learning Weekly Digest")

    print("\n" + "="*50)
    print("  NEWSLETTER AUTOMATION PIPELINE")
    print("="*50)
    print(f"  Topic: {topic}\n")

    # Step 1: Research
    print("🔍 Step 1/5: Researching topic...")
    try:
        from tools.research import run_research
        research = run_research(topic)
        print("  Research complete.\n")
    except Exception as e:
        print(f"  Research failed: {e}. Using fallback.\n")
        research = {
            "topic": topic,
            "main_story": {
                "title": f"Weekly Digest: {topic}",
                "content": f"This week in {topic}: key developments continue to shape the industry.",
                "source": ""
            },
            "secondary_stories": [
                {"title": "Trend Update", "summary": "Industry trends accelerating.", "source": ""},
                {"title": "Research Highlights", "summary": "New research findings published.", "source": ""},
                {"title": "Community News", "summary": "Open-source community growing.", "source": ""},
            ],
            "takeaway": f"Stay informed about {topic} to remain competitive."
        }

    # Step 2: Generate image
    print("🖼️  Step 2/5: Generating header image...")
    try:
        from tools.generate_image import generate_header_image
        image_path = generate_header_image(topic)
        print(f"  Image ready: {image_path}\n")
    except Exception as e:
        print(f"  Image generation failed: {e}. Using placeholder.\n")
        from PIL import Image
        os.makedirs("output", exist_ok=True)
        img = Image.new("RGB", (1280, 720), color=(26, 26, 46))
        image_path = "output/header_image.png"
        img.save(image_path)

    # Step 3: Write newsletter
    print("✍️  Step 3/5: Writing newsletter...")
    try:
        from tools.write_newsletter import write_newsletter
        html_path = write_newsletter(research, image_path, topic)
        print(f"  Newsletter draft ready: {html_path}\n")
    except Exception as e:
        print(f"  Newsletter writing failed: {e}")
        sys.exit(1)

    # Step 4: Human review
    print("👤 Step 4/5: Awaiting human approval...")
    try:
        from tools.human_review import get_approved_subject
        approved_subject = get_approved_subject("output/subject_lines.txt")
        print(f"  Approved subject: \"{approved_subject}\"\n")
    except Exception as e:
        print(f"  Human review failed: {e}")
        sys.exit(1)

    # Step 5: Send
    print("📤 Step 5/5: Sending newsletter...")
    try:
        from tools.send_email import send_newsletter
        success = send_newsletter(approved_subject, html_path)
        if success:
            print("  Send complete.\n")
        else:
            print("  Send failed (check credentials in .env).\n")
    except Exception as e:
        print(f"  Send error: {e}\n")

    print("✅ Pipeline complete!")
    print("\n" + "="*50)
    print("  NEXT STEPS")
    print("="*50)
    print("  1. Copy .env.example to .env")
    print("  2. Add your PERPLEXITY_API_KEY")
    print("  3. Add your IMAGE_API_KEY (Together.xyz)")
    print("  4. Add GMAIL_USER + GMAIL_APP_PASSWORD")
    print("  5. Replace brand_assets/AIS.PNG with your logo")
    print("  6. Run: python main.py")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
