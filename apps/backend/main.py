from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.embed import get_recent_articles, process_all_articles
from src.logger import get_logger, setup_logging
from src.rag import answer_query

setup_logging()
logger = get_logger(__name__)

app = FastAPI(title="Gossip API", version="1.0.0")

logger.info("Starting Gossip API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/process-articles")
async def process_articles():
    try:
        articles = process_all_articles()
        return {"status": "success", "articles": articles}
    except Exception as e:
        logger.error("Error processing articles", error=str(e), exc_info=True)
        return {"status": "error", "message": str(e)}


@app.get("/articles")
async def get_articles(limit: int = 100):
    try:
        articles = get_recent_articles(limit=limit)
        return {"status": "success", "articles": articles}
    except Exception as e:
        logger.error("Error fetching articles", error=str(e), exc_info=True)
        return {"status": "error", "message": str(e), "articles": []}


class QueryRequest(BaseModel):
    query: str
    top_k: int = 8


@app.post("/query")
async def query(request: QueryRequest):
    try:
        answer = answer_query(request.query, top_k=request.top_k)
        return {"answer": answer}
    except Exception as e:
        logger.error("Error answering query", error=str(e), exc_info=True)
        return {"status": "error", "message": str(e)}
