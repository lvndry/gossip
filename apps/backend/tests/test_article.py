"""Tests for the Article model."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from src.article import Article


class TestArticleModel:
    """Test the Article Pydantic model."""

    def test_create_article_with_all_fields(self):
        """Test creating an article with all fields."""
        article = Article(
            title="Test Article",
            url="https://example.com/article",
            publication_date=datetime(2024, 1, 1, 12, 0, 0),
            source="example.com",
            content="This is the article content.",
            description="This is the description.",
            categories=["tech", "news"],
            image_url="https://example.com/image.jpg",
        )

        assert article.title == "Test Article"
        assert article.url == "https://example.com/article"
        assert article.publication_date == datetime(2024, 1, 1, 12, 0, 0)
        assert article.source == "example.com"
        assert article.content == "This is the article content."
        assert article.description == "This is the description."
        assert article.categories == ["tech", "news"]
        assert article.image_url == "https://example.com/image.jpg"

    def test_create_article_with_required_fields_only(self):
        """Test creating an article with only required fields."""
        article = Article(
            title="Test Article",
            url="https://example.com/article",
            publication_date=None,
            source="example.com",
            content="Content",
        )

        assert article.title == "Test Article"
        assert article.url == "https://example.com/article"
        assert article.publication_date is None
        assert article.source == "example.com"
        assert article.content == "Content"
        assert article.description is None
        assert article.categories is None
        assert article.image_url is None

    def test_create_article_missing_required_field(self):
        """Test that creating an article without required fields raises error."""
        with pytest.raises(ValidationError):
            Article(
                title="Test Article",
                # Missing url, source, and content
            )

    def test_article_serialization(self):
        """Test article serialization to dict."""
        article = Article(
            title="Test Article",
            url="https://example.com/article",
            publication_date=datetime(2024, 1, 1, 12, 0, 0),
            source="example.com",
            content="Content",
            description="Description",
            categories=["tech"],
            image_url="https://example.com/image.jpg",
        )

        article_dict = article.model_dump()

        assert article_dict["title"] == "Test Article"
        assert article_dict["url"] == "https://example.com/article"
        assert article_dict["source"] == "example.com"
        assert article_dict["content"] == "Content"

    def test_article_json_serialization(self):
        """Test article JSON serialization."""
        article = Article(
            title="Test Article",
            url="https://example.com/article",
            publication_date=datetime(2024, 1, 1, 12, 0, 0),
            source="example.com",
            content="Content",
        )

        json_str = article.model_dump_json()

        assert isinstance(json_str, str)
        assert "Test Article" in json_str
        assert "example.com" in json_str

    def test_article_with_empty_categories(self):
        """Test article with empty categories list."""
        article = Article(
            title="Test Article",
            url="https://example.com/article",
            publication_date=None,
            source="example.com",
            content="Content",
            categories=[],
        )

        assert article.categories == []

    def test_article_with_special_characters(self):
        """Test article with special characters in fields."""
        article = Article(
            title="Test Article with émojis 🎉",
            url="https://example.com/article?param=value&other=123",
            publication_date=None,
            source="example.com",
            content="Content with spëcial çharacters!",
            description="Description with <html> tags",
        )

        assert "émojis" in article.title
        assert "🎉" in article.title
        assert "spëcial" in article.content
        assert "<html>" in article.description

    def test_article_equality(self):
        """Test article equality comparison."""
        article1 = Article(
            title="Test",
            url="https://example.com/1",
            publication_date=None,
            source="example.com",
            content="Content",
        )

        article2 = Article(
            title="Test",
            url="https://example.com/1",
            publication_date=None,
            source="example.com",
            content="Content",
        )

        assert article1 == article2

    def test_article_with_none_publication_date(self):
        """Test article with None publication date."""
        article = Article(
            title="Test",
            url="https://example.com/article",
            publication_date=None,
            source="example.com",
            content="Content",
        )

        assert article.publication_date is None
