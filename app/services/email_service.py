import os
from dotenv import load_dotenv
from pathlib import Path
from app.core.errors import InternalError
import resend

class EmailService:
    def __init__(self):
        try:
            load_dotenv(Path(__file__).parent.parent.parent / '.env')
            resend.api_key = os.environ['RESEND_API_KEY']

        except KeyError as e:
            raise InternalError(
                internal_message=f"Failed reading env vars for email service because of missing key: {e}"
            )
        except Exception as e:
            raise InternalError(
                internal_message=f"Email service init failed because of unexpected error: {e}"
            )

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
        except Exception as e:
            raise InternalError(
                internal_message=f"Failed sending verification code to email: {email} because: {e}"
            )