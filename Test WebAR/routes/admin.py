from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import shutil
import os
import json
import subprocess

router = APIRouter()
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "static/uploads"
TARGET_LIST_PATH = "tools/target_list.json"
TEMPLATE_HTML = "static/webar_template.html"

@router.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    return templates.TemplateResponse("admin.html", {
        "request": request, 
        "message": 'تارگت با موفقیت اضافه شد', 
        "success": True})

@router.post("/admin/upload", response_class=HTMLResponse)
async def upload_target(
    request: Request,
    target_id: str = Form(...),
    language: str = Form(...),
    image: UploadFile = File(...),
    video: UploadFile = File(...)
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    image_filename = f"{target_id}.jpg"
    video_filename = f"{target_id}_{language}.mp4"
    image_path = os.path.abspath(os.path.join(UPLOAD_DIR, image_filename))
    video_path = os.path.abspath(os.path.join(UPLOAD_DIR, video_filename))

    with open(image_path, "wb") as img_out:
        shutil.copyfileobj(image.file, img_out)

    with open(video_path, "wb") as vid_out:
        shutil.copyfileobj(video.file, vid_out)

    if os.path.exists(TARGET_LIST_PATH):
        with open(TARGET_LIST_PATH, "r", encoding="utf-8") as f:
            targets = json.load(f)
    else:
        targets = []

    existing = next((t for t in targets if t["id"] == target_id), None)
    if not existing:
        existing = {"id": target_id, "image": image_filename, "videos": {}}
        targets.append(existing)
    existing["videos"][language] = video_filename

    with open(TARGET_LIST_PATH, "w", encoding="utf-8") as f:
        json.dump(targets, f, ensure_ascii=False, indent=2)

    try:
        subprocess.run(["node", "scripts/compile_mind.js", image_path, target_id], check=True)
    except subprocess.CalledProcessError as e:
        return templates.TemplateResponse("admin.html", {
            "request": request,
            "message": f"خطا در تولید فایل .mind: {e}",
            "success": False
        })

    try:
        subprocess.run(["python3", "generate_all_mind.py"], check=True)
    except subprocess.CalledProcessError as e:
        return templates.TemplateResponse("admin.html", {
            "request": request,
            "message": f"خطا در ساخت all.mind: {e}",
            "success": False
        })

    # ساخت فایل HTML اختصاصی
    html_output_path = f"static/{target_id}.html"
    with open(TEMPLATE_HTML, "r", encoding="utf-8") as template_file:
        template_content = template_file.read()
        customized = template_content.replace("{{TARGET_ID}}", target_id)
        with open(html_output_path, "w", encoding="utf-8") as output_file:
            output_file.write(customized)

    return templates.TemplateResponse("admin.html", {
        "request": request,
        "message": "تارگت با موفقیت اضافه شد.",
        "success": True
    })
