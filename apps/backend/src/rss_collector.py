import os
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from typing import TypedDict
from xml.etree import ElementTree as ET

from dotenv import load_dotenv
from linkup import LinkupClient

from .article import Article
from .logger import get_logger

load_dotenv()

logger = get_logger(__name__)

linkup_client = LinkupClient(api_key=os.getenv("LINKUP_API_KEY"))


class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.text_parts.append(data)

    def get_text(self) -> str:
        return " ".join(self.text_parts)


def strip_html_tags(html_content: str) -> str:
    if not html_content:
        return ""

    parser = HTMLTextExtractor()
    parser.feed(html_content)
    return parser.get_text().strip()


class FeedSourceConfig(TypedDict):
    base_url: str
    sources: list[str]


feed_sources: dict[str, FeedSourceConfig] = {
    "public": {
        "base_url": "public.fr",
        "sources": [
            "https://www.public.fr/dernieres-actualites/feed",
            "https://www.public.fr/people/feed",
            "https://www.public.fr/tele/feed",
            "https://www.public.fr/faits-divers/feed",
            "https://www.public.fr/lifestyle/feed",
        ],
    },
    "vsd": {
        "base_url": "vsd.fr",
        "sources": [
            "https://vsd.fr/actu-people/feed",
            "https://vsd.fr/tele/feed",
            "https://vsd.fr/societe/feed",
            "https://vsd.fr/loisirs/feed",
            "https://vsd.fr/culture/feed",
        ],
    },
}


def parse_rss_feed(feed_url: str, source: str) -> list[Article]:
    articles: list[Article] = []
    try:
        feed_response = linkup_client.fetch(feed_url, include_raw_html=True, render_js=False)

        raw_html = feed_response.raw_html or ""

        logger.debug("Feed fetched successfully", feed_url=feed_url, html_length=len(raw_html))

        if not raw_html:
            logger.warning("No raw HTML content in feed response", feed_url=feed_url)
            return articles

        root = ET.fromstring(raw_html)

        namespaces = {
            "content": "http://purl.org/rss/1.0/modules/content/",
            "media": "http://search.yahoo.com/mrss/",
            "dc": "http://purl.org/dc/elements/1.1/",
        }

        items = root.findall(".//item")
        logger.debug("Found items in RSS feed", feed_url=feed_url, item_count=len(items))

        for item in items:
            try:
                title_elem = item.find("title")
                title = title_elem.text if title_elem is not None and title_elem.text else ""

                url = ""
                link_elem = item.find("link")
                if link_elem is not None and link_elem.text:
                    url = link_elem.text
                else:
                    guid_elem = item.find("guid")
                    if guid_elem is not None:
                        url = guid_elem.text if guid_elem.text else guid_elem.get("isPermaLink", "")

                desc_elem = item.find("description")
                description = desc_elem.text if desc_elem is not None and desc_elem.text else ""

                content = ""
                content_elem = item.find("content:encoded", namespaces)
                if content_elem is not None and content_elem.text:
                    content = strip_html_tags(content_elem.text)

                categories: list[str] = []
                for cat_elem in item.findall("category"):
                    if cat_elem.text:
                        cat_text = cat_elem.text.strip()
                        categories.append(cat_text)

                image_url = ""
                thumbnail_elem = item.find("media:thumbnail", namespaces)
                if thumbnail_elem is not None:
                    image_url = thumbnail_elem.get("url", "")

                publication_date = None
                pub_date_elem = item.find("pubDate")
                if pub_date_elem is not None and pub_date_elem.text:
                    try:
                        publication_date = parsedate_to_datetime(pub_date_elem.text)
                    except (ValueError, TypeError):
                        pass

                article = Article(
                    title=title,
                    url=url,
                    publication_date=publication_date,
                    source=source,
                    content=content,
                    description=description,
                    categories=categories,
                    image_url=image_url,
                )
                articles.append(article)

            except Exception as e:
                logger.warning(
                    "Error parsing RSS item",
                    feed_url=feed_url,
                    error=str(e),
                    exc_info=True,
                )
                continue

        logger.info(
            "Parsed RSS feed",
            feed_url=feed_url,
            source=source,
            article_count=len(articles),
        )

    except ET.ParseError as e:
        logger.error(
            "XML parsing error",
            feed_url=feed_url,
            source=source,
            error=str(e),
            exc_info=True,
        )
    except Exception as e:
        logger.error(
            "Error fetching RSS feed",
            feed_url=feed_url,
            source=source,
            error=str(e),
            exc_info=True,
        )

    return articles


def collect_articles_from_feeds() -> list[Article]:
    all_articles = []

    for source_key, source_config in feed_sources.items():
        base_url = source_config["base_url"]
        feed_urls = source_config["sources"]

        logger.info(
            "Collecting articles from RSS feeds",
            source=base_url,
            sources_len=len(feed_urls),
        )

        for feed_url in feed_urls:
            logger.info("Fetching RSS feed", feed_url=feed_url, source=base_url)
            articles = parse_rss_feed(feed_url, base_url)
            all_articles.extend(articles)
            logger.info(
                "Fetched articles from feed",
                feed_url=feed_url,
                article_count=len(articles),
                source=base_url,
            )

    logger.info(
        "Finished collecting articles from RSS feeds",
        total_articles=len(all_articles),
    )

    return all_articles


if __name__ == "__main__":
    articles = collect_articles_from_feeds()
    logger.info("Articles", articles=articles)
