from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from src.api.v1 import api_v1_router
from src.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="Сервис регистрации и верификации пользователей",
    debug=settings.DEBUG,
)

templates = Jinja2Templates(directory="src/templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
async def index_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")

app.include_router(api_v1_router)