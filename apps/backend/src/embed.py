import uuid
from typing import Any

from openai import OpenAI
from qdrant_client.models import PointStruct

from .logger import get_logger
from .qdrant_client import COLLECTION_NAME, ensure_collection_exists, get_qdrant_client
from .rss_collector import Article, collect_articles_from_feeds

logger = get_logger(__name__)

openai_client = OpenAI()
qdrant = get_qdrant_client()


def split_text_into_chunks(text: str, chunk_size: int = 1500, overlap: int = 200) -> list[dict]:
    chunks: list[dict] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(
            {
                "id": f"chunk_{len(chunks)}",
                "text": chunk.strip(),
            }
        )
        start = end - overlap
    return chunks


def embed_text(text: str) -> list[float]:
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small",
    )

    return response.data[0].embedding


def process_article(article: Article) -> int:
    text_to_chunk = article.content if article.content else article.description

    if not text_to_chunk or not text_to_chunk.strip():
        logger.warning(
            "Skipping article with no content or description",
            article_url=article.url,
            article_title=article.title,
        )
        return 0

    chunks = split_text_into_chunks(text_to_chunk)
    logger.debug(
        "Split article into chunks",
        article_url=article.url,
        chunk_count=len(chunks),
    )

    if not chunks:
        return 0

    points: list[PointStruct] = []
    for chunk_idx, chunk in enumerate(chunks):
        try:
            chunk_id = str(uuid.uuid4())
            embedding = embed_text(chunk["text"])

            metadata = {
                "article_title": article.title,
                "article_url": article.url,
                "source": article.source,
                "chunk_index": chunk_idx,
                "chunk_text": chunk["text"],
                "categories": article.categories,
                "image_url": article.image_url,
            }

            if article.publication_date:
                metadata["publication_date"] = article.publication_date.isoformat()

            point = PointStruct(
                id=chunk_id,
                vector=embedding,
                payload=metadata,
            )
            points.append(point)

        except Exception as e:
            logger.warning(
                "Error processing chunk",
                article_url=article.url,
                chunk_index=chunk_idx,
                error=str(e),
                exc_info=True,
            )
            continue

    if points:
        try:
            qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
            logger.info(
                "Stored article chunks in Qdrant",
                article_url=article.url,
                chunks_stored=len(points),
            )
        except Exception as e:
            logger.error(
                "Error storing chunks in Qdrant",
                article_url=article.url,
                error=str(e),
                exc_info=True,
            )
            raise

    return len(points)


def get_recent_articles(limit: int = 100) -> list[dict[str, Any]]:
    try:
        scroll_result = qdrant.scroll(
            collection_name=COLLECTION_NAME,
            limit=limit * 5,  # Fetch more to account for duplicates
            with_payload=True,
            with_vectors=False,
        )

        points = scroll_result[0] if scroll_result else []

        seen_urls: set[str] = set()
        articles: list[dict[str, Any]] = []

        for point in points:
            if not point.payload:
                continue

            article_url = point.payload.get("article_url", "")
            if article_url and article_url not in seen_urls:
                seen_urls.add(article_url)

                article_data = {
                    "title": point.payload.get("article_title", ""),
                    "url": article_url,
                    "source": point.payload.get("source", ""),
                    "description": point.payload.get("chunk_text", "")[:200] + "...",
                    "categories": point.payload.get("categories", []),
                    "image_url": point.payload.get("image_url"),
                    "publication_date": point.payload.get("publication_date"),
                }

                articles.append(article_data)

                if len(articles) >= limit:
                    break

        logger.info("Fetched recent articles", count=len(articles))
        return articles

    except Exception as e:
        logger.error(
            "Error fetching recent articles",
            error=str(e),
            exc_info=True,
        )
        return []


def process_all_articles() -> list[Article]:
    ensure_collection_exists()

    logger.info("Starting article collection and processing")
    articles = collect_articles_from_feeds()

    if not articles:
        logger.warning("No articles collected from RSS feeds")
        return []

    total_chunks = 0
    articles_processed = 0
    articles_failed = 0

    for article in articles:
        try:
            chunks_count = process_article(article)
            if chunks_count > 0:
                total_chunks += chunks_count
                articles_processed += 1
            else:
                articles_failed += 1
        except Exception as e:
            logger.error(
                "Error processing article",
                article_url=article.url,
                error=str(e),
                exc_info=True,
            )
            articles_failed += 1
            continue

    stats = {
        "articles_processed": articles_processed,
        "total_chunks": total_chunks,
        "articles_failed": articles_failed,
        "total_articles": len(articles),
    }

    logger.info("Finished processing articles", **stats)
    return articles


if __name__ == "__main__":
    process_all_articles()
