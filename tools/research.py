import os
import json
import re
import time
from dotenv import load_dotenv

load_dotenv()


def _parse_research(content: str, topic: str) -> dict:
    """Parse Gemini's markdown response into structured sections."""

    # Extract main story section
    main_match = re.search(
        r'###?\s*1\)?[^#\n]*\n(.*?)(?=###?\s*2\)|\Z)', content, re.DOTALL | re.IGNORECASE
    )
    main_raw = main_match.group(1).strip() if main_match else content[:800]

    # Extract main story title (first bold line)
    title_match = re.search(r'\*\*([^*]+)\*\*', main_raw)
    main_title = title_match.group(1).strip() if title_match else f"Latest in {topic}"

    # Clean main content — strip markdown bold/headers, keep text
    main_content = re.sub(r'\*\*([^*]+)\*\*', r'\1', main_raw)
    main_content = re.sub(r'#+\s*', '', main_content)
    main_content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', main_content)  # strip links
    main_content = re.sub(r'\n{3,}', '\n\n', main_content).strip()
    # Take first ~400 chars cleanly
    if len(main_content) > 500:
        main_content = main_content[:500].rsplit(' ', 1)[0] + '...'

    # Extract first source URL from main section
    source_match = re.search(r'https?://[^\s\)]+', main_raw)
    main_source = source_match.group(0).rstrip('.,)') if source_match else ''

    # Extract secondary stories section
    secondary_raw = re.search(
        r'###?\s*2\)?[^#\n]*\n(.*?)(?=###?\s*3\)|\Z)', content, re.DOTALL | re.IGNORECASE
    )
    secondary_text = secondary_raw.group(1).strip() if secondary_raw else ''

    # Split into individual stories by bold titles
    story_blocks = re.split(r'\n(?=\*\*[^*]+\*\*\n)', secondary_text)
    secondary_stories = []
    for block in story_blocks:
        block = block.strip()
        if not block:
            continue
        t_match = re.search(r'\*\*([^*]+)\*\*', block)
        title = t_match.group(1).strip() if t_match else "Story Update"
        # Remove the title line and clean
        body = re.sub(r'\*\*[^*]+\*\*', '', block, count=1)
        body = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', body)
        body = re.sub(r'Sources?:.*', '', body, flags=re.DOTALL | re.IGNORECASE)
        body = re.sub(r'\*', '', body)
        body = re.sub(r'\n{2,}', ' ', body).strip()
        if len(body) > 200:
            body = body[:200].rsplit(' ', 1)[0] + '...'
        src_match = re.search(r'https?://[^\s\)]+', block)
        src = src_match.group(0).rstrip('.,)') if src_match else ''
        if title and body:
            secondary_stories.append({"title": title, "summary": body, "source": src})
        if len(secondary_stories) == 3:
            break

    # Pad if fewer than 3
    while len(secondary_stories) < 3:
        secondary_stories.append({"title": "Industry Update", "summary": "More developments are emerging across the AI landscape.", "source": ""})

    # Extract takeaway
    takeaway_match = re.search(
        r'###?\s*3\)?[^#\n]*\n(.*)', content, re.DOTALL | re.IGNORECASE
    )
    takeaway_raw = takeaway_match.group(1).strip() if takeaway_match else content[-400:]
    takeaway = re.sub(r'\*\*([^*]+)\*\*', r'\1', takeaway_raw)
    takeaway = re.sub(r'#+\s*', '', takeaway)
    takeaway = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', takeaway)
    takeaway = re.sub(r'\n{2,}', ' ', takeaway).strip()
    if len(takeaway) > 400:
        takeaway = takeaway[:400].rsplit(' ', 1)[0] + '...'

    return {
        "topic": topic,
        "raw_content": content,
        "main_story": {
            "title": main_title,
            "content": main_content,
            "source": main_source
        },
        "secondary_stories": secondary_stories,
        "takeaway": takeaway
    }


def run_research(topic: str, num_sources: int = 5) -> dict:
    from google import genai

    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    os.makedirs("output", exist_ok=True)

    prompt = (
        f"You are a research assistant. Research the latest developments in: {topic}.\n\n"
        f"Return your response in this exact structure:\n\n"
        f"### 1) Main Story\n"
        f"**[Story Title]**\n"
        f"[150-200 word summary with 3 numbered key facts]\n"
        f"Sources:\n* [Source URL]\n\n"
        f"### 2) Secondary Stories\n"
        f"**[Story 1 Title]**\n[50-80 word summary]\nSources:\n* [URL]\n\n"
        f"**[Story 2 Title]**\n[50-80 word summary]\nSources:\n* [URL]\n\n"
        f"**[Story 3 Title]**\n[50-80 word summary]\nSources:\n* [URL]\n\n"
        f"### 3) Practical Takeaway\n"
        f"[2-3 sentence practical insight for the reader]"
    )

    delays = [5, 10, 20]

    for attempt, delay in enumerate(delays, 1):
        try:
            print(f"  Research attempt {attempt}/3...")
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            content = response.text.encode('utf-8', errors='replace').decode('utf-8')
            result = _parse_research(content, topic)

            with open("output/research_raw.json", "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            return result

        except Exception as e:
            print(f"  Research attempt {attempt} failed: {e}")
            if attempt < len(delays):
                print(f"  Retrying in {delay}s...")
                time.sleep(delay)

    print("  All research attempts failed. Using fallback data.")
    fallback = {
        "topic": topic,
        "raw_content": "",
        "main_story": {
            "title": f"Weekly Digest: {topic}",
            "content": f"This week in {topic}: key developments continue to shape the industry. Practitioners are seeing increased adoption and new tooling emerging across the ecosystem.",
            "source": ""
        },
        "secondary_stories": [
            {"title": "Industry Trend Update", "summary": "Major players are investing heavily in new capabilities.", "source": ""},
            {"title": "Research Highlights", "summary": "Academic research is yielding practical applications.", "source": ""},
            {"title": "Community News", "summary": "The open-source community continues to innovate.", "source": ""},
        ],
        "takeaway": f"Stay informed about {topic} to remain competitive in your field."
    }

    with open("output/research_raw.json", "w", encoding="utf-8") as f:
        json.dump(fallback, f, indent=2, ensure_ascii=False)

    return fallback
