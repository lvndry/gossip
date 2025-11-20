from openai import OpenAI

from .embed import embed_text
from .logger import get_logger
from .qdrant_client import COLLECTION_NAME, get_qdrant_client

logger = get_logger(__name__)

openai_client = OpenAI()
qdrant = get_qdrant_client()


def search_similar_chunks(query_embedding: list[float], limit: int = 8) -> list[dict]:
    try:
        query_response = qdrant.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            limit=limit,
        )

        chunks = []
        for point in query_response.points:
            payload = point.payload or {}
            score = point.score
            chunks.append(
                {
                    "text": payload.get("chunk_text", ""),
                    "article_title": payload.get("article_title", ""),
                    "article_url": payload.get("article_url", ""),
                    "source": payload.get("source", ""),
                    "score": score,
                }
            )

        logger.debug("Found similar chunks", count=len(chunks))
        return chunks

    except Exception as e:
        logger.error("Error searching similar chunks", error=str(e), exc_info=True)
        raise


def answer_query(query: str, top_k: int = 8):
    logger.info("Embedding query", query=query)
    query_embedding = embed_text(query)

    logger.info("Searching for similar chunks", top_k=top_k)
    chunks = search_similar_chunks(query_embedding, limit=top_k)

    if not chunks:
        logger.warning("No similar chunks found for query", query=query)
        return "I couldn't find any relevant articles to answer your question."

    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Article {i}] {chunk['article_title']}\n"
            f"Source: {chunk['source']}\n"
            f"Content: {chunk['text']}\n"
        )

    context = "\n".join(context_parts)

    try:
        response = openai_client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a friendly gossip assistant with a cheeky sense of humor. "
                        "Answer questions based on provided article in a warm, "
                        "conversational tone. You can be playful and a bit cheeky, but always "
                        "remain respectful about the people mentioned. Bring in some light gossip "
                        "humor while staying accurate to the information in the articles. "
                        "Always mention the source of information (the article source) "
                        "If the articles don't contain enough information, say so in a friendly way."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Question: {query}\n\nRelevant articles:\n{context}\n\nAnswer:",
                },
            ],
            temperature=1,
            stream=False,
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error("Error generating answer", error=str(e), exc_info=True)
        return "I encountered an error while generating the answer."
