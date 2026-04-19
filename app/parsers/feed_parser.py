from abc import ABC, abstractmethod
import xml.etree.ElementTree as ET
from app.models.article import Article
from typing import List
from datetime import datetime, timezone
from dateutil import parser

class FeedParser(ABC):
    @abstractmethod
    def can_parse(self, root: ET.Element) -> bool:
        pass

    @abstractmethod
    def parse(self, root: ET.Element, hours: int = 1) -> List[Article]:
        pass

    @staticmethod
    def _parse_str_to_date(date_str: str) -> datetime:
        try:
            dt = parser.parse(date_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            raise ValueError(f"Unknown date format: {date_str}")