from fastapi import FastAPI
from src.core.config import get_settings
from src.core.security import create_access_token, generate_verification_token

settings = get_settings()
app = FastAPI(title=settings.APP_NAME)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/debug/token")
async def debug_token(email: str = "lalala@mail.com"):
    raw_token, token_hash = generate_verification_token()
    link = f"{settings.APP_BASE_URL}/api/v1/auth/verify?token={raw_token}"
    jwt_token = create_access_token(user_id="demo-user-id", email=email)

    return {
        "email": email,
        "raw_token": raw_token,
        "token_hash": token_hash,
        "link": link,
        "jwt_token": jwt_token,
    }