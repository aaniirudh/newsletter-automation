import os
import time
from PIL import Image, ImageDraw
from dotenv import load_dotenv

load_dotenv()

def generate_header_image(topic: str) -> str:
    from google import genai
    from google.genai import types

    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    os.makedirs("output", exist_ok=True)
    output_path = "output/header_image.png"

    prompt = (
        f"Professional newsletter header image for topic: {topic}. "
        f"Clean, modern, corporate style. 16:9 ratio. No text."
    )

    for attempt in range(1, 4):
        try:
            print(f"  Image generation attempt {attempt}/3...")
            response = client.models.generate_images(
                model="imagen-4.0-generate-001",
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="16:9",
                )
            )
            image_bytes = response.generated_images[0].image.image_bytes
            with open(output_path, "wb") as f:
                f.write(image_bytes)
            print(f"  Header image saved to {output_path}")
            return output_path

        except Exception as e:
            print(f"  Image attempt {attempt} failed: {e}")
            if attempt < 3:
                time.sleep(5 * attempt)

    print("  Image generation failed. Creating placeholder...")
    return _create_placeholder(output_path, topic)


def _create_placeholder(path: str, topic: str) -> str:
    img = Image.new("RGB", (1280, 720), color=(26, 26, 46))
    draw = ImageDraw.Draw(img)
    draw.text((640, 360), topic, fill=(233, 69, 96), anchor="mm")
    img.save(path)
    print(f"  Placeholder header image saved to {path}")
    return path
