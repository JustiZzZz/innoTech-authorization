from fastapi import FastAPI
from src.core.config import get_settings
from src.core.security import create_access_token, generate_verification_token
from src.services.email_service import EmailService

settings = get_settings()
app = FastAPI(title=settings.APP_NAME)
email_service = EmailService()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/debug/token")
async def debug_token(email: str = "test@innotech.by"):
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


@app.post("/debug/send-email")
async def debug_send_email(to_email: str = "candidate@innotech.by"):
    raw_token, _ = generate_verification_token()
    demo_link = f"{settings.APP_BASE_URL}/api/v1/auth/verify?token={raw_token}"

    await email_service.send_verification_email(
        to_email=to_email,
        verification_link=demo_link,
    )

    return {
        "status": "email sent successfully",
        "to": to_email,
        "verification_link": demo_link,
        "smtp_server": f"{settings.SMTP_HOST}:{settings.SMTP_PORT}",
    }