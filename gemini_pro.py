import os

from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from environment variables or .env file.")

client = genai.Client(api_key=api_key)
model_name = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


def generate_story(outline: list) -> str:
    formatted_outline = "\n".join(
        f"Panel {item.get('panel')}: {item.get('title')} - {item.get('scene_description')}"
        for item in outline
    )
    prompt = f"""
You are a comic book writer creating readable dialogue and narration.

Given this panel breakdown, write a comic-style story with narration and dialogue:
{formatted_outline}

Start each section with "**Panel X: Title**". Label CAPTION, NARRATION, and dialogue clearly.
"""
    try:
        response = client.models.generate_content(model=model_name, contents=prompt)
        response_text = response.text
        if not response_text:
            raise ValueError("Gemini returned an empty story response.")
        return response_text
    except Exception as error:
        return f"Error generating story: {error}"