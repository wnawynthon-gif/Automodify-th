import os, io, json, base64, mimetypes, tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VISION_MODEL = os.getenv("VISION_MODEL", "gpt-5.6")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "gpt-image-2")
ALLOWED_ORIGINS = [x.strip() for x in os.getenv("ALLOWED_ORIGINS", "*").split(",") if x.strip()]

app = FastAPI(title="CarBiz AI AutoMod API", version="5.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_credentials=False,
    allow_methods=["GET","POST","OPTIONS"],
    allow_headers=["*"],
)

class VehicleIdentity(BaseModel):
    make: str = "Unknown"
    model: str = "Unknown"
    year: Optional[str] = None
    generation: Optional[str] = None
    body_type: Optional[str] = None
    color: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    notes: Optional[str] = None

def client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured on the backend.")
    return OpenAI(api_key=OPENAI_API_KEY)

def normalize_json_text(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1])
            if text.lstrip().startswith("json"):
                text = text.lstrip()[4:].lstrip()
    return text.strip()

@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "carbiz-v5.1-api",
        "vision_model": VISION_MODEL,
        "image_model": IMAGE_MODEL,
        "openai_key_configured": bool(OPENAI_API_KEY),
    }

@app.post("/api/identify", response_model=VehicleIdentity)
async def identify(image: UploadFile = File(...)):
    raw = await image.read()
    if not raw:
        raise HTTPException(400, "Empty image.")
    if len(raw) > 12 * 1024 * 1024:
        raise HTTPException(413, "Image is too large. Use a file under 12 MB.")

    mime = image.content_type or mimetypes.guess_type(image.filename or "")[0] or "image/jpeg"
    data_url = f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"

    prompt = """You are the vehicle-identification engine for a car customization app.
Inspect the uploaded photo and identify ONLY what is reasonably supported by visible evidence.
Return ONE valid JSON object and no markdown:
{
 "make": "manufacturer",
 "model": "model",
 "year": "likely year or year range, or null",
 "generation": "generation/chassis/facelift if reasonably identifiable, or null",
 "body_type": "sedan/SUV/pickup/hatch/coupe/van/etc",
 "color": "visible exterior color",
 "confidence": 0.0,
 "notes": "short uncertainty note or null"
}
Rules:
- Never invent an exact trim/year when visual evidence is weak.
- Confidence is 0 to 1 for make+model identity.
- If uncertain, use broader model/generation wording and explain briefly in notes.
- Ignore license-plate personal information."""
    try:
        resp = client().responses.create(
            model=VISION_MODEL,
            input=[{
                "role":"user",
                "content":[
                    {"type":"input_text","text":prompt},
                    {"type":"input_image","image_url":data_url,"detail":"high"},
                ],
            }],
        )
        obj = json.loads(normalize_json_text(resp.output_text))
        return VehicleIdentity(**obj)
    except json.JSONDecodeError:
        raise HTTPException(502, "Vision model returned invalid JSON. Try the image again.")
    except Exception as e:
        raise HTTPException(502, f"Vehicle identification failed: {str(e)}")

@app.post("/api/render")
async def render(
    image: UploadFile = File(...),
    kit: str = Form(...),
    style: str = Form(...),
    vehicle_json: str = Form("{}"),
):
    raw = await image.read()
    if not raw:
        raise HTTPException(400, "Empty image.")

    try:
        vehicle = json.loads(vehicle_json)
    except Exception:
        vehicle = {}

    vehicle_name = " ".join([str(vehicle.get("make","")).strip(), str(vehicle.get("model","")).strip()]).strip() or "the vehicle"
    prompt = f"""Photorealistic automotive customization edit.

Original subject: {vehicle_name}
Requested modification package: {kit}
Requested visual style: {style}

EDITING RULES:
- Keep the SAME vehicle identity, body proportions, windows, doors, roofline, headlights and recognizable factory design.
- Keep the SAME camera angle, perspective, framing, environment, lighting direction and background as the input photo.
- Change ONLY visually relevant modification parts for the requested package.
- Make modifications physically plausible and professionally installed.
- Preserve paint unless the requested package explicitly changes wrap/color.
- Preserve wheel position and tire geometry unless wheels/tyres are the requested modification.
- Do not add text, logos, watermarks, people, extra cars, license-plate text, or unrelated objects.
- The result should look like a realistic dealership/custom-shop preview, not concept art.
"""
    suffix = Path(image.filename or "car.jpg").suffix.lower() or ".jpg"
    if suffix not in [".jpg",".jpeg",".png",".webp"]:
        suffix = ".jpg"

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(raw)
            tmp_path = tmp.name

        with open(tmp_path, "rb") as f:
            result = client().images.edit(
                model=IMAGE_MODEL,
                image=f,
                prompt=prompt,
            )
        b64 = result.data[0].b64_json
        return {
            "ok": True,
            "image_data_url": f"data:image/png;base64,{b64}",
            "kit": kit,
            "style": style,
        }
    except Exception as e:
        raise HTTPException(502, f"Image render failed: {str(e)}")
    finally:
        if tmp_path:
            try: os.unlink(tmp_path)
            except OSError: pass
