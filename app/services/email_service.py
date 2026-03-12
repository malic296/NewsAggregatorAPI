import os
import resend
from dotenv import load_dotenv
from pathlib import Path

class EmailService:
    def __init__(self):
        try:
            load_dotenv(Path(__file__).parent.parent.parent / '.env')
            api_key = os.environ['RESEND_API_KEY']
            resend.api_key = api_key
            self._resend = resend
        except KeyError as e:
            raise e
        except Exception as e:
            raise e

    def send_verification_code(self, address, code: int) -> None:
        params = {
            "from": "FedUp <verification@fedup.com>",
            "to": address,
            "subject": "Verification Code",
            "html": f"Your verification code is: <strong>{code}</strong>",
        }
        self._resend.Emails.send(**params)