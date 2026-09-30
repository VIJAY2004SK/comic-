import traceback
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from gemini_flash import generate_outline
from gemini_pro import generate_story
from image_generator import generate_image
from layout_builder import build_comic_layout
from exporters import save_pdf

router = APIRouter()
templates = Jinja2Templates(directory="templates")

class PromptRequest(BaseModel):
    prompt: str
    character_name: str
    setting: str
    tone: str
    style: str

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request},
    )

@router.post("/generate", response_class=HTMLResponse)
async def generate_comic(
    request: Request,
    prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    style: str = Form(...)
):
    try:
        full_prompt = (
            f"{prompt}\n"
            f"The main character is {character_name}. "
            f"The setting is a {setting}. "
            f"The tone is {tone}. The art style is {style}."
        )

        # Step 1: Generate Outline
        outline = generate_outline(full_prompt)
        if isinstance(outline, list) and len(outline) > 0 and "error" in outline[0]:
            error_detail = outline[0]["error"]
            status_code = 429 if "quota" in error_detail.lower() else 500
            raise HTTPException(status_code=status_code, detail=error_detail)

        # Step 2: Generate Story
        full_story = generate_story(outline)

        # Step 3: Generate Images
        images = [generate_image(panel["image_prompt"]) for panel in outline]

        # Step 4: Build Layout
        layout = build_comic_layout(images, full_story, outline)

        # Step 5: Save PDF
        pdf_path = save_pdf(layout)
        web_pdf_path = "/" + pdf_path.replace("\\", "/")

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "request": request,
                "layout": layout,
                "pdf_path": web_pdf_path,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-comic/json")
async def generate_comic_json(payload: PromptRequest):
    try:
        full_prompt = (
            f"{payload.prompt}\n"
            f"Main character: {payload.character_name}. "
            f"Setting: {payload.setting}. Tone: {payload.tone}. Style: {payload.style}."
        )
        outline = generate_outline(full_prompt)
        full_story = generate_story(outline)
        images = [generate_image(panel["image_prompt"]) for panel in outline]
        layout = build_comic_layout(images, full_story, outline)
        pdf_path = save_pdf(layout)

        return {
            "status": "success",
            "layout": layout,
            "pdf_path": "/" + pdf_path.replace("\\", "/")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request, pdf_path: str):
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "request": request,
            "pdf_path": pdf_path,
        },
    )

@router.get("/test-image")
async def test_image(prompt: str = "A futuristic city at sunset, sci-fi, cinematic, artstation"):
    try:
        image_path = generate_image(prompt)
        return {"message": "Image generated successfully", "path": image_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))