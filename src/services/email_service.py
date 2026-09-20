from email.message import EmailMessage

import aiosmtplib

from src.core.config import get_settings

settings = get_settings()


class EmailService:
    """Асинхронная отправка транзакционных писем."""

    async def send_verification_email(
        self,
        to_email: str,
        verification_link: str,
    ) -> None:
        message = EmailMessage()
        message["From"] = f"{settings.EMAIL_SENDER_NAME} <{settings.EMAIL_SENDER_ADDRESS}>"
        message["To"] = to_email
        message["Subject"] = "Подтверждение регистрации | InnoTech Solutions"

        plain_text = (
            f"Здравствуйте!\n\n"
            f"Благодарим за регистрацию в InnoTech Solutions.\n"
            f"Для завершения регистрации перейдите по ссылке:\n"
            f"{verification_link}\n\n"
            f"Ссылка активна в течение {settings.ACCESS_TOKEN_EXPIRE_MINUTES} минут.\n"
            f"Если вы не регистрировались, просто проигнорируйте это письмо."
        )
        message.set_content(plain_text)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f6f8; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 8px; border: 1px solid #e1e4e8;">
                <h2 style="color: #1a1f36; margin-top: 0;">Добро пожаловать в InnoTech!</h2>
                <p style="color: #4f566b; line-height: 1.6;">
                    Для подтверждения вашего адреса электронной почты и входа в систему, пожалуйста, нажмите на кнопку ниже:
                </p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_link}" 
                       style="background-color: #0066cc; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: bold; display: inline-block;">
                        Подтвердить Email
                    </a>
                </div>
                <p style="color: #697386; font-size: 13px; line-height: 1.5;">
                    Если кнопка не нажимается, скопируйте эту ссылку в браузер:<br>
                    <a href="{verification_link}" style="color: #0066cc;">{verification_link}</a>
                </p>
                <hr style="border: none; border-top: 1px solid #e1e4e8; margin: 20px 0;">
                <p style="color: #a3acb9; font-size: 12px;">
                    Ссылка действует {settings.ACCESS_TOKEN_EXPIRE_MINUTES} минут.
                </p>
            </div>
        </body>
        </html>
        """
        message.add_alternative(html_content, subtype="html")

        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER if settings.SMTP_USER else None,
            password=settings.SMTP_PASSWORD if settings.SMTP_PASSWORD else None,
            use_tls=settings.SMTP_USE_TLS,
        )