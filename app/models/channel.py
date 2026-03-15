from dataclasses import dataclass

@dataclass
class Channel:
    id: int
    uuid: str
    title: str
    link: str
