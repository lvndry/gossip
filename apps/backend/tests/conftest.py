# Test configuration and fixtures
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from src.article import Article


@pytest.fixture
def sample_article():
    """Create a sample article for testing."""
    return Article(
        title="Test Article",
        url="https://example.com/article",
        publication_date=datetime(2024, 1, 1, 12, 0, 0),
        source="example.com",
        content="This is a test article content with enough text to be chunked properly.",
        description="Test description",
        categories=["test", "example"],
        image_url="https://example.com/image.jpg",
    )


@pytest.fixture
def sample_rss_xml():
    """Sample RSS feed XML for testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:media="http://search.yahoo.com/mrss/">
    <channel>
        <title>Test Feed</title>
        <item>
            <title>Test Article Title</title>
            <link>https://example.com/article1</link>
            <description>Test article description</description>
            <content:encoded><![CDATA[<p>This is the full content of the article.</p>]]></content:encoded>
            <category>Technology</category>
            <category>News</category>
            <media:thumbnail url="https://example.com/thumb.jpg"/>
            <pubDate>Mon, 01 Jan 2024 12:00:00 GMT</pubDate>
        </item>
    </channel>
</rss>"""


@pytest.fixture
def mock_openai_client(mocker):
    """Mock OpenAI client for testing."""
    mock_client = MagicMock()

    # Mock embeddings
    mock_embedding_response = MagicMock()
    mock_embedding_response.data = [MagicMock(embedding=[0.1] * 1536)]
    mock_client.embeddings.create.return_value = mock_embedding_response

    # Mock chat completions
    mock_completion_response = MagicMock()
    mock_completion_response.choices = [
        MagicMock(message=MagicMock(content="This is a test response"))
    ]
    mock_client.chat.completions.create.return_value = mock_completion_response

    return mock_client


@pytest.fixture
def mock_qdrant_client(mocker):
    """Mock Qdrant client for testing."""
    mock_client = MagicMock()

    # Mock query_points
    mock_point = MagicMock()
    mock_point.payload = {
        "chunk_text": "Test chunk text",
        "article_title": "Test Article",
        "article_url": "https://example.com/article",
        "source": "example.com",
    }
    mock_point.score = 0.95

    mock_query_response = MagicMock()
    mock_query_response.points = [mock_point]
    mock_client.query_points.return_value = mock_query_response

    # Mock scroll
    mock_scroll_point = MagicMock()
    mock_scroll_point.payload = {
        "article_title": "Test Article",
        "article_url": "https://example.com/article",
        "source": "example.com",
        "chunk_text": "Test content",
        "categories": ["test"],
        "image_url": "https://example.com/image.jpg",
        "publication_date": "2024-01-01T12:00:00",
    }
    mock_client.scroll.return_value = ([mock_scroll_point], None)

    # Mock upsert
    mock_client.upsert.return_value = None

    return mock_client


@pytest.fixture
def mock_linkup_client(mocker):
    """Mock Linkup client for testing."""
    mock_client = MagicMock()
    return mock_client


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    # Import here to avoid circular imports
    from main import app

    return TestClient(app)


@pytest.fixture(autouse=True)
def setup_env_vars(monkeypatch):
    """Set up environment variables for testing."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("LINKUP_API_KEY", "test-linkup-key")
    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
