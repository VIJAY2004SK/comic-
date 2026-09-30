import os
import re
import torch
from PIL import Image, ImageDraw, ImageFont
from diffusers import StableDiffusionPipeline
from dotenv import load_dotenv

load_dotenv()

pipe = None

def init_pipeline():
    global pipe
    if pipe is None:
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model_id = "runwayml/stable-diffusion-v1-5"
            
            if device == "cuda":
                pipe = StableDiffusionPipeline.from_pretrained(
                    model_id, 
                    torch_dtype=torch.float16
                ).to(device)
            else:
                pipe = StableDiffusionPipeline.from_pretrained(model_id).to(device)
            
            # Reduce memory footprint
            pipe.enable_attention_slicing()
        except Exception as e:
            print(f"Warning: Stable Diffusion pipeline could not be loaded: {e}")
            pipe = False

def sanitize_filename(prompt: str) -> str:
    clean = re.sub(r'[^\w\s-]', '', prompt).strip().lower()
    clean = re.sub(r'[-\s]+', '_', clean)
    return clean[:30] + ".png"

def create_placeholder_image(prompt: str, path: str):
    """Fallback generator when Diffusers environment is unequipped or GPU memory is unavailable."""
    img = Image.new('RGB', (512, 512), color=(240, 242, 245))
    d = ImageDraw.Draw(img)
    d.rectangle([(10, 10), (502, 502)], outline=(70, 130, 180), width=4)
    d.text((30, 240), f"Comic Illustration Preview\n\nPrompt: {prompt[:60]}...", fill=(50, 50, 50))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)

def generate_image(prompt: str, filename: str = None) -> str:
    if not filename:
        filename = sanitize_filename(prompt)
        
    path = f"static/panels/{filename}"
    os.makedirs(os.path.dirname(path), exist_ok=True)

    init_pipeline()
    
    if pipe:
        try:
            image = pipe(prompt, num_inference_steps=25).images[0]
            image.save(path)
            return path
        except Exception as e:
            print(f"Image generation failed: {e}. Falling back to placeholder.")
            create_placeholder_image(prompt, path)
            return path
    else:
        create_placeholder_image(prompt, path)
        return path