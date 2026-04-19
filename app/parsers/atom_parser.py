import xml.etree.ElementTree as ET
from .feed_parser import FeedParser
from app.core.errors import ScrapingError
from datetime import datetime, timedelta, timezone
from app.models.scraped_data import ScrapedChannel, ScrapedArticle

class AtomParser(FeedParser):
    def __init__(self):
        self.namespace = "{http://www.w3.org/2005/Atom}"

    def can_parse(self, root: ET.Element) -> bool:
        return root.tag == f"{self.namespace}feed"

    def parse(self, root: ET.Element, hours: int = 1) -> ScrapedChannel:
        channel_title = root.findtext(f"{self.namespace}title", None)
        link_elem = root.find(f"{self.namespace}link[@rel='alternate']")
        channel_link = link_elem.attrib.get("href", "") if link_elem is not None else None

        if channel_link is None or channel_title is None:
            raise ScrapingError(f"Channel or link elements returned none for feed: {root}")

        channel = ScrapedChannel(
            title=channel_title,
            link=channel_link
        )

        entries = root.findall(f"{self.namespace}entry")
        for e in entries:
            try:
                e_pub_date = e.findtext(f"{self.namespace}published") or e.findtext(f"{self.namespace}updated")
                e_pub_date = self._parse_str_to_date(e_pub_date)

                if e_pub_date < datetime.now(tz=timezone.utc) - timedelta(hours=hours):
                    continue

                e_link_tag = e.find(f"{self.namespace}link")
                e_link = e_link_tag.attrib.get("href", "") if e_link_tag is not None else None
                e_link = e_link.strip()

                e_title = e.findtext(f"{self.namespace}title", None).strip()
                e_desc = e.findtext(f"{self.namespace}summary", "").strip()
            except Exception as e:
                raise Exception(f"Atom parser failed to parse the Atom feed because {e}.")

            channel.articles.append(
                ScrapedArticle(
                    title=e_title,
                    link=e_link,
                    pub_date=e_pub_date,
                    description=e_desc
                )
            )

        return channel