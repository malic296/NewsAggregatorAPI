from app.core.errors import DependencyUnavailableError
import resend

class EmailService:
    def __init__(self, resend_key: str):
        resend.api_key = resend_key

    def send_verification_code(self, email: str, code: int) -> None:
        html = f"""
            <div style="font-family: sans-serif; max-width: 400px; margin: auto; border: 1px solid #eee; padding: 20px; border-radius: 10px;">
                <h2 style="color: #007bff; text-align: center;">Fed Up</h2>
                <p style="color: #333; font-size: 16px;">Your verification code is:</p>
                <div style="background: #f8f9fa; border: 2px dashed #007bff; padding: 15px; text-align: center;">
                    <span style="font-size: 30px; font-weight: bold; letter-spacing: 5px; color: #007bff;">
                        {code}
                    </span>
                </div>
                <p style="font-size: 12px; color: #999; margin-top: 20px; text-align: center;">
                    Expiring in 2 minutes. If this wasn't you, ignore this email.
                </p>
            </div>
        """

        params: resend.Emails.SendParams = {
            "from": "FedUp <onboarding@contact.fedup.live>",
            "to": [email],
            "subject": "FedUp - Your Email Verification Code",
            "html": html,
        }

        try:
            resend.Emails.send(params)
        except Exception:
            raise DependencyUnavailableError(dependency="RESEND")