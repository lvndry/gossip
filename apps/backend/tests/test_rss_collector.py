"""Tests for RSS collector functionality."""

from src.rss_collector import (
    HTMLTextExtractor,
    collect_articles_from_feeds,
    parse_rss_feed,
    strip_html_tags,
)


class TestHTMLTextExtractor:
    """Test the HTML text extraction functionality."""

    def test_extract_simple_text(self):
        """Test extracting text from simple HTML."""
        extractor = HTMLTextExtractor()
        extractor.feed("<p>Hello World</p>")
        assert extractor.get_text() == "Hello World"

    def test_extract_nested_html(self):
        """Test extracting text from nested HTML."""
        extractor = HTMLTextExtractor()
        extractor.feed("<div><p>Hello</p><p>World</p></div>")
        assert extractor.get_text() == "Hello World"

    def test_extract_with_attributes(self):
        """Test extracting text ignoring HTML attributes."""
        extractor = HTMLTextExtractor()
        extractor.feed('<p class="test" id="para">Content</p>')
        assert extractor.get_text() == "Content"

    def test_empty_html(self):
        """Test extracting from empty HTML."""
        extractor = HTMLTextExtractor()
        extractor.feed("")
        assert extractor.get_text() == ""


class TestStripHTMLTags:
    """Test the strip_html_tags function."""

    def test_strip_simple_tags(self):
        """Test stripping simple HTML tags."""
        html = "<p>Hello World</p>"
        result = strip_html_tags(html)
        assert result == "Hello World"

    def test_strip_complex_html(self):
        """Test stripping complex HTML with multiple tags."""
        html = "<div><h1>Title</h1><p>Paragraph</p></div>"
        result = strip_html_tags(html)
        assert "Title" in result
        assert "Paragraph" in result

    def test_strip_empty_string(self):
        """Test stripping empty string."""
        assert strip_html_tags("") == ""

    def test_strip_none(self):
        """Test stripping None value."""
        assert strip_html_tags(None) == ""

    def test_strip_with_entities(self):
        """Test stripping HTML with entities."""
        html = "<p>Hello &amp; goodbye</p>"
        result = strip_html_tags(html)
        assert "Hello" in result


class TestParseRSSFeed:
    """Test RSS feed parsing functionality."""

    def test_parse_valid_rss_feed(self, mocker, sample_rss_xml):
        """Test parsing a valid RSS feed."""
        # Mock the LinkupClient
        mock_linkup = mocker.patch("src.rss_collector.linkup_client")
        mock_response = mocker.MagicMock()
        mock_response.raw_html = sample_rss_xml
        mock_linkup.fetch.return_value = mock_response

        articles = parse_rss_feed("https://example.com/feed", "example.com")

        assert len(articles) > 0
        article = articles[0]
        assert article.title == "Test Article Title"
        assert article.url == "https://example.com/article1"
        assert article.source == "example.com"
        assert "Technology" in article.categories
        assert "News" in article.categories

    def test_parse_empty_feed(self, mocker):
        """Test parsing an empty RSS feed."""
        mock_linkup = mocker.patch("src.rss_collector.linkup_client")
        mock_response = mocker.MagicMock()
        mock_response.raw_html = ""
        mock_linkup.fetch.return_value = mock_response

        articles = parse_rss_feed("https://example.com/feed", "example.com")
        assert len(articles) == 0

    def test_parse_invalid_xml(self, mocker):
        """Test parsing invalid XML."""
        mock_linkup = mocker.patch("src.rss_collector.linkup_client")
        mock_response = mocker.MagicMock()
        mock_response.raw_html = "This is not valid XML"
        mock_linkup.fetch.return_value = mock_response

        articles = parse_rss_feed("https://example.com/feed", "example.com")
        assert len(articles) == 0

    def test_parse_feed_with_missing_fields(self, mocker):
        """Test parsing RSS feed with missing optional fields."""
        rss_xml = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <item>
            <title>Minimal Article</title>
            <link>https://example.com/minimal</link>
        </item>
    </channel>
</rss>"""

        mock_linkup = mocker.patch("src.rss_collector.linkup_client")
        mock_response = mocker.MagicMock()
        mock_response.raw_html = rss_xml
        mock_linkup.fetch.return_value = mock_response

        articles = parse_rss_feed("https://example.com/feed", "example.com")

        assert len(articles) == 1
        article = articles[0]
        assert article.title == "Minimal Article"
        assert article.url == "https://example.com/minimal"
        assert article.publication_date is None
        assert article.categories == []

    def test_parse_feed_with_invalid_date(self, mocker):
        """Test parsing RSS feed with invalid publication date."""
        rss_xml = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <item>
            <title>Test Article</title>
            <link>https://example.com/article</link>
            <pubDate>Invalid Date Format</pubDate>
        </item>
    </channel>
</rss>"""

        mock_linkup = mocker.patch("src.rss_collector.linkup_client")
        mock_response = mocker.MagicMock()
        mock_response.raw_html = rss_xml
        mock_linkup.fetch.return_value = mock_response

        articles = parse_rss_feed("https://example.com/feed", "example.com")

        assert len(articles) == 1
        assert articles[0].publication_date is None


class TestCollectArticlesFromFeeds:
    """Test the collect_articles_from_feeds function."""

    def test_collect_articles_success(self, mocker, sample_rss_xml):
        """Test successful article collection from feeds."""
        mock_linkup = mocker.patch("src.rss_collector.linkup_client")
        mock_response = mocker.MagicMock()
        mock_response.raw_html = sample_rss_xml
        mock_linkup.fetch.return_value = mock_response

        articles = collect_articles_from_feeds()

        # Should collect from multiple feeds
        assert isinstance(articles, list)
        # We have 2 sources with 5 feeds each = 10 feeds total
        # Each feed returns 1 article from our mock
        assert len(articles) == 10

    def test_collect_articles_handles_errors(self, mocker):
        """Test that collection continues even if some feeds fail."""
        mock_linkup = mocker.patch("src.rss_collector.linkup_client")

        # First call succeeds, second fails, third succeeds
        mock_response_success = mocker.MagicMock()
        mock_response_success.raw_html = """<?xml version="1.0"?>
<rss version="2.0">
    <channel>
        <item>
            <title>Test</title>
            <link>https://example.com/test</link>
        </item>
    </channel>
</rss>"""

        mock_linkup.fetch.side_effect = [
            mock_response_success,
            Exception("Network error"),
            mock_response_success,
        ]

        # Should not raise exception, just log and continue
        articles = collect_articles_from_feeds()
        assert isinstance(articles, list)
