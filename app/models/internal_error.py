from fastapi import status

class InternalError(Exception):
    def __init__(self, *, internal_message: str, public_message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super.__init__(internal_message)
        self.public_message = public_message
        self.status_code = status_code

    @property
    def internal_message(self) -> str:
        return self.args[0]

