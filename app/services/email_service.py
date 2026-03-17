import os
from dotenv import load_dotenv
from pathlib import Path
from app.core.errors import InternalError

class EmailService:
    def __init__(self):
        try:
            load_dotenv(Path(__file__).parent.parent.parent / '.env')
            api_key = os.environ['RESEND_API_KEY']
        except KeyError as e:
            raise InternalError(
                internal_message=f"Failed reading env vars for email service because of missing key: {e}",
                public_message=f"Failed due to invalid server configuration."
            )
        except Exception as e:
            raise InternalError(
                internal_message=f"Email service init failed because of unexpected error: {e}",
                public_message=f"Failed due to invalid server configuration."
            )

    def send_verification_code(self, email: str, code: int) -> None:
        #WILL NEED TO PROPERLY SET LATER ON
        return

        params: resend.Emails.SendParams = {
            "from": "onboarding@resend.dev",
            "to": [email],
            "subject": "Verification Code",
            "html": f"Your verification code is: <strong>{code}</strong>",
        }

        self._resend.Emails.send(params)