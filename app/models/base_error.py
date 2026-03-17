class BaseError(Exception):
    def __init__(self, *, internal_message, public_message):
        super.__init__(internal_message)
        self.public_message = public_message

    @property
    def internal_message(self) -> str:
        return self.args[0]

