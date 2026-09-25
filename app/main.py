from pathlib import Path
import json
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .database import init_db, create_user, get_user_by_email, save_recommendation, get_history, get_recommendation
from .auth import hash_password, verify_password, create_token, get_current_user, require_user, COOKIE_NAME
from .ai.gemini_service import generate_recommendation
from .services.planners import validate_home, validate_party, validate_jewelry

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
settings = get_settings()

app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/startup")
def startup_info():
    init_db()
    return {"status": "ready", "app": settings.app_name}

@app.get("/health")
def health():
    return {"status": "ok", "gemini_configured": bool(settings.gemini_api_key)}

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "user": get_current_user(request)})

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "user": get_current_user(request), "error": None})

@app.post("/register")
def register(name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    name, email = name.strip(), email.strip().lower()
    if len(name) < 2 or len(password) < 6:
        return RedirectResponse("/register?error=Name%20or%20password%20is%20invalid", status_code=303)
    if get_user_by_email(email):
        return RedirectResponse("/login?error=Account%20already%20exists", status_code=303)
    create_user(name, email, hash_password(password))
    return RedirectResponse("/login?registered=1", status_code=303)

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "user": get_current_user(request), "error": request.query_params.get("error")})

@app.post("/login")
def login(email: str = Form(...), password: str = Form(...)):
    user = get_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        return RedirectResponse("/login?error=Invalid%20email%20or%20password", status_code=303)
    response = RedirectResponse("/dashboard", status_code=303)
    response.set_cookie(COOKIE_NAME, create_token(user["id"]), httponly=True, samesite="lax", secure=False, max_age=86400)
    return response

@app.post("/token")
def token(email: str = Form(...), password: str = Form(...)):
    user = get_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        return JSONResponse({"detail": "Invalid credentials"}, status_code=401)
    return {"access_token": create_token(user["id"]), "token_type": "bearer"}

@app.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie(COOKIE_NAME)
    return response

@app.get("/session-info")
def session_info(request: Request):
    user = get_current_user(request)
    return {"logged_in": bool(user), "user_id": user["id"] if user else None, "name": user["name"] if user else None}

@app.get("/session-data")
def session_data(request: Request):
    user = require_user(request)
    history = get_history(user["id"])
    return {"user": {"id": user["id"], "name": user["name"], "email": user["email"]}, "recommendation_count": len(history)}

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user = require_user(request)
    history = get_history(user["id"])
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "history": history[:5]})

@app.get("/history", response_class=HTMLResponse)
def history_page(request: Request):
    user = require_user(request)
    return templates.TemplateResponse("history.html", {"request": request, "user": user, "history": get_history(user["id"])})

@app.get("/home-planner", response_class=HTMLResponse)
def home_planner(request: Request):
    return templates.TemplateResponse("home_planner.html", {"request": request, "user": get_current_user(request)})

@app.get("/party-planner", response_class=HTMLResponse)
def party_planner(request: Request):
    return templates.TemplateResponse("party_planner.html", {"request": request, "user": get_current_user(request)})

@app.get("/jewelry-planner", response_class=HTMLResponse)
def jewelry_planner(request: Request):
    return templates.TemplateResponse("jewelry_planner.html", {"request": request, "user": get_current_user(request)})

def _api_user(request: Request):
    return require_user(request)

@app.post("/generate-home")
async def generate_home(request: Request):
    user = _api_user(request)
    payload = await request.json()
    data = validate_home(payload)
    result = generate_recommendation("home", data)
    rec_id = save_recommendation(user["id"], "home", data, result)
    result["recommendation_id"] = rec_id
    return result

@app.post("/generate-party")
async def generate_party(request: Request):
    user = _api_user(request)
    payload = await request.json()
    data = validate_party(payload)
    result = generate_recommendation("party", data)
    rec_id = save_recommendation(user["id"], "party", data, result)
    result["recommendation_id"] = rec_id
    return result

@app.post("/generate-jewelry")
async def generate_jewelry(request: Request, outfit_image: UploadFile | None = File(default=None)):
    user = _api_user(request)
    form = await request.form()
    data = {
        "budget": float(form.get("budget")),
        "occasion": str(form.get("occasion")),
        "style": str(form.get("style", "Elegant")),
        "outfit_color": str(form.get("outfit_color", "")),
        "notes": str(form.get("notes", "")),
    }
    data = validate_jewelry(data)
    image_bytes = None
    mime_type = "image/jpeg"
    if outfit_image and outfit_image.filename:
        if outfit_image.content_type not in {"image/jpeg", "image/png", "image/webp"}:
            return JSONResponse({"detail": "Only JPG, PNG or WEBP images are allowed."}, status_code=400)
        image_bytes = await outfit_image.read()
        if len(image_bytes) > 5 * 1024 * 1024:
            return JSONResponse({"detail": "Image must be 5 MB or smaller."}, status_code=400)
        mime_type = outfit_image.content_type
    result = generate_recommendation("jewelry", data, image_bytes, mime_type)
    rec_id = save_recommendation(user["id"], "jewelry", data, result)
    result["recommendation_id"] = rec_id
    return result

@app.get("/recommendations-details/{recommendation_id}", response_class=HTMLResponse)
def recommendation_details(request: Request, recommendation_id: int):
    user = require_user(request)
    row = get_recommendation(user["id"], recommendation_id)
    if not row:
        return RedirectResponse("/history", status_code=303)
    result = json.loads(row["result_json"])
    return templates.TemplateResponse("recommendations.html", {"request": request, "user": user, "result": result, "planner_type": row["planner_type"]})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
