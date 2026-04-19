import xml.etree.ElementTree as ET
from app.core.errors import ScrapingError
from .feed_parser import FeedParser
from datetime import datetime, timedelta, timezone
from app.models.scraped_data import ScrapedArticle, ScrapedChannel

class RSSParser(FeedParser):
    def can_parse(self, root: ET.Element) -> bool:
        return root.tag == "rss"

    def parse(self, root: ET.Element, hours: int = 1) -> ScrapedChannel:
        channel = root.find("channel")
        if channel is None:
            raise ScrapingError(f"Channel tag not found for: {root}")

        channel_title = channel.findtext("title", default=None)
        channel_link = channel.findtext("link", default=None)

        if channel_link is None or channel_link is None:
            raise ScrapingError("RSS header is missing required title or link.")

        result = ScrapedChannel(
            title=channel_title.strip(),
            link=channel_link.strip()
        )

        items = channel.findall("item")
        for item in items:
            try:
                i_pubdate = item.findtext("pubDate", default=None).strip()
                parsed_pubdate = self._parse_str_to_date(i_pubdate)

                if parsed_pubdate < datetime.now(tz=timezone.utc) - timedelta(hours=hours):
                    continue

                i_title = item.findtext("title", default=None).strip()
                i_link = item.findtext("link", default=None).strip()
                i_description = item.findtext("description", default="").strip()

            except Exception as e:
                raise Exception(f"RSS parser failed to parse the RSS feed because {e}.")

            result.articles.append(
                ScrapedArticle(
                    title=i_title,
                    link=i_link,
                    description=i_description,
                    pub_date=parsed_pubdate,

                )
            )

        return result