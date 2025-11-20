from qdrant_client.models import Distance, VectorParams

from qdrant_client import QdrantClient as QdrantClientBase

from .logger import get_logger

logger = get_logger(__name__)

_qdrant_client: QdrantClientBase | None = None


def get_qdrant_client(path: str = "qdrant.db") -> QdrantClientBase:
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClientBase(path=path)
    return _qdrant_client


COLLECTION_NAME = "gossip_articles"
# text-embedding-3-small dimension
EMBEDDING_DIM = 1536


def ensure_collection_exists() -> None:
    try:
        qdrant = get_qdrant_client()
        collections = qdrant.get_collections()
        collection_names = [col.name for col in collections.collections]

        if COLLECTION_NAME not in collection_names:
            qdrant.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
            )
            logger.info("Created Qdrant collection", collection_name=COLLECTION_NAME)
        else:
            logger.debug("Qdrant collection already exists", collection_name=COLLECTION_NAME)
    except Exception as e:
        logger.error(
            "Error ensuring collection exists",
            collection_name=COLLECTION_NAME,
            error=str(e),
            exc_info=True,
        )
        raise
