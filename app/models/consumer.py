from dataclasses import dataclass

@dataclass
class Consumer:
    id: int
    uuid: str
    username: str
    email: str