import json
import os
import re

from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from environment variables or .env file.")

client = genai.Client(api_key=api_key)
model_name = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


def generate_outline(user_prompt: str) -> list:
    prompt = f"""
You are a professional comic planner.

Create exactly five panels based on this story idea:
{user_prompt}

Return only a JSON array. Each object must contain these keys:
panel, title, scene_description, image_prompt.
"""
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )
        response_text = response.text
        if not response_text:
            raise ValueError("Gemini returned an empty outline response.")
        output_text = response_text.strip()
        output_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", output_text).strip()
        panel_data = json.loads(output_text)
        if not isinstance(panel_data, list):
            raise ValueError("Gemini response is not a JSON list.")
        required_keys = ("panel", "title", "scene_description", "image_prompt")
        for panel in panel_data:
            if not isinstance(panel, dict) or not all(key in panel for key in required_keys):
                raise ValueError(f"Invalid panel format or missing keys: {panel}")
        return panel_data
    except json.JSONDecodeError as error:
        return [{"error": f"JSON parsing failed: {error}"}]
    except Exception as error:
        return [{"error": f"Generation failed: {error}"}]