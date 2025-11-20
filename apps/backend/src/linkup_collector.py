import os

from dotenv import load_dotenv
from linkup import LinkupClient, LinkupSearchStructuredResponse
from pydantic import BaseModel

from .article import Article
from .logger import get_logger

load_dotenv()

logger = get_logger(__name__)

linkup_client = LinkupClient(api_key=os.getenv("LINKUP_API_KEY"))


class LinkupSearchStructuredResponseSchema(BaseModel):
    results: list[Article]


def collect_articles_from_search(
    max_results: int = 100,
) -> list[Article]:
    query = "You are a web scraper. Crawl and extract the most crispy celebrity gossip articles from public.fr and vsd.fr. Prioritize breaking stories, gossips, exclusives, controversies, scandals, relationship reveals, legal issues, and viral social media moments. Include the title, source, url, publication date, description, and content of the article."
    include_domains = ["vsd.fr", "public.fr"]

    logger.info(
        "Collecting articles from linkup search",
        query=query,
        max_results=max_results,
        include_domains=include_domains,
    )

    try:
        response: LinkupSearchStructuredResponse = linkup_client.search(
            query=query,
            depth="deep",
            output_type="structured",
            include_images=False,
            include_domains=include_domains,
            include_sources=True,
            structured_output_schema=LinkupSearchStructuredResponseSchema,
            # from_date=(datetime.datetime.now() - timedelta(days=90)),
        )

        logger.info("Linkup search response", response=response.data.results)

        articles: list[Article] = response.data.results

        return articles

    except Exception as e:
        logger.error(
            "Error collecting articles from linkup search",
            query=query,
            error=str(e),
            exc_info=True,
        )
        return []


if __name__ == "__main__":
    articles = collect_articles_from_search()
    logger.info("Articles collected", article_count=len(articles))
    logger.info("Articles", articles=articles)
